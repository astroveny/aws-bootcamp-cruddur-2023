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



## Backend App: Production Image

We will build new backend-flask docker image for production using Dockerfile.prod that has no-debug enabled for security reasons.

### Create Dockerfile.prod

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

- Run the following command to build the new docker image    
`docker build -f Dockerfile.prod -t backend-flask-prod .`

### Run Production Docker Image

- Create docker script to run the backend production image
- 

