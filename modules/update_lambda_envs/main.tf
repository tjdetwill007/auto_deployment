locals {
  env_vars_json = jsonencode(var.env_vars)
}
resource "null_resource" "update_lambda_env" {
  count = var.env_vars == "" || var.env_vars == null ? 0 : 1
  triggers = {
    json_md5 = md5(local.env_vars_json)
  }
  provisioner "local-exec" {
    command = <<EOT
      python ${path.module}/updater.py --env_vars ${local.env_vars_json} --region ${data.aws_region.current.name} --profile ${var.profile} --function_name ${var.function_name}
    EOT
  }
}