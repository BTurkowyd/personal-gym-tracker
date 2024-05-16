# terraform {
#   required_providers {
#     aws = {
#       source  = "hashicorp/aws"
#       version = "~> 5.0"
#     }
#   }
#   backend "s3" {
#     bucket = "terraform-states-6mabw3s4smjiozsqyi76rq"
#     key    = "projects/silka"
#     region = "eu-central-1"
#   }
# }

# provider "aws" {
#   region = "eu-central-1"
# }

module "lambdas" {
  source = "./lambdas/"
  api_gateway_exec_arn = aws_api_gateway_rest_api.silka_workouts.execution_arn
  dynamo_workouts_table_name = aws_dynamodb_table.workouts_table.name
  lambda_role_arn = aws_iam_role.lambda_role.arn
  upload_bucket_name = aws_s3_bucket.upload_bucket.bucket
  local_envs = local.envs
}