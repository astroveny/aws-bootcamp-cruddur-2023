# Week 6 

## Deploying Containers

[1. Health Checks and Logs](#1-Health-Checks-and-Logs)
  - [Test RDS Connection](#Test-RDS-Connection)
  - [Flask App Health Check](#Flask-App-Health-Check)
  - [CloudWatch Log Group](#CloudWatch-Log-Group)

[2. ECS and ECR Setup](#2-ECS-and-ECR-Setup)
  - [ECS Cluster](#ECS-Cluster)
  - [ECR Repos](#ECR-Repos)
  - [Flask Repo](#Flask-Repo)

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
`aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com"`
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
---

### ECS Task Definition 

#### Env variables

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

#### Task and Execution Roles for Task Definition

Similar to docker compose file, we have to create a Task definition with all required attributes like Env variables, permissions, etc ..

##### Create Execution Role
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
  "Version":"2012-10-17",
  "Statement":[{
    "Effect": "Allow",
    "Action": [
      "ssm:GetParameters",
      "ssm:GetParameter"
    ],
    "Resource": "arn:aws:ssm:us-east-1:235696014680:parameter/cruddur/backend-flask/*"
  }]
}
```
- run the following command to create the role using service-assume-role-execution-policy.json policy 
```bash
aws iam create-role --role-name CruddurServiceExecutionRole  --assume-role-policy-document file://aws/policies/service-assume-role-execution-policy.json
```
- Run the following command to create abd add policy using service-execution-policy.json 
```bash
aws iam put-role-policy --policy-name CruddurServiceExecutionPolicy --role-name CruddurServiceExecutionRole \
  --policy-document file://aws/policies/service-execution-policy.json
```

##### Create Task Role

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

##### Create Task Definition 

- Create new dir: `aws/task-definitions`
- Create Task definition json file `backend-flask.json` and add the following 
```json
{
  "family": "backend-flask",
  "executionRoleArn": "arn:aws:iam::AWS_ACCOUNT_ID:role/CruddurServiceExecutionRole",
  "taskRoleArn": "arn:aws:iam::AWS_ACCOUNT_ID:role/CruddurTaskRole",
  "networkMode": "awsvpc",
  "containerDefinitions": [
    {
      "name": "backend-flask",
      "image": "BACKEND_FLASK_IMAGE_URL",
      "cpu": 256,
      "memory": 512,
      "essential": true,
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
        {"name": "AWS_COGNITO_USER_POOL_ID", "value": "YourUserPoolID"},
        {"name": "AWS_COGNITO_USER_POOL_CLIENT_ID", "value": "YourUserPoolClientID"},
        {"name": "FRONTEND_URL", "value": "*"},
        {"name": "BACKEND_URL", "value": "*"},
        {"name": "AWS_DEFAULT_REGION", "value": "us-east-1"}
      ],
      "secrets": [
        {"name": "AWS_ACCESS_KEY_ID"    , "valueFrom": "arn:aws:ssm:AWS_REGION:AWS_ACCOUNT_ID:parameter/cruddur/backend-flask/AWS_ACCESS_KEY_ID"},
        {"name": "AWS_SECRET_ACCESS_KEY", "valueFrom": "arn:aws:ssm:AWS_REGION:AWS_ACCOUNT_ID:parameter/cruddur/backend-flask/AWS_SECRET_ACCESS_KEY"},
        {"name": "CONNECTION_URL"       , "valueFrom": "arn:aws:ssm:AWS_REGION:AWS_ACCOUNT_ID:parameter/cruddur/backend-flask/CONNECTION_URL" },
        {"name": "ROLLBAR_ACCESS_TOKEN" , "valueFrom": "arn:aws:ssm:AWS_REGION:AWS_ACCOUNT_ID:parameter/cruddur/backend-flask/ROLLBAR_ACCESS_TOKEN" },
        {"name": "OTEL_EXPORTER_OTLP_HEADERS" , "valueFrom": "arn:aws:ssm:AWS_REGION:AWS_ACCOUNT_ID:parameter/cruddur/backend-flask/OTEL_EXPORTER_OTLP_HEADERS" }
        
      ]
    }
  ]
}
```

##### Register Task Defintion

- Run the following command to create the backend task definition 
`aws ecs register-task-definition --cli-input-json file://aws/task-definitionss/backend-flask.json`

- Run the following command to create the frontend task definition 
` `

##### Create Security Group

- Add CRUD_SERVICE_SG Env variable
```bash
export CRUD_SERVICE_SG=$(aws ec2 create-security-group \
  --group-name "crud-srv-sg" \
  --description "Security group for Cruddur services on ECS" \
  --vpc-id $DEFAULT_VPC_ID \
  --query "GroupId" --output text)
echo $CRUD_SERVICE_SG
```
- Allow inbound rule on port 80 from anywhere 
```bash
aws ec2 authorize-security-group-ingress \
  --group-id $CRUD_SERVICE_SG \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0
```
