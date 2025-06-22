// S3 bucket for storing Athena query results.
// The bucket name is unique per caller and environment.
resource "aws_s3_bucket" "athena_queries" {
    bucket = "${var.caller_identity_id}-athena-queries-${var.bucket_suffix}"
}

// Lifecycle policy to expire objects older than 180 days in the Athena queries bucket.
resource "aws_s3_bucket_lifecycle_configuration" "lifecycle_policy" {
    bucket = aws_s3_bucket.athena_queries.bucket

    rule {
        id     = "older_than_180_days"
        status = "Enabled"

        expiration {
            days = 180
        }
    }
}