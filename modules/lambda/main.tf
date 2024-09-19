resource "aws_lambda_function" "lambda_function_config" {
  architectures                  = ["x86_64"]
  code_signing_config_arn        = null
  description                    = null
  filename                       = data.archive_file.lambda_src_zip.output_path
  function_name                  = var.fn_name
  handler                        = "lambda_function.lambda_handler"
  image_uri                      = null
  kms_key_arn                    = null
  layers                         = var.layers_arn
  memory_size                    = 128
  package_type                   = "Zip"
  publish                        = null
  reserved_concurrent_executions = -1
  role                           = var.lambda_role
  runtime                        = "python3.11"
  s3_bucket                      = null
  s3_key                         = null
  s3_object_version              = null
  skip_destroy                   = false
  source_code_hash               = filebase64sha256(data.archive_file.lambda_src_zip.output_path)
  tags                           = {}
  tags_all                       = {}
  timeout                        = 180
  ephemeral_storage {
    size = 512
  }

  logging_config {
    application_log_level = null
    log_format            = "Text"
    log_group             = "/aws/lambda/${var.fn_name}"
    system_log_level      = null
  }
  tracing_config {
    mode = "PassThrough"
  }
  lifecycle {
    ignore_changes = [
      environment
    ]
  }
}