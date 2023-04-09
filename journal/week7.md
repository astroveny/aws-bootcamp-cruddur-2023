# Week 7 

## Solving CORS with a Load Balancer and Custom Domain

- [Custom Domain](#Custom-Domain)
    [1. Register New Domain](#1-Register-New-Domain)
    [2. Create Hosted Zone](#2-Create-Hosted-Zone)
    [3. Create Certificate](#3-Create-Certificate)
    [4. Update ALB](#4-Update-ALB)
    [5. Hosted Zone backend Record](#5-Hosted-Zone-backend-Record)
    [6. Hosted Zone frontend Record](#6-Hosted-Zone-frontend-Record)
    [7. Update Task Definitions](#7-Update-Task-Definitions)
    [8. Update frontend-react-js image](#8-Update-frontend-react-js-image)
    [9. Test Access](#9-Test-Access)


  
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

- Update backend-flask.json with the following
```json
 {"name": "FRONTEND_URL", "value": "https://YourDomainName.com"},
 {"name": "BACKEND_URL", "value": "https://api.YourDomainName.com"},
```
- Register the task definition again   
`aws ecs register-task-definition --cli-input-json file://aws/task-definitions/backend-flask.json`


### 8. Update frontend-react-js image

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

- Test access to the backend app using the health check endpoint
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023/aws (main) $ curl https://api.awsbc.flyingresnova.com/api/health-check
{
  "success": true
}
```
- Test access to the frontend app using the domain name URL







