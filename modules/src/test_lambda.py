import json
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import os



def lambda_handler(event, context):

    PUBLIC_KEY = os.environ.get('DISCORD_APP_PUBLIC_KEY')
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))

    signature = event['headers']['x-signature-ed25519']
    timestamp = event['headers']['x-signature-timestamp']
    body = event['body']

    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))

        body = json.loads(body)
        if body['type'] == 1:
            response_body = {"type": 1}

            return {
                "statusCode": 200,
                "body": json.dump(response_body)
            }
        else:
            print('smth went wrong')
    except BadSignatureError:
        response_body = {"Message": "Authorization Error"}

        return {
            "statusCode": 401,
            "body": json.dumps(response_body)
        }


