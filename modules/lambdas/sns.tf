# SNS topic for passing requests from the Discord bot to the Hevy API Lambda.
resource "aws_sns_topic" "pass_request" {
  name = "PassRequestToHevyAPILambdaCaller"
}

# Allow anyone to publish to the SNS topic (for demonstration; restrict in production).
resource "aws_sns_topic_policy" "sns_" {
  arn    = aws_sns_topic.pass_request.arn
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = "*"
      Action    = "sns:Publish"
      Resource  = aws_sns_topic.pass_request.arn
    }]
  })
}

# Subscribe the Hevy API Lambda function to the SNS topic.
resource "aws_sns_topic_subscription" "subscription" {
  endpoint  = aws_lambda_function.hevy_api_caller.arn
  protocol  = "lambda"
  topic_arn = aws_sns_topic.pass_request.arn
}