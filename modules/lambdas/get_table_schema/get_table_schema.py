import os
import boto3


def lambda_handler(event, context):
    # Fetch AWS account ID dynamically
    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]

    database_name = f"{account_id}_workouts_database"
    workouts_table_name = f"workouts_{account_id}_parquet"
    exercises_table_name = f"exercises_{account_id}_parquet"
    sets_table_name = f"sets_{account_id}_parquet"

    glue = boto3.client("glue")

    # Fetch the schema for all three tables
    table_names = [
        (workouts_table_name, "workouts"),
        (exercises_table_name, "exercises"),
        (sets_table_name, "sets"),
    ]
    schemas = {}
    for table_name, label in table_names:
        response = glue.get_table(DatabaseName=database_name, Name=table_name)
        columns = response["Table"]["StorageDescriptor"]["Columns"]
        schemas[label] = {
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
