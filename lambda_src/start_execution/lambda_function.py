import boto3
import json
import os

WEBSOCKET_URL=os.environ['WEBSOCKET_URL']
STATEMACHINE_ARN=os.environ['STATEMACHINE_ARN']

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

    """SQS Poller Lambda polls the message from SQS and starts the execution of stateMachine.
    
    Keyword arguments:
    argument -- event -- event object from SQS
    Return: None
    Exception: Returns status code 500 with error message.
    Author: Teqfocus
    """
    
    body=event["Records"][0]["body"]
    body=json.loads(body)
    connection_Id=body["connectionId"]

    try:
        stepfunctions_client = boto3.client('stepfunctions')
        state_machine_arn=STATEMACHINE_ARN
        response = stepfunctions_client.start_execution(
        stateMachineArn=state_machine_arn,
        input=json.dumps(body)
    )
        execution_arn=response["executionArn"]
        send_update(connection_Id,message=f"Started the execution with exection ARN {execution_arn}")
    except Exception as e:
        print(e)
        return {"statusCode": 500, "body": "Error creating stepfunctions client"}
    

    