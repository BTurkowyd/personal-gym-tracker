resource "aws_ecr_repository" "discord_bot_ecr" {
  name = "discord-bot-lambda"
  force_delete = true
}

resource "aws_ecr_repository" "hevy_api_caller" {
  name = "hevy-api-caller"
  force_delete = true
}

resource "aws_ecr_repository" "fetch_all_workouts" {
  name = "fetch-all-workouts"
  force_delete = true
}

resource "aws_ecr_lifecycle_policy" "discord_bot" {
  policy     = jsonencode(local.lifecycle_policy)
  repository = aws_ecr_repository.discord_bot_ecr.name
}

resource "aws_ecr_lifecycle_policy" "hevy_api_caller" {
  policy     = jsonencode(local.lifecycle_policy)
  repository = aws_ecr_repository.hevy_api_caller.name
}

resource "aws_ecr_lifecycle_policy" "fetch_all_workouts" {
  policy     = jsonencode(local.lifecycle_policy)
  repository = aws_ecr_repository.fetch_all_workouts.name
}

locals {
  lifecycle_policy = {
    rules = [
      {
        rulePriority = 1
        description  = "Delete untagged images older than 1 day"
        selection    = {
          tagStatus     = "untagged"
          countType     = "sinceImagePushed"
          countUnit     = "days"
          countNumber   = 1
        }
        action = {
          type = "expire"
        }
      }
    ]
  }
}