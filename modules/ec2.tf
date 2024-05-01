# resource "aws_instance" "postgres" {
#   ami = "ami-01e444924a2233b07"
#   instance_type = "t2.micro"
#   vpc_security_group_ids = [aws_security_group.ec2_pg_sg.id]
#   associate_public_ip_address = true
#   subnet_id = aws_subnet.public_a.id
#
#   user_data = <<-EOF
#     #!/bin/bash
#     sudo apt update
#     apt install -y postgresql postgresql-contrib
#
#     sudo service postgresql start
#     sleep 5
#
#     sudo -u postgres psql -c "CREATE DATABASE testdb;"
#     sudo -u postgres psql -c "CREATE USER vertislav WITH ENCRYPTED PASSWORD 'password';"
#     sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE testdb TO vertislav;"
#
#     echo "listen_addresses = '*'          # what IP address(es) to listen on;" >> /etc/postgresql/16/main/postgresql.conf
#     echo "host    all    all    0.0.0.0/0   md5" >> /etc/postgresql/16/main/pg_hba.conf
#     echo "host    all    all    ::/0        md5" >> /etc/postgresql/16/main/pg_hba.conf
#
#     sudo systemctl restart postgresql
#
#
#   EOF
#
#   tags = {
#     Name = "WorkoutsPostgresDB"
#   }
# }