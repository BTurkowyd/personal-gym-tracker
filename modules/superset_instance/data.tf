# Fetches the public IP address of the user running Terraform.
# Used to restrict access to the EC2 instance for security.
data "http" "myip" {
  url = "https://ipv4.icanhazip.com"
}


# Output the current public IP address for reference and use in security group rules.
output "current_ip" {
  value = chomp(data.http.myip.response_body)
}