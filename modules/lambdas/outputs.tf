output "discord_bot_arn" {
  value = aws_lambda_function.discord_bot.invoke_arn
}