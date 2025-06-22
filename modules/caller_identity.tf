# Data source to get information about the current AWS account.
data "aws_caller_identity" "current" {}

# Output the AWS account ID.
output "account_id" {
  value = data.aws_caller_identity.current.account_id
}

# Output the full ARN of the caller.
output "caller_arn" {
  value = data.aws_caller_identity.current.arn
}

# Output the user ID of the caller.
output "caller_user" {
  value = data.aws_caller_identity.current.user_id
}

