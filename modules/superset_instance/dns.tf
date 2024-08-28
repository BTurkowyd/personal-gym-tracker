resource "aws_route53_record" "www" {
  zone_id = "Z094815326EO2E4H1PRCA"
  name    = "superset.turkowyd.com"
  type    = "A"
  ttl     = 300
  records = [aws_instance.superset.public_ip]
}