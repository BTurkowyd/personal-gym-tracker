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
    columns = "\n".join(f"- {col}" for col in body["column_names"])

    return f"""Database name: `{db_name}`
Table name: `{table_name}`
Columns:
{columns}"""


@tool
def execute_athena_query(input: str) -> str:
    """Executes an Athena SQL query and returns up to 10 rows."""
    payload = {"query": input}
    response = lambda_client.invoke(
        FunctionName="ExecuteAthenaQuery",
        Payload=json.dumps(payload).encode("utf-8"),
    )
    raw_body = response["Payload"].read().decode("utf-8")
    body = json.loads(raw_body).get("body")
    if isinstance(body, str):
        body = json.loads(body)

    if "rows" not in body:
        return f"Query failed or returned no data: {body}"

    rows = body["rows"]
    formatted_rows = "\n".join(", ".join(row) for row in rows[1:])  # skip header row
    return f"Results for query:\n{body['query']}\n\n{formatted_rows}"


tools = [get_glue_table_schema, execute_athena_query]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={
        "system_message": (
            "You are a precise and efficient data assistant specialized in analyzing structured data from databases via Athena queries.\n"
            "You have access to:\n"
            "- A tool to fetch table schemas: `get_glue_table_schema`\n"
            "- A tool to run SQL queries: `execute_athena_query`\n\n"
            "Your job:\n"
            "1. If the user asks a question that requires data lookup, first call `get_glue_table_schema`.\n"
            "2. Think carefully about the SQL query needed.\n"
            "3. Use `execute_athena_query` to run the query.\n"
            "4. Return the answer based only on query output.\n\n"
            "Guidelines:\n"
            "- Do not guess schema, always use the schema tool.\n"
            "- Use correct column names from the schema.\n"
            "- Limit output to 10 rows unless asked otherwise.\n"
            "- Be concise. Do not over-explain. Do not repeat thoughts.\n"
            "- Format results clearly as plain text tables or bullet points.\n"
            "- When asked about body parts or muscle groups, use them interchangeably, both mean the same.\n"
            "- If the user is using `I`, `me`, or `my`, assume the user is referring to the data in the database.\n"
        )
    },
)

response = agent.invoke(
    {
        "input": "give me a summary of my latest recorded, what exercises did I do, how many sets, how many reps and how much weight, if available?"
    }  # Example input
)
print(response["output"])
