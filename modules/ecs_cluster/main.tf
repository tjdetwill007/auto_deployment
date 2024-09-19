resource "aws_ecs_cluster" "coe_ecs" {
    name     = var.cluster_name
    configuration {
        execute_command_configuration {
            logging    = "DEFAULT"
        }
    }
    setting {
        name  = "containerInsights"
        value = "disabled"
    }
}

resource "aws_ecs_cluster_capacity_providers" "coe_ecs_capacity" {
  cluster_name = aws_ecs_cluster.coe_ecs.name

  capacity_providers = ["FARGATE"]
}