import boto3
from botocore.client import BaseClient
import os


def s3_client() -> BaseClient:
    s3 = boto3.client('s3')
    return s3


def dynamo_client() -> BaseClient:
    dynamo = boto3.client('dynamodb')
    return dynamo


def download_file(bucket: str, key: str, local_folder: str):
    s3 = s3_client()
    filename = os.path.basename(key)

    with open(os.path.join(local_folder, filename), 'wb') as file:
        s3.download_fileobj(bucket, key, file)


def fetch_from_dynamo(table: str) -> list:
    dynamo = dynamo_client()
    response = dynamo.scan(
        TableName=table,
        Limit=1000,
        AttributesToGet=[
            'bucket_name',
            'key'
        ]
    )
    return response['Items']


def download_locally(local_folder: str, dynamo_table: str):
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)
        print(f"Folder '{local_folder}' created.")
    else:
        print(f"Folder '{local_folder}' already exists.")

    items = fetch_from_dynamo(dynamo_table)
    for i in items:
        try:
            download_file(i['bucket_name']['S'], i['key']['S'], local_folder)
        except Exception as e:
            print(e)


download_locally('workouts', 'WorkoutsTable-vebHVZG9-DRTXQehc6pqJg')
