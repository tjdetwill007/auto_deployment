output "lambda_layer_arn" {
  value = aws_lambda_layer_version.lambda_layer.arn
}

output "git_arn" {
  value = local.external_layers.git.arn
}