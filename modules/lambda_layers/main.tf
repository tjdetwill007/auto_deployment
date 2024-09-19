resource "aws_lambda_layer_version" "lambda_layer" {
  filename   = var.lambda_layer_filename
  layer_name = var.lambda_layer_name
  compatible_runtimes = ["python3.11"]
}
