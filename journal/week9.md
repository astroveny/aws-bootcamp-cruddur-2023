# Week 9 

## CI/CD with CodePipeline, CodeBuild and CodeDeploy


## CodePipeline 

### Create Pipeline
[Back to Top](#Week-9)

- Go to AWS CodePipeline console
- Click on **Create pipeline**
- **Pipeline settings/Pipeline name:** cruddur-backend-fargate
  - **Service role:** New service role
- **Source/Source provider:** Github (Version2)
  - Select **Connect to Github**
  - **Connection name:** Cruddur
  - Click on **Connect to Github** then authorize access to your Github
  - Select **Install a new app** then chose **Only select repositories**
  - Select **aws-bootcamp-cruddur-2023** then click **Connect**
  - Go to Github Repo, click on Branches then **New branch**
  - type "prod" then create the branch
  - Go back to AWS CodePipline page, then enter **Branch name:** prod
  - Select **Output artifact format** as CodePipeline default
- Select **Skip build**
- Select **Deploy/Deploy provider:** Amazon ECS
  - **Cluster name:** cruddur
  - **Service name:** backend-flask
- Click **Create pipeline**

---
### Create CodeBuild Build Project
[Back to Top](#Week-9)

- Go to AWS CodeBuild console then Select **Create project**
- **Project name:** cruddur-backend-flask-bake-image
- Enable **Build badge**
- **Source/Source provider:** Github
  - Select **Repository in my GitHub account**
  - **GitHub repository:** chose "aws-bootcamp-cruddur-2023"
  - **Source version:** prod
- **Environment/Environment image:** Managed image
  - **Operating system:** Amazon Linux 2
  - **Runtime:** Standard 
  - **Image:** chose the latest 
  - **Environment type:** Linux
  - Enable **Privileged** 
  - **Additional configuration/Timeout:** 20 minutes
- **Buildspec/Buildspec name:** [backend-flask/buildspec.yml](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/66129a174895d7160c8b0cdcbaac85cd391f0f4a/backend-flask/buildspec.yml)
- **Logs/Group name:** /cruddur/build/backend-flask
    - **Stream name:** backend-flask
  
 --- 
### Add Build Stage
[Back to Top](#Week-9)

- Click on **Edit** at the top
- Select **Add stage** before **Deploy** stage
- Type **Stage name:** Build
  - Click **Add action group**
  - **Action name:**  bake-image
  - **Action provider:** CodeBuild 
  - **Input artifacts:** SourceArtifact
  - **Project name:** cruddur-backend-flask-bake-image
  - **Build type:** Single build
  - **Output artifacts:** imagedefinitions
  - Click **Done** 
- then **Done**
- Edit **Deploy** stage
  - Click Edit action **Deploy**
  - Update **Input artifacts:** imagedefinitions
  - Click **Done** 
- then **Done**
- Click **Save**

---  
### Create ECR Policy
[Back to Top](#Week-9)

Create a new IAM policy to allow ECR actions then attach it to CodeBuild bake image role

- Create new IAM policy using the following json 
- Attach the policy to CodeBuild bake image role
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ecr:GetRegistryPolicy",
                "ecr:PutImageTagMutability",
                "ecr:GetLifecyclePolicyPreview",
                "ecr:GetDownloadUrlForLayer",
                "ecr:GetAuthorizationToken",
                "ecr:UploadLayerPart",
                "ecr:ListImages",
                "ecr:BatchGetRepositoryScanningConfiguration",
                "ecr:GetRegistryScanningConfiguration",
                "ecr:PutImage",
                "ecr:BatchImportUpstreamImage",
                "ecr:SetRepositoryPolicy",
                "ecr:BatchGetImage",
                "ecr:CompleteLayerUpload",
                "ecr:DescribeImages",
                "ecr:DescribeRepositories",
                "ecr:StartLifecyclePolicyPreview",
                "ecr:InitiateLayerUpload",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetRepositoryPolicy",
                "ecr:GetLifecyclePolicy"
            ],
            "Resource": "*"
        }
    ]
}
```
---
### Test The Pipeline
[Back to Top](#Week-9)

- After updating Github main branch, go to **Pull Requests** tab
- Click **New pull request**
- Select base **prod** <- compare **main** 
- Click **Create pull request** then commit the changes 
- This will trigger the CodePipeline pipeline to run the stages
- once code is deployed successfully, backend-flask ECS service will start

---
### Speeding up Deployment
[Back to Top](#Week-9)

To speed up the deployment, we have to udpate the loadbalancer health check time, deregistration time and Task definition container stop time.
The following changes, reduced the pipeline processing time from around **30 minutes to 8 minutes**

- Loadbalancer - Target Group
  - list target groups and relevant ARN   
  `aws elbv2 describe-target-groups --query "TargetGroups[*].[TargetGroupName, TargetGroupArn]" --output table`
  - update target group health check interval to 10 seconds and threshold to 2   
  `aws elbv2 modify-target-group --target-group-arn <target-group-arn> --health-check-interval-seconds 10 --healthy-threshold-count 2`
  - update deregistration_delay.timeout_seconds to 10 seconds    
  ` aws elbv2 modify-target-group-attributes --target-group-arn <target-group-arn> --attributes Key=deregistration_delay.timeout_seconds,Value=10`
- Task Definition
  - update the Backend container health check properties, decrease the interval to 10, and the number of retries to 2. 
    ```yml
    "interval": 10,
    "retries": 2,
    ```
  - Add task definition ECS_CONTAINER_STOP_TIMEOUT to 6    
  `"environment":` `{"name": "ECS_CONTAINER_STOP_TIMEOUT", "value": "6"}`
  
  ---
  ---
  
  
## Domain Failover 

During the develompment phase, we will setup a Route 53 DNS failover method. This will route the access to your Cruddur app DomainName to a static website sayin that Crudder app is under construction. We will start by creating a S3 static website, then to access the website over HTTPS we will create a CloudFormation distribution with origin as the S3 sattic website. Findally, we will Update the primary A record in the Route 53 hosted zone to failover after evaluating target health, then create a new A record using the same record name pointing to the CloudFront Distribution domain name, and routing as secondary failover.

### S3 Static Website

- Go to AWS S3 console
- Create a bucket using your DomainName as the name of the bucket
- Select the bucket then Edit **Static website hosting** under **Properties** tab
- Select **Enable** Static website hosting
- Enter the **Index document** file name e.g. index.html
- Save changes then go to **Permissions** tab, Edit **Block public access**
- De-select **Block all public access** then save changes
- Edit **Bucket policy** then add the following (repalce the _"S3-Bucket-ARN"_)
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::S3-Bucket-ARN/*"
        }
    ]
}
```

### Cloudfront Distribution 

- Go to AWS CloudFront console
- Click on **Create Distribution**
- **Origin domain:** Select the S3 bucket created previously 
- Click on **Use website endpoint**
- **Viewer/Viewer protocol policy:** Redirect HTTP to HTTPS
  - **Allowed HTTP methods:** GET, HEAD
- **Settings/Alternate domain name (CNAME):** Add your DomainName
  - **Custom SSL certificate - optional:** Select your ACM certificate
  - **Supported HTTP versions:** Select both HTTTP 2/3
- Click on **Creat distribution**


### Route 53 Hosted Zone Records

- Go to AWS Route 53 console
- Select and edit the exiting primary A record pointing to your website via the ALB
- Change **Routing policy:** to Failover
- **Failover record type:** Primary
- Make sure **Evaluate target health** is enabled
- **Record ID:** enter any value
- Click on **Save**
