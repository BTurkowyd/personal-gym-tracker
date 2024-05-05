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
    }
  }
}

data "archive_file" "recent_workouts" {
  type        = "zip"
  source_file = "${path.module}/src/load_recent_workouts.py"
  output_path = "${path.module}/src/load_recent_workouts.zip"
}

resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fetch_recent_from_hevy.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.silka_workouts.execution_arn}/*/*"
}