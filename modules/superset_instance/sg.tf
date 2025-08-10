// Security group for the Superset EC2 instance.
resource "aws_security_group" "ec2_pg_sg" {
  vpc_id = aws_vpc.workouts_vpc.id

  tags = {
    Name = "WorkoutsLambdaSG"
  }
}

// Allow all outbound traffic from the instance.
resource "aws_vpc_security_group_egress_rule" "allow_all_traffic_ipv4" {
  security_group_id = aws_security_group.ec2_pg_sg.id
  cidr_ipv4         = aws_vpc.workouts_vpc.cidr_block
  ip_protocol       = "-1" // All protocols/ports
}

// Restrict HTTP access (port 80) to the user's current public IP.
resource "aws_vpc_security_group_ingress_rule" "http_port" {
  ip_protocol       = "tcp"
  security_group_id = aws_security_group.ec2_pg_sg.id
  from_port = 80
  to_port = 80
  cidr_ipv4 = "${chomp(data.http.myip.response_body)}/32"
}

// Restrict HTTPS access (port 443) to the user's current public IP.
resource "aws_vpc_security_group_ingress_rule" "https_port" {
  ip_protocol       = "tcp"
  security_group_id = aws_security_group.ec2_pg_sg.id
  from_port = 443
  to_port = 443
  cidr_ipv4 = "${chomp(data.http.myip.response_body)}/32"
}

// Restrict Superset UI access (port 8088) to the user's current public IP.
resource "aws_vpc_security_group_ingress_rule" "superset_port" {
  ip_protocol       = "tcp"
  security_group_id = aws_security_group.ec2_pg_sg.id
  from_port = 8088
  to_port = 8088
  cidr_ipv4 = "${chomp(data.http.myip.response_body)}/32"
}

// Restrict SSH access (port 22) to the user's current public IP.
resource "aws_vpc_security_group_ingress_rule" "ssh_port" {
  ip_protocol       = "tcp"
  security_group_id = aws_security_group.ec2_pg_sg.id
  from_port = 22
  to_port = 22
  cidr_ipv4 = "${chomp(data.http.myip.response_body)}/32"
}

// Allow SSH from AWS Instance Connect IP range for temporary access.
resource "aws_vpc_security_group_ingress_rule" "instant_connect" {
  ip_protocol       = "tcp"
  security_group_id = aws_security_group.ec2_pg_sg.id
  from_port = 22
  to_port = 22
  cidr_ipv4 = "3.120.181.40/29"
}