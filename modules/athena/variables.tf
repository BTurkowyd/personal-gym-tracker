// Suffix to append to the Athena S3 bucket name for uniqueness.
variable "bucket_suffix" {
  type = string
}

// The AWS account or caller identity ID, used for resource naming.
variable "caller_identity_id" {
  type = string
}

// The S3 bucket where workout data is stored.
variable "data_bucket" {
  type = string
}