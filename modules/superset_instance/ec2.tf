resource "aws_instance" "superset" {
  ami = "ami-01e444924a2233b07"
  instance_type = "t3.nano"
  vpc_security_group_ids = [aws_security_group.ec2_pg_sg.id]
  associate_public_ip_address = true
  subnet_id = aws_subnet.public_a.id

  connection {
    type = "ssh"
    user = "ubuntu"
    private_key = file("~/.ssh/superset-ec2")
    host = self.public_ip
  }

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update -y",
      "sudo apt-get install -y docker.io",
      "sudo usermod -aG docker ubuntu",
      "sudo curl -L \"https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)\" -o /usr/local/bin/docker-compose",
      "sudo chmod +x /usr/local/bin/docker-compose"
    ]
  }

  # Upload necessary files
  provisioner "file" {
    source      = "modules/superset_instance/docker/docker-compose.yml"
    destination = "/home/ubuntu/docker-compose.yml"
  }

  provisioner "file" {
    source      = "modules/superset_instance/docker/.env"
    destination = "/home/ubuntu/.env"
  }

  provisioner "file" {
    source      = "modules/superset_instance/docker/superset/superset_config.py"
    destination = "/home/ubuntu/superset/superset_config.py"
  }

  provisioner "file" {
    source      = "modules/superset_instance/docker/superset/.env"
    destination = "/home/ubuntu/superset/.env"
  }

  # Run Docker Compose
  provisioner "remote-exec" {
    inline = [
      "cd /home/ubuntu",
      "sudo docker-compose up -d"
    ]
  }

  tags = {
    Name = "Superset"
  }
}