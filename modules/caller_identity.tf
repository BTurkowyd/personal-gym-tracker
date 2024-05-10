data "aws_caller_identity" "current" {}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}

output "caller_arn" {
  value = data.aws_caller_identity.current.arn
}

output "caller_user" {
  value = data.aws_caller_identity.current.user_id
}

data "http" "myip" {
  url = "https://ipv4.icanhazip.com"
}

output "current_ip" {
  value = chomp(data.http.myip.response_body)
}