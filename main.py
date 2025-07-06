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


tools = [get_glue_table_schema]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={
        "system_message": (
            "You are a precise and concise assistant specialized in database schemas."
            "Your job is to return schema information in a clear, bullet-pointed format."
            "Guidelines:"
            "- Only use the `get_glue_table_schema` tool when asked about database or table schemas."
            "- `get_glue_table_schema` tool returns a valid database and table name, use those in your answers."
            "- Never make assumptions. Use only the tool output."
            "- Always return:"
            "  • Database name"
            "  • Table name"
            "  • List of column names (bullet points)"
            "- Do not repeat thoughts or the same action multiple times."
            "- Format the final answer cleanly and do not add commentary."
        )
    },
)

response = agent.invoke(
    {"input": "Get the schema for the workout table in the workouts database."}
)
print(response["output"])
