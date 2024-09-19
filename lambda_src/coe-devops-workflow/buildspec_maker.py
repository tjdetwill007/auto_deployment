import yaml
import os

def create_buildspec(path_to_create,repo_name,version_tag):
    """Prepares the buildspec  file for CodeBuild and returns the Image"""
  
    REGION=os.environ.get("REGION")
    ECR_PREFIX=os.environ.get("ECR_PREFIX")
    ECR_REPO_NAME= repo_name
    content={
      "version": 0.2,
      "phases": {
        "build": {
          "commands": [
            f"REPOSITORY_URI={ECR_PREFIX}/{ECR_REPO_NAME}",
            "echo Build started on `date`",
            "echo Building the Docker image...",
            f"docker build --build-arg OUTPUT_DIR=\"$OUTPUT_DIR\" --build-arg PORT=\"$PORT\" --build-arg INSTALL_COMMAND=\"$INSTALL_COMMAND\" --build-arg BUILD_COMMAND=\"$BUILD_COMMAND\" --build-arg VERSION=\"$VERSION\" -t $REPOSITORY_URI:v{version_tag} .",
            f"aws ecr get-login-password --region {REGION} | docker login --username AWS --password-stdin {ECR_PREFIX}"
            
          ]
        },
        "post_build": {
          "commands": [
            "echo Build completed on `date`",
            "echo Pushing the Docker images...",
            f"docker push $REPOSITORY_URI:v{version_tag}",
            "echo Build Completed"
          ]
        }
      }
    }
    try:
        
        data=yaml.dump(content,default_flow_style=False)
        with open(f"{path_to_create}/buildspec.yml",'w') as file:
            file.write(data)
            print("Created the buildspec.yml")
            return (f"{ECR_PREFIX}/{ECR_REPO_NAME}:v{version_tag}")
    except Exception as e:
        print("An error occurred while creating the buildspec file")