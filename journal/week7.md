# Week 7 

## Solving CORS with a Load Balancer and Custom Domain

- [Custom Domain](#Custom-Domain)    
    
    &emsp;[1. Register New Domain](#1-Register-New-Domain)    
    &emsp;[2. Create Hosted Zone](#2-Create-Hosted-Zone)    
    &emsp;[3. Create Certificate](#3-Create-Certificate)    
    &emsp;[4. Update ALB](#4-Update-ALB)    
    &emsp;[5. Hosted Zone backend Record](#5-Hosted-Zone-backend-Record)    
    &emsp;[6. Hosted Zone frontend Record](#6-Hosted-Zone-frontend-Record)    
    &emsp;[7. Update Task Definitions](#7-Update-Task-Definitions)    
    &emsp;[8. Update frontend-react-js image](#8-Update-frontend-react-js-image)    
    &emsp;[9. Test Access](#9-Test-Access)    

- [Backend App: Production Image](#Backend-App-Production-Image)
  - [Create Dockerfile.prod](#Create-Dockerfileprod)
  - [Build Production Docker Image](#Build-Production-Docker-Image)
  - [Run Production Docker Container](#Run-Production-Docker-Container)
- [Utility Scripts](#Utility-Scripts)
  - [Frontend Scripts](#Frontend-Scripts)
    - [Build Frontend Image](#Build-Frontend-Image)
    - [Push Frontend Image](#Push-Frontend-Image)
    - [Deploy Frontend Service](#Deploy-Frontend-Service)
    - [Connect Frontend Service](#Connect-Frontend-Service)
    - [Register Frontend Task Definition](#Register-Frontend-Task-Definition)
  - [Backend Scripts](#Backend-Scripts)
    - [Build Backend Image](#Build-Backend-Image)
    - [Push Backend Image](#Push-Backend-Image)
    - [Deploy Backend Service](#Deploy-Backend-Service)
    - [Connect Backend Service](#Connect-Backend-Service)
    - [Register Backend Task Definition](#Register-Backend-Task-Definition)
  - [AWS Scripts](#AWS-Scripts)
  
## Custom Domain
[Back to top](#week-7)

### 1. Register New Domain

We will register a new domain by following the steps in this document https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/domain-register.html.
Once the domain is registered them we will create hosted zone .

>> NOTE: If you create records in a hosted zone other than the one that Route 53 creates automatically, you must update the name servers for the domain to use the name servers for the new hosted zone.

### 2. Create Hosted Zone
[Back to top](#week-7)

- Go to AWS Route53 console
- Click on create **Create hosted zone**
- Enter your **Domain name** & Description
- Select **Public hosted zone** 
- Click on **Create Hosted zone**


### 3. Create Certificate 
[Back to top](#week-7)

- Go To AWS Certificate Manager (ACM) console 
- Click on **request**
- Select **Request a public certificate** then **Next**
- Enter the **Domain name FQDN **
- Choose how you want to validate from **Validation method**
- Select the **Key algorithm** then click on **Request**


### 4. Update ALB
[Back to top](#week-7)

We will add new listeners to the ALB, one to redirect HTTP rquests from port 80 to 443 "HTTPS"


- Go TO AWS EC2 console
- Select **Load Balancer** from the left-side menu
- Click on the ALB "**cruddur-alb**"
- Under **Listener** tab click on **Add listener**
- **Listener HTTP > HTTPS**
  - Select Protocol: HTTP - Port: 80
  - Select **Default actions** as "Redirect"
  - Choose Protocol: HTTP - Port: 3000
  - Choose **Status code** as "Found"
- **Listener HTTPS >> Frontend TG**
  - Select Protocol: HTTPS - Port: 443
  - Select **Default actions** as "Forward"
  - Select **Target Group**: cruddur-frontend-react-js
  - Under **Secure listener settings** select "From ACM" the ACM certificated created previously 
- Once HTTPS:443 listener is created, select it then click on **Actions**
- Select **Manage Rules**
- Click on the **+** sign then **insert rule**
- under **IF (match all)** select **Add condition** as **Host header:** api.YourDomainName.come
- Under **THEN** select **Add action** as **Forward to:** then select the _target group_ "cruddur-backend-flask-tg"


### 5. Hosted Zone backend Record
[Back to top](#week-7)

- Go to AWS Route53 console
- Click on the hosted zone then select the domain name
- Click on **Create record**
- **Record name:** api
- **Record type:** A record
- enable **Alias**
- Select **Route traffic to** as "Alias to Application and Classic Load Balancer"
- Click on **Create record**
- Test access to the subdomain using dig or nslookup `dig api.YourDomainName.com`   
- Test access to the backend app using curl    
`curl https://api.YourDomainName.com/api/health-check`

### 6. Hosted Zone frontend Record
[Back to top](#week-7)

- Go to AWS Route53 console
- Click on the hosted zone then select the domain name
- Click on **Create record**
- **Record name:** 
- **Record type:** A record
- enable **Alias**
- Select **Route traffic to** as "Alias to Application and Classic Load Balancer"
- Click on **Create record**
- Test access to the subdomain using dig or nslookup `dig YourDomainName.com`   
- Test access to the backend app using curl    
`curl https://YourDomainName.com/`


### 7. Update Task Definitions
[Back to top](#week-7)

- Update backend-flask.json with the following
```json
 {"name": "FRONTEND_URL", "value": "https://YourDomainName.com"},
 {"name": "BACKEND_URL", "value": "https://api.YourDomainName.com"},
```
- Register the task definition again   
`aws ecs register-task-definition --cli-input-json file://aws/task-definitions/backend-flask.json`


### 8. Update frontend-react-js image
[Back to top](#week-7)

- Login to ECR   
`aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com"`

- Re-build the frontend-react-js image using the domain name URL
- Go to dir: frontend-react-js then run the following
```bash
docker build \
--build-arg REACT_APP_BACKEND_URL="https://api.YourDomainName.com" \
--build-arg REACT_APP_AWS_PROJECT_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_COGNITO_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_USER_POOLS_ID="YourUserPoolId" \
--build-arg REACT_APP_CLIENT_ID="YourUserPoolClient" \
-t frontend-react-js \
-f Dockerfile.prod \
.
```

- Tag the image `docker tag frontend-react-js:latest $ECR_FRONTEND_REACT_URL:latest`
- Push the image `docker push $ECR_FRONTEND_REACT_URL:latest`
- Start the ECS services (backend & frontend)

### 9. Test Access 
[Back to top](#week-7)

- Test access to the backend app using the health check endpoint
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023/aws (main) $ curl https://api.awsbc.flyingresnova.com/api/health-check
{
  "success": true
}
```
- Test access to the frontend app using the domain name URL

---
---  

## Backend App: Production Image

We will build new backend-flask docker image for production using Dockerfile.prod that has no-debug enabled for security reasons.

### Create Dockerfile.prod
[Back to top](#week-7)

- Go to dir: backend-flask
- Login to AWS ECR by running the following command  
`aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com"`
- Create file Dockerfile.prod and add the following:
```yml
FROM YourAwsAccountId.dkr.ecr.us-east-1.amazonaws.com/cruddur-python:3.10-slim-buster


# [TODO] For debugging, don't leave these in
#RUN apt-get update -y
#RUN apt-get install iputils-ping -y
# -----

# Inside Container
# make a new folder inside container
WORKDIR /backend-flask

# Outside Container -> Inside Container
# this contains the libraries want to install to run the app
COPY requirements.txt requirements.txt

# Inside Container
# Install the python libraries used for the app
RUN pip3 install -r requirements.txt

# Outside Container -> Inside Container
# . means everything in the current directory
# first period . - /backend-flask (outside container)
# second period . /backend-flask (inside container)
COPY . .

EXPOSE ${PORT}

# CMD (Command)
# python3 -m flask run --host=0.0.0.0 --port=4567
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567", "--no-debug","--no-debugger","--no-reload"]
```

### Build Production Docker Image
[Back to top](#week-7)

- Run the following command to build the new docker image    
`docker build -f Dockerfile.prod -t backend-flask-prod .`

### Run Production Docker Container
[Back to top](#week-7)

- Create docker script **run-backend-flask-prod** under dir: bin/docker
- Add the following to the script to run the backend production container
```bash
#! /usr/bin/bash

docker run --rm \
-p 4567:4567 -d \
--env AWS_ENDPOINT_URL="http://localhost:8000" \
--env CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur" \
--env FRONTEND_URL="https://3000-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}" \
--env BACKEND_URL="https://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}" \
--env OTEL_SERVICE_NAME='backend-flask' \
--env OTEL_EXPORTER_OTLP_ENDPOINT="https://api.honeycomb.io" \
--env OTEL_EXPORTER_OTLP_HEADERS="x-honeycomb-team=${HONEYCOMB_API_KEY}" \
--env AWS_XRAY_URL="*4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}*" \
--env AWS_XRAY_DAEMON_ADDRESS="xray-daemon:2000" \
--env AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION}" \
--env AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
--env AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
--env ROLLBAR_ACCESS_TOKEN="${ROLLBAR_ACCESS_TOKEN}" \
--env AWS_COGNITO_USER_POOL_ID="${AWS_COGNITO_USER_POOL_ID}" \
--env AWS_COGNITO_USER_POOL_CLIENT_ID="YourUserPoolClientId" \
-it backend-flask-prod 
```
---
---  

## Utility Scripts

We will create new utility scripts, update exiting ones and place them insdie dir: bin at the root dir

- Go to dir: bin then creat these dir: frontend; backend; and aws

### Frontend Scripts 

#### Build Frontend Image
[Back to top](#week-7)

- This script will build a frontend docker image 
- Create file **build** inside bin/frontend then add the following script
```bash
#! /usr/bin/bash

ABS_PATH=$(readlink -f "$0")
BIN_PATH=$(dirname $ABS_PATH)
PROJECT_PATH=$(dirname $BIN_PATH)
FRONTEND_REACT_JS_PATH="$PROJECT_PATH/frontend-react-js"

docker build \
--build-arg REACT_APP_BACKEND_URL="https://api.YourDomainName.com" \
--build-arg REACT_APP_AWS_PROJECT_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_COGNITO_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_USER_POOLS_ID="$AWS_COGNITO_USER_POOL_ID" \
--build-arg REACT_APP_CLIENT_ID="YourUserPoolClientId" \
-t frontend-react-js \
-f "$FRONTEND_REACT_JS_PATH/Dockerfile.prod" \
"$FRONTEND_REACT_JS_PATH/."
```

#### Push Frontend Image
[Back to top](#week-7)

- This script will tag then push the frontend image to ECR
- Create file **push** inside /bin/frontend then add the following script
```bash
#! /usr/bin/bash


ECR_FRONTEND_REACT_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/frontend-react-js"
echo $ECR_FRONTEND_REACT_URL

docker tag frontend-react-js:latest $ECR_FRONTEND_REACT_URL:latest
docker push $ECR_FRONTEND_REACT_URL:latest
```

#### Deploy Frontend Service
[Back to top](#week-7)

- This script will force deploy new frontend service 
- Create file **deploy** inside /bin/frontend then add the following script
```bash
#! /usr/bin/bash

CLUSTER_NAME="cruddur"
SERVICE_NAME="frontend-react-js"
TASK_DEFINTION_FAMILY="frontend-react-js"

LATEST_TASK_DEFINITION_ARN=$(aws ecs describe-task-definition \
--task-definition $TASK_DEFINTION_FAMILY \
--query 'taskDefinition.taskDefinitionArn' \
--output text)

echo "TASK DEF ARN:"
echo $LATEST_TASK_DEFINITION_ARN

aws ecs update-service \
--cluster $CLUSTER_NAME \
--service $SERVICE_NAME \
--task-definition $LATEST_TASK_DEFINITION_ARN \
--force-new-deployment
```

#### Connect Frontend Service
[Back to top](#week-7)

- This script will connect to the frontend service using the task number
- Create file **connect** inside /bin/frontend then add the following script
```bash
#! /usr/bin/bash
if [ -z "$1" ]; then
  echo "No TASK_ID argument supplied eg ./bin/ecs/connect-to-frontend-react-js 99b2f8953616495e99545e5a6066fbb5d"
  exit 1
fi
TASK_ID=$1

CONTAINER_NAME=frontend-react-js

echo "TASK ID : $TASK_ID"
echo "Container Name: $CONTAINER_NAME"

aws ecs execute-command  \
--region $AWS_DEFAULT_REGION \
--cluster cruddur \
--task $TASK_ID \
--container $CONTAINER_NAME \
--command "/bin/sh" \
--interactive
```

#### Register Frontend Task Definition 
[Back to top](#week-7)

- This script will register the frontend task definition 
- Create file **register** inside /bin/frontend then add the following script
```bash
#! /usr/bin/bash

ABS_PATH=$(readlink -f "$0")
FRONTEND_PATH=$(dirname $ABS_PATH)
BIN_PATH=$(dirname $FRONTEND_PATH)
PROJECT_PATH=$(dirname $BIN_PATH)
TASK_DEF_PATH="$PROJECT_PATH/aws/task-definitions/backend-flask.json"

echo $TASK_DEF_PATH

aws ecs register-task-definition \
--cli-input-json "file://$TASK_DEF_PATH"
```

---

### Backend Scripts

#### Build Backend Image
[Back to top](#week-7)

- This script will build backend docker image
- Create file **build** inside /bin/backend then add the following script
```bash
#! /usr/bin/bash

ABS_PATH=$(readlink -f "$0")
BIN_PATH=$(dirname $ABS_PATH)
PROJECT_PATH=$(dirname $BIN_PATH)
BACKEND_FLASK_PATH="$PROJECT_PATH/backend-flask"

docker build \
-f "$BACKEND_FLASK_PATH/Dockerfile.prod" \
-t backend-flask-prod \
"$BACKEND_FLASK_PATH/."
```

#### Push Backend Image
[Back to top](#week-7)

- This script will tag then push the backend image to ECR
- Create file **push** inside /bin/backend then add the following script
```bash
#! /usr/bin/bash

ECR_BACKEND_FLASK_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/backend-flask"
echo $ECR_BACKEND_FLASK_URL

docker tag backend-flask-prod:latest $ECR_BACKEND_FLASK_URL:latest
docker push $ECR_BACKEND_FLASK_URL:latest
```
#### Deploy Backend Service
[Back to top](#week-7)

- This script will force deploy new backend service 
- Create file **deploy** inside /bin/frontend then add the following script
```bash
#! /usr/bin/bash

CLUSTER_NAME="cruddur"
SERVICE_NAME="backend-flask"
TASK_DEFINTION_FAMILY="backend-flask"


LATEST_TASK_DEFINITION_ARN=$(aws ecs describe-task-definition \
--task-definition $TASK_DEFINTION_FAMILY \
--query 'taskDefinition.taskDefinitionArn' \
--output text)

echo "TASK DEF ARN:"
echo $LATEST_TASK_DEFINITION_ARN

aws ecs update-service \
--cluster $CLUSTER_NAME \
--service $SERVICE_NAME \
--task-definition $LATEST_TASK_DEFINITION_ARN \
--force-new-deployment
```

#### Connect Backend Service
[Back to top](#week-7)

- This script will connect to the backend service using the task number
- Create file **connect** inside /bin/frontend then add the following script
```bash
#! /usr/bin/bash
if [ -z "$1" ]; then
  echo "No TASK_ID argument supplied eg ./bin/ecs/connect-to-backend-flask 99b2f8953616495e99545e5a6066fbb5d"
  exit 1
fi
TASK_ID=$1

CONTAINER_NAME=backend-flask

echo "TASK ID : $TASK_ID"
echo "Container Name: $CONTAINER_NAME"

aws ecs execute-command  \
--region $AWS_DEFAULT_REGION \
--cluster cruddur \
--task $TASK_ID \
--container $CONTAINER_NAME \
--command "/bin/bash" \
--interactive
```

#### Register Backend Task Definition 
[Back to top](#week-7)

- This script will register the backend task definition 
- Create file **register** inside /bin/frontend then add the following script
```bash
#! /usr/bin/bash

ABS_PATH=$(readlink -f "$0")
BACKEND_PATH=$(dirname $ABS_PATH)
BIN_PATH=$(dirname $BACKEND_PATH)
PROJECT_PATH=$(dirname $BIN_PATH)
TASK_DEF_PATH="$PROJECT_PATH/aws/task-definitions/frontend-react-js.json"

echo $TASK_DEF_PATH

aws ecs register-task-definition \
--cli-input-json "file://$TASK_DEF_PATH"
```

---

### AWS Scripts

- Move the rds, ecs and ecr scripts to dir: bin/aws