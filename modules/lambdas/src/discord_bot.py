import json
from datetime import datetime

import requests
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import os
from pprint import pprint
import boto3

PUBLIC_KEY = os.environ.get('DISCORD_APP_PUBLIC_KEY')
DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

RESPONSE_TYPES = {
    "PONG": 1,
    "ACK_NO_SOURCE": 2,
    "MESSAGE_NO_SOURCE": 3,
    "MESSAGE_WITH_SOURCE": 4,
    "ACK_WITH_SOURCE": 5
}

PONG_RESPONSE = {
    'statusCode': 200,
    'body': json.dumps({
        'type': 1
    })
}

UNHANDLED_RESPONSE = {
    'statusCode': 400,
    'body': json.dumps('unhandled request type')
}

COMMAND_ACCEPTED = {
    'statusCode': 200,
    'body': json.dumps({
        'type': 4,
        'data': {
            'content': 'Command accepted. The webhook will come to you with the response.',
        }
    })
}

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
    if not verify_call(event):
        return

    body = json.loads(event['body'])
    request_type = body['type']

    if request_type == RESPONSE_TYPES['PONG']:
        return PONG_RESPONSE
    elif request_type == RESPONSE_TYPES['ACK_NO_SOURCE']:
        command_handler(body)
        return COMMAND_ACCEPTED
    else:
        return UNHANDLED_RESPONSE


def verify_call(event) -> bool:
    body_str = event['body']
    signature = event['headers']['x-signature-ed25519']
    timestamp = event['headers']['x-signature-timestamp']

    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))

    try:
        verify_key.verify(f'{timestamp}{body_str}'.encode(), bytes.fromhex(signature))
        print('Verification successful')
        return True
    except BadSignatureError as e:
        pprint(e)
        print('Verification failed')
        return False


def fetch_recent_workouts() -> None:
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(
        Name='/926728314305/latest-workout-index'
    )

    latest_workout_index = int(response['Parameter']['Value'])

    bucket_name = os.environ.get('BUCKET_NAME')
    table_name = os.environ.get('DYNAMODB_TABLE_NAME')

    response = requests.get(f'https://api.hevyapp.com/workouts_batch/{str(latest_workout_index+1)}', headers=HEVY_HEADER)
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
                'index': {'N': str(w['index'])},
                'name': {'S': w['name']},
                'id': {'S': w['id']},
                'nth_workout': {'N': str(w['nth_workout'])},
                'start_time': {'N': str(w['start_time'])},
                'bucket_name': {'S': bucket_name},
                'key': {'S': file_path}

            }

            register_file_in_dynamodb(table_name, item)

        update_latest_workout_parameter_store(workouts[-1]['index'])

        send_message(
            message='All missing workouts loaded.',
            webhook_url=DISCORD_WEBHOOK
        )


def print_latest_workout() -> None:
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(
        Name='/926728314305/latest-workout-index'
    )

    latest_workout_index = int(response['Parameter']['Value'])

    dynamodb = boto3.client('dynamodb')
    response = dynamodb.query(
        TableName=os.environ.get('DYNAMODB_TABLE_NAME'),
        Select='SPECIFIC_ATTRIBUTES',
        ProjectionExpression='bucket_name, #key',
        KeyConditionExpression='#index = :v1',
        ExpressionAttributeNames={
            '#index': 'index',
            '#key': 'key'
        },
        ExpressionAttributeValues={
            ':v1': {
                'N': str(latest_workout_index),
            },
        }
    )

    item = response['Items'][0]

    s3 = boto3.client('s3')
    response = s3.get_object(
        Bucket=item['bucket_name']['S'],
        Key=item['key']['S']
    )

    body = response['Body'].read().decode('utf-8')
    workout_json = json.loads(body)

    message = ''
    for e in workout_json['exercises']:
        message += f'{e["title"]}\n'
        for s in e['sets']:
            message += f'Weight: {s["weight_kg"]} kg, reps: {s["reps"]}\n'
        message += '------------------\n'

    message += f'https://hevy.com/workout/{workout_json["id"]}\n'

    send_message(
        message=message,
        webhook_url=DISCORD_WEBHOOK
    )


def command_handler(body):
    command = body['data']['name']
    if command == 'bleb':
        publish_to_sns(command, SNS_TOPIC_ARN)
        print('bleb')
    elif command == "fetch_workouts":
        fetch_recent_workouts()
    elif command == 'print_latest_workout':
        print_latest_workout()
    else:
        print('no bleb')


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


def update_latest_workout_parameter_store(latest_workout_index: int) -> None:
    ssm = boto3.client('ssm')

    ssm.put_parameter(
        Name='/926728314305/latest-workout-index',
        Value=str(latest_workout_index),
        Type='String',
        Overwrite=True
    )


def send_message(message: str, webhook_url: str) -> None:
    message_dict = {"content": message}
    try:
        response = requests.post(webhook_url, json=message_dict)
    except Exception as e:
        print(e)


def publish_to_sns(message: str, sns_topic_arn: str):
    sns = boto3.client('sns')
    response = sns.publish(
        TopicArn=sns_topic_arn,
        Message=message
    )

    print(response)
