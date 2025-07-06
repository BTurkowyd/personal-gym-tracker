import boto3
import json
from langchain_core.tools import tool
from langchain.agents import initialize_agent, AgentType
from langchain_community.chat_models import BedrockChat


region = "eu-central-1"
bedrock_client = boto3.client("bedrock-runtime", region_name=region)

# Claude 3 via Bedrock
llm = BedrockChat(
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    region_name=region,
    client=bedrock_client,
)

lambda_client = boto3.client("lambda", region_name=region)


@tool
def get_glue_table_schema(input: str) -> str:
    """Get schema for a Glue table using format `database.table`."""
    try:
        database, table = input.split(".")
    except ValueError:
        return "Invalid format. Use 'database.table'."

    payload = {"database": database, "table": table}
    response = lambda_client.invoke(
        FunctionName="GetGlueTableSchema",
        Payload=json.dumps(payload).encode("utf-8"),
    )
    return response["Payload"].read().decode("utf-8")


tools = [get_glue_table_schema]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

response = agent.run("Get the schema for the workout table in the workouts database.")
print(response)
