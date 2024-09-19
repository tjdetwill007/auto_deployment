variable "lambda_iam_role_name" {
  type = string
  default = "coe-devops-lambda-role"
}
variable "lambda_iam_trust_relationship" {
  type = string
  default = "policy_json/trust_relationship/lambda.json"
}
variable "lambda_iam_policy_arns" {
  type = list(string)
  default = ["arn:aws:iam::aws:policy/AmazonAPIGatewayInvokeFullAccess",
            "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess",
            "arn:aws:iam::aws:policy/AmazonECS_FullAccess",
            "arn:aws:iam::aws:policy/AmazonRoute53FullAccess",
            "arn:aws:iam::aws:policy/AmazonS3FullAccess",
            "arn:aws:iam::aws:policy/AmazonSQSFullAccess",
            "arn:aws:iam::aws:policy/AWSCodeBuildAdminAccess",
            "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
            "arn:aws:iam::aws:policy/AWSStepFunctionsFullAccess"]
}

variable "codebuild_iam_role_name" {
  type = string
  default = "codebuild-coe-role"
}
variable "codebuild_iam_trust_relationship" {
  type = string
  default = "policy_json/trust_relationship/codebuild.json"
}
variable "codebuild_iam_policy_arns" {
  type = list(string)
  default = ["arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess",
            "arn:aws:iam::aws:policy/AmazonS3FullAccess",
            "arn:aws:iam::aws:policy/AWSCodeBuildDeveloperAccess",
            "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"]
}

variable "ecs_iam_role_name" {
  type = string
  default = "ecs-task-executionrole"
}
variable "ecs_iam_trust_relationship" {
  type = string
  default = "policy_json/trust_relationship/ecs.json"
}
variable "ecs_iam_policy_arns" {
  type = list(string)
  default = ["arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy","arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"]
}

variable "step_function_iam_role_name" {
  type = string
  default = "stepfunctions-role" 
}
variable "step_function_iam_trust_relationship" {
  type = string
  default = "policy_json/trust_relationship/step_function.json"
}
variable "step_function_iam_policy_arns" {
  type = list(string)
  default = []
}
variable "step_function_policy_name" {
  type = string
  default = "step_function_invoke_lambda"
}
variable "step_function_action" {
  type = list(string)
  default = [ "lambda:InvokeFunction" ]
}
variable "step_function_resources" {
  type = string
  default = "*"
}

variable "codebuild_project_name" {
  type = string
  default = "coe-devops-builder"
}

variable "src_bucket_name" {
  description = "The name of the source s3 bucket"
  type        = string
  default = "teqfocuslanguagesrc"
  validation {
    condition     = length(var.src_bucket_name) > 0
    error_message = "The bucket name cannot be empty"
  }
}

variable "docker_bucket_name" {
  description = "The name of the docker files s3 bucket"
  type        = string
  default = "teqfocusdockerbucket"
  validation {
    condition     = length(var.docker_bucket_name) > 0
    error_message = "The bucket name cannot be empty"
  }
}

variable "build_bucket_name" {
  description = "The name of the build s3 bucket"
  type        = string
  default = "teqfocusbuildbucket"
  validation {
    condition     = length(var.build_bucket_name) > 0
    error_message = "The bucket name cannot be empty"
  }
}

variable "yaml_layer_name" {
  default = "yaml"
}

variable "git_layer_name" {
  default = "git"
}
variable "vpc_cidr" {
  type = string
  default = "192.168.0.0/16"
}
variable "public1_cidr" {
  type = string
  default = "192.168.0.0/20"
}
variable "public1_name" {
  type = string
  default = "coe_public_subnet_1"
}
variable "public2_cidr" {
  type = string
  default = "192.168.16.0/20"
}
variable "public2_name" {
  type = string
  default = "coe_public_subnet_2"
}
variable "private1_cidr" {
  type = string
  default = "192.168.128.0/20"
}
variable "private1_name" {
  type = string
  default = "coe_private_subnet_1"
}
variable "private2_cidr" {
  type = string
  default = "192.168.144.0/20"
}
variable "private2_name" {
  type = string
  default = "coe_private_subnet_2"
}

variable "queue_name" {
  type = string
  default = "coe_devops_queue"
}
variable "statemachine_name" {
  type = string
  default = "coe_stepfunction"
}
variable "cluster_name" {
  type = string
  default = "coe-devops-cluster"
}
variable "websocket_name" {
  type = string
  default = "coe_websocket"
}
variable "stage_name" {
  type = string
  default = "dev"
}

variable "aws_profile" {
  type = string
  default = "teqfocus"
}