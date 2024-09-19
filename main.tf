module "step_function_policy" {
  source       = "./modules/iam_policy"
  policy_name  = var.step_function_policy_name
  action       = var.step_function_action
  resources    = var.step_function_resources
}

module "iam_roles" {
  source = "./modules/iam_role"
  for_each = local.iam_roles
  role_name          = each.value.role_name
  trust_relationship = file("${path.module}/${each.value.trust_relationship}")
  policy_arns        = each.value.policy_arns
}
module "s3_buckets" {
  source = "./modules/s3"
  for_each = local.s3_buckets
  bucket_name = each.value.name
}

module "codebuild" {
  source = "./modules/codebuild"
  codebuild_name = var.codebuild_project_name
  codebuild_iam = module.iam_roles["codebuild"].role_arn
  src_bucket = module.s3_buckets["build_bucket"].bucket_name
}

module "lambdalayers" {
  source = "./modules/lambda_layers"
  for_each = local.lambda_layers
  lambda_layer_name= each.value.layer_name
  lambda_layer_filename = each.value.filename
}

module "lambda_function" {
  source = "./modules/lambda"
  for_each = local.lambda_fn
  filename = each.value.filename
  fn_name= each.value.fn_name
  lambda_role= module.iam_roles["lambda"].role_arn
  layers_arn  = lookup(each.value, "layers_arn", [])
}

module "coe_vpc" {
  source = "./modules/vpc"
  cidr = var.vpc_cidr
}

module "coe_subnet" {
  source = "./modules/subnet"
  for_each = local.subnets
  vpc_id = module.coe_vpc.vpc_id
  cidr = each.value.cidr
  subnet_name=each.value.subnet_name
}

module "route_table_pub"{
  source = "./modules/route_table"
  for_each = local.route_tables
  route_table_name = each.value.route_table_name
  vpc_id = module.coe_vpc.vpc_id
  igw_id=module.coe_vpc.igw_id
  subnet_id = module.coe_subnet["${each.value.subnet_name}"].subnet_id
}

module "allowed_sg_rule" {
  source = "./modules/allow_sg"
  for_each = local.allowed_ip_ports
  sg_id = module.coe_vpc.security_group_id
  allowed_ip_address= each.value.allowed_ip_address
  allow_port = each.value.allow_port
}

module "egress_sg_rule" {
  source = "./modules/egress_sg_rule"
  sg_id = module.coe_vpc.security_group_id
}

module "coe_sqs" {
  source = "./modules/sqs"
  queue_name = var.queue_name
}

resource "aws_lambda_event_source_mapping" "sqs_event" {
  event_source_arn  = module.coe_sqs.sqs_arn
  function_name     = module.lambda_function["start_execution"].lambda_fn_arn
  batch_size        = 10
  enabled           = true
}

module "stepfunction" {
  source = "./modules/stepfunction"
  statemachine_name= var.statemachine_name
  step_fn_role= module.iam_roles["step_function"].role_arn
  coe-devops-workflow= module.lambda_function["coe-devops-workflow"].lambda_fn_arn
  check_codeBuild_status= module.lambda_function["check_codeBuild_status"].lambda_fn_arn
  check_alb_status= module.lambda_function["check_alb_status"].lambda_fn_arn
  Deploy_to_ecs= module.lambda_function["Deploy_to_ecs"].lambda_fn_arn
  check_ecs_deploy_status= module.lambda_function["check_ecs_deploy_status"].lambda_fn_arn
  cleanup_ecr = module.lambda_function["cleanup_ecr"].lambda_fn_arn
  create_alb = module.lambda_function["create_alb"].lambda_fn_arn
  check_service_status = module.lambda_function["check_service_status"].lambda_fn_arn
}

module "ecs_cluster" {
  source = "./modules/ecs_cluster"
  cluster_name = var.cluster_name
}

module "websocket_api"{
  source = "./modules/websocket_api"
  stage_name = var.stage_name
  websocket_name = var.websocket_name
  connect= module.lambda_function["authenticate_websocket"].lambda_invoke_arn
  addqueue = module.lambda_function["add_to_queue"].lambda_invoke_arn
  getpresignedurl = module.lambda_function["generate_presigned_url"].lambda_invoke_arn

}

module "lambda_allow_websocket" {
  source = "./modules/lambda_resource_policy"
  for_each = local.lambda_allow_wss
  function_name = each.value.function_name
  api_id = module.websocket_api.api_id
  route_key = each.value.route_key
}

resource "aws_s3_object" "upload_dockerfiles" {
  for_each = local.dockerfiles_key
  bucket = var.docker_bucket_name
  key    = "${each.key}/dockerfile"
  source = "${path.module}/dockerfiles/${each.key}/dockerfile"
  etag   = filemd5("${path.module}/dockerfiles/${each.key}/dockerfile")
  acl    = "private"
}

module "update_lambda" {
  source = "./modules/update_lambda_envs"
  for_each = local.lambda_update
  env_vars = lookup(each.value, "env_vars", "")
  function_name = each.value.fn_name
  profile = var.aws_profile
  depends_on = [ module.lambda_function,module.stepfunction ]
}

