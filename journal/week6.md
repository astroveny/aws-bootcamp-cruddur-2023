# Week 6 

## Deploying Containers

[1. Health Checks and Logs](#1-Health-Checks-and-Logs)
  - [Test RDS Connection](#Test-RDS-Connection)
  - [Flask App Health Check](#Flask-App-Health-Check)
  - [CloudWatch Log Group](#CloudWatch-Log-Group)

[2. ECS and ECR Setup](#2-ECS-and-ECR-Setup)
  - [ECS Cluster](#ECS-Cluster)
  - [ECR Repos](#ECR-Repos)
    - [Base-image python Repo](#Base-image-python-Repo) 
    - [Flask Repo](#Flask-Repo)
    - [Frontend React Repo](#Frontend-React-Repo)
  - [ECS Task Definition](#ECS-Task-Definition)
    - [Env variables](#Env-variables)
    - [Task and Execution Roles](#Task-and-Execution-Roles)
      - [Create Execution Role](#Create-Execution-Role)
      - [Create Task Role](#Create-Task-Role)
      - [Create Task Definition](#Create-Task-Definition)
      - [Register Task Defintion](#Register-Task-Defintion)
      - [Create Security Group](#Create-Security-Group)
   
[3. ECS Services](#3-ECS-Services)
  - [Connect to the Service](#Connect-tothe-Service)
  - [BASH scripts](#BASH-scripts)
    - [ECS Service Connect](#ECS-Service-Connect)
    - [ECS Task Public IP](#ECS-Task-Public-IP)
    - [ECS Task List](#ECS-Task-List)
    - [ECS Start Task](#ECS-Start-Task)
    - [ECS Stop Task](#ECS-Stop-Task)
  - [ECS Service Health Check](#ECS-Service-Health-Check)
  - [RDS Security Group Update](#RDS-Security-Group-Update)
    
[4. Load Balancer ALB](#4-Load-Balancer-ALB)  

  &emsp;[1. Create Security Group](#1-Create-Security-Group)  
  &emsp;[2. Create ALB](#2-Create-ALB)  
  &emsp;[3. Create Target Group](#3-Create-Target-Group)  
  &emsp;[4. Create Load Balancer Listener](#4-Create-Load-Balancer-Listener)  
  &emsp;[5. Add ALB to ECS service](#5-Add-ALB-to-ECS-service)  
  &emsp;[6. Create ECS service](#6-Create-ECS-service)  
  &emsp;[7. Test ALB URL Access](#7-Test-ALB-URL-Access)  
  &emsp;[8. Create ALB Logs S3 Bucket](#8-Create-ALB-Logs-S3-Bucket)  
  &emsp;[9. Enable ALB logs](#9-Enable-ALB-logs)

---
---  
## 1. Health Checks and Logs

### Test RDS Connection
[Back to Top](#Week-6)

- We will create a script to test RDS connection and verify the status 
- Go to backemd-flask/bin/db then create test file and add the following code
- make the test file executable `chmod +x test`
```python
#!/usr/bin/env python3

import psycopg
import os
import sys

connection_url = os.getenv("CONNECTION_URL")

conn = None
try:
  print('attempting connection')
  conn = psycopg.connect(connection_url)
  print("Connection successful!")
except psycopg.Error as e:
  print("Unable to connect to the database:", e)
finally:
  conn.close()
```
---
### Flask App Health Check
[Back to Top](#Week-6)

- We will create a new endpoint `/api/health-check` inside the app.py to verify health status
```python 
@app.route('/api/health-check')
def health_check():
  return {'success': True}, 200
```
- Then we will create a new python script `bin/flask/health-check` to test access to the health-check endpoint
```python
#!/usr/bin/env python3

import urllib.request

try:
  response = urllib.request.urlopen('http://localhost:4567/api/health-check')
  if response.getcode() == 200:
    print("[OK] Flask server is running")
    exit(0) # success
  else:
    print("[BAD] Flask server is not running")
    exit(1) # false
# This for some reason is not capturing the error....
#except ConnectionRefusedError as e:
# so we'll just catch on all even though this is a bad practice
except Exception as e:
  print(e)
  exit(1) # false
```
---
### CloudWatch Log Group
[Back to Top](#Week-6)

- We will create a CloudWatch log group 
```bash
aws logs create-log-group --log-group-name "cruddur"
aws logs put-retention-policy --log-group-name "cruddur" --retention-in-days 1
```
---
---

## 2. ECS and ECR Setup

### ECS Cluster
[Back to Top](#Week-6)

- Create ECS cluster using the following command
```bash
aws ecs create-cluster --cluster-name cruddur --service-connect-defaults namespace=cruddur
```
---
### ECR Repos
[Back to Top](#Week-6)

#### Base-image python Repo

First we will create ECR repo then use base-image from dockerhub "python:3.10-slim-buster",so we will pull the image, add tag to it then push it to ECR repo

- Create a repo and upload the image
```bash
aws ecr create-repository --repository-name cruddur-python --image-tag-mutability MUTABLE
```
- Set the Env variable for ECR URL
```bash
export AWS_ACCOUNT_ID=YourAWS-ID
export ECR_PYTHON_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/cruddur-python"
```
- Login to ECR  
```bash
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com"
```
- Pull the image
`docker pull python:3.10-slim-buster`
- Tag the image  
`docker tag python:3.10-slim-buster $ECR_PYTHON_URL:3.10-slim-buster`
- Push the image  
`docker push $ECR_PYTHON_URL:3.10-slim-buster`
- update backend Dockerfile with the new ECR repo image by changing `FROM python:3.10-slim-buster` to  
`FROM AWS-ACCPUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cruddur-python:3.10-slim-buster`
- run docker compose to start backend-flask and db, issue the command from the same shell you used to login to ECR  
`docker compose up backend-flask db -d`
- Access backend health check endpoint to check the status of the app


#### Flask Repo
[Back to Top](#Week-6)

- Create a repo for backend-flask
```bash
aws ecr create-repository --repository-name backend-flask --image-tag-mutability MUTABLE
```
- Set Env variable URL for backend-flask repo
```bash
export ECR_BACKEND_FLASK_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/backend-flask"
echo $ECR_BACKEND_FLASK_URL
```
- Build the backend-flask image
`docker build -t backend-flask .`
- Tag the image
`docker tag backend-flask:latest $ECR_BACKEND_FLASK_URL:latest`
- Push the image to ECR repo
`docker push $ECR_BACKEND_FLASK_URL:latest`

#### Frontend React Repo
[Back to Top](#Week-6)

- Create a repo for frontend-react  
`aws ecr create-repository  --repository-name frontend-react-js --image-tag-mutability MUTABLE`
- Set Env variable URL for frontend-react repo
```bash
export ECR_FRONTEND_REACT_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/frontend-react-js"
echo $ECR_FRONTEND_REACT_URL
```
- Create new Dockerfile for production `Dockerfile.prod`
```yml
# Base Image ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
FROM node:16.18 AS build

ARG REACT_APP_BACKEND_URL
ARG REACT_APP_AWS_PROJECT_REGION
ARG REACT_APP_AWS_COGNITO_REGION
ARG REACT_APP_AWS_USER_POOLS_ID
ARG REACT_APP_CLIENT_ID

ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL
ENV REACT_APP_AWS_PROJECT_REGION=$REACT_APP_AWS_PROJECT_REGION
ENV REACT_APP_AWS_COGNITO_REGION=$REACT_APP_AWS_COGNITO_REGION
ENV REACT_APP_AWS_USER_POOLS_ID=$REACT_APP_AWS_USER_POOLS_ID
ENV REACT_APP_CLIENT_ID=$REACT_APP_CLIENT_ID

COPY . ./frontend-react-js
WORKDIR /frontend-react-js
RUN npm install
RUN npm run build

# New Base Image ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
FROM nginx:1.23.3-alpine

# --from build is coming from the Base Image
COPY --from=build /frontend-react-js/build /usr/share/nginx/html
COPY --from=build /frontend-react-js/nginx.conf /etc/nginx/nginx.conf

EXPOSE 3000
```

- Create nginx.conf file under frontend-react then add the following config

```c
# Set the worker processes
worker_processes 1;

# Set the events module
events {
  worker_connections 1024;
}

# Set the http module
http {
  # Set the MIME types
  include /etc/nginx/mime.types;
  default_type application/octet-stream;

  # Set the log format
  log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

  # Set the access log
  access_log  /var/log/nginx/access.log main;

  # Set the error log
  error_log /var/log/nginx/error.log;

  # Set the server section
  server {
    # Set the listen port
    listen 3000;

    # Set the root directory for the app
    root /usr/share/nginx/html;

    # Set the default file to serve
    index index.html;

    location / {
        # First attempt to serve request as file, then
        # as directory, then fall back to redirecting to index.html
        try_files $uri $uri/ $uri.html /index.html;
    }

    # Set the error page
    error_page  404 /404.html;
    location = /404.html {
      internal;
    }

    # Set the error page for 500 errors
    error_page  500 502 503 504  /50x.html;
    location = /50x.html {
      internal;
    }
  }
}
```
- Add the following to **.gitignore** file
```
docker/**/*
frontend-react-js/build/*
*.env
``` 

- Run `npm run build`

- Build the frontend-react-js image
```bash
docker build \
--build-arg REACT_APP_BACKEND_URL="http://You-ALB-DNS-URL:4567" \
--build-arg REACT_APP_AWS_PROJECT_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_COGNITO_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_USER_POOLS_ID="YourUserPoolId" \
--build-arg REACT_APP_CLIENT_ID="YourUserPoolClient" \
-t frontend-react-js \
-f Dockerfile.prod \
.
```
- Tag the image 
`docker tag frontend-react-js:latest $ECR_FRONTEND_REACT_URL:latest`
- Push the image to ECR repo
`docker push $ECR_FRONTEND_REACT_URL:latest`
- Test the image
`docker run --rm -p 3000:3000 -it frontend-react-js `


---

### ECS Task Definition 

#### Env variables
[Back to Top](#Week-6)

- Add DEFAULT_VPC_ID Env variable
```bash
export DEFAULT_VPC_ID=$(aws ec2 describe-vpcs \
--filters "Name=isDefault, Values=true" \
--query "Vpcs[0].VpcId" \
--output text)
echo $DEFAULT_VPC_ID
```
- Add DEFAULT_SUBNET_IDS Env variable
```bash
export DEFAULT_SUBNET_IDS=$(aws ec2 describe-subnets  \
 --filters Name=vpc-id,Values=$DEFAULT_VPC_ID \
 --query 'Subnets[*].SubnetId' \
 --output json | jq -r 'join(",")')
echo $DEFAULT_SUBNET_IDS
```

#### Task and Execution Roles

Similar to docker compose file, we have to create a Task definition with all required attributes like Env variables, permissions, etc ..

#### Create Execution Role
[Back to Top](#Week-6)

- Start by creating new ENV var for **OTEL EXPORTER**
`export OTEL_EXPORTER_OTLP_HEADERS="x-honeycomb-team=${HONEYCOMB_API_KEY}"`
- Then create the following **AWS System Manager** parameters 
```bash
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/AWS_ACCESS_KEY_ID" --value $AWS_ACCESS_KEY_ID
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/AWS_SECRET_ACCESS_KEY" --value $AWS_SECRET_ACCESS_KEY
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/CONNECTION_URL" --value $PROD_CONNECTION_URL
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/ROLLBAR_ACCESS_TOKEN" --value $ROLLBAR_ACCESS_TOKEN
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/OTEL_EXPORTER_OTLP_HEADERS" --value "x-honeycomb-team=$HONEYCOMB_API_KEY"
```
- Create Trust policy file `service-assume-role-execution-policy.json` under aws/policies 
```json
{
  "Version":"2012-10-17",
  "Statement":[{
      "Action":["sts:AssumeRole"],
      "Effect":"Allow",
      "Principal":{
      "Service":["ecs-tasks.amazonaws.com"]
      }
  }]
}
```
- Create permissions policy file `service-execution-policy.json` under aws/policies 
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:BatchCheckLayerAvailability",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
                ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "ssm:GetParameters",
                "ssm:GetParameter"
            ],
            "Resource": [
                "arn:aws:ssm:us-east-1:235696014680:parameter/cruddur/backend-flask/*"
            ]
        }
    ]
}
```
- Run the following command to create the role **CruddurServiceExecutionRole** using service-assume-role-execution-policy.json policy 
```bash
aws iam create-role --role-name CruddurServiceExecutionRole  --assume-role-policy-document file://aws/policies/service-assume-role-execution-policy.json
```
- Run the following command to create and add the policy using service-execution-policy.json 
```bash
aws iam put-role-policy --policy-name CruddurServiceExecutionPolicy --role-name CruddurServiceExecutionRole \
  --policy-document file://aws/policies/service-execution-policy.json
```

#### Create Task Role
[Back to Top](#Week-6)

- Run the following command to create **CruddurTaskRole**
```bash
aws iam create-role \
    --role-name CruddurTaskRole \
    --assume-role-policy-document "{
  \"Version\":\"2012-10-17\",
  \"Statement\":[{
    \"Action\":[\"sts:AssumeRole\"],
    \"Effect\":\"Allow\",
    \"Principal\":{
      \"Service\":[\"ecs-tasks.amazonaws.com\"]
    }
  }]
}"
```
- Run the following command to create **SSMAccessPolicy** permissions policy
```bash
aws iam put-role-policy \
  --policy-name SSMAccessPolicy \
  --role-name CruddurTaskRole \
  --policy-document "{
  \"Version\":\"2012-10-17\",
  \"Statement\":[{
    \"Action\":[
      \"ssmmessages:CreateControlChannel\",
      \"ssmmessages:CreateDataChannel\",
      \"ssmmessages:OpenControlChannel\",
      \"ssmmessages:OpenDataChannel\"
    ],
    \"Effect\":\"Allow\",
    \"Resource\":\"*\"
  }]
}"
```
- Run the following to attach policy **CloudWatchFullAccess** to role **CruddurTaskRole**
```bash
aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess --role-name CruddurTaskRole
```
- Run the following to attach policy **AWSXRayDaemonWriteAccess** to role **CruddurTaskRole**
```bash
aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess --role-name CruddurTaskRole
```
---

#### Create Task Definition 
[Back to Top](#Week-6)

- Create new dir: `aws/task-definitions`
- Create **backend Task definition** json file `backend-flask.json` and add the following 
```json
{
    "family": "backend-flask",
    "executionRoleArn": "arn:aws:iam::235696014680:role/CruddurServiceExecutionRole",
    "taskRoleArn": "arn:aws:iam::235696014680:role/CruddurTaskRole",
    "networkMode": "awsvpc",
    "cpu": "256",
    "memory": "512",
    "requiresCompatibilities": [ 
      "FARGATE" 
    ],
    "containerDefinitions": [
      {
        "name": "backend-flask",
        "image": "235696014680.dkr.ecr.us-east-1.amazonaws.com/backend-flask",
        "essential": true,
        "healthCheck": {
          "command": [
            "CMD-SHELL",
            "python /backend-flask/bin/flask/health-check"
          ],
          "interval": 30,
          "timeout": 5,
          "retries": 3,
          "startPeriod": 60
        },
        "portMappings": [
          {
            "name": "backend-flask",
            "containerPort": 4567,
            "protocol": "tcp", 
            "appProtocol": "http"
          }
        ],
        "logConfiguration": {
          "logDriver": "awslogs",
          "options": {
              "awslogs-group": "cruddur",
              "awslogs-region": "us-east-1",
              "awslogs-stream-prefix": "backend-flask"
          }
        },
        "environment": [
          {"name": "OTEL_SERVICE_NAME", "value": "backend-flask"},
          {"name": "OTEL_EXPORTER_OTLP_ENDPOINT", "value": "https://api.honeycomb.io"},
          {"name": "AWS_COGNITO_USER_POOL_ID", "value": "us-east-1_LALJjTn8z"},
          {"name": "AWS_COGNITO_USER_POOL_CLIENT_ID", "value": "1giqls5t852vsv5ga1bpfnjcjo"},
          {"name": "FRONTEND_URL", "value": "*"},
          {"name": "BACKEND_URL", "value": "*"},
          {"name": "AWS_DEFAULT_REGION", "value": "us-east-1"}
        ],
        "secrets": [
          {"name": "AWS_ACCESS_KEY_ID"    , "valueFrom": "arn:aws:ssm:us-east-1:235696014680:parameter/cruddur/backend-flask/AWS_ACCESS_KEY_ID"},
          {"name": "AWS_SECRET_ACCESS_KEY", "valueFrom": "arn:aws:ssm:us-east-1:235696014680:parameter/cruddur/backend-flask/AWS_SECRET_ACCESS_KEY"},
          {"name": "CONNECTION_URL"       , "valueFrom": "arn:aws:ssm:us-east-1:235696014680:parameter/cruddur/backend-flask/CONNECTION_URL" },
          {"name": "ROLLBAR_ACCESS_TOKEN" , "valueFrom": "arn:aws:ssm:us-east-1:235696014680:parameter/cruddur/backend-flask/ROLLBAR_ACCESS_TOKEN" },
          {"name": "OTEL_EXPORTER_OTLP_HEADERS" , "valueFrom": "arn:aws:ssm:us-east-1:235696014680:parameter/cruddur/backend-flask/OTEL_EXPORTER_OTLP_HEADERS" }
          
        ]
      }
    ]
  }
```
  
    
- Create **frontend Task definition** json file `frontend-react-js.json` and add the following 
```json
{
    "family": "frontend-react-js",
    "executionRoleArn": "arn:aws:iam::235696014680:role/CruddurServiceExecutionRole",
    "taskRoleArn": "arn:aws:iam::235696014680:role/CruddurTaskRole",
    "networkMode": "awsvpc",
    "cpu": "256",
    "memory": "512",
    "requiresCompatibilities": [ 
      "FARGATE" 
    ],
    "containerDefinitions": [
      {
        "name": "xray",
        "image": "public.ecr.aws/xray/aws-xray-daemon" ,
        "essential": true,
        "user": "1337",
        "portMappings": [
          {
            "name": "xray",
            "containerPort": 2000,
            "protocol": "udp"
          }
        ]
      },
      {
        "name": "frontend-react-js",
        "image": "235696014680.dkr.ecr.us-east-1.amazonaws.com/frontend-react-js",
        "essential": true,
        "healthCheck": {
          "command": [
            "CMD-SHELL",
            "curl -f http://localhost:3000 || exit 1"
          ],
          "interval": 30,
          "timeout": 5,
          "retries": 3
        },
        "portMappings": [
          {
            "name": "frontend-react-js",
            "containerPort": 3000,
            "protocol": "tcp", 
            "appProtocol": "http"
          }
        ],
  
        "logConfiguration": {
          "logDriver": "awslogs",
          "options": {
              "awslogs-group": "cruddur",
              "awslogs-region": "us-east-1",
              "awslogs-stream-prefix": "frontend-react-js"
          }
        }
      }
    ]
  }
```
  
#### Register Task Defintion
[Back to Top](#Week-6)

- Run the following command to create the backend task definition   
`aws ecs register-task-definition --cli-input-json file://aws/task-definitions/backend-flask.json`

- Run the following command to create the frontend task definition   
` aws ecs register-task-definition --cli-input-json file://aws/task-definitions/frontend-react-js.json`

#### Create Security Group
[Back to Top](#Week-6)

- Create SG and add **CRUD_SERVICE_SG** Env variable
```bash
export CRUD_SERVICE_SG=$(aws ec2 create-security-group \
  --group-name "crud-srv-sg" \
  --description "Security group for Cruddur services on ECS" \
  --vpc-id $DEFAULT_VPC_ID \
  --query "GroupId" --output text)
echo $CRUD_SERVICE_SG
```
- Allow inbound rule on port 4567 from anywhere to backend 
```bash
aws ec2 authorize-security-group-ingress \
  --group-id $CRUD_SERVICE_SG \
  --protocol tcp \
  --port 4567 \
  --cidr 0.0.0.0/0
```
- Allow inbound rule on port 3000 from anywhere to Frontend 
```bash
aws ec2 authorize-security-group-ingress \
  --group-id $CRUD_SERVICE_SG \
  --protocol tcp \
  --port 3000 \
  --cidr 0.0.0.0/0
```
- Retrieve the SG ID and save it as Env var **CRUD_SERVICE_SG**
```bash
export CRUD_SERVICE_SG=$(aws ec2 describe-security-groups \
  --filters Name=group-name,Values=crud-srv-sg \
  --query 'SecurityGroups[*].GroupId' \
  --output text)
```

---
---

### 3. ECS Services 
[Back to Top](#Week-6)

We will create a new service using the Task Definition we have created before.

- Create ECS service json file `aws/json/service-backend-flask.json`
```json
{
    "cluster": "cruddur",
    "launchType": "FARGATE",
    "desiredCount": 1,
    "enableECSManagedTags": true,
    "enableExecuteCommand": true,
    "networkConfiguration": {
      "awsvpcConfiguration": {
        "assignPublicIp": "ENABLED",
        "securityGroups": [
          "sg-0c351ea1a1f6ee48d"
        ],
        "subnets": [
          "subnet-0d1c7dd92f4e4dc0c",
          "subnet-02310dd57d18d89c1",
          "subnet-08449b933a2cbee79"
        ]
      }
    },
    "serviceConnectConfiguration": {
      "enabled": true,
      "namespace": "cruddur",
      "services": [
        {
          "portName": "backend-flask",
          "discoveryName": "backend-flask",
          "clientAliases": [{"port": 4567}]
        }
      ]
    },
    "propagateTags": "SERVICE",
    "serviceName": "backend-flask",
    "taskDefinition": "backend-flask"
  }
  ```

- Run the following command to create the backend service based on the json file   
`aws ecs create-service --cli-input-json file://aws/json/service-backend-flask.json`

- Create ECS service json file `aws/json/service-frontend-react-js.json`
```json
{
    "cluster": "cruddur",
    "launchType": "FARGATE",
    "desiredCount": 1,
    "enableECSManagedTags": true,
    "enableExecuteCommand": true,
    "loadBalancers": [
        {
            "targetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:235696014680:targetgroup/cruddur-frontend-react-tg/84e76a51a2d12fd6",
            "containerName": "frontend-react-js",
            "containerPort": 3000
        }
      ],
    "networkConfiguration": {
      "awsvpcConfiguration": {
        "assignPublicIp": "ENABLED",
        "securityGroups": [
          "sg-0c351ea1a1f6ee48d"
        ],
        "subnets": [
            "subnet-0d1c7dd92f4e4dc0c",
            "subnet-02310dd57d18d89c1",
            "subnet-08449b933a2cbee79"
        ]
      }
    },
    "propagateTags": "SERVICE",
    "serviceName": "frontend-react-js",
    "taskDefinition": "frontend-react-js",
    "serviceConnectConfiguration": {
      "enabled": true,
      "namespace": "cruddur",
      "services": [
        {
          "portName": "frontend-react-js",
          "discoveryName": "frontend-react-js",
          "clientAliases": [{"port": 3000}]
        }
      ]
    }
  }
```
- Run the following command to create the frontend service based on the json file    
`aws ecs create-service --cli-input-json file://aws/json/service-frontend-react-js.json`
  
#### Connect to the Service
[Back to Top](#Week-6)

We will need Session Manager plugin installed in the shell to be able to connect to the ECS service using AWS CLI with option ' ecs execute-command'
- Download and install **Sessions Manager plugin** using the following commands
```bash
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" \
-o "session-manager-plugin.deb"
sudo dpkg -i session-manager-plugin.deb
```
- Once The service is running and healthy, run the following to get the Task ID   
`aws ecs list-tasks --cluster cruddur`  
- Then run the following command to connect to the ECS service
```bash
aws ecs execute-command  \
--region $AWS_DEFAULT_REGION \
--cluster cruddur \
--task UseTheTaskID \
--container backend-flask \
--command "/bin/bash" \
--interactive
```
```bash
# Output
The Session Manager plugin was installed successfully. Use the AWS CLI to start a session.

Starting session with SessionId: ecs-execute-command-01145e5fbe521d5e2
root@ip-172-31-XXX-XXX:/backend-flask# 
```
  
#### BASH scripts

Created new AWS utility scripts that will help connect to the ECS service, obtain the Task public IP, list running tasks, start and stop the task based on service desired count. Also updated previous rds utility scripts

```bash
aws/bin
├── ecs-service-connect
├── ecs-task-get-public-ip
├── ecs-task-list
├── ecs-task-start-service-update-1
├── ecs-task-stop-service-update-0
├── rds-db-start
├── rds-db-stop
├── rds-status
└── rds-update-sg-rule
```
  
  #### ECS Service Connect
  [Back to Top](#Week-6)
  
  - We can use the above command in a bash script 
  - create a new script `ecs-service-connect` add the following code and make it executable

  ```bash
  #! /usr/bin/bash

  if [ -z "$1" ]; then
    echo "No TASK_ID argument supplied eg: ecs-service-connect 7c1196a7bb8546ebb99935a35a725156 backend-flask"
  exit 1
  fi
  TASK_ID=$1

  if [ -z "$2" ]; then
    echo "No CONTAINER_NAME argument supplied eg: ecs-service-connect 7c1196a7bb8546ebb99935a35a725156 backend-flask"
  exit 1
  fi
  CONTAINER_NAME=$2

  aws ecs execute-command  \
  --region $AWS_DEFAULT_REGION \
  --cluster cruddur \
  --task $TASK_ID \
  --container $CONTAINER_NAME \
  --command "/bin/bash" \
  --interactive
  ```
  
  #### ECS Task Public IP
  [Back to Top](#Week-6)
  
  - Create script `ecs-task-get-public-ip` to retrieve ECS Task public IP
  - Add the following and make it executable 
  ```bash
  #! /usr/bin/bash

  if [ -z "$1" ]; then
  echo "No CLUSTER argument supplied eg: ecs-task-get-public-ip cruddur 7c1196a7bb8546ebb99935a35a725156 "
  exit 1
  fi
  CLUSTER=$1
    
  TASK_ID=$2
  if [ -z "$2" ]; then
  echo "No TASK_ID argument supplied eg: ecs-task-get-public-ip cruddur 7c1196a7bb8546ebb99935a35a725156"
  exit 1
  fi

  task_eni=$(aws ecs describe-tasks --cluster $CLUSTER --tasks $TASK_ID --query 'tasks[].attachments[].details[?name==`networkInterfaceId`].value' --output text)
  aws ec2 describe-network-interfaces --network-interface-ids $task_eni --query 'NetworkInterfaces[].Association.PublicIp' --output text
  ```
  
  #### ECS Task List
  [Back to Top](#Week-6)

  - Create script `ecs-task-list` to list running tasks and their family name 
  ```bash
  #! /usr/bin/bash

  for task in $(aws ecs list-tasks --cluster cruddur --desired-status RUNNING --query 'taskArns[*]' --output text); do
      task_details=$(aws ecs describe-tasks --cluster cruddur --tasks $task --query 'tasks[0]')
      task_number=$(echo $task_details | jq -r '.taskDefinitionArn | split("/") | .[1]')
      task_family=$(echo $task_details | jq -r '.taskDefinitionArn | split("/") | .[0]')
      echo "Task $task_number is running in task family $task_family"
  done

  ```

  #### ECS Start Task
  [Back to Top](#Week-6)

  - Create script `cs-task-start-service-update-1` that will update service desired count to 1 and starts a task

  ```bash
  #! /usr/bin/bash

  if [ -z "$1" ]; then
    echo "No SERVICE argument supplied eg: ecs-task-start-service-update-1 backend-flask"
  exit 1
  fi

  servicename=$1

  aws ecs update-service --cluster cruddur --service $servicename --desired-count 1
  ```

  #### ECS Stop Task
  [Back to Top](#Week-6)

  - Create script `ecs-task-stop-service-update-0` that will update service desired count to 0 and stop the running tasks
  ```bash
  #! /usr/bin/bash

  if [ -z "$1" ]; then
    echo "No SERVICE argument supplied eg: ecs-task-stop-service-update-0 backend-flask"
  exit 1
  fi

  servicename=$1

  aws ecs update-service --cluster cruddur --service $servicename --desired-count 0

  ```

  


#### ECS Service Health Check
[Back to Top](#Week-6)

- Once ECS Task public ip is obtained, run the following to verify health check
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask/bin/ecs (main) $ curl http://TASK_PUBLIC_IP:4567/api/health-check
{
  "success": true
}
```
- Delete the ECS service 
  
#### RDS Security Group Update
[Back to Top](#Week-6)

- We need to add a new inbound rule to RDS SG to allow access from ECS service SG to RDS database
- Run the following to add new inbound rule using port 5432 and SG crud-srv as a source 

```bash
aws ec2 authorize-security-group-ingress \
  --group-id $DB_SG_ID \
  --protocol tcp \
  --port 5432 \
  --source-group $CRUD_SERVICE_SG 
  ```

---
---

### 4. Load Balancer ALB
[Back to Top](#Week-6)

We will create a Load Balancer to distrebute access to the frontend and backend app. This will help to decouple requests and manage access to the app.
First we will create new ALB security group to allow traffic over port 80 & 443 (temporary as well on ports 4567 & 3000) then update ECS service security group to allow traffic from the ALB only. Next we will create ALB load balancer, create Target Groups (Frontend/Backend), and Listeners. Once ALB is ready, we will update the ECS service json file to enable ALB for the backend, create the ECS service then test access via ALB URL.

#### 1. Create Security Group
[Back to Top](#Week-6)

- Run the following command to create a new security group **cruddur-alb-sg**   
`aws ec2 create-security-group --group-name cruddur-alb-sg --description "cruddur ALB SG" --vpc-id vpc-XXXXXXXXXX`
- Note the SG ID to be used later to create the Listener in step 2
- Run the following commands to create inbound to allow access from anywhere on ports 80 and 443
```bash
aws ec2 authorize-security-group-ingress --group-name cruddur-alb-sg --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-name cruddur-alb-sg --protocol tcp --port 443 --cidr 0.0.0.0/0
```
- Run the following to create **temp** inbound rule so health check will not fail
```bash
aws ec2 authorize-security-group-ingress --group-name cruddur-alb-sg --protocol tcp --port 4567 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-name cruddur-alb-sg --protocol tcp --port 3000 --cidr 0.0.0.0/0
```
- Remove existing inbound rule from ECS Service SG **crud-srv-sg**
- Add a new inbound rule to SG **crud-srv-sg** that allow access from ALB SG 
- Rule: **port** 4567 - **Source** cruddur-alb-sg

#### 2. Create ALB
[Back to Top](#Week-6)

- Run the following command to create ALB **cruddur-alb**
```bash
aws elbv2 create-load-balancer --name cruddur-alb \
--subnets subnet-XXXXXXXXXX subnet-XXXXXXXXXX subnet-XXXXXXXXXX \
--security-groups sg-XXXXXXXXXX --scheme internet-facing --type application
```
- Note the **ALB ARN** to be used later to create the Listener in step 4

#### 3. Create Target Group
[Back to Top](#Week-6)

- Run the following command to create backend Target Group **cruddur-backend-flask-tg**
```bash
aws elbv2 create-target-group --name cruddur-backend-flask-tg --target-type ip \
--vpc-id vpc-XXXXXXXXXX --protocol HTTP --port 4567 \
--health-check-protocol HTTP --health-check-path "/api/health-check" \
--health-check-interval-seconds 30 --healthy-threshold-count 3
```
- Run the following command to create frontend Target Group **cruddur-frontend-react-tg**
```bash
aws elbv2 create-target-group --name cruddur-frontend-react-tg --target-type ip \
--vpc-id vpc-XXXXXXXXXX --protocol HTTP --port 3000 \
--health-check-protocol HTTP --health-check-path "/" \
--health-check-interval-seconds 30 --healthy-threshold-count 3
```
- Note the **Target Group ARN** to be used later to create the Listener in step 4

#### 4. Create Load Balancer Listener 
[Back to Top](#Week-6)

- Run the following command to create **backend Listener**
```bash
aws elbv2 create-listener --load-balancer-arn <load-balancer-arn>\
 --protocol HTTP --port 4567 --default-actions \
 Type=forward,TargetGroupArn=<backend-target-group-arn>
```

- Run the following command to create **frontend Listener**
```bash
aws elbv2 create-listener --load-balancer-arn <load-balancer-arn>\
 --protocol HTTP --port 3000 --default-actions \
 Type=forward,TargetGroupArn=<frontend-target-group-arn>
```

#### 5. Add ALB to ECS service
[Back to Top](#Week-6)

- We will update the `service-backend-flask.json` with ALB config
```json
"loadBalancers": [
    {
        "targetGroupArn": "<backend-target-group-arn>",
        "containerName": "backend-flask",
        "containerPort": 4567
    }
  ],
```
- We will update the `service-frontend-react-js.json` with ALB config
```json
  "loadBalancers": [
        {
            "targetGroupArn": "<backend-target-group-arn>",
            "containerName": "frontend-react-js",
            "containerPort": 3000
        }
      ],
```

#### 6. Create ECS service
[Back to Top](#Week-6)

- Run the following command to create the backend ECS service again
`aws ecs create-service --cli-input-json file://aws/json/service-backend-flask.json`
- Verify it is running and healthy 
- Run the following command to create the frontend ECS service again
`aws ecs create-service --cli-input-json file://aws/json/service-frontend-react-js.json`
- Verify it is running and healthy 

#### 7. Test ALB URL Access
[Back to Top](#Week-6)

- Get the ALB DNS URL
- Run the following to verify the backend health check
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ curl http://cruddur-alb-xxxxx5074.us-east-1.elb.amazonaws.com:4567/api/health-check
{
  "success": true
}
```
- Access the frontend app by browsing the ALB URL using port 3000  

![Screen Shot 2023-04-06 at 12 21 09 AM](https://user-images.githubusercontent.com/91587569/230216146-b1053dbe-5111-498c-9133-cb3528c6eec4.png)
  

#### 8. Create ALB Logs S3 Bucket
[Back to Top](#Week-6)

- Go to AWS S3 console then click on **Create bucket**
- Enter the bucket name - Yourbucket-alb-logs
- select the same region 
- uncheck **Block all public access**, but keep block ACL checked
- Check **Acknowledge public access**
- click on **Create bucket**
- Add the following Bucket policy
  - Replace the 'elb-account-id' with the elb account id of your region by checking this list
  - Replace the bucket name with your bucket name then add '/AWSLogs/YourAccountID/*'
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::elb-account-id:root"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::bucket-name/prefix/AWSLogs/your-aws-account-id/*"
    }
  ]
}
```

#### 9. Enable ALB logs
[Back to Top](#Week-6)

- Go to AWS EC2 console then select Load Balancer
- Select the ALB created previously then click on **Attributes** tab
- Click on **Edit** then enable **Access logs** 
- Browse and select the S3 bucket name created previously 
- Click on save

