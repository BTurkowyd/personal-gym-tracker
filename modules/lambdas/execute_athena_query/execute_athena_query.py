import datetime
import json
import os
import uuid
import boto3
import time
import re

import lancedb
import numpy as np

ATHENA_DATABASE = os.environ.get("ATHENA_DATABASE")
ATHENA_OUTPUT = os.environ.get("ATHENA_OUTPUT")
DB_PATH = f"s3://{os.getenv('LANCE_DB_BUCKET')}/lancedb"
TABLE_NAME = "workout_queries"

athena = boto3.client("athena")


def extract_sql_metadata_regex(sql_query: str) -> dict:
    """Extract tables and columns using regex patterns, excluding aliases."""
    tables = set()
    columns = set()

    # Extract table names from FROM and JOIN clauses (excluding aliases)
    from_pattern = r"FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)"
    join_pattern = r"JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)"

    from_matches = re.findall(from_pattern, sql_query, re.IGNORECASE)
    join_matches = re.findall(join_pattern, sql_query, re.IGNORECASE)

    tables.update(from_matches)
    tables.update(join_matches)

    # Build alias mapping to exclude them
    alias_pattern = r"FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)|JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)"
    alias_matches = re.findall(alias_pattern, sql_query, re.IGNORECASE)

    # Create set of known aliases
    aliases = set()
    for match in alias_matches:
        if match[1]:  # FROM table alias
            aliases.add(match[1])
        if match[3]:  # JOIN table alias
            aliases.add(match[3])

    # Extract column names from table.column patterns (excluding aliases)
    column_pattern = r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\.\s*([a-zA-Z_][a-zA-Z0-9_]*)"
    table_column_matches = re.findall(column_pattern, sql_query)

    for table_alias, column in table_column_matches:
        if table_alias not in ("DATE", "FROM_UNIXTIME", "CAST", "LOWER", "SUM"):
            # Only add the column, never add aliases to columns
            columns.add(column)
            # Only add table name if it's not an alias
            if table_alias not in aliases:
                tables.add(table_alias)

    # Extract standalone column names from SELECT (excluding AS aliases and table.column patterns)
    select_pattern = r"SELECT\s+(.*?)\s+FROM"
    select_match = re.search(select_pattern, sql_query, re.IGNORECASE | re.DOTALL)
    if select_match:
        select_clause = select_match.group(1)

        # Remove AS aliases from select clause
        select_clause = re.sub(
            r"\s+AS\s+[a-zA-Z_][a-zA-Z0-9_]*", "", select_clause, flags=re.IGNORECASE
        )

        # Remove table.column patterns to avoid picking up table aliases
        select_clause = re.sub(
            r"\b[a-zA-Z_][a-zA-Z0-9_]*\s*\.\s*[a-zA-Z_][a-zA-Z0-9_]*", "", select_clause
        )

        # Extract simple column names (standalone, not prefixed)
        simple_columns = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", select_clause)
        for col in simple_columns:
            if (
                col.upper()
                not in (
                    "DATE",
                    "FROM_UNIXTIME",
                    "CAST",
                    "AS",
                    "DOUBLE",
                    "SUM",
                    "LOWER",
                    "TOTAL_VOLUME",
                )
                and col not in aliases  # Exclude known aliases
            ):
                columns.add(col)

    return {
        "tables_used": list(tables),
        "columns_used": list(columns),
        "query_type": ["SELECT"],
    }


def titan_embed(text: str, region: str = "eu-central-1") -> np.ndarray:
    bedrock = boto3.client("bedrock-runtime", region_name=region)
    body = {"inputText": text}
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps(body),
        accept="application/json",
        contentType="application/json",
    )
    result = json.loads(response["body"].read())
    return np.array(result["embedding"], dtype=np.float32)


def add_successful_query_to_lancedb(
    user_prompt: str,
    sql_query: str,
    returned_rows: int,
    region: str = "eu-central-1",
):

    # Extract metadata from the SQL query
    query_metadata = extract_sql_metadata_regex(sql_query)
    tables_used = query_metadata.get("tables_used", [])
    columns_used = query_metadata.get("columns_used", [])
    query_type = query_metadata.get("query_type", ["SELECT"])

    # stringify everything for embedding
    # Combine and stringify all relevant fields for embedding
    query_id = uuid.uuid4().hex  # Generate a unique query ID
    sql_query = str(sql_query)
    tables_used = [str(table) for table in tables_used]
    columns_used = [str(column) for column in columns_used]
    query_type = [str(qt) for qt in query_type]
    returned_rows = int(returned_rows)

    embedding = titan_embed(user_prompt, region=region)

    record = {
        "user_prompt": user_prompt,
        "query_id": query_id,
        "sql_query": sql_query,
        "vector": embedding,
        "tables_used": tables_used,
        "columns_used": columns_used,
        "query_type": query_type,
        "returned_rows": returned_rows,
        "timestamp": datetime.datetime.now(),
    }

    print(record)

    # Add the record to the LanceDB table
    db = lancedb.connect(DB_PATH)
    print(f"Connecting to LanceDB at {DB_PATH}...")
    print(db.table_names())
    table = db.open_table(TABLE_NAME)
    table.merge_insert(
        "query_id"
    ).when_matched_update_all().when_not_matched_insert_all().execute([record])
    print(f"✅ Successfully added query {query_id} to LanceDB.")


def lambda_handler(event, context):
    query = event.get("query")
    user_prompt = event.get("user_prompt")
    if not query:
        return {"statusCode": 400, "body": "Missing 'query' in event."}

    print(f"ATHENA_DATABASE = {ATHENA_DATABASE}")
    print(f"ATHENA_OUTPUT = {ATHENA_OUTPUT}")
    print(f"Query = {query}")

    # Start Athena query execution
    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": ATHENA_DATABASE},
        ResultConfiguration={"OutputLocation": ATHENA_OUTPUT},
    )
    execution_id = response["QueryExecutionId"]

    # Wait for the query to finish
    while True:
        result = athena.get_query_execution(QueryExecutionId=execution_id)
        state = result["QueryExecution"]["Status"]["State"]
        if state in ["SUCCEEDED", "FAILED", "CANCELLED"]:
            break
        time.sleep(1)

    if state != "SUCCEEDED":
        # Get the error message from Athena if available
        error_message = f"Athena query failed with state: {state}"
        if state == "FAILED":
            status_info = result["QueryExecution"]["Status"]
            if "StateChangeReason" in status_info:
                error_message += f" - {status_info['StateChangeReason']}"
        return {"statusCode": 500, "body": {"error": error_message}}

    # Fetch results
    results = athena.get_query_results(QueryExecutionId=execution_id)
    rows = []
    for row in results["ResultSet"]["Rows"]:
        rows.append([col.get("VarCharValue", "") for col in row["Data"]])

        # here will be the logic to insert the query into LanceDB
    returned_rows = len(rows) - 1  # Exclude header row

    add_successful_query_to_lancedb(
        user_prompt,
        query,
        returned_rows,
        region="eu-central-1",
    )

    return {"statusCode": 200, "body": {"query": query, "rows": rows}}
