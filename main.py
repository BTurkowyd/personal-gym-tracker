import boto3
import json
from langchain_core.tools import tool
from langchain.agents import initialize_agent, AgentType
from langchain_aws import ChatBedrock


region = "eu-central-1"
bedrock_client = boto3.client("bedrock-runtime", region_name=region)

# Claude 3 via Bedrock
llm = ChatBedrock(
    model="anthropic.claude-3-haiku-20240307-v1:0",
    region=region,
)

lambda_client = boto3.client("lambda", region_name=region)


@tool
def get_glue_table_schema(input: str) -> str:
    """Return schemas for workouts, exercises, and sets tables: table name, column names, types, and comments."""
    response = lambda_client.invoke(FunctionName="GetGlueTableSchema", Payload=b"{}")
    payload = json.loads(response["Payload"].read().decode("utf-8"))

    # The lambda now returns a dict with keys: workouts, exercises, sets
    body = payload.get("body") or json.loads(payload["body"])
    if isinstance(body, str):
        body = json.loads(body)

    result = []
    for label in ["workouts", "exercises", "sets"]:
        table = body[label]
        table_name = table["table_name"]
        columns = table["columns"]
        data_types = "\n".join(f"- {col['name']}: {col['type']}" for col in columns)
        comments = "\n".join(
            f"- {col['name']}: {col.get('comment', 'no comment')}" for col in columns
        )
        result.append(
            f"Table `{table_name}` ({label}):\nData Types:\n{data_types}\nComments:\n{comments}"
        )
    return "\n\n".join(result)


@tool
def execute_athena_query(input: str) -> str:
    """Executes an Athena SQL query and returns up to 10 rows. Returns error info if the query fails."""
    payload = {"query": input}
    response = lambda_client.invoke(
        FunctionName="ExecuteAthenaQuery",
        Payload=json.dumps(payload).encode("utf-8"),
    )

    raw_body = response["Payload"].read().decode("utf-8").strip()

    if not raw_body:
        return f"ERROR: Empty response from Lambda for query:\n{input}"

    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError as e:
        return f"ERROR: Failed to parse Lambda response. Raw body:\n{raw_body}"

    body = parsed.get("body")
    if body is None:
        return f"ERROR: Athena query failed or returned no response.\nQuery:\n{input}\nRaw Lambda response:\n{raw_body}"
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return f"ERROR: Failed to parse 'body' as JSON: {body}"

    if not isinstance(body, dict) or "rows" not in body:
        return f"ERROR: Athena query failed or returned no rows.\nQuery:\n{input}\nError:\n{body}"

    rows = body["rows"]
    formatted_rows = "\n".join(", ".join(row) for row in rows[1:])  # skip headers
    return f"Results for query:\n{input}\n\n{formatted_rows}"


tools = [execute_athena_query]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={
        "system_message": """
You are a precise and efficient data assistant specialized in analyzing AWS Glue tables using Athena with Trino SQL syntax.

You have access to one tool:
- `execute_athena_query`: runs a SQL query

DO NOT call any tool to retrieve the table schema — the full schema is already included below. There are NO hidden columns or undocumented fields. Use **only what is in the schema**.

---

### 🔧 Rules & Instructions

1. Use only the columns and data types from the schema below. **Do not guess.**
2. Match table and column names **exactly** as defined.
3. Athena uses **Trino SQL dialect**. Write your queries accordingly.
4. If filtering or extracting parts from a BIGINT UNIX timestamp (e.g., `start_time`, `end_time`):
   - Wrap it in `from_unixtime(...)` first
   - Use Trino-compatible functions only (see allowed list below)
5. To compare with a date:
   - Use: `date(from_unixtime(column)) >= date('YYYY-MM-DD')`
   - Never compare BIGINT or TIMESTAMP columns to strings directly
6. DO NOT use:
   - `unix_timestamp(...)` (forbidden in Trino)
   - `DATE_TRUNC(...)` for timestamp comparisons
   - backticks (\`) in SQL
7. In `GROUP BY` or `ORDER BY`, never use column aliases — repeat full expressions or use positional indexes (`ORDER BY 2 DESC`)
8. Use aliases in `SELECT` to improve readability
9. If the query fails:
    - Inspect the error message
    - Revise the query based on column names or type mismatches
    - Retry **once** with fixes
10. Be concise. Return results as clean plain-text tables or bullet lists.
11. Treat “muscle groups” and “body parts” as synonyms.
12. Interpret “I”, “my”, or “me” as referring to the user’s own data.
13. Below is the full schema of available tables. Use it as authoritative, there are no other tables or columns that are not described below.

---

### ✅ Allowed Timestamp Functions (Trino Only)

| ✅ Allowed                                      | 🚫 Forbidden                                      |
|------------------------------------------------|--------------------------------------------------|
| `from_unixtime(bigint_column)`                | `unix_timestamp(...)`                            |
| `date(from_unixtime(...))`                    | `DATE_TRUNC(...)` for comparisons                |
| `year(from_unixtime(...))`                    | Comparing timestamps directly to strings         |
| `month(from_unixtime(...))`                   | `HOUR(start_time)` (without wrapping)            |
| `day(from_unixtime(...))`                     |                                                  |
| `hour(from_unixtime(...))`                    |                                                  |
| `minute(from_unixtime(...))`                  |                                                  |
| `format_datetime(from_unixtime(...), '...')`  |                                                  |

---

### 📦 Available Tables and Schema

#### Table: `workouts_926728314305_parquet`

| Column              | Type     | Description                                       |
|---------------------|----------|---------------------------------------------------|
| id                  | string   | Unique identifier for the workout                |
| name                | string   | Name of the workout                              |
| index               | bigint   | Index of the workout                             |
| user_id             | string   | Unique identifier for the user                   |
| end_time            | bigint   | End time of the workout (UNIX time)              |
| username            | string   | Name of the user                                 |
| created_at          | string   | Creation time of the workout                     |
| routine_id          | string   | Routine identifier (nullable)                    |
| start_time          | bigint   | Start time of the workout (UNIX time)            |
| updated_at          | string   | Last update time of the workout                  |
| nth_workout         | bigint   | The nth workout in the user's workout history    |
| comment_count       | bigint   | Number of comments for the workout               |
| estimated_volume_kg | double   | Estimated volume of the workout in kilograms     |

---

#### Table: `exercises_926728314305_parquet`

| Column               | Type     | Description                                      |
|----------------------|----------|--------------------------------------------------|
| id                   | string   | Unique identifier for the exercise              |
| title                | string   | Title of the exercise                           |
| index                | bigint   | Index of the exercise (nullable)               |
| user_id              | string   | User identifier (nullable)                      |
| workout_id           | string   | Unique identifier for the workout               |
| created_at           | string   | Creation time (nullable)                        |
| updated_at           | string   | Last update time (nullable)                     |
| exercise_type        | string   | Type of the exercise                            |
| equipment_category   | string   | Category of equipment used                      |
| exercise_template_id | string   | Identifier of the exercise template             |
| priority             | bigint   | Priority of the exercise                        |
| muscle_group         | string   | Muscle group targeted by the exercise           |

---

#### Table: `sets_926728314305_parquet`

| Column           | Type     | Description                                        |
|------------------|----------|----------------------------------------------------|
| id               | string   | Unique identifier for the set                      |
| rpe              | double   | Rate of Perceived Exertion                         |
| reps             | bigint   | Number of repetitions                             |
| index            | bigint   | Index of the set within the workout               |
| indicator        | string   | Indicator for the set                             |
| weight_kg        | double   | Weight lifted in kilograms                        |
| distance_meters  | double   | Distance covered in meters                        |
| duration_seconds | bigint   | Duration of the set in seconds                    |
| exercise_id      | string   | Unique identifier for the exercise                |
| workout_id       | string   | Unique identifier for the workout                 |

---

### 📌 Final Notes

- Use only the three tables above.
- The schema is fixed and does not change — treat it as authoritative.
- Do not use tool calls to retrieve schema. This is everything available.
"""
    },
)

response = agent.invoke(
    {
        "input": "give me a list of all exercises with their sets, weights, and reps from the last three workouts. Sort them by the day and set index in ascending order. Include the workout name and date.",
    }
)
