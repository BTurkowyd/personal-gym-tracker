data "http" "myip" {
  url = "https://ipv4.icanhazip.com"
}


# in case I forget to destroy the infrastructure, I will limit the IP addresses from which I can access the EC2 instance
output "current_ip" {
  value = chomp(data.http.myip.response_body)
}