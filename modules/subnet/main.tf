resource "aws_subnet" "coe_subnets" {
  vpc_id     = var.vpc_id
  cidr_block = var.cidr

  tags = {
    Name = var.subnet_name
  }
}