import boto3
from botocore.exceptions import ClientError

def delete_ecr_repo(client,repo_name):
    try:
        response = client.delete_repository(
        repositoryName=repo_name,
        force=True)
        return True
    except Exception as e:
        raise Exception("An error occured while deleting the repository")
    
def delete_image_from_ecr(client, repo_name, image_tag):
    try:
        response = client.batch_delete_image(
    repositoryName = repo_name,
    imageIds=[  {            
            'imageTag': image_tag
        },
    ])
        return True
    except Exception as e:
        raise Exception("An error occured while deleting the image")
    
def check_repository_exists(client, repo_name):
    try:
        response = client.describe_repositories(
        repositoryNames=[
            repo_name,
        ],
    )
        return True
    except ClientError as e:
        # If the repository doesn't exist, catching the exception
        if e.response['Error']['Code'] == 'RepositoryNotFoundException':
            return False
        else:
            raise Exception("An error occured while checking do repository exists")

def check_empty_repository(client, repo_name):
    try:
        response = client.describe_images(
        repositoryName=repo_name,
    )
        if len(response["imageDetails"]) == 0:
            return True
        else:
            return False
    except Exception as e:
        raise Exception("An error occured while checking the repository status as empty or not")
    
def lambda_handler(event, context):

    try:
        if event["error"] is True:

            repo_uris=event["repo_uris"]
            project_name=event["project_name"]
            user_id=event["user_id"]
            deployment_type=event["deployment_type"]
            stage=event["stage"]
            client = boto3.client('ecr')
            

            # assuming deployment failed after build
            try:
                if len(repo_uris) > 0:
                    for key in repo_uris:
                        repo_name=f"{user_id}/{project_name}/{key}"
                        image_uri = repo_uris[key]
                        image_tag = image_uri.split(":")[-1]
                        if image_tag == "v1":
                            is_deleted = delete_ecr_repo(client, repo_name)
                            if is_deleted:
                                print("Deleted the repository")
                        else:
                            is_image_deleted = delete_image_from_ecr(client, repo_name, image_tag)
                            if is_image_deleted:
                                print("Deleted the image")
                else:
                # assuming deployment failed before build but created a blank repository || Deployment failed even before repository creation
                    
                    if deployment_type == "frontend":
                        repo_name=f"{user_id}/{project_name}/frontend"
                        check_repo = check_repository_exists(client, repo_name)
                        if check_repo:
                            is_repo_empty = check_empty_repository(client, repo_name)
                            if is_repo_empty:
                                delete_ecr_repo(client, repo_name)
                            else:
                                print("Repository is not empty, build failed before image creation")
                        else:
                            print("Repository doesn't exist, build failed before repo creation")
                    elif deployment_type == "backend":
                        repo_name=f"{user_id}/{project_name}/backend"
                        check_repo = check_repository_exists(client, repo_name)
                        if check_repo:
                            is_repo_empty = check_empty_repository(client, repo_name)
                            if is_repo_empty:
                                delete_ecr_repo(client, repo_name)
                            else:
                                print("Repository is not empty, build failed before image creation")
                        else:
                            print("Repository doesn't exist, build failed before repo creation")

                    elif deployment_type == "fullstack":

                        supported_types=["frontend", "backend"]
                        for types in supported_types:
                            repo_name=f"{user_id}/{project_name}/{types}"
                            check_repo = check_repository_exists(client, repo_name)
                            if check_repo:
                                is_repo_empty = check_empty_repository(client, repo_name)
                                if is_repo_empty:
                                    delete_ecr_repo(client, repo_name)
                                else:
                                    print("Repository is not empty, build failed before image creation")
                            else:
                                print("Repository doesn't exist, build failed before repo creation")
                    else:
                        raise Exception("Invalid deployment type, or some unexpected error occurred")
            except Exception as e:
                raise Exception("An unexpected error occured in cleanup process")
    except Exception as e:
        print("possible error could be, ",e)