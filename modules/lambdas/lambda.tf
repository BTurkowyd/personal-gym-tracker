# Lambda function for fetching all workouts from Hevy and storing them in S3/DynamoDB.
resource "aws_lambda_function" "fetching_from_hevy" {
  function_name = "FetchAllWorkoutsFromHevy"
  role          = var.lambda_role_arn
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.fetch_all_workouts_repo.repository_url}:latest"
  timeout       = 900
  source_code_hash = split(":", data.aws_ecr_image.fetch_all_latest_image.id)[1]

  environment {
    variables = {
      HEVY_TOKEN         = var.local_envs["HEVY_TOKEN"]
      BUCKET_NAME        = var.upload_bucket_name,
      DYNAMODB_TABLE_NAME = var.dynamo_workouts_table_name
    }
  }
}

# Lambda function for handling Discord bot interactions.
resource "aws_lambda_function" "discord_bot" {
  function_name = "DiscordBotWorkouts"
  role          = var.lambda_role_arn
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.discord_bot_repo.repository_url}:latest"
  timeout       = 900
  source_code_hash = split(":", data.aws_ecr_image.discord_bot_latest_image.id)[1]

  environment {
    variables = {
      DISCORD_APP_PUBLIC_KEY = var.local_envs["DISCORD_APP_PUBLIC_KEY"]
      SNS_TOPIC_ARN          = aws_sns_topic.pass_request.arn
      OTP_RANDOM_KEY         = var.local_envs["OTP_RANDOM_KEY"]
    }
  }
}

# Lambda function for calling the Hevy API and processing workout data.
resource "aws_lambda_function" "hevy_api_caller" {
  function_name = "HevyAPICaller"
  role          = var.lambda_role_arn
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.hevy_api_caller_repo.repository_url}:latest"
  timeout       = 900
  source_code_hash = split(":", data.aws_ecr_image.hevy_api_caller_latest_image.id)[1]

  environment {
    variables = {
      DISCORD_WEBHOOK      = var.local_envs["DISCORD_WEBHOOK"]
      HEVY_TOKEN           = var.local_envs["HEVY_TOKEN"]
      BUCKET_NAME          = var.upload_bucket_name
      DYNAMODB_TABLE_NAME  = var.dynamo_workouts_table_name
    }
  }
}

# Lambda function for fetching Glue table schema (column names) from workouts_database.
resource "aws_lambda_function" "get_table_schema" {
  function_name = "GetGlueTableSchema"
  role          = var.lambda_role_arn
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.get_table_schema_repo.repository_url}:latest"
  timeout       = 120
  source_code_hash = split(":", data.aws_ecr_image.get_table_schema_latest_image.id)[1]
  environment {
    variables = {
      BUCKET_NAME     = var.lance_db_bucket_name
    }
  }
}

# Lambda function for executing Athena queries.
resource "aws_lambda_function" "execute_athena_query" {
  function_name = "ExecuteAthenaQuery"
  role          = var.lambda_role_arn
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.execute_athena_query_repo.repository_url}:latest"
  timeout       = 120
  source_code_hash = split(":", data.aws_ecr_image.execute_athena_query_latest_image.id)[1]
  environment {
    variables = {
      ATHENA_DATABASE = var.athena_database_name
      ATHENA_OUTPUT   = "s3://${var.athena_queries_bucket}/"
      LANCE_DB_BUCKET = var.lance_db_bucket_name
    }
  }
}

# Lambda function for AI Agent execution.
resource "aws_lambda_function" "ai_agent" {
  function_name = "AIAgent"
  role          = var.lambda_role_arn
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.ai_agent_repo.repository_url}:latest"
  timeout       = 120
  source_code_hash = split(":", data.aws_ecr_image.ai_agent_latest_image.id)[1]

  environment {
    variables = {
      DISCORD_WEBHOOK_URL = var.local_envs["DISCORD_WEBHOOK"]
    }
  }
}

# Allow SNS to invoke the Hevy API caller Lambda function.
resource "aws_lambda_permission" "invoke_lambda_by_sns" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.hevy_api_caller.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.pass_request.arn
}

# Allow API Gateway to invoke the Discord bot Lambda function.
resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.discord_bot.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${var.api_gateway_exec_arn}/*/*"
}
