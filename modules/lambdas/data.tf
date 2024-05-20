data "aws_ecr_repository" "discord_bot_repo" {
  name = var.discord_bot_ecr_repo_name
  depends_on = [var.discord_bot_ecr_repo_name]
}

data "aws_ecr_repository" "hevy_api_caller_repo" {
  name = var.hevy_api_caller_repo_name
  depends_on = [var.hevy_api_caller_repo_name]
}

data "aws_ecr_repository" "fetch_all_workouts_repo" {
  name = var.fetch_all_workouts_repo_name
  depends_on = [var.fetch_all_workouts_repo_name]
}