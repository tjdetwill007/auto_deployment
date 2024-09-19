import boto3
from botocore.exceptions import ClientError
import json
import urllib.parse

def lambda_handler(event, context):
    """Generates the presigned URL to allow users to upload their source code directly into the bucket"""
    print(json.dumps(event))
    encoded_filename=event["queryStringParameters"]["filename"]
    filename = urllib.parse.unquote(encoded_filename)

    print(filename)
    try:
        client = boto3.client('s3')
        response = client.generate_presigned_url(ClientMethod='put_object', Params={'Bucket': 'teqfocuslanguagesrc', 'Key': filename, 'ContentType':"application/x-zip-compressed"}, ExpiresIn=3600)
        print(response)
        return {"statusCode":200,"body":response}
    except ClientError as e:
        print(e)
        return {"statusCode":500,"body":"Error generating presigned url"}