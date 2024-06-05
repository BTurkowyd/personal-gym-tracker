output "athena_bucket_arn" {
  value = aws_s3_bucket.athena_queries.arn
}