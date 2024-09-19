import boto3
import os

WEBSOCKET_URL=os.environ["WEBSOCKET_URL"]
def send_update(connectionId,message):

    """Sends message to connected clients
    
    Keyword arguments:
    argument -- connectionId of the client
    argumnet -- message to be sent to the client

    Return: None

    Note: In future this funtion will be used as layers for all the StateMachine lambda function. Message type will be changed to json.
    Author: Teqfocus
    """

    apigateway_management_api = boto3.client('apigatewaymanagementapi', endpoint_url = WEBSOCKET_URL)
    apigateway_management_api.post_to_connection(ConnectionId=connectionId,Data=message)

def lambda_handler(event, context):
    alb_name=event["user_id"]
    client=boto3.client("elbv2")
    response = client.describe_load_balancers()
    send_update(event["connection_id"],"Checking load balancer status" )
    for albs in response["LoadBalancers"]:
        if albs["LoadBalancerName"] == alb_name:
            state = albs["State"]["Code"]
            send_update(event["connection_id"], f"Current state of load balancer is {state}")
            if state == "active":
                event["alb_arn"]=albs["LoadBalancerArn"]
                event["alb_status"]=state
            else:
                event["alb_status"]=state

    return event