import json
import boto3
import uuid
import os

WEBSOCKET_URL=os.environ['WEBSOCKET_URL']

def send_update(connectionId,message):
    """Sends message to connected clients
    
    Keyword arguments:
    argument -- connectionId of the client
    argumnet -- message to be sent to the client

    Return: None

    Note: In future this funtion will be used as layers for all the StateMachine lambda function. Message type will be changed to json.
    Author: Teqfocus
    """
    apigateway_management_api = boto3.client('apigatewaymanagementapi', endpoint_url=WEBSOCKET_URL)
    apigateway_management_api.post_to_connection(ConnectionId=connectionId,Data=message)

def create_definition(name, repo_uri, port, command, container_env=None):
    definition={
            "name": name,
            "image": repo_uri,
            "cpu": 0,
            "portMappings": [
                {
                    "name": f"{name}-{port}-tcp",
                    "containerPort": port,
                    "hostPort": port,
                    "protocol": "tcp",
                    "appProtocol": "http"
                }
            ],
            "essential": True,
            "command": command,
            "environment": [],
            "environmentFiles": [],
            "mountPoints": [],
            "volumesFrom": [],
            "ulimits": [],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-create-group": "true",
                    "awslogs-group": "/ecs/",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ecs"
                },
                "secretOptions": []
            },
            "systemControls": []
        }
    if name == "nginx":
        definition["environment"]=[{"name":"nginx_conf","value":str(container_env)}]
    else:
        definition["environment"]=container_env
    return definition

def get_container_definition(frontend_config,backend_config,repo_uris,nginx_conf):
    container_definition=[]
    if frontend_config:
        command = frontend_config["RUN_COMMAND"]
        env_vars=[{"name":str(key),"value":str(value)}for key, value in frontend_config["ENV_VARIABLES"].items()]
        if frontend_config["LANGUAGE_TYPE"] == "nextjs":
            container_definition.append(create_definition("frontend", repo_uris["frontend"], frontend_config["PORT"], command, env_vars))
            container_definition.append(create_definition("nginx",repo_uris["nginx"], 80,[], nginx_conf))
        else:
            container_definition.append(create_definition("frontend", repo_uris["frontend"], frontend_config["PORT"], command, env_vars))
    if backend_config:
        command = backend_config["RUN_COMMAND"]
        env_vars=[{"name":str(key),"value":str(value)}for key, value in backend_config["ENV_VARIABLES"].items()]
        container_definition.append(create_definition("backend", repo_uris["backend"], backend_config["PORT"], command, env_vars))
    return container_definition

def lambda_handler(event, context):

    """Deploys the Task to ECS using taskdefinition.
    
    Keyword arguments:
    argument -- event -- event object from check_build_status
    Return: Returns the Task status(PENDING | RUNNING | PROVISIONING etc.), TaskArn to be used in next Lambda and Language_config.
    Exception: Returns status FAILED with error message.

    Note: Currently TASK_FAMILY and Container NAME is hardcoded to test, in future this will be changed to language type.
    Author: Teqfocus
    """
    deployment_type=event["deployment_type"]
    deployment_mode=event["deployment_mode"]
    user_id=event["user_id"]
    project_name=event["project_name"]
    frontend_config=event.get("frontend_config",None)
    backend_config=event.get("backend_config", None)
    connection_id=event["connection_id"]
    repo_uris=event["repo_uris"]
    nginx_conf=event.get("nginx_config", None)
    repo_uris["nginx"]="094979283411.dkr.ecr.us-east-1.amazonaws.com/nginx_custom:latest"

    TASK_FAMILY=f"{user_id}-{project_name}"
    CLUSTER_NAME=os.environ['CLUSTER_NAME']
    SUBNET_ID=os.environ["PUB_SUBNET_1"]
    SUBNET_ID2=os.environ["PUB_SUBNET_2"]
    SECURITY_GROUP_ID=os.environ["SECURITY_GROUP_ID"]
    
    container_definition=get_container_definition(frontend_config, backend_config, repo_uris, nginx_conf)

    client = boto3.client('ecs')
    try:
        send_update(connection_id, message="Starting the Application Deployment")
        required_cpu = "2048" if deployment_mode == "prod" else "1024"
        required_memory = "5120" if deployment_mode == "prod" else "3072"
        # create task definition
        response = client.register_task_definition(
        family=TASK_FAMILY,
        containerDefinitions=container_definition, cpu=required_cpu, memory=required_memory, requiresCompatibilities=["FARGATE"],networkMode="awsvpc",executionRoleArn=os.environ["ECS_TASK_ROLE_ARN"])
        try:
            task_definition_arn=response['taskDefinition']['taskDefinitionArn']
            # deploy application as task to ecs if the mode is dev
            if event["deployment_mode"] == "dev":
                ecs_deploy = client.run_task(
                cluster=CLUSTER_NAME,
                taskDefinition=task_definition_arn,
                count=1,launchType='FARGATE',networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': [
                        SUBNET_ID
                    ],
                    'securityGroups': [
                        SECURITY_GROUP_ID,
                    ],
                    'assignPublicIp': 'ENABLED'
                }
            })
                if ecs_deploy:
                    task_arn=ecs_deploy['tasks'][0]['taskArn']
                    status=ecs_deploy['tasks'][0]['containers'][0]['lastStatus']
                    send_update(connection_id, f"Deployment status is {status}")
                    return {"status":status,
                            "taskArn":task_arn,
                            "backend_config":backend_config,
                            "deployment_type":deployment_type,
                            "connection_id":connection_id,
                            "deployment_mode":event["deployment_mode"]}
                else:
                    raise Exception("Error in deploying application")
                
            # deploy application as service to ecs if the mode is prod
            else:
                if deployment_type in ["frontend","fullstack"]:
                    container_name="nginx" if frontend_config["LANGUAGE_TYPE"] == "nextjs" else "frontend"
                    container_port=80
                else:
                    container_name="backend"
                    container_port=backend_config["PORT"]
                 
                try:
                    service_name=f"{user_id}_{project_name}_"+str(uuid.uuid1())
                    response = client.create_service(
                            cluster=CLUSTER_NAME,
                            serviceName=service_name,
                            taskDefinition=task_definition_arn,
                            loadBalancers=[
                                {
                                    'targetGroupArn': event["target_group_arn"],
                                    'containerName': container_name,
                                    'containerPort': container_port
                                },
                            ],
                            desiredCount=3, # Fixed to max 3 for now
                            launchType='FARGATE',
                            
                            networkConfiguration={
                                'awsvpcConfiguration': {
                                    'subnets': [
                                        SUBNET_ID,SUBNET_ID2
                                    ],
                                    'securityGroups': [
                                        SECURITY_GROUP_ID,
                                    ],
                                    'assignPublicIp': 'ENABLED'
                                }
                            },
                        
                        )
                    send_update(connection_id, message="Service initialized successfully, waiting for all containers to become operational.")

                    return {"status":"ACTIVE",
                            "service_name": service_name, 
                            "error":False, 
                            "repo_uris":event["repo_uris"], 
                            "stage":"DEPLOY", 
                            "project_name":event["project_name"], 
                            "user_id":event["user_id"], 
                            "connection_id":connection_id, 
                            "deployment_type":event["deployment_type"], 
                            "deployment_mode":event["deployment_mode"],
                            "alb_hosted_zone_id":event["alb_hosted_zone_id"],
                            "dns_name":event["dns_name"]}
                
                except Exception as e:
                    send_update(connection_id, message="An error occurred while initalizing service, deployment will stop!")
                    print("An error occurred while creating service", e)
                    raise Exception("An error occurred while creating service")
                
        except Exception as e:
            print("An error occurred while deploying to ecs",e)
            send_update(connection_id, message="An error occurred while deploying to ecs")
            return {"status":"FAILED", 
                "taskArn": None,
                "error":True,
                "repo_uris":event["repo_uris"],
                "stage":"BUILD",
                "project_name":event["project_name"],
                "user_id":event["user_id"],
                "connection_id":connection_id,
                "deployment_type":event["deployment_type"],
                "deployment_mode":event["deployment_mode"] }
            
    except Exception as e:
        print("An error occurred while registering Task Definition", e)
        send_update(connection_id, message="An error occurred while registering Application")
        return {"status":"FAILED", 
                "taskArn": None,
                "error":True,
                "repo_uris":event["repo_uris"],
                "stage":"BUILD",
                "project_name":event["project_name"],
                "user_id":event["user_id"],
                "connection_id":connection_id,
                "deployment_type":event["deployment_type"],
                "deployment_mode":event["deployment_mode"] }
        