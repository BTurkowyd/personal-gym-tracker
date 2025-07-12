from langchain_core.tools import tool
from .lambda_client import invoke_lambda
import json
from .config import region, model_name, model_kwargs
from langchain_aws import ChatBedrock

_tool_cache = {}


@tool
def get_glue_table_schema(input: str) -> str:
    """Return schemas for workouts, exercises, and sets tables: table name, column names, types, and comments."""
    cache_key = "glue_schema"
    if cache_key in _tool_cache:
        return _tool_cache[cache_key]
    response = invoke_lambda("GetGlueTableSchema", b"{}")
    body = response.get("body") or json.loads(response["body"])
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
    final_result = "\n\n".join(result)
    _tool_cache[cache_key] = final_result
    return final_result


@tool
def execute_athena_query(input: str) -> str:
    """Execute a SQL query on AWS Athena and return the results as a formatted string."""
    import re

    # ...existing validation logic...
    payload = {"query": input}
    response = invoke_lambda(
        "ExecuteAthenaQuery",
        json.dumps(payload).encode("utf-8"),
    )
    raw_body = response.get("Payload", "").strip() if isinstance(response, dict) else ""
    if not raw_body:
        return f"ERROR: Empty response from Lambda for query:\n{input}"
    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError:
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
    formatted_rows = "\n".join(", ".join(row) for row in rows[1:])
    return f"Results for query:\n{input}\n\n{formatted_rows}"


tools = [get_glue_table_schema, execute_athena_query]

llm = ChatBedrock(model=model_name, region=region, model_kwargs=model_kwargs)
llm_with_tools = llm.bind_tools([get_glue_table_schema, execute_athena_query])
