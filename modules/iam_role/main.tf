resource "aws_iam_role" "resouce_role" {
  name                = var.role_name
  assume_role_policy  = var.trust_relationship
  managed_policy_arns = var.policy_arns
}