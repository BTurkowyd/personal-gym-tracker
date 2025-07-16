import boto3
import json
from .config import region

lambda_client = boto3.client("lambda", region_name=region)


def invoke_lambda(function_name, payload):
    response = lambda_client.invoke(FunctionName=function_name, Payload=payload)
    return json.loads(response["Payload"].read().decode("utf-8"))
