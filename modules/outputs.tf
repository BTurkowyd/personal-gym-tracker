output "superset_user_access_key" {
  value     = module.superset_user.aws_access_key_id
  sensitive = true
}

output "superset_user_secret_key" {
  value     = module.superset_user.aws_secret_access_key
  sensitive = true
}