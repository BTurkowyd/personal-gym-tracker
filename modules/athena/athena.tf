// Athena database resource for storing workout data.
// The database is named using the caller's identity for uniqueness.
resource "aws_athena_database" "athena_workouts_database" {
  bucket = aws_s3_bucket.athena_queries.id  // S3 bucket for Athena query results
  name   = "${var.caller_identity_id}_workouts_database" // Unique database name
}