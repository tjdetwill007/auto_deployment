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
    
    apigateway_management_api = boto3.client('apigatewaymanagementapi', endpoint_url=WEBSOCKET_URL)
    apigateway_management_api.post_to_connection(ConnectionId=connectionId,Data=message)

def lambda_handler(event, context):
    
    """Checks the build status
    
    Keyword arguments:
    argument -- event -- event object from the coe-devops-workflow
    Return: -- status of the build
            -- build id of the execution
            -- repo uri of the build
            -- Language config is passed to the next funtion.
    Author: Teqfocus
    """
    

    codebuild=boto3.client("codebuild")
    build_ids=event["build_ids"]
    repo_uris=event["repo_uris"]
    connection_id=event["connection_id"]
    listener_arn=event.get("listener_arn", None)
    target_group_arn=event.get("target_group_arn", None)
    alb_hosted_zone_id=event.get("alb_hosted_zone_id", None)
    dns_name=event.get("dns_name", None)
    final_status=[]
    try:
        for type, build_id in build_ids.items():
            response = codebuild.batch_get_builds(ids=[build_id])
            status=response["builds"][0]["buildStatus"]
            message=f"Build status of {type} is {status}"
            final_status.append(status)
            send_update(connection_id, message)
            print("The status is :", status)
        if any(status_word in final_status for status_word in ["FAILED", "STOPPED", "FAULT", "TIMED_OUT"]):
            status="FAILED"
            raise Exception("Build Failed due to final status as FAILED")           
        elif "IN_PROGRESS" in final_status:
            status="IN_PROGRESS"
        elif all(status_word == "SUCCEEDED" for status_word in final_status):
            status="SUCCEEDED"
        else:
            send_update(connection_id, "An Unexpected error occured. Couldn't identitfy the Status")
            raise Exception("An Unexpected error occured. Couldn't identitfy the Status")
        
        return {"Status":status, 
            "build_ids":build_ids,
            "repo_uris":repo_uris, 
            "deployment_type":event["deployment_type"],
            "deployment_mode":event["deployment_mode"], 
            "nginx_config":event["nginx_config"],
            "frontend_config":event["frontend_config"],
            "backend_config":event["backend_config"],
            "user_id":event["user_id"],
            "project_name":event["project_name"],
            "listener_arn":listener_arn,
            "target_group_arn":target_group_arn,
            "connection_id":connection_id,
            "alb_hosted_zone_id":alb_hosted_zone_id,
            "dns_name":dns_name}
            
    except Exception as e:
        print("Error while geting build status:",e)

        return {"Status":"FAILED",
                "repo_uris":repo_uris,
                "stage":"BUILD",
                "project_name":event["project_name"],
                "user_id":event["user_id"],
                "connection_id":connection_id,
                "deployment_type":event["deployment_type"],
                "deployment_mode":event["deployment_mode"]}
    
