resource "aws_s3_bucket" "athena_queries" {
    bucket = "${var.caller_identity_id}-athena-queries-${var.bucket_suffix}"
}

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