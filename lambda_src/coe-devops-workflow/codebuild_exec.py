import boto3
import os

PROJECT_NAME=os.environ.get("CODE_BUILD_NAME")
codebuild=boto3.client('codebuild')

def execute_codebuild(src_location,env_variables):
    """
    Executes the build process
    
    """
    
    try:
        build = codebuild.start_build( projectName=PROJECT_NAME,sourceTypeOverride='S3', sourceLocationOverride=src_location, environmentVariablesOverride=env_variables)
        return (build["build"]["id"])
    except Exception as e:
        print("An error occurred while starting build",e)