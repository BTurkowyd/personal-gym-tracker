resource "aws_instance" "superset" {
  ami = "ami-01e444924a2233b07"
  instance_type = "t3.micro"
  vpc_security_group_ids = [aws_security_group.ec2_pg_sg.id]
  associate_public_ip_address = true
  subnet_id = aws_subnet.public_a.id
  key_name = aws_key_pair.superset_ec2_pubkey.key_name

  connection {
    type = "ssh"
    user = "ubuntu"
    private_key = file("~/.ssh/superset-ec2")
    host = self.public_ip
  }

  # Upload necessary files
  provisioner "file" {
    source      = "/Users/bartoszturkowyd/Projects/aws/silka/modules/superset_instance/docker/"
    destination = "/home/ubuntu"
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


resource "aws_key_pair" "superset_ec2_pubkey" {
  key_name = "superset-ec2-pubkey"
  public_key = file("~/.ssh/superset-ec2.pub")
}