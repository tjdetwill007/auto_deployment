output "lambda_fn_arn" {
  value = aws_lambda_function.lambda_function_config.arn
}

output "lambda_invoke_arn" {
  value = aws_lambda_function.lambda_function_config.invoke_arn
}