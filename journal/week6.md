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
- Login to RCR  
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
- Build the frontend-react image
```bash
docker build \
--build-arg REACT_APP_BACKEND_URL="https://4567-$GITPOD_WORKSPACE_ID.$GITPOD_WORKSPACE_CLUSTER_HOST" \
--build-arg REACT_APP_AWS_PROJECT_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_COGNITO_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_USER_POOLS_ID="ca-central-1_CQ4wDfnwc" \
--build-arg REACT_APP_CLIENT_ID="5b6ro31g97urk767adrbrdj1g5" \
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

>> **MISSING STEPS!!**

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
- Create Task definition json file `backend-flask.json` and add the following 
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

#### Register Task Defintion
[Back to Top](#Week-6)

- Run the following command to create the backend task definition 
`aws ecs register-task-definition --cli-input-json file://aws/task-definitions/backend-flask.json`

- Run the following command to create the frontend task definition 
` `

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
- Allow inbound rule on port 4567 from anywhere 
```bash
aws ec2 authorize-security-group-ingress \
  --group-id $CRUD_SERVICE_SG \
  --protocol tcp \
  --port 4567 \
  --cidr 0.0.0.0/0
```
- Retrieve the SG ID and save it to Env var **CRUD_SERVICE_SG**
```bash
export CRUD_SERVICE_SG=$(aws ec2 describe-security-groups \
  --filters Name=group-name,Values=crud-srv-sg \
  --query 'SecurityGroups[*].GroupId' \
  --output text)
```

---
---

### ECS Service 

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

- Run the following command to create the service based on the json file 
`aws ecs create-service --cli-input-json file://aws/json/service-backend-flask.json`

#### Connect to the Service

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

Utility scripts that will help connect to the ECS service and obtain the Task public IP.

#### ECS Service Connect script
- We can use the above command in a bash script 
- create a new script `backend-flask/bin/ecs/connect-to-service` add the following code and make it executable

```bash
#! /usr/bin/bash

if [ -z "$1" ]; then
  echo "No TASK_ID argument supplied eg ./bin/ecs/conect-to-service 7c1196a7bb8546ebb99935a35a725156 backend-flask"
 exit 1
fi
TASK_ID=$1

if [ -z "$2" ]; then
  echo "No CONTAINER_NAME argument supplied eg ./bin/ecs/conect-to-service 7c1196a7bb8546ebb99935a35a725156 backend-flask"
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
- Create another script `get-task-public-ip` to retrieve ECS Task public IP
- Add the following and make it executable 
```bash
#! /usr/bin/bash

if [ -z "$1" ]; then
  echo "No CLUSTER argument supplied eg ./bin/ecs/conect-to-service cruddur 7c1196a7bb8546ebb99935a35a725156 "
 exit 1
fi
CLUSTER=$1
  
TASK_ID=$2
if [ -z "$2" ]; then
echo "No TASK_ID argument supplied eg ./bin/ecs/conect-to-service cruddur 7c1196a7bb8546ebb99935a35a725156"
 exit 1
fi

task_eni=$(aws ecs describe-tasks --cluster $CLUSTER --tasks $TASK_ID --query 'tasks[].attachments[].details[?name==`networkInterfaceId`].value' --output text)
aws ec2 describe-network-interfaces --network-interface-ids $task_eni --query 'NetworkInterfaces[].Association.PublicIp' --output text
```

#### ECS Service Health Check

- Once ECS Task public ip is obtained, run the following to verify health check
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask/bin/ecs (main) $ curl http://TASK_PUBLIC_IP:4567/api/health-check
{
  "success": true
}
```

#### RDS Security Group Update

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

### Load Balancer ALB

#### 1. Create Security Group

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

- Run the following command to create ALB **cruddur-alb**
```bash
aws elbv2 create-load-balancer --name cruddur-alb \
--subnets subnet-XXXXXXXXXX subnet-XXXXXXXXXX subnet-XXXXXXXXXX \
--security-groups sg-XXXXXXXXXX --scheme internet-facing --type application
```
- Note the ALB ARN to be used later to create the Listener in step 4

#### 3. Create Target Group

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
- Note the Target Group ARN to be used later to create the Listener in step 4

#### 4. Create Load Balancer Listener 

- Run the following command to create **backend Listener **
```bash
aws elbv2 create-listener --load-balancer-arn <load-balancer-arn>\
 --protocol HTTP --port 4567 --default-actions \
 Type=forward,TargetGroupArn=<backend-target-group-arn>
```

- Run the following command to create **frontend Listener **
```bash
aws elbv2 create-listener --load-balancer-arn <load-balancer-arn>\
 --protocol HTTP --port 3000 --default-actions \
 Type=forward,TargetGroupArn=<frontend-target-group-arn>
```

#### 5. Add ALB to ECS service

- We will update the `service-backend-flask.json` with the following
```json
"loadBalancers": [
    {
        "targetGroupArn": "<backend-target-group-arn>",
        "containerName": "backend-flask",
        "containerPort": 4567
    }
  ],
  ```

#### 6. Test ALB URL Access

- Run the following to verify health check
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ curl http://cruddur-alb-xxxxx5074.us-east-1.elb.amazonaws.com:4567/api/health-check
{
  "success": true
}
```
