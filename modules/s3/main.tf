resource "aws_s3_bucket" "coe_buckets" {
  bucket = var.bucket_name
  force_destroy = true
  tags = {
    environment = "coe-devops"
  }
}