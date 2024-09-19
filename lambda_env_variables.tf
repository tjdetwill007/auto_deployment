locals {
  SQS_URL=module.coe_sqs.sqs_queue_url
  WEBSOCKET_URL="https://${module.websocket_api.api_id}.execute-api.${data.aws_region.current.name}.amazonaws.com/${var.stage_name}"
  CLUSTER_NAME=var.cluster_name
  VPC_ID=module.coe_vpc.vpc_id
  SECURITY_GROUP_ID=module.coe_vpc.security_group_id
  PUB_SUBNET_1=module.coe_subnet["public_1"].subnet_id
  PUB_SUBNET_2=module.coe_subnet["public_1"].subnet_id
  SRC_BUCKET=var.src_bucket_name
  BUILD_BUCKET=var.build_bucket_name
  DOCKER_BUCKET=var.docker_bucket_name
  ACCOUNT_ID=data.aws_caller_identity.current.account_id
  REGION=data.aws_region.current.name
  STATEMACHINE_ARN=module.stepfunction.step_function_arn
  ECR_PREFIX="${data.aws_caller_identity.current.id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com"
  CODE_BUILD_NAME=var.codebuild_project_name
  ECS_TASK_ROLE_ARN=module.iam_roles["ecs"].role_arn
  }

