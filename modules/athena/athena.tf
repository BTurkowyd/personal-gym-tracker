resource "aws_athena_database" "athena_workouts_database" {
  bucket = aws_s3_bucket.athena_queries.id
  name   = "${var.caller_identity_id}_workouts_database"
}