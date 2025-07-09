import os
import boto3


def lambda_handler(event, context):
    # Fetch AWS account ID dynamically
    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]

    database_name = f"{account_id}_workouts_database"

    glue = boto3.client("glue")

    # Fetch the schema for all three tables
    table_names = ["workouts", "exercises", "sets"]
    schemas = {}
    for table_name in table_names:
        response = glue.get_table(DatabaseName=database_name, Name=table_name)
        columns = response["Table"]["StorageDescriptor"]["Columns"]
        schemas[table_name] = {
            "table_name": table_name,
            "columns": [
                {
                    "name": col["Name"],
                    "type": col["Type"],
                    "comment": col.get("Comment", ""),
                }
                for col in columns
            ],
        }
    return {"statusCode": 200, "body": schemas}


if __name__ == "__main__":
    event = {}
    context = None
    result = lambda_handler(event, context)
    print(result)
