data "aws_ecr_repository" "discord_bot_repo" {
  name = var.discord_bot_ecr_repo_name
}

data "aws_ecr_repository" "hevy_api_caller_repo" {
  name = var.hevy_api_caller_repo_name
}