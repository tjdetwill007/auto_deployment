resource "aws_vpc_security_group_ingress_rule" "allow_protocol_ipv4" {
  security_group_id = var.sg_id
  cidr_ipv4         = var.allowed_ip_address
  from_port         = var.allow_port
  ip_protocol       = "tcp"
  to_port           = var.allow_port
}

