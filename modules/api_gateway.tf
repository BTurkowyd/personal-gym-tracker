# Create a REST API for the Silka Workouts Discord Bot.
resource "aws_api_gateway_rest_api" "silka_workouts" {
  name = "SilkaWorkoutsDiscordBotRestAPI"
}

# Create a resource path /discord_bot under the API.
resource "aws_api_gateway_resource" "silka_workouts_resource" {
  rest_api_id = aws_api_gateway_rest_api.silka_workouts.id
  parent_id   = aws_api_gateway_rest_api.silka_workouts.root_resource_id
  path_part   = "discord_bot"
}

# Allow POST requests to /discord_bot (no authorization).
resource "aws_api_gateway_method" "silka_workouts_post" {
  rest_api_id   = aws_api_gateway_rest_api.silka_workouts.id
  resource_id   = aws_api_gateway_resource.silka_workouts_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# Define the method response for POST /discord_bot.
resource "aws_api_gateway_method_response" "post_method_response" {
  http_method = aws_api_gateway_method.silka_workouts_post.http_method
  resource_id = aws_api_gateway_resource.silka_workouts_resource.id
  rest_api_id = aws_api_gateway_rest_api.silka_workouts.id
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }
}

# Integrate the POST method with the Discord bot Lambda function using AWS_PROXY.
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.silka_workouts.id
  resource_id             = aws_api_gateway_resource.silka_workouts_resource.id
  http_method             = aws_api_gateway_method.silka_workouts_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = module.lambdas.discord_bot_arn
}

# Deploy the API after integration is set up.
resource "aws_api_gateway_deployment" "rest_api_deployment" {
  depends_on = [aws_api_gateway_integration.lambda_integration]
  rest_api_id = aws_api_gateway_rest_api.silka_workouts.id
}

# Create a stage named "dev" for the API deployment.
resource "aws_api_gateway_stage" "dev_stage" {
  deployment_id = aws_api_gateway_deployment.rest_api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.silka_workouts.id
  stage_name    = "dev"
}

# Usage plan for rate limiting API calls (100 requests per day).
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