data "template_file" "external_layers" {
  template = file("${path.root}/lambda_layer_zip/outsource_layers/lambda_layer.tpl")
}
locals {
  external_layers = jsondecode(data.template_file.external_layers.rendered)
}
