resource "aws_lambda_function" "fetching_from_hevy" {
  function_name = "FetchAllWorkoutsFromHevy"
  role          = var.lambda_role_arn
  package_type = "Image"
  image_uri = "${data.aws_ecr_repository.fetch_all_workouts_repo.repository_url}:latest"
  timeout = 900
  source_code_hash = data.aws_ecr_image.fetch_all_latest_image.id

  environment {
    variables = {
      HEVY_TOKEN = var.local_envs["HEVY_TOKEN"]
      BUCKET_NAME = var.upload_bucket_name,
      DYNAMODB_TABLE_NAME = var.dynamo_workouts_table_name
    }
  }
}

resource "aws_lambda_function" "discord_bot" {
  function_name = "DiscordBotWorkouts"
  role          = var.lambda_role_arn
  package_type = "Image"
  image_uri = "${data.aws_ecr_repository.discord_bot_repo.repository_url}:latest"
  timeout = 900
  source_code_hash = data.aws_ecr_image.discord_bot_latest_image.id

  environment {
    variables = {
      DISCORD_APP_PUBLIC_KEY = var.local_envs["DISCORD_APP_PUBLIC_KEY"]
      SNS_TOPIC_ARN = aws_sns_topic.pass_request.arn
      OTP_RANDOM_KEY = var.local_envs["OTP_RANDOM_KEY"]
    }
  }
}

resource "aws_lambda_function" "hevy_api_caller" {
  function_name = "HevyAPICaller"
  role          = var.lambda_role_arn
  package_type = "Image"
  image_uri = "${data.aws_ecr_repository.hevy_api_caller_repo.repository_url}:latest"
  timeout = 900
  source_code_hash = data.aws_ecr_image.hevy_api_caller_latest_image.id

  environment {
    variables = {
      DISCORD_WEBHOOK = var.local_envs["DISCORD_WEBHOOK"]
      HEVY_TOKEN = var.local_envs["HEVY_TOKEN"]
      BUCKET_NAME = var.upload_bucket_name
      DYNAMODB_TABLE_NAME = var.dynamo_workouts_table_name
    }
  }
}

resource "aws_lambda_permission" "invoke_lambda_by_sns" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.hevy_api_caller.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.pass_request.arn
}

resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.discord_bot.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${var.api_gateway_exec_arn}/*/*"
}