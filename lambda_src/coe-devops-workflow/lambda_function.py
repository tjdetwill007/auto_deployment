import boto3
import urllib.parse
import zipfile
import os
import base64
import git
from git import RemoteProgress
from buildspec_maker import create_buildspec
from codebuild_exec import execute_codebuild
from language_config import create_deployment_config


s3 = boto3.client('s3')

#Pre-configured S3 Constants.
BUCKET_NAME=os.environ.get("SRC_BUCKET")
DOCKERFILE_BUCKET=os.environ.get("DOCKER_BUCKET")
BUILDER_BUCKET= os.environ.get("BUILD_BUCKET")
WEBSOCKET_URL=os.environ.get("WEBSOCKET_URL")

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
    
def clone_repository(github_configs, project_name, project_type, connection_id):

    repo_url=github_configs["Frontend_Url"] if project_type=="frontend" else github_configs["Backend_Url"]
    destination=f"/tmp/{project_name}"+project_type
    try:
        git.Repo.clone_from(repo_url, destination,progress=ProgressPrinter(connection_id,project_type))
        print("Repository cloned successfully")
        send_update(connection_id, f"{project_type} repository cloned successfully")
        return destination
    except Exception as e:
        print(f"Error cloning repository: {e}")
        send_update(connection_id, f"Error while cloning {project_type} repository")
        return False
        
class ProgressPrinter(RemoteProgress):
    """
    Progress printer class for Git clone progress.
    """
    
    def __init__(self, connection_id, project_type):
        super().__init__()
        self.connection_id = connection_id
        self.project_type = project_type

    def update(self, op_code, cur_count, max_count=None, message=''):
        
        if op_code == git.remote.RemoteProgress.RECEIVING:
            percentage = cur_count / (max_count or 100.0) * 100
            update_message=f"{self.project_type} code downloaded {int(percentage)}% {message}"
            send_update(self.connection_id,update_message)

def download_src_file(file_name):
    """
    Downloads the source code from language-source-code S3 bucket. Experimental for now and
    will be changed after adding source code download from Github Repository

    """
    
    try:
    #Download file from S3 language-source-code
        download_path = f'/tmp/{file_name}'
        s3.download_file(BUCKET_NAME, file_name, download_path)
        return download_path
    except Exception as e:
        print("An error occurred while downloading file from s3")
        raise Exception("An error occurred while downloading file from s3")
        
def extract_file(downloaded_file):
    """
    Downloaded source code from S3 bucket will be extracted. Experimental for now and 
    will be changed after adding source code download from Github Repository

    """
    
    extract_to=os.path.splitext(downloaded_file)[0]
    try:
        with zipfile.ZipFile(downloaded_file, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print("File successfully extracted.")
        return extract_to
    except Exception as e:
        print("Error occurred while extracting the file:", e)
        raise Exception("Error occurred while extracting the file")
def add_dockerfile(extracted_path,language_type):
    """
    Adding Dockerfile as per language type to the source code

    """
    
    DOCKERFILE_FILE=f'{language_type}-dockerfile/dockerfile'
    
    download_path=extracted_path+'/'+"Dockerfile"
    #download the dockerfile to the extracted_path
    try:
        s3.download_file(DOCKERFILE_BUCKET, DOCKERFILE_FILE, download_path)
        return True
    except Exception as e:
        print("An error occurred while downloading Dockerfile")
        return False
        
def zip_folder(folder_path):
    """
    Source code zipped after bundling with required Dockerfile and Buildspec file

    """
    
    zip_file_path=folder_path+".zip"
    try:
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zip_ref.write(file_path, os.path.relpath(file_path, folder_path))
        print("Folder successfully zipped.")
        return zip_file_path
    except Exception as e:
        print("Error occurred while zipping the folder:", e)
        raise Exception("Error occurred while zipping the folder")
        
def upload_to_builder(zip_file_path, file_name):
    """
    Zipped Source code will be uploaded back to proceedtobuildapp S3 bucket

    """
    
    try:
        s3.upload_file(zip_file_path, BUILDER_BUCKET, file_name)
        print("Uploaded to builder Bucket")
    except Exception as e:
        print("An error occurred while uploading file to Builder Bucket")
        raise Exception("An error occurred while uploading file to Builder Bucket")
def get_env_variables(lang_config):
    """
    Returns the environment_variables for CodeBuild.

    """
    try:
        environment_variables=[]
        for key, value in lang_config.items():
            
            if value is not None:
                environment_variables.append({
                        'name': key,
                        'value': str(value),
                        'type': 'PLAINTEXT'})
        
        return environment_variables
    except Exception as e:
        raise Exception("Error occurred while getting environment variables for building")
    
def create_ecr(user_id, project_name, project_type):
    client = boto3.client('ecr')
    try:
        response = client.create_repository(
            repositoryName=f'{user_id}/{project_name}/{project_type}')
        version_tag=1
        return version_tag
    
    except client.exceptions.RepositoryAlreadyExistsException:

        print("Repository already exists")
        response = client.describe_images(
        repositoryName=f'{user_id}/{project_name}/{project_type}')
        sorted_images = sorted(response['imageDetails'], key=lambda x: x['imagePushedAt'], reverse=True)
        if sorted_images:
            tag = sorted_images[0]['imageTags'][0] if 'imageTags' in sorted_images[0] else None
            version_tag=int(tag[1:])
            return (version_tag+1)
        else:
            return None
    except Exception as e:
        print("An error occurred while creating ECR repository")
        return None
    
def execute_build(lang_config, user_id, project_name, source_type, connection_id, nginx_conf=None,github_configs=None):
    """
    Executes the build for the given language configuration.

    """
    
    project_type=lang_config["type"]
    file_name = lang_config["File_Name"] if source_type=="S3" else f"{project_name}-{project_type}.zip"
    # Download the s3 file and get the downloaded path
    if source_type=="S3":
        send_update(connection_id, f"Started downloading {project_type} files from S3")
        downloaded_file = download_src_file(file_name)
    # Download the github repository and get the downloaded path
    elif source_type=="GITHUB":
        send_update(connection_id, f"Started cloning {project_type} repository")
        downloaded_file=clone_repository(github_configs, project_name, project_type, connection_id)
    else:
        raise Exception("Invalid source type")
    if downloaded_file:
        send_update(connection_id, f"{project_type} source code downloaded")
            
        # Extract the Downloaded src code and get the extracted path
        if source_type=="GITHUB":
            extracted_path=downloaded_file
        else:
            extracted_path=extract_file(downloaded_file)
            send_update(connection_id, f"{project_type} source code extracted")
            
        language_type=lang_config["LANGUAGE_TYPE"]

        # Adding nginx conf file for language type react only
        if nginx_conf:
            with open(extracted_path+"/default.conf", "w") as file:
                file.write(nginx_conf)
                print("Nginx conf file created")

        # Adding Dockerfile to the code
        add_docker=add_dockerfile(extracted_path,language_type)

        if add_docker:

            # create ECR
            version_tag = create_ecr(user_id, project_name, project_type)

            if version_tag:
                # Create and add buildspec file
                repo_name = f"{user_id}/{project_name}/{project_type}"
                repo_uri = create_buildspec(extracted_path,repo_name, version_tag)
                
                # Zip the folder again
                zip_file_path=zip_folder(extracted_path)
                print("Zip file path is", zip_file_path)
                
                if zip_file_path:
                    
                    #upload back to builderBucket
                    upload_to_builder(zip_file_path,file_name)
                    
                    #Start the codebuild project and gets the build ID
                    src_code_location=f"{BUILDER_BUCKET}/{file_name}"
                    print(src_code_location)
                    
                    environment_variables=get_env_variables(lang_config)
                    
                    build_id= execute_codebuild(src_code_location, environment_variables)

                    if build_id:
                        message=f"{project_type} Build started with the Build ID - {build_id}"
                        send_update(connection_id, message)
                    else:
                        message=f"{project_type} Build failed"
                        send_update(connection_id, message)
                        raise Exception(f"{project_type} Build failed")
                    
                    return {"build_id":build_id,"repo_uri":repo_uri}
                
                else:
                    send_update(connection_id, f"Failed to zip the folder")
                    raise Exception("Failed to zip the folder")
            else:
                send_update(connection_id, f"Failed to create ECR repository for {project_type}")
                raise Exception("Failed to create ECR repository")
    else:
        send_update(connection_id, f"{project_type} source code download failed")
        raise Exception("Failed to download the file")
           
            
def lambda_handler(event, context):
    """Handler function Bundles the package and proceeds the building
    
    Keyword arguments:
    argument -- event -- event object from the SQS poller lambda i.e (start_execution).
    Return: returns the build ID, Repo_uri and language config for check build lambda
    Exception: Prints the error
    
    Note: In future language source code bucket key will depend on UserID which is yet to be implemented. 
    Author: Teqfocus
    """
    # Extending fullstack feature
    user_id = urllib.parse.unquote_plus(event["User_Id"])
    project_name = urllib.parse.unquote_plus(event["Project_Name"])
    deployment_type = event["Deployment_Type"]
    langauge_configs = event["Language_Configs"]
    connection_id=event["connectionId"]
    source_type=event["Source_Type"]
    github_configs=event.get("Github_Configs", None)
    build_ids={}
    repo_uris={}
    nginx_config=None
    frontend_config=None
    backend_config=None
    deployment_mode=event["Deployment_Mode"]
    # creating deployment_config
    try:
                
        if deployment_mode not in ["dev","prod"]:
            raise Exception("Invalid deployment mode")
        if deployment_mode=="dev":
            send_update(connection_id, """Starting deployment in DEV mode, Application will run in minimal capacity""")
        else:
            send_update(connection_id, """Starting deployment in PROD mode, Application will run in maximum capacity, with One ALB and 3 minimum tasks.""")
                
        deployment_config = create_deployment_config(deployment_type, langauge_configs)
        print("Deployment Config created:", deployment_config)
        if hasattr(deployment_config, "frontend_config"):
            frontend_config = vars(deployment_config.frontend_config)
            nginx_config = deployment_config.nginx_configuration
            response = execute_build(frontend_config, user_id, project_name, source_type,connection_id,nginx_config,github_configs)
            nginx_config= base64.b64encode(nginx_config.encode("utf-8"))
            build_ids["frontend"] = response["build_id"]
            repo_uris["frontend"] = response["repo_uri"]
        if hasattr(deployment_config, "backend_config"):
            backend_config = vars(deployment_config.backend_config)
            print("github configs", github_configs)
            response = execute_build(backend_config, user_id, project_name,source_type,connection_id,github_configs=github_configs)
            build_ids["backend"] = response["build_id"]
            repo_uris["backend"] = response["repo_uri"]

        return {"build_ids":build_ids, 
                "repo_uris":repo_uris, 
                "deployment_type":deployment_type,
                "deployment_mode":deployment_mode, 
                "nginx_config":nginx_config,
                "frontend_config":frontend_config,
                "backend_config":backend_config, 
                "connection_id":connection_id,
                "user_id":user_id,
                "project_name":project_name}     
    except Exception as e:
        print("Error occurred",e)
        send_update(connection_id, "Error occurred while building the project")            
        return {"error":True,
                "repo_uris":repo_uris,
                "stage":"BUILD",
                "project_name":project_name,
                "user_id":user_id,
                "connection_id":connection_id,
                "deployment_type":deployment_type}