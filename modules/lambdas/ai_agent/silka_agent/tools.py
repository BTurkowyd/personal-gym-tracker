import os
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

    # Pass the user input as prompt to get relevant chunks
    payload = {"prompt": input}
    response = invoke_lambda("GetGlueTableSchema", json.dumps(payload).encode("utf-8"))
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

    # Add relevant chunks section
    relevant_chunks = body.get("relevant_chunks", [])
    if relevant_chunks:
        chunks_section = ["RELEVANT SIMILAR QUERIES FROM HISTORY:"]
        for i, chunk in enumerate(relevant_chunks, 1):
            chunks_section.append(f"{i}. User Query: {chunk['user_prompt']}")
            chunks_section.append(f"   SQL Query: {chunk['sql_query']}")
            chunks_section.append(f"   Tables Used: {', '.join(chunk['tables_used'])}")
            chunks_section.append(
                f"   Columns Used: {', '.join(chunk['columns_used'])}"
            )
            chunks_section.append(f"   Returned Rows: {chunk['returned_rows']}")
            chunks_section.append("")  # Empty line for spacing

        result.append("\n".join(chunks_section))
    else:
        result.append(
            "RELEVANT SIMILAR QUERIES FROM HISTORY:\nNo similar queries found in history."
        )

    final_result = "\n\n".join(result)
    _tool_cache[cache_key] = final_result
    return final_result


@tool
def execute_athena_query(input: str) -> str:
    """Execute a SQL query on AWS Athena and return the results as a formatted string."""

    payload = {"query": input}
    payload["user_prompt"] = os.getenv("PROMPT", "")

    response = invoke_lambda(
        "ExecuteAthenaQuery",
        json.dumps(payload).encode("utf-8"),
    )
    # response is a dict: {"statusCode": ..., "body": ...}
    status = response.get("statusCode")
    body = response.get("body")
    # If body is a string, try to parse as JSON
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except Exception:
            pass
    if status != 200:
        # Error from Lambda
        error_msg = body.get("error") if isinstance(body, dict) else body
        return (
            "\n==================== ATHENA QUERY ERROR ====================\n"
            f"ERROR: Lambda returned statusCode {status}.\n"
            f"FULL QUERY:\n{input}\n"
            f"ERROR CONTENT:\n{error_msg}\n"
            "==========================================================\n"
        )
    if not isinstance(body, dict) or "rows" not in body:
        return (
            "\n==================== ATHENA QUERY ERROR ====================\n"
            "ERROR: Athena query failed or returned no rows.\n"
            f"FULL QUERY:\n{input}\n"
            f"ERROR CONTENT:\n{json.dumps(body, indent=2) if isinstance(body, dict) else body}\n"
            "==========================================================\n"
        )
    rows = body["rows"]
    # If only header or no data rows, return a clear marker
    if len(rows) <= 1:
        return "NO_DATA: Athena query returned no results.\n" f"FULL QUERY:\n{input}\n"
    formatted_rows = "\n".join(", ".join(row) for row in rows[1:])
    header = ", ".join(rows[0])
    data_block = f"---BEGIN DATA---\n{header}\n{formatted_rows}\n---END DATA---"
    return (
        "\n==================== ATHENA QUERY RESULT ====================\n"
        "CRITICAL: COPY THE DATA BELOW INTO YOUR FINAL ANSWER!\n"
        "RESULTS FOR QUERY (FULL QUERY SHOWN):\n"
        f"{input}\n\n{data_block}\n"
        "INSTRUCTION: You MUST include the actual data rows above in your response to the user.\n"
        "Do NOT just describe what the query does - show the real data!\n"
        "===========================================================\n"
    )


tools = [get_glue_table_schema, execute_athena_query]

llm = ChatBedrock(model=model_name, region=region, model_kwargs=model_kwargs)
llm_with_tools = llm.bind_tools([get_glue_table_schema, execute_athena_query])
