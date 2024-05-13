# The network is not used at all in the entire configuration. But I keep it as a placeholder for my future work,
# as I might try to set up a tiny EC2 instance with Postgres.
resource "aws_vpc" "workouts_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "Workouts_vpc"
  }
}

resource "aws_subnet" "public_a" {
  vpc_id = aws_vpc.workouts_vpc.id
  availability_zone = "eu-central-1a"
  cidr_block = "10.0.1.0/24"
  tags = {
    Name="public_a"
  }
}

resource "aws_subnet" "public_b" {
  vpc_id = aws_vpc.workouts_vpc.id
  availability_zone = "eu-central-1b"
  cidr_block = "10.0.2.0/24"
  tags = {
    Name="public_b"
  }
}

resource "aws_internet_gateway" "gateway" {
  vpc_id = aws_vpc.workouts_vpc.id
}

resource "aws_route_table" "route_to_ig" {
  vpc_id = aws_vpc.workouts_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gateway.id
  }

  tags = {
    Name = "InternetAccessRT"
  }
}

resource "aws_route_table_association" "public_subnet_a" {
  route_table_id = aws_route_table.route_to_ig.id
  subnet_id = aws_subnet.public_a.id
}

resource "aws_route_table_association" "public_subnet_b" {
  route_table_id = aws_route_table.route_to_ig.id
  subnet_id = aws_subnet.public_b.id
}