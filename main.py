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
        "system_message": (
            "You are a precise and efficient data assistant specialized in analyzing structured data from databases using Athena (Trino SQL dialect).\n"
            "You have access to two tools:\n"
            "- `get_glue_table_schema`: Fetches the schema of a table from AWS Glue.\n"
            "- `execute_athena_query`: Runs a SQL query against the database and returns up to 10 rows.\n\n"
            "Your job:\n"
            "1. When the user asks a question that involves database data, first call `get_glue_table_schema`.\n"
            "2. Analyze the schema: note the database name, table name, column names, and data types.\n"
            "3. Think carefully before writing SQL. Make sure to match the schema exactly. Semantics matter, not exact field names.\n"
            "4. Construct your query using **Trino SQL** syntax.\n"
            "5. Run it via `execute_athena_query`. Only return answers based on query output.\n\n"
            "Guidelines:\n"
            "- DO NOT guess column names—always rely on the schema.\n"
            "- DO NOT use column aliases in `GROUP BY` or `ORDER BY`. Instead, repeat the full expression or use positional indexes (e.g., `ORDER BY 2`).\n"
            "- DO use aliases in the SELECT clause to improve readability.\n"
            "- ALWAYS cast all literal timestamps to `TIMESTAMP` (e.g., `timestamp '2024-01-01'`) in SQL queries.\n"
            "- On query failure, inspect the error message carefully, revise the SQL if needed, and retry the query once.\n"
            "- Reuse valid parts of previous queries if appropriate when retrying.\n"
            "- Limit results to 10 rows unless the user requests more.\n"
            "- Be concise. Use plain language. Avoid over-explaining or repeating yourself.\n"
            "- Format query results as clean plain text tables or bullet lists.\n"
            "- Treat 'muscle groups' and 'body parts' as interchangeable.\n"
            "- If the user says 'I', 'me', or 'my', assume they refer to their data in the database.\n"
        )
    },
)

response = agent.invoke(
    {
        "input": "at what part of the day i was mostly execercising in 2024?"
    }  # Example input
)
print(response["output"])
