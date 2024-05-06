# resource "aws_apigatewayv2_api" "silka_workouts" {
#   name          = "SilkaWorkouts"
#   protocol_type = "HTTP"
#   cors_configuration {
#     allow_origins = ["*"]
#     allow_methods = ["GET", "POST"]
#     allow_headers = ["Authorization"]
#     max_age = 300
#   }
# }
#
# resource "aws_apigatewayv2_integration" "fetch_latest" {
#   api_id               = aws_apigatewayv2_api.silka_workouts.id
#   integration_type     = "AWS_PROXY"
#   integration_uri      = aws_lambda_function.test_lambda.invoke_arn
#   integration_method   = "POST"
#   connection_type      = "INTERNET"
# }
#
# resource "aws_apigatewayv2_route" "fetch_latest_route" {
#   api_id    = aws_apigatewayv2_api.silka_workouts.id
#   route_key = "POST /fetch_latest"
#   target    = "integrations/${aws_apigatewayv2_integration.fetch_latest.id}"
# }
#
# resource "aws_apigatewayv2_stage" "stage" {
#   api_id    = aws_apigatewayv2_api.silka_workouts.id
#   name      = "dev"
#   auto_deploy = true
# }
#
# output "api_gateway_url" {
#   value = aws_apigatewayv2_api.silka_workouts.api_endpoint
# }
#
# resource "aws_apigatewayv2_deployment" "deployment" {
#   api_id      = aws_apigatewayv2_api.silka_workouts.id
#   description = "Dev deployment"
#
#   depends_on = [aws_apigatewayv2_route.fetch_latest_route]
#
#   lifecycle {
#     create_before_destroy = true
#   }
# }