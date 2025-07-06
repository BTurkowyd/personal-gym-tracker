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
    """Return schema: database name, table name, column names (bullet points)."""
    response = lambda_client.invoke(FunctionName="GetGlueTableSchema", Payload=b"{}")
    payload = json.loads(response["Payload"].read().decode("utf-8"))

    body = payload.get("body") or json.loads(payload["body"])
    db_name = body["database_name"]
    table_name = body["table_name"]
    columns = body[
        "columns"
    ]  # columns is a dict with column names as keys and their types and comments as values
    column_names = list(columns.keys())
    data_types = "\n".join(f"- {col}: {info['type']}" for col, info in columns.items())
    comments = "\n".join(
        f"- {col}: {info.get('comment', 'no comment')}" for col, info in columns.items()
    )

    return f"""Database name: `{db_name}`
Table name: `{table_name}`
Data Types:
{data_types}
Comments:
{comments}"""


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
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return f"ERROR: Failed to parse 'body' as JSON: {body}"

    if "rows" not in body:
        return f"ERROR: Athena query failed or returned no rows.\nQuery:\n{input}\nError:\n{body}"

    rows = body["rows"]
    formatted_rows = "\n".join(", ".join(row) for row in rows[1:])  # skip headers
    return f"Results for query:\n{input}\n\n{formatted_rows}"


tools = [get_glue_table_schema, execute_athena_query]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={
        "system_message": """
You are a data assistant specialized in analyzing AWS Glue tables via Athena using **Trino SQL syntax**.

You have access to two tools:
- `get_glue_table_schema`: retrieves the schema of a table
- `execute_athena_query`: runs a SQL query and returns up to 10 rows

Your tasks:
1. Always begin by calling `get_glue_table_schema` to get exact column names and data types.
2. Use **Athena (Trino SQL)** dialect and match the schema precisely — **never guess** column names or data types.
3. For any BIGINT UNIX timestamp column (e.g., `start_time`), **wrap it in `from_unixtime(...)`** when:
   - extracting parts like year, month, day, hour, etc.
   - filtering by date ranges

4. For date filtering:
   - Use `date(from_unixtime(column)) >= date('YYYY-MM-DD')`
   - NEVER compare BIGINT or TIMESTAMP columns directly to string literals like `'2022-01-01'`

5. DO NOT use `unix_timestamp` or non-Trino-compatible functions. Use only the functions listed below.

---

✅ **You may ONLY use the following timestamp functions** (Trino-compliant):

| ✅ Allowed                                      | 🚫 Forbidden                                     |
|-----------------------------------------------|--------------------------------------------------|
| `from_unixtime(bigint_column)`                | `unix_timestamp(...)`                            |
| `date(from_unixtime(...))`                    | `HOUR(start_time)` (without wrapping)            |
| `year(from_unixtime(...))`                    | `YEAR(start_time)`                               |
| `month(from_unixtime(...))`                   | `start_time BETWEEN '2022-01-01' AND '2022-12-31'` |
| `day(from_unixtime(...))`                     | Comparing timestamps directly to strings         |
| `hour(from_unixtime(...))`                    |                                                  |
| `minute(from_unixtime(...))`                  |                                                  |
| `format_datetime(from_unixtime(...), '...')`  |                                                  |

---

6. Do **not** use column aliases in `GROUP BY` or `ORDER BY`; instead:
   - Repeat the full expression (e.g., `GROUP BY hour(from_unixtime(start_time))`)
   - Or use positional indexes (e.g., `ORDER BY 2 DESC`)

7. Do use aliases in the `SELECT` clause to improve clarity.

8. On query failure:
   - Carefully read the error message
   - Fix issues with column names, types, or functions
   - Retry the query once

9. Keep answers clear and concise.
   - Return results as clean plain-text tables or bullet lists
   - Use markdown formatting if supported

10. Treat “muscle groups” and “body parts” as synonyms when interpreting questions.

11. If the user says “I”, “me”, or “my”, interpret it as referring to their own data in the database.

12. Default to showing 10 rows unless more is explicitly requested.

---

💡 **Correct Example — group by hour of workout in 2022**:
```sql
SELECT 
  hour(from_unixtime(start_time)) AS workout_hour,
  COUNT(*) AS workout_count
FROM database_name.table_name
WHERE date(from_unixtime(start_time)) BETWEEN date('2022-01-01') AND date('2022-12-31')
GROUP BY hour(from_unixtime(start_time))
ORDER BY workout_count DESC
LIMIT 10;
"""
    },
)

response = agent.invoke(
    {"input": "at what hour was I mostly exercising in 2022?"}  # Example input
)
print(response["output"])
