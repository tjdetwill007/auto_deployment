data "archive_file" "lambda_src_zip" {
type        = "zip"
source_dir  = "${path.root}/lambda_src/${var.filename}"
output_path = "${path.root}/lambda_src_zip/${var.filename}.zip"
}