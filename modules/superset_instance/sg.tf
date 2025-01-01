resource "aws_security_group" "ec2_pg_sg" {
  vpc_id = aws_vpc.workouts_vpc.id

  tags = {
    Name = "WorkoutsLambdaSG"
  }
}

resource "aws_vpc_security_group_egress_rule" "allow_all_traffic_ipv4" {
  security_group_id = aws_security_group.ec2_pg_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}

# This ingres rule limits the access only from my own IP (which is dynamic, thus it is not hardcoded)
resource "aws_vpc_security_group_ingress_rule" "http_port" {
  ip_protocol       = "tcp"
  security_group_id = aws_security_group.ec2_pg_sg.id
  from_port = 80
  to_port = 80
  cidr_ipv4 = "${chomp(data.http.myip.response_body)}/32"
}

resource "aws_vpc_security_group_ingress_rule" "https_port" {
  ip_protocol       = "tcp"
  security_group_id = aws_security_group.ec2_pg_sg.id
  from_port = 443
  to_port = 443
  cidr_ipv4 = "${chomp(data.http.myip.response_body)}/32"
}

resource "aws_vpc_security_group_ingress_rule" "superset_port" {
  ip_protocol       = "tcp"
  security_group_id = aws_security_group.ec2_pg_sg.id
  from_port = 8088
  to_port = 8088
  cidr_ipv4 = "${chomp(data.http.myip.response_body)}/32"
}

resource "aws_vpc_security_group_ingress_rule" "ssh_port" {
  ip_protocol       = "tcp"
  security_group_id = aws_security_group.ec2_pg_sg.id
  from_port = 22
  to_port = 22
  cidr_ipv4 = "${chomp(data.http.myip.response_body)}/32"
}

# This ingress rule is for the instance connect only.
resource "aws_vpc_security_group_ingress_rule" "instant_connect" {
  ip_protocol       = "tcp"
  security_group_id = aws_security_group.ec2_pg_sg.id
  from_port = 22
  to_port = 22
  cidr_ipv4 = "3.120.181.40/29"
}