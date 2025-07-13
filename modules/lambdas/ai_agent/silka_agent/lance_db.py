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


def add_successful_query_to_lancedb(
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
    user_prompt = os.getenv("PROMPT", "")
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
