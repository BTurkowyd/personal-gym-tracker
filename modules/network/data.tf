data "http" "myip" {
  url = "https://ipv4.icanhazip.com"
}

output "current_ip" {
  value = chomp(data.http.myip.response_body)
}