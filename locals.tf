# local variables for IAM roles creation
locals {
  iam_roles = {
    lambda = {
      role_name            = var.lambda_iam_role_name
      trust_relationship   = var.lambda_iam_trust_relationship
      policy_arns          = var.lambda_iam_policy_arns
    }
    codebuild = {
      role_name            = var.codebuild_iam_role_name
      trust_relationship   = var.codebuild_iam_trust_relationship
      policy_arns          = var.codebuild_iam_policy_arns
    }
    ecs = {
      role_name            = var.ecs_iam_role_name
      trust_relationship   = var.ecs_iam_trust_relationship
      policy_arns          = var.ecs_iam_policy_arns
    }
    step_function = {
      role_name            = var.step_function_iam_role_name
      trust_relationship   = var.step_function_iam_trust_relationship
      policy_arns          = [module.step_function_policy.policy_arn]
    }
  }
}

#local variables for s3 buckets
locals {
  s3_buckets={
    src_bucket={
      name=var.src_bucket_name
    }
    docker_bucket={
      name=var.docker_bucket_name
    }
    build_bucket={
      name=var.build_bucket_name
  }
}
}

# Local variables for lambda layers
locals {
  lambda_layers = {
    yaml={
      filename="${path.module}/lambda_layer_zip/yaml.zip"
      layer_name=var.yaml_layer_name
    }
    git={
      filename="${path.module}/lambda_layer_zip/git.zip"
      layer_name=var.git_layer_name
    }
  }
}

# Lambda function configuration
locals {
  lambda_fn={
    check_ecs_deploy_status={
      filename="check_ecs_deploy_status"
      fn_name="check_ecs_deploy_status"
    }
  
  check_codeBuild_status={
    filename="check_codeBuild_status"
    fn_name="check_codeBuild_status"
  }
  coe-devops-workflow={
    filename="coe-devops-workflow"
    fn_name="coe-devops-workflow"
    layers_arn=[module.lambdalayers["yaml"].lambda_layer_arn,
                module.lambdalayers["git"].lambda_layer_arn,
                module.lambdalayers["git"].git_arn]
  }
  Deploy_to_ecs={
    filename="Deploy_to_ecs"
    fn_name="Deploy_to_ecs"
  }
  authenticate_websocket={
    filename="authenticate_websocket"
    fn_name="authenticate_websocket"
  }
  generate_presigned_url={
    filename="generate_presigned_url"
    fn_name="generate_presigned_url"
  }
  add_to_queue={
    filename="add_to_queue"
    fn_name="add_to_queue"
  }
  start_execution={
    filename="start_execution"
    fn_name="start_execution"
  }
  cleanup_ecr={
    filename="cleanup_ecr"
    fn_name="cleanup_ecr"
  }
  create_alb={
    filename="create_alb"
    fn_name="create_alb"
  }
  check_alb_status={
    filename="check_alb_status"
    fn_name="check_alb_status"
  }
  check_service_status={
    filename="check_service_status"
    fn_name="check_service_status"
  }
}
}

# subnet configuration
locals {
  subnets={
    public_1={
      cidr=var.public1_cidr
      subnet_name= var.public1_name
    }
    public_2={
      cidr=var.public2_cidr
      subnet_name= var.public2_name
    }
    private_1={
      cidr=var.private1_cidr
      subnet_name= var.private1_name
    }
    private_2={
      cidr=var.private2_cidr
      subnet_name= var.private2_name
    }
  }
}

# Route table configuration
locals {
  route_tables={
    public_rt_1={
      route_table_name="public_rt_1"
      subnet_name="public_1"
    }
    public_rt_2={
      route_table_name="public_rt_2"
      subnet_name="public_2"
    }
  }
}

# Allowed ports and IPs
locals {
  allowed_ip_ports={
    http={
      allowed_ip_address="0.0.0.0/0"
      allow_port=80
    }
    https={
      allowed_ip_address="0.0.0.0/0"
      allow_port=443
    }
  }
}

# Add resource based policy to lambda to allow websocket 
locals {
  lambda_allow_wss={
    lambda1={
      function_name="authenticate_websocket"
      route_key="$connect"
    }
    lambda2={
      function_name="add_to_queue"
      route_key="addqueue"
    }
    lambda3={
      function_name="generate_presigned_url"
      route_key="getpresignedurl"
    }
  }
}

# dockerfiles key names
locals {
  dockerfiles_key = toset(["nextjs-dockerfile",
  "nodejs-dockerfile",
  "python_flask-dockerfile",
  "react-dockerfile"])
}


locals {
  lambda_update={
    check_ecs_deploy_status={
      filename="check_ecs_deploy_status"
      fn_name="check_ecs_deploy_status"
      env_vars=tomap({"WEBSOCKET_URL"="${local.WEBSOCKET_URL}","CLUSTER_NAME"="${local.CLUSTER_NAME}"})
    }
  
  check_codeBuild_status={
    filename="check_codeBuild_status"
    fn_name="check_codeBuild_status"
    env_vars=tomap({"WEBSOCKET_URL"="${local.WEBSOCKET_URL}"})
  }
  coe-devops-workflow={
    filename="coe-devops-workflow"
    fn_name="coe-devops-workflow"
    env_vars=tomap({"WEBSOCKET_URL"="${local.WEBSOCKET_URL}","REGION"="${local.REGION}",
    "ECR_PREFIX"="${local.ECR_PREFIX}","CODE_BUILD_NAME"="${local.CODE_BUILD_NAME}",
    "SRC_BUCKET"="${local.SRC_BUCKET}","DOCKER_BUCKET"="${local.DOCKER_BUCKET}",
    "BUILD_BUCKET"="${local.BUILD_BUCKET}"})
  }
  Deploy_to_ecs={
    filename="Deploy_to_ecs"
    fn_name="Deploy_to_ecs"
    env_vars=tomap({"WEBSOCKET_URL"="${local.WEBSOCKET_URL}","CLUSTER_NAME"="${local.CLUSTER_NAME}","PUB_SUBNET_1"="${local.PUB_SUBNET_1}","PUB_SUBNET_2"="${local.PUB_SUBNET_2}","SECURITY_GROUP_ID"="${local.SECURITY_GROUP_ID}","ECS_TASK_ROLE_ARN"="${local.ECS_TASK_ROLE_ARN}"})
  }
  authenticate_websocket={
    filename="authenticate_websocket"
    fn_name="authenticate_websocket"
  }
  generate_presigned_url={
    filename="generate_presigned_url"
    fn_name="generate_presigned_url"
  }
  add_to_queue={
    filename="add_to_queue"
    fn_name="add_to_queue"
    env_vars=tomap({"SQS_URL"="${local.SQS_URL}"})
  }
  start_execution={
    filename="start_execution"
    fn_name="start_execution"
    env_vars=tomap({"WEBSOCKET_URL"="${local.WEBSOCKET_URL}","STATEMACHINE_ARN"="${local.STATEMACHINE_ARN}"})
  }
  cleanup_ecr={
    filename="cleanup_ecr"
    fn_name="cleanup_ecr"
    env_vars={}
  }
  create_alb={
    filename="create_alb"
    fn_name="create_alb"
    env_vars=tomap({"WEBSOCKET_URL"="${local.WEBSOCKET_URL}","PUB_SUBNET_1" = "${local.PUB_SUBNET_1}","PUB_SUBNET_2"="${local.PUB_SUBNET_2}"})
  }
  check_alb_status={
    filename="check_alb_status"
    fn_name="check_alb_status"
    env_vars=tomap({"WEBSOCKET_URL"="${local.WEBSOCKET_URL}"})
  }
  check_service_status={
    filename="check_service_status"
    fn_name="check_service_status"
    env_vars=tomap({"WEBSOCKET_URL"="${local.WEBSOCKET_URL}","CLUSTER_NAME"="${local.CLUSTER_NAME}"})
  }
}
}