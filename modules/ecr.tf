resource "aws_ecr_repository" "discord_bot_ecr" {
  name = "discord-bot-lambda"
  force_delete = true
}



resource "aws_ecr_repository" "hevy_api_caller" {
  name = "hevy-api-caller"
  force_delete = true
}