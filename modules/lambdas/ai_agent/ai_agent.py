import os
import json
from silka_agent.workflow import run_agent


def lambda_handler(event, context):
    """
    AWS Lambda handler for executing the agent workflow.
    This function is triggered by an event, such as an API Gateway request.
    """
    query = event.get("query", "")
    print(f"Received query: {query}")

    response = run_agent(query)

    print("Final Response:")
    print(response)

    return {"statusCode": 200, "body": response}


if __name__ == "__main__":
    query = "in total how many cable crunch reps i did in 2023?"

    lambda_handler({"query": query}, None)
