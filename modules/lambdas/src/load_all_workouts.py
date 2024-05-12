import json
import requests
import boto3
from datetime import datetime
import os


def upload_file_to_s3(file_path, bucket_name, body):
    # Create an S3 client
    s3 = boto3.client('s3')

    # Upload the file to S3
    s3.put_object(
        Bucket=bucket_name,
        Key=file_path,
        Body=body
    )


def register_file_in_dynamodb(table_name: str, item: dict) -> None:
    dynamodb = boto3.client('dynamodb')
    dynamodb.put_item(
        TableName=table_name,
        Item=item
    )


def update_latest_workout_parameter_store(table_name: str) -> None:
    dynamodb = boto3.client('dynamodb')

    scan_params = {
        'TableName': table_name,
        'ProjectionExpression': '#Index',
        'ExpressionAttributeNames': {'#Index': 'index'}
    }

    response = dynamodb.scan(**scan_params)
    items = response.get('Items', [])

    indexes = []
    for item in items:
        indexes.append(int(item['index']['N']))

    latest_workout_index = max(indexes)

    ssm = boto3.client('ssm')

    ssm.put_parameter(
        Name='/926728314305/latest-workout-index',
        Value=str(latest_workout_index),
        Type='String',
        Overwrite=True
    )


def lambda_fetch_workouts(event, context):
    all_workouts = []

    headers = {
        'accept': 'application/json, text/plain, */*',
        'x-api-key': 'klean_kanteen_insulated',
        'auth-token': os.environ.get('HEVY_TOKEN'),
        'Host': 'api.hevyapp.com',
        'User-Agent': 'okhttp/4.9.3',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }

    response = requests.get('https://api.hevyapp.com/workout_count', headers=headers)
    workout_count = response.json()['workout_count']

    response = requests.get('https://api.hevyapp.com/workouts_batch/0', headers=headers)
    workouts = response.json()
    all_workouts += workouts

    bucket_name = os.environ.get('BUCKET_NAME')
    table_name = os.environ.get('DYNAMODB_TABLE_NAME')

    while len(workouts) == 10:
        response = requests.get('https://api.hevyapp.com/workouts_batch/' + str(workouts[-1]['index']+1), headers=headers)
        workouts = response.json()
        all_workouts += workouts

    for w in all_workouts:
        workout_id = w['id']
        timestamp = str(datetime.fromtimestamp(w['start_time']))
        year, month, day = timestamp.split(' ')[0].split('-')

        file_path = f'sorted_workouts/{year}/{month}/{day}/{workout_id}.json'
        body = bytes(json.dumps(w).encode('UTF-8'))

        upload_file_to_s3(file_path, bucket_name, body)

        item = {
            'index': {'N': str(w['index'])},
            'name': {'S': w['name']},
            'id': {'S': w['id']},
            'nth_workout': {'N': str(w['nth_workout'])},
            'start_time': {'N': str(w['start_time'])},
            'bucket_name': {'S': bucket_name},
            'key': {'S': file_path}

        }

        register_file_in_dynamodb(table_name, item)

    update_latest_workout_parameter_store(table_name)


