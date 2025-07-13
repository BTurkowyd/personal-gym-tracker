# Lookup the ECR repository for the Discord bot Lambda image.
data "aws_ecr_repository" "discord_bot_repo" {
  name       = var.discord_bot_ecr_repo_name
  depends_on = [var.discord_bot_ecr_repo_name]
}

# Lookup the ECR repository for the Hevy API caller Lambda image.
data "aws_ecr_repository" "hevy_api_caller_repo" {
  name       = var.hevy_api_caller_repo_name
  depends_on = [var.hevy_api_caller_repo_name]
}

# Lookup the ECR repository for the fetch all workouts Lambda image.
data "aws_ecr_repository" "fetch_all_workouts_repo" {
  name       = var.fetch_all_workouts_repo_name
  depends_on = [var.fetch_all_workouts_repo_name]
}

# Lookup the ECR repository for the Get Glue table schema Lambda image.
data "aws_ecr_repository" "get_table_schema_repo" {
  name       = var.get_table_schema_repo_name
  depends_on = [var.get_table_schema_repo_name]
}

# Lookup the ECR repository for the Execute Athena Query Lambda image.
data "aws_ecr_repository" "execute_athena_query_repo" {
  name       = var.execute_athena_query_repo_name
  depends_on = [var.execute_athena_query_repo_name]
}

# Get the most recent image from the Discord bot ECR repository.
data "aws_ecr_image" "discord_bot_latest_image" {
  repository_name = data.aws_ecr_repository.discord_bot_repo.name
  most_recent     = true
}

# Get the most recent image from the fetch all workouts ECR repository.
data "aws_ecr_image" "fetch_all_latest_image" {
  repository_name = data.aws_ecr_repository.fetch_all_workouts_repo.name
  most_recent     = true
}

# Get the most recent image from the Hevy API caller ECR repository.
data "aws_ecr_image" "hevy_api_caller_latest_image" {
  repository_name = data.aws_ecr_repository.hevy_api_caller_repo.name
  most_recent     = true
}

# Get the most recent image from the Get Glue table schema ECR repository.
data "aws_ecr_image" "get_table_schema_latest_image" {
  repository_name = data.aws_ecr_repository.get_table_schema_repo.name
  most_recent     = true
}

# Get the most recent image from the Execute Athena Query ECR repository.
data "aws_ecr_image" "execute_athena_query_latest_image" {
  repository_name = data.aws_ecr_repository.execute_athena_query_repo.name
  most_recent     = true
}