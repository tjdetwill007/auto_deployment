resource "aws_vpc" "coe_vpc" {
  cidr_block       = var.cidr
  instance_tenancy = "default"

  tags = {
    Name = "coe_devops_vpc"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.coe_vpc.id

  tags = {
    Name = "coe_igw"
  }
}

resource "aws_security_group" "coe_sg" {
  name        = "coe_devops_sg"
  vpc_id      = aws_vpc.coe_vpc.id

  tags = {
    Name = "coe_devops_sg"
  }
}


