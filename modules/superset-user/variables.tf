# ARN of the S3 bucket containing workout data.
variable "data_bucket_arn" {
  type = string
}

# ARN of the S3 bucket used for Athena query results.
variable "athena_bucket_arn" {
  type = string
}