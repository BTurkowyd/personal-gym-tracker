from pprint import pprint
import requests
import os

DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK')


def lambda_handler(event, context):
    received_message = event['Records'][0]['Sns']['Message']
    print(received_message)

    send_message(
        message='Hi, I jut got invoked via SNS <3',
        webhook_url=DISCORD_WEBHOOK
    )


def send_message(message: str, webhook_url: str) -> None:
    message_dict = {"content": message}
    try:
        response = requests.post(webhook_url, json=message_dict)
    except Exception as e:
        print(e)