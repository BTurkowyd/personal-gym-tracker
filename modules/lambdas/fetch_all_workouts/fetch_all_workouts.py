import json
import requests
import boto3
from datetime import datetime
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def upload_file_to_s3(file_path, bucket_name, body):
    """
    Uploads a file to the specified S3 bucket.
    Args:
        file_path (str): The S3 key (path) for the file.
        bucket_name (str): The S3 bucket name.
        body (bytes): The file content as bytes.
    """
    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucket_name, Key=file_path, Body=body)


def register_file_in_dynamodb(table_name: str, item: dict) -> None:
    """
    Registers a workout file in DynamoDB.
    Args:
        table_name (str): The DynamoDB table name.
        item (dict): The item to put in the table.
    """
    dynamodb = boto3.client("dynamodb")
    dynamodb.put_item(TableName=table_name, Item=item)


def update_latest_workout_parameter_store(table_name: str) -> None:
    """
    Scans DynamoDB for the highest workout index and updates SSM Parameter Store.
    Args:
        table_name (str): The DynamoDB table name.
    """
    dynamodb = boto3.client("dynamodb")

    scan_params = {
        "TableName": table_name,
        "ProjectionExpression": "#Index",
        "ExpressionAttributeNames": {"#Index": "index"},
    }

    response = dynamodb.scan(**scan_params)
    items = response.get("Items", [])

    indexes = []
    for item in items:
        indexes.append(int(item["index"]["S"]))

    latest_workout_index = max(indexes)

    ssm = boto3.client("ssm")

    ssm.put_parameter(
        Name="/926728314305/latest-workout-index",
        Value=str(latest_workout_index),
        Type="String",
        Overwrite=True,
    )


def normalize_workout_to_sets(workout):
    discard_workout = {
        "media",
        "comments",
        "short_id",
        "verified",
        "image_urls",
        "description",
        "like_images",
        "profile_image",
        "is_liked_by_user",
        "apple_watch",
        "wearos_watch",
        "is_private",
        "like_count",
    }
    discard_exercise = {
        "url",
        "notes",
        "de_title",
        "es_title",
        "fr_title",
        "it_title",
        "ja_title",
        "ko_title",
        "pt_title",
        "ru_title",
        "tr_title",
        "media_type",
        "other_muscles",
        "prs",
        "personalRecords",
        "superset_id",
        "zh_cn_title",
        "zh_tw_title",
        "thumbnail_url",
        "custom_exercise_image_url",
        "custom_exercise_image_thumbnail_url",
        "volume_doubling_enabled",
    }
    rows = []
    workout_fields = {
        k: v
        for k, v in workout.items()
        if k != "exercises" and k not in discard_workout
    }
    for exercise in workout.get("exercises", []):
        exercise_fields = {}
        for k, v in exercise.items():
            if k == "sets":
                continue
            if k.endswith("title") and k != "title":
                continue  # keep only 'title' (English)
            if k in discard_exercise:
                continue
            exercise_fields[f"exercise_{k}"] = v
        for s in exercise.get("sets", []):
            set_row = workout_fields.copy()
            set_row.update(exercise_fields)
            for set_k, set_v in s.items():
                set_row[f"set_{set_k}"] = set_v
            rows.append(set_row)
    return rows


def enforce_types(df):
    # Define the target types for columns, based on your Glue schema:
    dtype_map = {
        "id": "string",
        "name": "string",
        "index": "Int64",
        "user_id": "string",
        "end_time": "Int64",
        "username": "string",
        "created_at": "string",
        "routine_id": "string",
        "start_time": "Int64",
        "updated_at": "string",
        "nth_workout": "Int64",
        "comment_count": "Int64",
        "estimated_volume_kg": "float64",
        "exercise_id": "string",
        "exercise_title": "string",
        "exercise_priority": "Int64",
        "exercise_muscle_group": "string",
        "exercise_rest_seconds": "Int64",
        "exercise_exercise_type": "string",
        "exercise_equipment_category": "string",
        "exercise_exercise_template_id": "string",
        "set_id": "string",
        "set_rpe": "float64",
        "set_reps": "Int64",
        "set_index": "Int64",
        "set_indicator": "string",
        "set_weight_kg": "float64",
        "set_distance_meters": "float64",
        "set_duration_seconds": "Int64",
    }

    for col, dtype in dtype_map.items():
        if col in df.columns:
            if dtype == "string":
                # Convert to string, filling missing with None
                df[col] = df[col].astype(str).replace({"nan": None, "None": None})
            elif dtype == "Int64":
                # Nullable integer type, convert safely
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
            elif dtype == "float64":
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")
    return df


def lambda_handler(event, context):
    all_workouts = []

    headers = {
        "accept": "application/json, text/plain, */*",
        "x-api-key": "klean_kanteen_insulated",
        "auth-token": os.environ.get("HEVY_TOKEN"),
        "Host": "api.hevyapp.com",
        "User-Agent": "okhttp/4.9.3",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    response = requests.get("https://api.hevyapp.com/workout_count", headers=headers)
    workout_count = response.json()["workout_count"]

    response = requests.get("https://api.hevyapp.com/workouts_batch/0", headers=headers)
    workouts = response.json()
    all_workouts += workouts

    bucket_name = os.environ.get("BUCKET_NAME")
    table_name = os.environ.get("DYNAMODB_TABLE_NAME")

    while len(workouts) == 10:
        response = requests.get(
            "https://api.hevyapp.com/workouts_batch/" + str(workouts[-1]["index"] + 1),
            headers=headers,
        )
        workouts = response.json()
        all_workouts += workouts

    for w in all_workouts:
        workout_id = w["id"]
        timestamp = str(datetime.fromtimestamp(w["start_time"]))
        year, month, day = timestamp.split(" ")[0].split("-")

        file_path = f"sorted_workouts/{year}/{month}/{day}/{workout_id}.json"
        body = bytes(json.dumps(w).encode("UTF-8"))
        upload_file_to_s3(file_path, bucket_name, body)

        file_path_parquet = (
            f"sorted_workouts_parquet/{year}/{month}/{day}/{workout_id}.parquet"
        )
        set_rows = normalize_workout_to_sets(w)
        if set_rows:
            df = pd.DataFrame(set_rows)
            df = enforce_types(df)  # enforce data types here
            table = pa.Table.from_pandas(df)
            import io

            parquet_buffer = io.BytesIO()
            pq.write_table(table, parquet_buffer)
            parquet_buffer.seek(0)
            upload_file_to_s3(file_path_parquet, bucket_name, parquet_buffer.read())

        item = {
            "index": {"S": str(w["index"])},
            "name": {"S": str(w["name"])},
            "id": {"S": str(w["id"])},
            "nth_workout": {"N": str(w["nth_workout"])},
            "start_time": {"N": str(w["start_time"])},
            "bucket_name": {"S": str(bucket_name)},
            "key": {"S": str(file_path)},
            "workout_day": {
                "S": datetime.fromtimestamp(w["start_time"]).strftime("%Y-%m-%d")
            },
        }

        register_file_in_dynamodb(table_name, item)

    update_latest_workout_parameter_store(table_name)
