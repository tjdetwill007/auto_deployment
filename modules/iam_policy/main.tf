resource "aws_iam_policy" "step_fn_policy" {
  name = var.policy_name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "${var.action}"
        Effect   = "Allow"
        Resource = "${var.resources}"
      },
    ]
  })
}