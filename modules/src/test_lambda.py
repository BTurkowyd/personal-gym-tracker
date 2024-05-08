import json
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import os
from pprint import pprint

PUBLIC_KEY = os.environ.get('DISCORD_APP_PUBLIC_KEY')


def lambda_handler(event, context):
    try:
        body_str = event['body']
        signature = event['headers']['x-signature-ed25519']
        timestamp = event['headers']['x-signature-timestamp']

        verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))

        try:
            verify_key.verify(f'{timestamp}{body_str}'.encode(), bytes.fromhex(signature))
            print('Verification successful')
        except BadSignatureError as e:
            pprint(e)
            print('Verification failed')
            return {
                'statusCode': 401,
                'body': json.dumps('invalid request signature')
            }

        # handle the interaction

        body = json.loads(body_str)

        t = body['type']

        if t == 1:
            print('Type 1')
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'type': 1
                })
            }
        elif t == 2:
            print('Type 2')
            return command_handler(body)
        else:
            print('smth went wrong')
            return {
                'statusCode': 400,
                'body': json.dumps('unhandled request type')
            }
    except Exception as e:
        print(e)
        print('I just crashed')


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
