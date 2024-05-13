variable "lambda_role_arn" {
  description = "The lambda execution role ARN"
  type = string
}

variable "upload_bucket_name" {
  description = "The S3 bucket name to which files are uploaded"
  type = string
}

variable "dynamo_workouts_table_name" {
  description = "Name of the dynamoDB table where workouts infos are uploaded"
  type = string
}

variable "api_gateway_exec_arn" {
  description = "The ARN of the API Gateway which will call the lambda function"
  type = string
}

variable "local_envs" {
  description = "A set of sensitive variables which are not present in the repository"
}