import boto3
import os

PUB_SUBNET_1=os.environ.get("PUB_SUBNET_1")
PUB_SUBNET_2=os.environ.get("PUB_SUBNET_2")
WEBSOCKET_URL=os.environ.get("WEBSOCKET_URL")
SECURITY_GROUP_ID=os.environ.get("SECURITY_GROUP_ID")

SUBNETS=[PUB_SUBNET_1,PUB_SUBNET_1]
PRIORITY=1 # Later priority value will be fetched from db
DOMAIN_NAME="cloud-deepak.shop"

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

def lambda_handler(event, context):
    # session = boto3.Session(profile_name='teq')
    client = boto3.client('elbv2')
    # client = session.client('elbv2')
    try:
        send_update(event["connection_id"], "Request generated for creating ALB")
        response = client.create_load_balancer(
            Name = event["user_id"],
            Subnets= SUBNETS,
            SecurityGroups=[
                SECURITY_GROUP_ID,
            ],
            Scheme='internet-facing',
            Tags=[
                {
                    'Key': 'Name',
                    'Value': event["user_id"]
                },
            ]
        )
        alb_hosted_zone_id = response['LoadBalancers'][0]['CanonicalHostedZoneId']
        dns_name = response['LoadBalancers'][0]['DNSName']

        # creating listener with default response
        listener = client.create_listener(LoadBalancerArn=response['LoadBalancers'][0]['LoadBalancerArn'],Protocol="HTTP",Port=80,DefaultActions=[{"Type":"fixed-response",'FixedResponseConfig': {
                    'MessageBody': 'Wait we are trying to get your application up.',
                    'StatusCode': '503',
                    'ContentType': 'text/plain'
                }}])
        listener_arn=listener['Listeners'][0]['ListenerArn']
        send_update(event["connection_id"], "Request generated for creating ALB Listener")

        # creating target group
        port = 80 if event["deployment_type"] in ["frontend","fullstack"] else event["backend_config"]["PORT"]
        target_group = client.create_target_group(Name=f"{event['user_id']}-{event['project_name']}",Protocol="HTTP",Port = port,VpcId="vpc-070d80108295b085f",TargetType="ip")
        target_group_arn=target_group['TargetGroups'][0]['TargetGroupArn']
        send_update(event["connection_id"], "Request generated for creating ALB Target Group")

        # adding rule to the listener
        rule = client.create_rule(ListenerArn=listener_arn,Actions=[{"TargetGroupArn":target_group_arn,"Type":"forward"}],Conditions=[{"Field":"host-header","Values":[f"{event['user_id']}.{event['project_name']}.{DOMAIN_NAME}"]}],Priority=PRIORITY)
        send_update(event["connection_id"], "Creating ALB Rule for this project.")

        # adding extra prod attributes to event
        event["listener_arn"]=listener_arn
        event["target_group_arn"]=target_group_arn
        event["alb_hosted_zone_id"]=alb_hosted_zone_id
        event["dns_name"]=dns_name
        return event
    except Exception as e:
        print(e)
        
        '''No execption return for now, later need to add exception return with error as true and further workflow will go to final failed state.
        '''
        send_update(event["connection_id"], "An error occurred while creating ALB, deployment will stop!")
    
