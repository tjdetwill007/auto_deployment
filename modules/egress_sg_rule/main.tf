resource "aws_vpc_security_group_egress_rule" "allow_all_traffic_ipv4" {
  security_group_id = var.sg_id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}