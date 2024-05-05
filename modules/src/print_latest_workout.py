import json
import os
from pprint import pprint

import boto3


def print_latest_workout(event, context):
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

    for e in workout_json['exercises']:
        print(e['title'])
        for s in e['sets']:
            print(f'Weight: {s["weight_kg"]} kg, reps: {s["reps"]}')
        print('------------------')
