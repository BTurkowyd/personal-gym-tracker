import datetime
import os
from typing import List
import lancedb
import numpy as np
from dotenv import load_dotenv

load_dotenv(".env")

DB_PATH = f"s3://{os.getenv('BUCKET_NAME')}/lancedb"
TABLE_NAME = "workout_queries"

# Connect to LanceDB and get or create the table
db = lancedb.connect(DB_PATH)

EMBEDDING_SIZE = 1024

if TABLE_NAME not in db.table_names():
    # Let LanceDB infer the schema from the first record you add
    table = db.create_table(
        TABLE_NAME,
        data=[
            {
                "user_prompt": "",
                "query_id": "example_query_id",
                "sql_query": "SELECT * FROM table",
                "vector": np.zeros(EMBEDDING_SIZE, dtype=np.float32),
                "tables_used": ["", ""],
                "columns_used": ["", ""],
                "query_type": ["SELECT"],
                "returned_rows": 0,
                "timestamp": datetime.datetime.now(),
            }
        ],
    )
    table.delete("query_id = 'example_query_id'")  # Remove the dummy row
else:
    table = db.open_table(TABLE_NAME)
