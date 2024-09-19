# Prerequisites
-   **Terraform**
-   **python**
-   **boto3**
-   **docker**

**Before running terraform apply make sure python is installed on the host machine with boto3 package installed, as these are required to run the module update lambda env vars module.**
```
python --version

pip install boto3
```
**Make sure aws profile variable is configured in root variables.tf with your current AWS cli profile.**
```
variable "aws_profile" {
  type = string
  default = "teqfocus"
}
```
## To add feature
This Project is using custom nginx image that are uploaded manually to ECR which is required to run react and nextjs application. 

Steps to add custom nginx.
-   Pull Docker image ``` docker pull tjdetwill007/nginx_custom ```
-   Tag Docker Image with your ECR and push the docker image.
-   Update the code in **lambda_src/Deploy_to_ecs/lambda_function.py** with your ECR repository
    ```
    repo_uris["nginx"]="<Account_ID>.dkr.ecr.<Region>.amazonaws.com/nginx_custom:latest"
    ```
# Deployment
```
terraform init
```
```
terraform validate
```
```
terraform apply --auto-approve
```
## Note
Additionally .tfvars can be used for deployment. Currently the project will use default values for all resources.
>Make sure S3 bucket names are globally unique else the deployment will fail with an error.