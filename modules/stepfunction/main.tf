resource "aws_sfn_state_machine" "sfn_state_machine" {
  name     = var.statemachine_name
  role_arn = var.step_fn_role

  definition = <<EOF
    {
        "Comment": "Example Step Functions state machine for CodeBuild workflow",
        "StartAt": "Start workflow Build",
        "States": {
        "Start workflow Build": {
            "Type": "Task",
            "Resource": "${var.coe-devops-workflow}",
            "Next": "Status Choice"
        },
        "Status Choice": {
            "Type": "Choice",
            "Choices": [
            {
                "Variable": "$.error",
                "IsPresent": false,
                "Next": "deployment mode choice"
            },
            {
                "Variable": "$.error",
                "BooleanEquals": true,
                "Next": "Cleanup"
            }
            ],
            "Default": "deployment mode choice"
        },
        "deployment mode choice": {
            "Type": "Choice",
            "Choices": [
            {
                "Variable": "$.deployment_mode",
                "StringEquals": "dev",
                "Next": "Check Build Status"
            },
            {
                "Variable": "$.deployment_mode",
                "StringEquals": "prod",
                "Next": "create_alb"
            }
            ],
            "Default": "Check Build Status"
        },
        "WaitState": {
            "Type": "Wait",
            "Seconds": 5,
            "Next": "Check Build Status"
        },
        "Check Build Status": {
            "Type": "Task",
            "Resource": "${var.check_codeBuild_status}",
            "Retry": [
            {
                "ErrorEquals": [
                "States.TaskFailed"
                ],
                "MaxAttempts": 3,
                "IntervalSeconds": 10
            }
            ],
            "Next": "CheckLambda2Status"
        },
        "CheckLambda2Status": {
            "Type": "Choice",
            "Choices": [
            {
                "Variable": "$.Status",
                "StringEquals": "SUCCEEDED",
                "Next": "deployment mode choice after build"
            },
            {
                "Variable": "$.Status",
                "StringEquals": "STOPPED",
                "Next": "Cleanup"
            },
            {
                "Variable": "$.Status",
                "StringEquals": "FAILED",
                "Next": "Cleanup"
            },
            {
                "Variable": "$.Status",
                "StringEquals": "FAULT",
                "Next": "Cleanup"
            },
            {
                "Variable": "$.Status",
                "StringEquals": "TIMED_OUT",
                "Next": "Cleanup"
            }
            ],
            "Default": "WaitState"
        },
        "deployment mode choice after build": {
            "Type": "Choice",
            "Choices": [
            {
                "Variable": "$.deployment_mode",
                "StringEquals": "prod",
                "Next": "check alb status"
            },
            {
                "Variable": "$.deployment_mode",
                "StringEquals": "dev",
                "Next": "Deploy to ECS"
            }
            ],
            "Default": "Deploy to ECS"
        },
        "check alb status": {
            "Type": "Task",
            "Resource": "arn:aws:states:::lambda:invoke",
            "OutputPath": "$.Payload",
            "Parameters": {
            "Payload.$": "$",
            "FunctionName": "${var.check_alb_status}"
            },
            "Retry": [
            {
                "ErrorEquals": [
                "Lambda.ServiceException",
                "Lambda.AWSLambdaException",
                "Lambda.SdkClientException",
                "Lambda.TooManyRequestsException"
                ],
                "IntervalSeconds": 1,
                "MaxAttempts": 3,
                "BackoffRate": 2
            }
            ],
            "Next": "Choice"
        },
        "Choice": {
            "Type": "Choice",
            "Choices": [
            {
                "Variable": "$.alb_status",
                "StringEquals": "active",
                "Next": "Deploy to ECS"
            },
            {
                "Variable": "$.alb_status",
                "StringEquals": "failed",
                "Next": "Cleanup"
            }
            ],
            "Default": "Wait"
        },
        "Wait": {
            "Type": "Wait",
            "Seconds": 5,
            "Next": "check alb status"
        },
        "Deploy to ECS": {
            "Type": "Task",
            "Resource": "arn:aws:states:::lambda:invoke",
            "OutputPath": "$.Payload",
            "Parameters": {
            "Payload.$": "$",
            "FunctionName": "${var.Deploy_to_ecs}"
            },
            "Retry": [
            {
                "ErrorEquals": [
                "Lambda.ServiceException",
                "Lambda.AWSLambdaException",
                "Lambda.SdkClientException",
                "Lambda.TooManyRequestsException"
                ],
                "IntervalSeconds": 1,
                "MaxAttempts": 3,
                "BackoffRate": 2
            }
            ],
            "Next": "WaitStateDeploy"
        },
        "WaitStateDeploy": {
            "Type": "Wait",
            "Seconds": 5,
            "Next": "Check Deploy Status"
        },
        "Check Deploy Status": {
            "Type": "Task",
            "Resource": "${var.check_ecs_deploy_status}",
            "Retry": [
            {
                "ErrorEquals": [
                "States.TaskFailed"
                ],
                "MaxAttempts": 3,
                "IntervalSeconds": 10
            }
            ],
            "Next": "Check Deploy Status Result"
        },
        "Check Deploy Status Result": {
            "Type": "Choice",
            "Choices": [
            {
                "Variable": "$.status",
                "StringEquals": "RUNNING",
                "Next": "SuccessState"
            },
            {
                "Variable": "$.status",
                "StringEquals": "STOPPED",
                "Next": "Cleanup"
            },
            {
                "Variable": "$.status",
                "StringEquals": "FAILED",
                "Next": "Cleanup"
            },
            {
                "Variable": "$.status",
                "StringEquals": "ACTIVE",
                "Next": "check service status"
            }
            ],
            "Default": "WaitStateDeploy"
        },
        "SuccessState": {
            "Type": "Pass",
            "End": true
        },
        "Cleanup": {
            "Type": "Task",
            "Resource": "arn:aws:states:::lambda:invoke",
            "Next": "FailureState",
            "Parameters": {
            "FunctionName": "${var.cleanup_ecr}"
            }
        },
        "FailureState": {
            "Type": "Fail",
            "Error": "Lambda2Failed",
            "Cause": "Lambda 2 encountered an error"
        },
        "create_alb": {
            "Type": "Task",
            "Resource": "arn:aws:states:::lambda:invoke",
            "OutputPath": "$.Payload",
            "Parameters": {
            "Payload.$": "$",
            "FunctionName": "${var.create_alb}"
            },
            "Retry": [
            {
                "ErrorEquals": [
                "Lambda.ServiceException",
                "Lambda.AWSLambdaException",
                "Lambda.SdkClientException",
                "Lambda.TooManyRequestsException"
                ],
                "IntervalSeconds": 1,
                "MaxAttempts": 3,
                "BackoffRate": 2
            }
            ],
            "Next": "Check Build Status"
        },
        "check service status": {
            "Type": "Task",
            "Resource": "arn:aws:states:::lambda:invoke",
            "OutputPath": "$.Payload",
            "Parameters": {
            "Payload.$": "$",
            "FunctionName": "var.check_service_status"
            },
            "Retry": [
            {
                "ErrorEquals": [
                "Lambda.ServiceException",
                "Lambda.AWSLambdaException",
                "Lambda.SdkClientException",
                "Lambda.TooManyRequestsException"
                ],
                "IntervalSeconds": 1,
                "MaxAttempts": 3,
                "BackoffRate": 2
            }
            ],
            "Next": "service status choice"
        },
        "service status choice": {
            "Type": "Choice",
            "Choices": [
            {
                "Variable": "$.status",
                "StringEquals": "ACTIVE",
                "Next": "Wait (1)"
            },
            {
                "Variable": "$.status",
                "StringEquals": "DRAINING",
                "Next": "Cleanup"
            },
            {
                "Variable": "$.status",
                "StringEquals": "INACTIVE",
                "Next": "Cleanup"
            },
            {
                "Variable": "$.status",
                "StringEquals": "SUCCEEDED",
                "Next": "SuccessState"
            }
            ],
            "Default": "check service status"
        },
        "Wait (1)": {
            "Type": "Wait",
            "Seconds": 5,
            "Next": "check service status"
        }
        }
    }
EOF
}
