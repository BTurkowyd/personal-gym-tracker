resource "aws_instance" "superset" {
  ami = "ami-01e444924a2233b07"
  instance_type = "t3.nano"
  vpc_security_group_ids = [aws_security_group.ec2_pg_sg.id]
  associate_public_ip_address = true
  subnet_id = aws_subnet.public_a.id

  user_data = <<-EOF
    #!/bin/bash
    sudo apt update
    sudo apt install -y docker.io docker-compose
    sudo systemctl start docker
    sudo systemctl enable docker
  EOF

  tags = {
    Name = "Superset"
  }
}