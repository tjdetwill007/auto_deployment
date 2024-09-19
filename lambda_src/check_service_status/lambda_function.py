import boto3
import os

WEBSOCKET_URL=os.environ["WEBSOCKET_URL"]
CLUSTER_NAME = os.environ["CLUSTER_NAME"]
DOMAIN_NAME= "cloud-deepak.shop"
HOSTED_ZONE_ID= "Z03905202LZV9VJQ5U2PQ"

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

def add_route_record(dns_name,alb_hosted_zone_id, project_name, user_id):

    client = boto3.client('route53')
    record_name= f"{user_id}.{project_name}.{DOMAIN_NAME}"
    try:
        add_record = client.change_resource_record_sets(
            HostedZoneId=HOSTED_ZONE_ID,
            ChangeBatch={
                'Comment': 'Add loadbalancer DNS record',
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': record_name,
                            'Type': 'A',
                            'AliasTarget': {
                                'HostedZoneId': alb_hosted_zone_id,
                                'DNSName': dns_name,
                                'EvaluateTargetHealth': False
                            }
                        }
                    }
                ]
            }
        )
        return record_name
    except Exception as e:
        print(e)
        return None
def lambda_handler(event, context):

    project_name=event["project_name"]
    dns_name=event["dns_name"]
    user_id=event["user_id"]
    alb_hosted_zone_id=event["alb_hosted_zone_id"]
    try:
        client = boto3.client('ecs')
        response = client.describe_services(
            cluster=CLUSTER_NAME,
            services=[
                event["service_name"]
            ]
        )
        
        status = response["services"][0]["status"]
        if status == "ACTIVE":
            desired_count = response["services"][0]["desiredCount"]
            running_count = response["services"][0]["runningCount"]
            pending_count = response["services"][0]["pendingCount"]
            send_update(event["connection_id"], f"Desired Count: {desired_count} Running Count: {running_count} Pending Count: {pending_count}")
            if desired_count == running_count:
                print("accuired the running count")
                send_update(event["connection_id"], "All containers are operational, requesting for domain name.")
                record_name = add_route_record(dns_name, alb_hosted_zone_id, project_name, user_id)
                if record_name:
                    send_update(event["connection_id"], f"Application deployed successfully.")
                    send_update(event["connection_id"], f"Access link: {record_name}")
                event["status"]="SUCCEEDED"
                return event
            elif pending_count > 0:
                event["status"]= status
                return event
        else:
            event["status"]=status
            return event
    except Exception as e:
        print(e)
        send_update(event["connection_id"], "Application deployment failed due to unexpected error.")