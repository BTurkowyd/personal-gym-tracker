import json
import requests
import boto3
from datetime import datetime
import os


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
    # Workout-level fields to discard
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
    # Exercise-level fields to discard
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


def lambda_handler(event, context):
    """
    AWS Lambda entry point for fetching all workouts from Hevy API.
    Downloads all workouts, uploads them to S3, registers them in DynamoDB,
    and updates the latest workout index in SSM.
    """
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

    # Get total workout count (not used, but could be for progress)
    response = requests.get("https://api.hevyapp.com/workout_count", headers=headers)
    workout_count = response.json()["workout_count"]

    # Fetch first batch of workouts
    response = requests.get("https://api.hevyapp.com/workouts_batch/0", headers=headers)
    workouts = response.json()
    all_workouts += workouts

    bucket_name = os.environ.get("BUCKET_NAME")
    table_name = os.environ.get("DYNAMODB_TABLE_NAME")

    # Continue fetching batches of 10 until all are retrieved
    while len(workouts) == 10:
        response = requests.get(
            "https://api.hevyapp.com/workouts_batch/" + str(workouts[-1]["index"] + 1),
            headers=headers,
        )
        workouts = response.json()
        all_workouts += workouts

    # Store each workout in S3 and DynamoDB
    for w in all_workouts:
        workout_id = w["id"]
        timestamp = str(datetime.fromtimestamp(w["start_time"]))
        year, month, day = timestamp.split(" ")[0].split("-")

        # Create the S3 file path for json file
        file_path = f"sorted_workouts/{year}/{month}/{day}/{workout_id}.json"
        body = bytes(json.dumps(w).encode("UTF-8"))
        upload_file_to_s3(file_path, bucket_name, body)

        # Create the s3 file path for CSV file
        file_path_csv = f"sorted_workouts_csv/{year}/{month}/{day}/{workout_id}.csv"
        csv_rows = normalize_workout_to_sets(w)
        csv_body = bytes(
            "\n".join(
                ",".join(str(row.get(col, "")) for col in row.keys())
                for row in csv_rows
            ).encode("UTF-8")
        )
        upload_file_to_s3(file_path_csv, bucket_name, csv_body)

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

    # Update the latest workout index in SSM
    update_latest_workout_parameter_store(table_name)
