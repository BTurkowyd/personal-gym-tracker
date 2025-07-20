import json
import os
import boto3
import lancedb
import numpy as np
import datetime

DB_PATH = f"s3://{os.getenv('BUCKET_NAME')}/lancedb"
TABLE_NAME = "workout_queries"


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


def retrieve_relevant_chunks(user_query: str, k: int = 3) -> list[dict]:

    db = lancedb.connect(DB_PATH)
    print(f"Connecting to LanceDB at {DB_PATH}...")
    print(db.table_names())
    table = db.open_table(TABLE_NAME)

    k = 20 if k > 20 else k  # Limit k to a maximum of 20
    query_embedding = titan_embed(user_query, region="eu-central-1")
    results = table.search(query_embedding).limit(k).to_pandas()
    print("Raw search results DataFrame:")
    print(results)
    if results.empty:
        print("⚠️  Search returned no results.")
    # Each row in results is a dict-like object
    return [
        {
            "user_prompt": str(row["user_prompt"]),
            "query_id": str(row["query_id"]),
            "sql_query": str(row["sql_query"]),
            "tables_used": list(map(str, row["tables_used"])),
            "columns_used": list(map(str, row["columns_used"])),
            "query_type": list(map(str, row["query_type"])),
            "returned_rows": int(row["returned_rows"]),
            "timestamp": (
                row["timestamp"].isoformat()
                if isinstance(row["timestamp"], datetime.datetime)
                else str(row["timestamp"])
            ),
        }
        for _, row in results.iterrows()
    ]


def lambda_handler(event, context):
    # Fetch AWS account ID dynamically
    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]

    database_name = f"{account_id}_workouts_database"

    glue = boto3.client("glue")

    # Fetch the schema for all four tables
    table_names = ["workouts", "exercises", "sets", "exercise_descriptions"]
    schemas = {}
    for table_name in table_names:
        response = glue.get_table(DatabaseName=database_name, Name=table_name)
        columns = response["Table"]["StorageDescriptor"]["Columns"]
        schemas[table_name] = {
            "table_name": table_name,
            "columns": [
                {
                    "name": col["Name"],
                    "type": col["Type"],
                    "comment": col.get("Comment", ""),
                }
                for col in columns
            ],
        }

    prompt = event.get("prompt")
    schemas["relevant_chunks"] = retrieve_relevant_chunks(prompt, k=5)
    return {"statusCode": 200, "body": schemas}


if __name__ == "__main__":
    event = {}
    context = None
    result = lambda_handler(event, context)
    print(result)
