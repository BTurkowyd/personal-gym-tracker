import os
import json
import requests
from silka_agent.workflow import run_agent


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


def lambda_handler(event, context):
    """
    AWS Lambda handler for executing the agent workflow.
    This function is triggered by an event, such as an API Gateway request.
    """
    prompt = event.get("prompt", "")
    print(f"Received prompt: {prompt}")

    response = run_agent(prompt)

    print("Final Response:")
    print(response)

    q_and_a = f"Question: {prompt}\nAnswer: {response}"

    # Send the response to a Discord webhook if configured
    send_message(q_and_a, os.getenv("DISCORD_WEBHOOK_URL"))

    return {"statusCode": 200, "body": response}


if __name__ == "__main__":
    prompt = "please check my latest several workouts and suggest a full body workout to do next. list me the exercises with descriptions, such as what muscles they work, and what equipment is needed."

    lambda_handler({"prompt": prompt}, None)
