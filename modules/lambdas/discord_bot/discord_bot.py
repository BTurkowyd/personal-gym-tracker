import json
import pyotp
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import os
from pprint import pprint
import boto3

# Environment variables for configuration
PUBLIC_KEY = os.environ.get(
    "DISCORD_APP_PUBLIC_KEY"
)  # Discord application's public key for signature verification
DISCORD_WEBHOOK = os.environ.get(
    "DISCORD_WEBHOOK"
)  # Discord webhook URL (not used in this script)
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")  # SNS topic ARN for publishing messages
OTP_RANDOM_KEY = os.environ.get("OTP_RANDOM_KEY")  # Secret key for TOTP verification

# Initialize TOTP generator
totp = pyotp.TOTP(OTP_RANDOM_KEY)

# Discord interaction response types
RESPONSE_TYPES = {
    "PONG": 1,
    "ACK_NO_SOURCE": 2,
    "MESSAGE_NO_SOURCE": 3,
    "MESSAGE_WITH_SOURCE": 4,
    "ACK_WITH_SOURCE": 5,
}

# Predefined responses for various interaction types
PONG_RESPONSE = {"statusCode": 200, "body": json.dumps({"type": 1})}

UNHANDLED_RESPONSE = {"statusCode": 400, "body": json.dumps("unhandled request type")}

COMMAND_ACCEPTED = {
    "statusCode": 200,
    "body": json.dumps(
        {
            "type": 4,
            "data": {
                "content": "Command accepted. The webhook will come to you with the response.",
            },
        }
    ),
}

# Headers for Hevy API requests (not used in this script)
HEVY_HEADER = {
    "accept": "application/json, text/plain, */*",
    "x-api-key": "klean_kanteen_insulated",
    "auth-token": os.environ.get("HEVY_TOKEN"),
    "Host": "api.hevyapp.com",
    "User-Agent": "okhttp/4.9.3",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}


def lambda_handler(event, context):
    """
    AWS Lambda handler for Discord bot interactions.
    Verifies the request signature, processes the interaction type,
    verifies OTP for commands, and publishes valid commands to SNS.
    """
    if not verify_call(event):
        return

    body = json.loads(event["body"])
    request_type = body["type"]

    if request_type == RESPONSE_TYPES["PONG"]:
        # Respond to Discord PING
        return PONG_RESPONSE
    elif request_type == RESPONSE_TYPES["ACK_NO_SOURCE"]:
        # Handle command with OTP verification
        options = body["data"]["options"]
        otp = [o["value"] for o in options if o["name"] == "otp"]

        if totp.verify(*otp):
            command = body["data"]["name"]

            if command != "print_workout":
                # Publish generic command to SNS
                message = {"command": command}
                publish_to_sns(message, SNS_TOPIC_ARN)
            else:
                # Publish print_workout command with date to SNS
                date = [o["value"] for o in options if o["name"] == "date"]
                message = {"command": command, "date": date[0]}
                publish_to_sns(message, SNS_TOPIC_ARN)
        return COMMAND_ACCEPTED
    else:
        # Unhandled interaction type
        return UNHANDLED_RESPONSE


def verify_call(event) -> bool:
    """
    Verifies the Discord request signature using Ed25519.
    Returns True if the signature is valid, False otherwise.
    """
    body_str = event["body"]
    signature = event["headers"]["x-signature-ed25519"]
    timestamp = event["headers"]["x-signature-timestamp"]

    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))

    try:
        verify_key.verify(f"{timestamp}{body_str}".encode(), bytes.fromhex(signature))
        print("Verification successful")
        return True
    except BadSignatureError as e:
        pprint(e)
        print("Verification failed")
        return False


def publish_to_sns(message: dict, sns_topic_arn: str):
    """
    Publishes a message to the specified AWS SNS topic.
    Args:
        message (dict): The message to publish.
        sns_topic_arn (str): The ARN of the SNS topic.
    """
    sns = boto3.client("sns")
    response = sns.publish(TopicArn=sns_topic_arn, Message=json.dumps(message))

    print(response)
