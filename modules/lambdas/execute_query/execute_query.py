import os
import boto3
import time

ATHENA_DATABASE = os.environ.get("ATHENA_DATABASE")
ATHENA_OUTPUT = os.environ.get("ATHENA_OUTPUT")

athena = boto3.client("athena")


def lambda_handler(event, context):
    query = event.get("query")
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

    return {"statusCode": 200, "body": {"query": query, "rows": rows}}
