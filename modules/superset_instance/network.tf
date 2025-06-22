# Placeholder VPC and networking resources for future expansion.
# Currently, only a single public subnet is used for the Superset EC2 instance.

resource "aws_vpc" "workouts_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "Workouts_vpc"
  }
}

# Public subnet A in eu-central-1a
resource "aws_subnet" "public_a" {
  vpc_id = aws_vpc.workouts_vpc.id
  availability_zone = "eu-central-1a"
  cidr_block = "10.0.1.0/24"
  tags = {
    Name="public_a"
  }
}

# Public subnet B in eu-central-1b (not currently used)
resource "aws_subnet" "public_b" {
  vpc_id = aws_vpc.workouts_vpc.id
  availability_zone = "eu-central-1b"
  cidr_block = "10.0.2.0/24"
  tags = {
    Name="public_b"
  }
}

# Internet gateway for public internet access
resource "aws_internet_gateway" "gateway" {
  vpc_id = aws_vpc.workouts_vpc.id
}

# Route table for internet access
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

# Associate public subnet A with the route table
resource "aws_route_table_association" "public_subnet_a" {
  route_table_id = aws_route_table.route_to_ig.id
  subnet_id = aws_subnet.public_a.id
}

# Associate public subnet B with the route table (not currently used)
resource "aws_route_table_association" "public_subnet_b" {
  route_table_id = aws_route_table.route_to_ig.id
  subnet_id = aws_subnet.public_b.id
}