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

# Cache for tool results to avoid repeated calls
_tool_cache = {}


@tool
def get_glue_table_schema(input: str) -> str:
    """Return schemas for workouts, exercises, and sets tables: table name, column names, types, and comments."""
    cache_key = "glue_schema"
    if cache_key in _tool_cache:
        return _tool_cache[cache_key]

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

    _tool_cache[cache_key] = "\n\n".join(result)
    return _tool_cache[cache_key]


@tool
def execute_athena_query(input: str) -> str:
    """Executes an Athena SQL query and returns up to 10 rows. Returns error info if the query fails."""
    # Add basic error handling for common mistakes
    if "DATE_FORMAT" in input:
        return f"ERROR: DATE_FORMAT is not supported in Trino. Use format_datetime(from_unixtime(...), 'format') instead.\nQuery:\n{input}"
    if "unix_timestamp" in input.lower():
        return f"ERROR: unix_timestamp is not supported in Trino. Use from_unixtime(...) instead.\nQuery:\n{input}"
    if 'LIKE "' in input:
        return f"ERROR: Use single quotes for string literals in LIKE clauses. Double quotes are for identifiers only.\nQuery:\n{input}"  # Check for any string equality comparisons - always enforce LIKE for strings
    import re

    # Look for patterns like column_name = 'value' for string columns (but not numeric comparisons)
    string_equality_pattern = r"[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*'[^']*'"
    if re.search(string_equality_pattern, input):
        matches = re.findall(string_equality_pattern, input)
        return f"ERROR: Always use LIKE with wildcards for string matching, never use exact equality (=). Found: {matches}\nExample: WHERE LOWER(title) LIKE LOWER('%Squat%') AND LOWER(equipment_category) LIKE LOWER('%barbell%')\nQuery:\n{input}"

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


tools = [get_glue_table_schema, execute_athena_query]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={
        "system_message": """
You are a data assistant specialized in analyzing AWS Glue tables via Athena using Trino SQL syntax.

CRITICAL: You have access to TWO tools:
- get_glue_table_schema: retrieves schemas for workouts, exercises, and sets tables
- execute_athena_query: runs SQL queries against the Athena database

ALWAYS start by calling get_glue_table_schema first to get the exact table and column names.

FORBIDDEN FUNCTIONS (Will cause query failure):
- DATE_FORMAT(...) (MySQL function, NOT Trino)
- unix_timestamp(...)
- DATE_TRUNC(...) for timestamp comparisons

REQUIRED Trino Functions for Timestamps:
- from_unixtime(bigint_column) - converts UNIX timestamp to timestamp
- format_datetime(from_unixtime(column), '%H:%i') - for HH:MM format
- hour(from_unixtime(column)) - extract hour
- minute(from_unixtime(column)) - extract minute
- year(from_unixtime(column)) - extract year

Rules:
1. ALWAYS call get_glue_table_schema first to get exact table names
2. Use only columns from the schema - never guess.
3. Use comments from the schema to understand column types and meanings.
4. For BIGINT UNIX timestamps, wrap in from_unixtime(...)
5. For date filtering: date(from_unixtime(column)) >= date('YYYY-MM-DD')
6. For time formatting: format_datetime(from_unixtime(column), '%H:%i')
7. No column aliases in GROUP BY/ORDER BY - use full expressions
8. If query fails, read error and fix syntax issues
9. Use proper Trino table name syntax: "database_name"."table_name"
10. MANDATORY: Always use LOWER() for case-insensitive string comparisons
11. MANDATORY: NEVER use exact equality (=) for ANY string values - ALWAYS use LIKE with wildcards
12. MANDATORY: String matching format: WHERE LOWER(column) LIKE LOWER('%search_term%')
13. REASON: Exercise names, equipment categories, and other strings can have slight variations
14. NEVER use ESCAPE clause - it's not supported in Trino. Use LIKE with proper wildcards or regexp_like() for complex patterns
15. ALWAYS use single quotes for string literals, NEVER double quotes. Double quotes are for identifiers only.
16. As a response return the query result in a human-readable format, not JSON or code blocks.

CORRECT EXAMPLES:
- WHERE LOWER(e.title) LIKE LOWER('%Squat%') AND LOWER(e.equipment_category) LIKE LOWER('%barbell%')
- WHERE LOWER(e.muscle_group) LIKE LOWER('%chest%')

INCORRECT EXAMPLES:
- WHERE e.title = 'Squat' (exact match, case-sensitive)
- WHERE e.equipment_category = 'barbell' (exact match, case-sensitive)
- WHERE LOWER(e.title) = LOWER('Squat') (exact match, even if case-insensitive)
"""
    },
)

response = agent.invoke(
    {
        "input": "On what day I did my latest Squat with 100 kg weight? Please provide the date in YYYY-MM-DD format. Use the workouts table and filter by equipment_category = 'barbell'.",
    }
)

print("Final Response:")
print(response)
