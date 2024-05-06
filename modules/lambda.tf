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

resource "aws_lambda_function" "fetch_recent_from_hevy" {
  function_name = "FetchRecentWorkoutsFromHevy"
  role          = aws_iam_role.lambda_role.arn
  source_code_hash = data.archive_file.recent_workouts.output_base64sha256
  handler       = "load_recent_workouts.lambda_fetch_workouts"
  runtime = "python3.11"
  timeout = 900
  filename      = "${path.module}/src/load_recent_workouts.zip"
  layers = [aws_lambda_layer_version.python_requests.arn]

  environment {
    variables = {
      HEVY_TOKEN = local.envs["HEVY_TOKEN"]
      BUCKET_NAME = aws_s3_bucket.upload_bucket.bucket,
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.workouts_table.name
      DISCORD_WEBHOOK = local.envs["DISCORD_WEBHOOK"]
    }
  }
}

data "archive_file" "recent_workouts" {
  type        = "zip"
  source_file = "${path.module}/src/load_recent_workouts.py"
  output_path = "${path.module}/src/load_recent_workouts.zip"
}

resource "aws_lambda_function" "print_latest_workout" {
  function_name = "PrintLatestWorkout"
  role          = aws_iam_role.lambda_role.arn
  source_code_hash = data.archive_file.print_latest_workout.output_base64sha256
  handler       = "print_latest_workout.print_latest_workout"
  runtime = "python3.11"
  timeout = 900
  filename      = "${path.module}/src/print_latest_workout.zip"
  layers = [aws_lambda_layer_version.python_requests.arn]

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.upload_bucket.bucket,
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.workouts_table.name
      DISCORD_WEBHOOK = local.envs["DISCORD_WEBHOOK"]
    }
  }
}

data "archive_file" "print_latest_workout" {
  type        = "zip"
  source_file = "${path.module}/src/print_latest_workout.py"
  output_path = "${path.module}/src/print_latest_workout.zip"
}

resource "aws_lambda_function" "test_lambda" {
  function_name = "TestLambda"
  role          = aws_iam_role.lambda_role.arn
  source_code_hash = data.archive_file.test_lambda.output_base64sha256
  handler       = "test_lambda.lambda_handler"
  runtime = "python3.11"
  timeout = 900
  filename      = "${path.module}/src/test_lambda.zip"
  layers = [
    aws_lambda_layer_version.python_requests.arn,
    aws_lambda_layer_version.pynacl.arn
  ]

  environment {
    variables = {
      DISCORD_APP_PUBLIC_KEY = local.envs["DISCORD_APP_PUBLIC_KEY"]
    }
  }
}

data "archive_file" "test_lambda" {
    type        = "zip"
  source_file = "${path.module}/src/test_lambda.py"
  output_path = "${path.module}/src/test_lambda.zip"
}

# resource "aws_lambda_permission" "api_gw" {
#   statement_id  = "AllowExecutionFromAPIGateway"
#   action        = "lambda:InvokeFunction"
#   function_name = aws_lambda_function.test_lambda.function_name
#   principal     = "apigateway.amazonaws.com"
#
#   source_arn = "${aws_apigatewayv2_api.silka_workouts.execution_arn}/*/*"
# }