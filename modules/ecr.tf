# ECR repository for Discord bot Lambda Docker image.
resource "aws_ecr_repository" "discord_bot_ecr" {
  name = "discord-bot-lambda"
  force_delete = true
}

# ECR repository for Hevy API caller Lambda Docker image.
resource "aws_ecr_repository" "hevy_api_caller" {
  name = "hevy-api-caller"
  force_delete = true
}

# ECR repository for fetch all workouts Lambda Docker image.
resource "aws_ecr_repository" "fetch_all_workouts" {
  name = "fetch-all-workouts"
  force_delete = true
}

# ECR repository for Get Glue table schema Lambda Docker image.
resource "aws_ecr_repository" "get_table_schema" {
  name = "get-glue-table-schema"
  force_delete = true
}

# ECR repository for Execute Athena Query Lambda Docker image.
resource "aws_ecr_repository" "execute_athena_query" {
  name = "execute-athena-query"
  force_delete = true
}

# Lifecycle policy for Discord bot ECR repository.
resource "aws_ecr_lifecycle_policy" "discord_bot" {
  policy     = jsonencode(local.lifecycle_policy)
  repository = aws_ecr_repository.discord_bot_ecr.name
}

# Lifecycle policy for Hevy API caller ECR repository.
resource "aws_ecr_lifecycle_policy" "hevy_api_caller" {
  policy     = jsonencode(local.lifecycle_policy)
  repository = aws_ecr_repository.hevy_api_caller.name
}

# Lifecycle policy for fetch all workouts ECR repository.
resource "aws_ecr_lifecycle_policy" "fetch_all_workouts" {
  policy     = jsonencode(local.lifecycle_policy)
  repository = aws_ecr_repository.fetch_all_workouts.name
}

# Lifecycle policy for Get Glue table schema ECR repository.
resource "aws_ecr_lifecycle_policy" "get_table_schema" {
  policy     = jsonencode(local.lifecycle_policy)
  repository = aws_ecr_repository.get_table_schema.name
}

# Lifecycle policy for Execute Athena Query ECR repository.
resource "aws_ecr_lifecycle_policy" "execute_athena_query" {
  policy     = jsonencode(local.lifecycle_policy)
  repository = aws_ecr_repository.execute_athena_query.name
}

# Local variable defining ECR lifecycle policy to delete untagged images older than 1 day.
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