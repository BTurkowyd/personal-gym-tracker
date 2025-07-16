// Bucket policy to allow Athena to access query results bucket
resource "aws_s3_bucket_policy" "athena_queries_policy" {
  bucket = aws_s3_bucket.athena_queries.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = { Service = "athena.amazonaws.com" },
        Action = [
          "s3:GetBucketLocation",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:ListBucketMultipartUploads",
          "s3:AbortMultipartUpload",
          "s3:PutObject"
        ],
        Resource = [
          aws_s3_bucket.athena_queries.arn,
          "${aws_s3_bucket.athena_queries.arn}/*"
        ]
      }
    ]
  })
}
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

        filter {
          prefix = ""
        }

        expiration {
            days = 180
        }
    }
}