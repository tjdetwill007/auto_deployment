output "vpc_id" {
  value = aws_vpc.coe_vpc.id
}

output "igw_id" {
  value = aws_internet_gateway.igw.id
}

output "security_group_id" {
  value = aws_security_group.coe_sg.id
}