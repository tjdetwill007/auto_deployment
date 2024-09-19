resource "aws_codebuild_project" "name" {
    build_timeout          = 60
    name                   = var.codebuild_name
    project_visibility     = "PRIVATE"
    queued_timeout         = 480
    service_role           = var.codebuild_iam
    tags                   = {}
    tags_all               = {}

    artifacts {
        type                   = "NO_ARTIFACTS"
    }

    cache {
        type     = "NO_CACHE"
    }

    environment {
        compute_type                = "BUILD_GENERAL1_SMALL"
        image                       = "aws/codebuild/standard:7.0"
        image_pull_credentials_type = "CODEBUILD"
        privileged_mode             = false
        type                        = "LINUX_CONTAINER"
    }

    logs_config {
        cloudwatch_logs {
            status      = "ENABLED"
        }
    }

    source {
        git_clone_depth     = 0
        insecure_ssl        = false
        location            = "${var.src_bucket}/app.zip"
        report_build_status = false
        type                = "S3"
    }
}