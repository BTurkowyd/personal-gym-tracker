resource "aws_sns_topic" "pass_request" {
  name = "PassRequestToHevyAPILambdaCaller"
}

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

resource "aws_sns_topic_subscription" "subscription" {
  endpoint  = aws_lambda_function.test_lambda.arn
  protocol  = "lambda"
  topic_arn = aws_sns_topic.pass_request.arn
}