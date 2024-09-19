import boto3
import json
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

def get_public_ip(networkInterfaceId):
    try:
        """Gets the Public Ip using the Interface ID of Container Task"""
        
        ec2 = boto3.client('ec2')
        response = ec2.describe_network_interfaces(NetworkInterfaceIds=[networkInterfaceId])
        print(response)
        return response['NetworkInterfaces'][0]['Association']['PublicIp']  
    except Exception as e:
        print("An error occurred while fetching public ip", e)
        return None
    
def lambda_handler(event,context):

    """Check the ECS deployment Status
    
    Keyword arguments:
    argument -- event -- event object from Deploy to ECS
    Return: status -- returns task status
            taskArn -- returns task ARN
            Language_config -- to get the event as Language_config after wait state
    Exception: Returns the status of Task and a deployment failed message.
    Author: Teqfocus 
    """
    if event["deployment_mode"] == "dev":

        CLUSTER_NAME=os.environ['CLUSTER_NAME']
        status=event["status"]
        print(json.dumps(event))
        connection_id=event["connection_id"]
        if status == 'FAILED':
            send_update(connection_id,message="Deployement Failed")
            return {"status":status,"body": "Deployment failed"} #need to return complete deletion body, returning failed body for test
        else:
            send_update(connection_id,message=f"Deployment Status is {status}")
        
        task_arn=event["taskArn"]
        
        try:
            client = boto3.client('ecs')
            response = client.describe_tasks(cluster=CLUSTER_NAME, tasks=[task_arn])
            print(response)
            last_status=response['tasks'][0]['containers'][0]['lastStatus']
            send_update(connection_id, message=f"Deployment Status is {last_status}")
            if last_status == 'RUNNING':
                networkInterfaceId=response['tasks'][0]['attachments'][0]['details'][1]["value"]
                public_ip=get_public_ip(networkInterfaceId)
                if public_ip is None:
                    raise Exception("Public IP not found")
                port=event["backend_config"]["PORT"] if event["deployment_type"] == "backend" else 80
                send_update(connection_id, message=f"Application is Running on {public_ip}:{port}")
                
            return {"status":last_status,
                    "taskArn":task_arn,
                    "backend_config":event["backend_config"], 
                    "deployment_type":event["deployment_type"],
                    "deployment_mode":event["deployment_mode"],
                    "connection_id":connection_id}
            
        except Exception as e:
            print("An error occurred while fetching status",e)
            send_update(connection_id,message="Deployement Failed")
            return {"error":True,
                    "repo_uris":event["repo_uris"],
                    "stage":"BUILD",
                    "project_name":event["project_name"],
                    "user_id":event["user_id"],
                    "connection_id":connection_id,
                    "deployment_type":event["deployment_type"],
                    "deployment_mode":event["deployment_mode"]}
    else:
        return event        
