import pandas as pd
import boto3
import os
from dotenv import load_dotenv

load_dotenv(".env")

CSV_FILE = "enriched_exercises.csv"
PARQUET_FILE = "exercise_descriptions.parquet"
S3_BUCKET = os.getenv("S3_BUCKET")
S3_PREFIX = "sorted/exercise_descriptions/"
S3_KEY = os.path.join(S3_PREFIX, PARQUET_FILE)

expected_columns = [
    "title",
    "equipment_category",
    "muscle_group",
    "body_part",
    "movement_type",
]
df = pd.read_csv(CSV_FILE)
df = df[expected_columns].astype(str)

df.to_parquet(PARQUET_FILE, index=False)
print(f"Parquet file '{PARQUET_FILE}' created.")

s3 = boto3.client("s3")
s3.upload_file(PARQUET_FILE, S3_BUCKET, S3_KEY)
print(f"Uploaded to s3://{S3_BUCKET}/{S3_KEY}")
