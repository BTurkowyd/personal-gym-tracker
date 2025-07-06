output "athena_bucket_arn" {
  // Output the ARN of the Athena S3 bucket for use in other modules or environments.
  value = aws_s3_bucket.athena_queries.arn
}

output "athena_queries_bucket" {
  // Output the name of the S3 bucket used for Athena query results.
  value = aws_s3_bucket.athena_queries.bucket
}

output "athena_database_name" {
  // Output the name of the Athena database created for workouts.
  value = aws_athena_database.athena_workouts_database.name
}