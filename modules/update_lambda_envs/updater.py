import boto3
import argparse
import os
import json

def update_function(function_name, env_vars, region, profile):
    session = boto3.Session(profile_name=profile, region_name=region)
    lambda_client = session.client('lambda')
    lambda_client.update_function_configuration(
        FunctionName=function_name,
        Environment={
            'Variables': env_vars
        }
    )

def json_type(json_string):
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        raise argparse.ArgumentTypeError(f"Invalid JSON: {e}")
try:
    parser = argparse.ArgumentParser()
    parser.add_argument('--env_vars', type=json_type, required=True)
    parser.add_argument('--region', type=str, required=True)
    parser.add_argument('--profile', type=str,default="default")
    parser.add_argument('--function_name', type=str,required=True)
    args = parser.parse_args()

    env_vars = args.env_vars
    print("ENV vars:",env_vars)
    region = args.region
    profile = args.profile
    function_name=args.function_name
    update_function(function_name, env_vars, region, profile)
except:
    print("Error: Unable to connect to AWS")