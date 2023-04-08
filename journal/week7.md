# Week 7 

## Solving CORS with a Load Balancer and Custom Domain



  
## Custom Domain
[Back to top](#week-7)

We will register a new domain by following the steps in this document https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/domain-register.html.
Once the domain is registered them we will create hosted zone .

>> NOTE: If you create records in a hosted zone other than the one that Route 53 creates automatically, you must update the name servers for the domain to use the name servers for the new hosted zone.

### Create Hosted Zone
[Back to top](#week-7)

- Go to AWS Route53 console
- Click on create **Create hosted zone**
- Enter your **Domain name** & Description
- Select **Public hosted zone** 
- Click on **Create Hosted zone**


### Create Certificate 
[Back to top](#week-7)

- Go To AWS Certificate Manager (ACM) console 
- Click on **request**
- Select **Request a public certificate** then **Next**
- Enter the **Domain name FQDN **
- Choose how you want to validate from **Validation method**
- Select the **Key algorithm** then click on **Request**


### ALB Update

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
- Once HTTPS:443 listener is created, select it then click on Actions
- Select **Manage Rules**
- Click on the **+** sign then **insert rule**
- under **IF (match all)** select **Add condition** as **Host header:** api.YourDomainName.come
- Under **THEN** select **Add action** as **Forward to:** then select the _target group_ "cruddur-backend-flask-tg"


### Hosted Zone backend Record

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



