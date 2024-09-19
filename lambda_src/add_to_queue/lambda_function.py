import boto3
import json
import os

SQS_URL= os.environ['SQS_URL']
def lambda_handler(event, context):
    
    """Adds the deployment request to the queue for processing. 
    
    Keyword arguments:
    argument -- Expects an event from Api Gateway
    Return: Returns the status code 200 and a message indicating that the request was added to the queue.
    Exception: Returns the status code 500 and a message indicating that an error occurred while adding the request to the queue.
    Author: Teqfocus
    
    """
    connection_id=event["requestContext"]["connectionId"]
    body=event["body"]
    body=json.loads(body)
    deploy_request=body["message"]
    deploy_request["connectionId"]=connection_id
    try:
        sqs = boto3.client('sqs')
        queue_url = SQS_URL
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(deploy_request)
        )
        return {"statusCode":200,"body":"Added to queue"}
    
    except Exception as e:
        print("An error occurred while adding to queue", e)
        return {"statusCode":500,"body":"Internal Server Error"}