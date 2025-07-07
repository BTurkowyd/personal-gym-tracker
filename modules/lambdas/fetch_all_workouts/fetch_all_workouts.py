import json
import requests
import boto3
from datetime import datetime
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import io


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


def normalize_workout_star_schema(workout):
    # Discard logic (same as in normalize_workout_to_sets)
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
        "preview_workout_likes",
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
    discard_set = {
        "prs",
        "personalRecords",
        "custom_metric",
        "completed_at",
    }

    # Workout table: one row per workout
    workout_row = {
        k: v
        for k, v in workout.items()
        if k != "exercises" and k not in discard_workout
    }
    workouts = [workout_row]

    exercises = []
    sets = []

    for exercise in workout.get("exercises", []):
        exercise_id = exercise.get("id")
        # Exercise table: one row per exercise, with workout_id as FK
        exercise_row = {
            k: v
            for k, v in exercise.items()
            if k != "sets"
            and not (k.endswith("title") and k != "title")
            and k not in discard_exercise
        }
        exercise_row["workout_id"] = workout["id"]
        exercises.append(exercise_row)

        for s in exercise.get("sets", []):
            set_row = {k: v for k, v in s.items() if k not in discard_set}
            set_row["exercise_id"] = exercise_id
            set_row["workout_id"] = workout["id"]
            sets.append(set_row)

    return workouts, exercises, sets


def enforce_types(df, table: str):
    # Define the target types for columns, based on your Glue schema:
    dtype_map = {
        "workout": {
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
        },
        "exercise": {
            "id": "string",
            "title": "string",
            "index": "Int64",
            "user_id": "string",
            "workout_id": "string",
            "created_at": "string",
            "updated_at": "string",
            "exercise_type": "string",
            "equipment_category": "string",
            "exercise_template_id": "string",
            "priority": "Int64",
            "muscle_group": "string",
        },
        "set": {
            "id": "string",
            "rpe": "float64",
            "reps": "Int64",
            "index": "Int64",
            "indicator": "string",
            "weight_kg": "float64",
            "distance_meters": "float64",
            "duration_seconds": "Int64",
            "exercise_id": "string",
            "workout_id": "string",
        },
    }

    for col, dtype in dtype_map[table].items():
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

    all_workouts.sort(key=lambda x: x["start_time"], reverse=True)

    for w in all_workouts:
        workout_id = w["id"]
        timestamp = str(datetime.fromtimestamp(w["start_time"]))
        year, month, day = timestamp.split(" ")[0].split("-")

        file_path = f"sorted_workouts/{year}/{month}/{day}/{workout_id}.json"
        body = bytes(json.dumps(w).encode("UTF-8"))
        upload_file_to_s3(file_path, bucket_name, body)

        file_path_parquet_workouts = (
            f"sorted/workouts/{year}/{month}/{day}/{workout_id}.parquet"
        )

        file_path_parquet_exercises = (
            f"sorted/exercises/{year}/{month}/{day}/{workout_id}.parquet"
        )

        file_path_parquet_sets = (
            f"sorted/sets/{year}/{month}/{day}/{workout_id}.parquet"
        )

        workout, exercises, sets = normalize_workout_star_schema(w)
        if workout:
            df = pd.DataFrame(workout)
            df = enforce_types(df, "workout")
            table = pa.Table.from_pandas(df)
            parquet_buffer = io.BytesIO()
            pq.write_table(table, parquet_buffer)
            parquet_buffer.seek(0)
            upload_file_to_s3(
                file_path_parquet_workouts, bucket_name, parquet_buffer.read()
            )

        if exercises:
            df = pd.DataFrame(exercises)
            df = enforce_types(df, "exercise")
            table = pa.Table.from_pandas(df)
            parquet_buffer = io.BytesIO()
            pq.write_table(table, parquet_buffer)
            parquet_buffer.seek(0)
            upload_file_to_s3(
                file_path_parquet_exercises, bucket_name, parquet_buffer.read()
            )

        if sets:
            df = pd.DataFrame(sets)
            df = enforce_types(df, "set")
            table = pa.Table.from_pandas(df)
            parquet_buffer = io.BytesIO()
            pq.write_table(table, parquet_buffer)
            parquet_buffer.seek(0)
            upload_file_to_s3(
                file_path_parquet_sets, bucket_name, parquet_buffer.read()
            )

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
