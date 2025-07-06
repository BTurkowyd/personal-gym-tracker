import os
import boto3


def lambda_handler(event, context):
    # Fetch AWS account ID dynamically
    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]

    database_name = f"{account_id}_workouts_database"
    table_name = f"workouts_{account_id}_parquet"

    glue = boto3.client("glue")
    response = glue.get_table(DatabaseName=database_name, Name=table_name)
    columns = response["Table"]["StorageDescriptor"]["Columns"]
    result = {
        "database_name": database_name,
        "table_name": table_name,
        "columns": {
            col["Name"]: {
                "type": col["Type"],
                "comment": col.get("Comment", ""),
            }
            for col in columns
        },
    }
    return {"statusCode": 200, "body": result}


if __name__ == "__main__":
    event = {}
    context = None
    result = lambda_handler(event, context)
    print(result)
