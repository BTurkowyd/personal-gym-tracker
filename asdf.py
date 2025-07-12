from datetime import datetime
import os
import json
import numpy as np
import lancedb
import boto3
from dotenv import load_dotenv

from silka_agent.lance_db import titan_embed

load_dotenv(".env")

bucket_name = os.getenv("BUCKET_NAME")
region = os.getenv("AWS_REGION", "eu-central-1")  # Set your default region


DB_PATH = f"s3://{bucket_name}/lancedb"
TABLE_NAME = "workout_queries"


def embed_text(text):
    client = boto3.client("bedrock-runtime", region_name="eu-central-1")
    model_id = "amazon.titan-embed-text-v2:0"

    response = client.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({"inputText": text}),
    )

    response_body = json.loads(response["body"].read())
    return response_body["embedding"]


def retrieve_relevant_chunks(user_query: str, k: int = 3) -> list[dict]:

    db = lancedb.connect(DB_PATH)
    print(f"Connecting to LanceDB at {DB_PATH}...")
    print(db.table_names())
    table = db.open_table(TABLE_NAME)

    k = 20 if k > 20 else k  # Limit k to a maximum of 20
    query_embedding = titan_embed(user_query, region=region)
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


if __name__ == "__main__":
    # Example usage
    user_query = "how many workouts in total are recorded?"
    relevant_chunks = retrieve_relevant_chunks(user_query, k=5)
    print("Relevant chunks retrieved:")
    for chunk in relevant_chunks:
        print(chunk["user_prompt"], chunk["sql_query"], chunk["returned_rows"])
