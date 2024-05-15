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
        command = body['data']['name']
        publish_to_sns(command, SNS_TOPIC_ARN)
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


def publish_to_sns(message: str, sns_topic_arn: str):
    sns = boto3.client('sns')
    response = sns.publish(
        TopicArn=sns_topic_arn,
        Message=message
    )

    print(response)
