resource "aws_lambda_function" "fetching_from_hevy" {
  function_name = "FetchAllWorkoutsFromHevy"
  role          = aws_iam_role.lambda_role.arn
  source_code_hash = data.archive_file.all_workouts.output_base64sha256
  handler       = "load_all_workouts.lambda_fetch_workouts"
  runtime = "python3.11"
  timeout = 900
  filename      = "${path.module}/src/load_all_workouts.zip"
  layers = [aws_lambda_layer_version.python_requests.arn]

  environment {
    variables = {
      HEVY_TOKEN = local.envs["HEVY_TOKEN"]
      BUCKET_NAME = aws_s3_bucket.upload_bucket.bucket,
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.workouts_table.name
    }
  }
}

data "archive_file" "all_workouts" {
  type        = "zip"
  source_file = "${path.module}/src/load_all_workouts.py"
  output_path = "${path.module}/src/load_all_workouts.zip"
}

resource "aws_lambda_function" "discord_bot" {
  function_name = "DiscordBotWorkouts"
  role          = aws_iam_role.lambda_role.arn
  source_code_hash = data.archive_file.discord_bot.output_base64sha256
  handler       = "discord_bot.lambda_handler"
  runtime = "python3.11"
  timeout = 900
  filename      = "${path.module}/src/discord_bot.zip"
  layers = [
    aws_lambda_layer_version.python_requests.arn,
    aws_lambda_layer_version.pynacl.arn
  ]

  environment {
    variables = {
      HEVY_TOKEN = local.envs["HEVY_TOKEN"]
      BUCKET_NAME = aws_s3_bucket.upload_bucket.bucket,
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.workouts_table.name
      DISCORD_APP_PUBLIC_KEY = local.envs["DISCORD_APP_PUBLIC_KEY"]
    }
  }
}

data "archive_file" "discord_bot" {
    type        = "zip"
  source_file = "${path.module}/src/discord_bot.py"
  output_path = "${path.module}/src/discord_bot.zip"
}

resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.discord_bot.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.silka_workouts.execution_arn}/*/*"
}