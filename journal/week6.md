# Week 6 

## Deploying Containers
  

## Health Checks and Logs

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

## ECS and ECR 

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