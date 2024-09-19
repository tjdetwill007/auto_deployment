import boto3
import json

def lambda_handler(event,context):
        """Authenticates the Websocket Connection.
        
        Keyword arguments:
        argument -- event -- the event object
        Return: Returns the status code 200.
        
        Note: In the future JWT authentication will be implemented. Currently it allows all user.
        Author: Teqfocus
        """
        
        print(json.dumps(event))
        return {"statusCode": 200}
        
