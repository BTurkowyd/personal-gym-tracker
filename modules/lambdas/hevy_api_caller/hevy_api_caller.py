import requests
import os
import boto3
from datetime import datetime
import json

# Discord webhook URL for sending notifications
DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK')

# Headers for authenticating with the Hevy API
HEVY_HEADER = {
    'accept': 'application/json, text/plain, */*',
    'x-api-key': 'klean_kanteen_insulated',
    'auth-token': os.environ.get('HEVY_TOKEN'),
    'Host': 'api.hevyapp.com',
    'User-Agent': 'okhttp/4.9.3',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}


def lambda_handler(event, context):
    """
    AWS Lambda entry point.
    Receives SNS event, extracts the message, and dispatches to the command handler.
    """
    received_message = event['Records'][0]['Sns']['Message']
    command_handler(received_message)


def send_message(message: str, webhook_url: str) -> None:
    """
    Sends a message to the specified Discord webhook.
    Args:
        message (str): The message content.
        webhook_url (str): The Discord webhook URL.
    """
    message_dict = {"content": message}
    try:
        response = requests.post(webhook_url, json=message_dict)
    except Exception as e:
        print(e)


def command_handler(message: str):
    """
    Handles commands received via SNS.
    Dispatches to the appropriate function based on the command.
    Args:
        message (str): The JSON-encoded command message.
    """
    message = json.loads(message)

    command = message['command']
    if command == 'bleb':
        send_message(
            message='Hi, I jut got invoked via SNS <3',
            webhook_url=DISCORD_WEBHOOK
        )
        print('bleb')
    elif command == "fetch_workouts":
        fetch_recent_workouts()
    elif command == 'print_latest_workout':
        print_latest_workout()
    elif command == 'print_workout':
        date = message['date']
        print_workout(date)
    else:
        print('no bleb')


def fetch_recent_workouts() -> None:
    """
    Fetches recent workouts from the Hevy API, uploads them to S3,
    registers them in DynamoDB, and updates the latest workout index in SSM.
    Sends notifications to Discord on completion or error.
    """
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(
        Name='/926728314305/latest-workout-index'
    )

    latest_workout_index = int(response['Parameter']['Value'])

    bucket_name = os.environ.get('BUCKET_NAME')
    table_name = os.environ.get('DYNAMODB_TABLE_NAME')

    try:
        response = requests.get(f'https://api.hevyapp.com/workouts_batch/{str(latest_workout_index + 1)}',
                                headers=HEVY_HEADER)
        workouts = response.json()

        if len(workouts) == 0:
            print('No workouts to fetch since the last update.')

            send_message(
                message='No workouts to fetch since the last update.',
                webhook_url=DISCORD_WEBHOOK
            )
        else:
            for w in workouts:
                workout_id = w['id']
                timestamp = str(datetime.fromtimestamp(w['start_time']))
                year, month, day = timestamp.split(' ')[0].split('-')

                file_path = f'sorted_workouts/{year}/{month}/{day}/{workout_id}.json'
                body = bytes(json.dumps(w).encode('UTF-8'))

                upload_file_to_s3(file_path, bucket_name, body)

                item = {
                    'index': {'S': str(w['index'])},
                    'name': {'S': w['name']},
                    'id': {'S': w['id']},
                    'nth_workout': {'N': str(w['nth_workout'])},
                    'start_time': {'N': str(w['start_time'])},
                    'bucket_name': {'S': bucket_name},
                    'key': {'S': file_path},
                    'workout_day': {'S': datetime.fromtimestamp(w['start_time']).strftime('%Y-%m-%d')}
                }

                register_file_in_dynamodb(table_name, item)

            update_latest_workout_parameter_store(workouts[-1]['index'])

            send_message(
                message='All missing workouts loaded.',
                webhook_url=DISCORD_WEBHOOK
            )

    except Exception as e:
        send_message(
            message=f'Looks like something went wrong:\n\n{e}',
            webhook_url=DISCORD_WEBHOOK
        )


def print_latest_workout() -> None:
    """
    Retrieves and sends the latest workout to Discord.
    """
    try:
        latest_workout_index = get_parameter('/926728314305/latest-workout-index')
        item = query_dynamodb('index', latest_workout_index)

        workout_json = get_s3_object(item['bucket_name']['S'], item['key']['S'])

        message = format_workout_message(workout_json)

        send_message(
            message=message,
            webhook_url=DISCORD_WEBHOOK
        )
    except Exception as e:
        send_message(
            message=f'Looks like something went wrong:\n\n{e}',
            webhook_url=DISCORD_WEBHOOK
        )


def print_workout(date: str) -> None:
    """
    Retrieves and sends a workout for a specific date to Discord.
    Args:
        date (str): The workout date in 'YYYY-MM-DD' format.
    """
    try:
        item = query_dynamodb('workout_day', date, 'WorkoutsTableWorkoutsDayGSI-vebHVZG9-DRTXQehc6pqJg')
        workout_json = get_s3_object(item['bucket_name']['S'], item['key']['S'])
        message = format_workout_message(workout_json)

        send_message(
            message=message,
            webhook_url=DISCORD_WEBHOOK
        )
    except Exception as e:
        send_message(
            message=f'Looks like something went wrong:\n\n{e}',
            webhook_url=DISCORD_WEBHOOK
        )


def upload_file_to_s3(file_path, bucket_name, body):
    """
    Uploads a file to the specified S3 bucket.
    Args:
        file_path (str): The S3 key (path) for the file.
        bucket_name (str): The S3 bucket name.
        body (bytes): The file content as bytes.
    """
    s3 = boto3.client('s3')
    s3.put_object(
        Bucket=bucket_name,
        Key=file_path,
        Body=body
    )


def register_file_in_dynamodb(table_name: str, item: dict) -> None:
    """
    Registers a workout file in DynamoDB.
    Args:
        table_name (str): The DynamoDB table name.
        item (dict): The item to put in the table.
    """
    dynamodb = boto3.client('dynamodb')
    dynamodb.put_item(
        TableName=table_name,
        Item=item
    )


def update_latest_workout_parameter_store(latest_workout_index: int) -> None:
    """
    Updates the latest workout index in AWS SSM Parameter Store.
    Args:
        latest_workout_index (int): The latest workout index to store.
    """
    ssm = boto3.client('ssm')

    ssm.put_parameter(
        Name='/926728314305/latest-workout-index',
        Value=str(latest_workout_index),
        Type='String',
        Overwrite=True
    )


def get_parameter(name: str) -> str:
    """
    Retrieves a parameter value from AWS SSM Parameter Store.
    Args:
        name (str): The parameter name.
    Returns:
        str: The parameter value.
    """
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(Name=name)
    return str(response['Parameter']['Value'])


def query_dynamodb(column_name: str, value: str, index_name: str = None) -> dict:
    """
    Queries DynamoDB for an item by column and value.
    Args:
        column_name (str): The column to query.
        value (str): The value to match.
        index_name (str, optional): The index to use for the query.
    Returns:
        dict: The first matching item.
    """
    key_condition_expression = f'#{column_name} = :v1'
    expression_attribute_names = {
        f'#{column_name}': column_name,
        '#key': 'key'
    }
    expression_attribute_values = {
        ':v1': {
            'S': value,
        },
    }

    dynamodb = boto3.client('dynamodb')
    if index_name:
        response = dynamodb.query(
            TableName=os.environ.get('DYNAMODB_TABLE_NAME'),
            IndexName=index_name,
            Select='SPECIFIC_ATTRIBUTES',
            ProjectionExpression='bucket_name, #key',
            KeyConditionExpression=key_condition_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )
    else:
        response = dynamodb.query(
            TableName=os.environ.get('DYNAMODB_TABLE_NAME'),
            Select='SPECIFIC_ATTRIBUTES',
            ProjectionExpression='bucket_name, #key',
            KeyConditionExpression=key_condition_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )

    return response['Items'][0]


def get_s3_object(bucket_name: str, key: str) -> dict:
    """
    Retrieves and parses a JSON object from S3.
    Args:
        bucket_name (str): The S3 bucket name.
        key (str): The S3 object key.
    Returns:
        dict: The parsed JSON object.
    """
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=key)
    body = response['Body'].read().decode('utf-8')
    return json.loads(body)


def format_workout_message(workout_json: dict) -> str:
    """
    Formats a workout JSON object into a human-readable message.
    Args:
        workout_json (dict): The workout data.
    Returns:
        str: The formatted message.
    """
    message = ''
    for e in workout_json['exercises']:
        message += f'{e["title"]}\n'
        message += f'Notes: {e["notes"]}\n'
        for s in e['sets']:
            message += f'Weight: {s["weight_kg"]} kg, reps: {s["reps"]}\n'
        message += '------------------\n'
    message += f'https://hevy.com/workout/{workout_json["id"]}\n'
    return message
