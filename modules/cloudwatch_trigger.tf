resource "aws_cloudwatch_event_rule" "daily_trigger" {
  name                = "DailyLambdaTrigger"
  schedule_expression = "cron(0 22 * * ? *)"  # Trigger at 8:00 AM UTC every day
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule = aws_cloudwatch_event_rule.daily_trigger.name
  arn  = aws_lambda_function.fetch_recent_from_hevy.arn
}

resource "aws_lambda_permission" "cloudwatch_permission" {
  statement_id  = "AllowCloudWatchToInvokeLambda"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fetch_recent_from_hevy.arn
  principal     = "events.amazonaws.com"

  source_arn = aws_cloudwatch_event_rule.daily_trigger.arn
}
