# S3 bucket for storing workout data uploads.
resource "aws_s3_bucket" "upload_bucket" {
  bucket = "${data.aws_caller_identity.current.account_id}-workouts-bucket-${lower(random_id.bucket_suffix.b64_url)}"
}

# Random suffix for bucket name uniqueness.
resource "random_id" "bucket_suffix" {
  byte_length = 16
}