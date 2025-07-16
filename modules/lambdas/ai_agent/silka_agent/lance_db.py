import os
import uuid
import datetime
import lancedb
import numpy as np
import boto3
import json
from dotenv import load_dotenv
from .sql_metadata import extract_sql_metadata_regex

load_dotenv(".env")

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
            "user_prompt": row["user_prompt"],
            "query_id": row["query_id"],
            "sql_query": row["sql_query"],
            "vector": row["vector"],
            "tables_used": row["tables_used"],
            "columns_used": row["columns_used"],
            "query_type": row["query_type"],
            "returned_rows": row["returned_rows"],
            "timestamp": (
                row["timestamp"].isoformat()
                if isinstance(row["timestamp"], datetime)
                else row["timestamp"]
            ),
        }
        for _, row in results.iterrows()
    ]
