# Output the ARN for the Discord bot Lambda function (for API Gateway integration).
output "discord_bot_arn" {
  value = aws_lambda_function.discord_bot.invoke_arn
}