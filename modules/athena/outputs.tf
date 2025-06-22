output "athena_bucket_arn" {
  // Output the ARN of the Athena S3 bucket for use in other modules or environments.
  value = aws_s3_bucket.athena_queries.arn
}