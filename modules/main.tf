# Lambda functions module for Discord bot and Hevy API integration.
module "lambdas" {
  source = "./lambdas/"
  api_gateway_exec_arn = aws_api_gateway_rest_api.silka_workouts.execution_arn
  dynamo_workouts_table_name = aws_dynamodb_table.workouts_table.name
  lambda_role_arn = aws_iam_role.lambda_role.arn
  upload_bucket_name = aws_s3_bucket.upload_bucket.bucket
  local_envs = local.envs
  discord_bot_ecr_repo_name = aws_ecr_repository.discord_bot_ecr.name
  hevy_api_caller_repo_name = aws_ecr_repository.hevy_api_caller.name
  fetch_all_workouts_repo_name = aws_ecr_repository.fetch_all_workouts.name
  get_table_schema_repo_name = aws_ecr_repository.get_table_schema.name
  execute_athena_query_repo_name = aws_ecr_repository.execute_athena_query.name
  ai_agent_repo_name = aws_ecr_repository.ai_agent.name
  athena_database_name = module.athena.athena_database_name
  athena_queries_bucket = module.athena.athena_queries_bucket
  lance_db_bucket_name = aws_s3_bucket.lancedb_bucket.bucket
}

# Athena module for query and data lake integration.
module "athena" {
  source = "./athena/"
  bucket_suffix = lower(random_id.bucket_suffix.b64_url)
  caller_identity_id = data.aws_caller_identity.current.account_id
  data_bucket = aws_s3_bucket.upload_bucket.bucket
}

# Superset user IAM module for secure access to Athena and S3.
module "superset_user" {
  source = "./superset-user/"
  athena_bucket_arn = module.athena.athena_bucket_arn
  data_bucket_arn = aws_s3_bucket.upload_bucket.arn
}

# # Superset EC2 instance module for analytics UI.
# module "superset_instance" {
#   source  = "./superset_instance"
# }