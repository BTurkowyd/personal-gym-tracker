# ARN of the Lambda execution role.
variable "lambda_role_arn" {
  description = "The lambda execution role ARN"
  type        = string
}

# Name of the S3 bucket for file uploads.
variable "upload_bucket_name" {
  description = "The S3 bucket name to which files are uploaded"
  type        = string
}

# Name of the DynamoDB table for workout metadata.
variable "dynamo_workouts_table_name" {
  description = "Name of the dynamoDB table where workouts infos are uploaded"
  type        = string
}

# ARN of the API Gateway that will invoke the Lambda function.
variable "api_gateway_exec_arn" {
  description = "The ARN of the API Gateway which will call the lambda function"
  type        = string
}

# Map of sensitive environment variables (not stored in the repository).
variable "local_envs" {
  description = "A set of sensitive variables which are not present in the repository"
}

# Name of the ECR repository for the Discord bot Lambda image.
variable "discord_bot_ecr_repo_name" {
  description = "The name of the ECR repository"
}

# Name of the ECR repository for the Hevy API caller Lambda image.
variable "hevy_api_caller_repo_name" {
  description = "The name of the ECR repository"
}

# Name of the ECR repository for the fetch all workouts Lambda image.
variable "fetch_all_workouts_repo_name" {
  description = "The name of the ECR repository"
}

# Name of the ECR repository for the Get Glue table schema Lambda image.
variable "get_table_schema_repo_name" {
  description = "The name of the ECR repository"
}

# Name of the ECR repository for the Execute Athena Query Lambda image.
variable "execute_athena_query_repo_name" {
  description = "The name of the ECR repository"
}

# Name of the ECR repository for the AI Agent Lambda image.
variable "ai_agent_repo_name" {
  description = "The name of the ECR repository"
}

variable "athena_database_name" {
  description = "The name of the Athena database for workouts"
  type        = string
}

variable "athena_queries_bucket" {
  description = "The S3 bucket location for Athena query results"
  type        = string
}

variable "lance_db_bucket_name" {
  description = "The S3 bucket name for LanceDB storage"
  type        = string
}