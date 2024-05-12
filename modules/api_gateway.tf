resource "aws_api_gateway_rest_api" "silka_workouts" {
  name        = "SilkaWorkoutsDiscordBotRestAPI"
}

resource "aws_api_gateway_resource" "silka_workouts_resource" {
  rest_api_id = aws_api_gateway_rest_api.silka_workouts.id
  parent_id   = aws_api_gateway_rest_api.silka_workouts.root_resource_id
  path_part   = "discord_bot"
}

resource "aws_api_gateway_method" "silka_workouts_post" {
  rest_api_id   = aws_api_gateway_rest_api.silka_workouts.id
  resource_id   = aws_api_gateway_resource.silka_workouts_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_method_response" "post_method_response" {
  http_method = aws_api_gateway_method.silka_workouts_post.http_method
  resource_id = aws_api_gateway_resource.silka_workouts_resource.id
  rest_api_id = aws_api_gateway_rest_api.silka_workouts.id
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.silka_workouts.id
  resource_id             = aws_api_gateway_resource.silka_workouts_resource.id
  http_method             = aws_api_gateway_method.silka_workouts_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = module.lambdas.discord_bot_arn
}

resource "aws_api_gateway_deployment" "rest_api_deployment" {
  depends_on = [aws_api_gateway_integration.lambda_integration]

  rest_api_id = aws_api_gateway_rest_api.silka_workouts.id
}

resource "aws_api_gateway_stage" "dev_stage" {
  deployment_id = aws_api_gateway_deployment.rest_api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.silka_workouts.id
  stage_name    = "dev"
}

resource "aws_api_gateway_usage_plan" "rate_limiting" {
  name = "SilkaWorkoutsDiscordBotRestAPIRateLimiter"

  api_stages {
    api_id = aws_api_gateway_rest_api.silka_workouts.id
    stage  = aws_api_gateway_stage.dev_stage.stage_name
  }

  quota_settings {
    limit  = 100
    period = "DAY"
  }
}