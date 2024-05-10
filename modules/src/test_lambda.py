import json
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import os
from pprint import pprint

PUBLIC_KEY = os.environ.get('DISCORD_APP_PUBLIC_KEY')

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


def lambda_handler(event, context):
    try:
        if not verify_call(event):
            return

        body = json.loads(event['body'])
        request_type = body['type']

        if request_type == RESPONSE_TYPES['PONG']:
            return PONG_RESPONSE
        elif request_type == RESPONSE_TYPES['ACK_NO_SOURCE']:
            return command_handler(body)
        else:
            return UNHANDLED_RESPONSE
    except Exception as e:
        print(e)


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


def command_handler(body):
    command = body['data']['name']
    if command == 'bleb':
        print('bleb')
        return {
            'statusCode': 200,
            'body': json.dumps({
                'type': 4,
                'data': {
                    'content': 'Hello, World.',
                }
            })
        }
    else:
        print('no bleb')
        return {
            'statusCode': 400,
            'body': json.dumps('unhandled command')
        }
