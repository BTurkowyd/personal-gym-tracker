resource "aws_s3_bucket" "athena_queries" {
    bucket = "${var.caller_identity_id}-athena-queries-${var.bucket_suffix}"
}