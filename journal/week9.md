# Week 9 

## CI/CD with CodePipeline, CodeBuild and CodeDeploy

- [CodePipeline](#CodePipeline)
  - [Create Pipeline](#Create-Pipeline)
  - [Create CodeBuild Build Project](#Create-CodeBuild-Build-Project)
  - [Add Build Stage](#Add-Build-Stage)
  - [Create ECR Policy](#Create-ECR-Policy)
  - [Test The Pipeline](#Test-The-Pipeline)
  - [Speeding up Deployment](#Speeding-up-Deployment)
- [Domain Failover](#Domain-Failover)
  - [S3 Static Website](#S3-Static-Website)
  - [Cloudfront Distribution](#Cloudfront-Distribution)
  - [Route 53 Hosted Zone Records](#Route-53-Hosted-Zone-Records)
  - [Logging Static Website Traffic](#Logging-Static-Website-Traffic)

During this week we will automate code deployment using Codepipeline then Create a DNS failover mechanism to route access to a static website in the event that the Cruddur app is unavailable due to maintenance. 


## CodePipeline 

We will setup CodePipeline using Github as the source repository, CodeBuild to build the image and deploy it using ECS 

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
- **Primary source webhook events/Webhook**
  - Enable **Rebuild every time a code change is pushed to this repository**
  - **Build type:** Single build
  - **Event type:** PULL_REQUEST_MERGED
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

During the develompment phase, we will setup a Route 53 DNS failover method. This will route the access to a static website in the event that the Cruddur app is unavailable due to maintenance. We will start by creating a S3 static website, then to access the website over HTTPS we will create a CloudFormation distribution with origin as the S3 sattic website. Findally, we will Update the primary A record in the Route 53 hosted zone to failover after evaluating target health, then create a new A record using the same record name pointing to the CloudFront Distribution domain name, and routing as secondary failover.

### S3 Static Website

- Go to AWS S3 console
- Create a bucket using your DomainName as the name of the bucket
- Select the bucket then Edit **Static website hosting** under **Properties** tab
- Select **Enable** Static website hosting
- Enter the **Index document** file name e.g. index.html that display "Under Maintenance"
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
- Create a new A record to point to the static website:
  - Select **Create record**
  - Select **Record type** as A record
  - Enable **Alias** then under **Route traffic to** select CloudFront distribution
  - Select the CloudFront Distribution domain name created in the previous step  
  - Select **Routing policy** as Failover
  - Select **Failover record type** as Secondary 
  - **Record ID:** enter any value
  - Click on **Create record**

Route 53 can now failover to the static website in the event that the Cruddur app is unavailable due to maintenance.

![Screen Shot 2023-04-26 at 4 24 49 PM](https://user-images.githubusercontent.com/91587569/234575041-6ae8abe6-4313-4c87-bb27-0cc80ec7543d.png)
  

### Logging Static Website Traffic

- Go to **AWS S3** console
  - Create a logs bucket for CloudFront and enable ACL the create a logs folder
  - Create another bucket to be used by Athena 
- Go to **AWS Cloudfront** console
  - Select the **distribution** then click **Edit**
  - Turn On **Standard logging** then select the S3 bucket you have just created
  - **Prefix:** the logs folder
  - **Save changes**
  - Wait until Cloudfront distribution is deployed
  - If the Web App is down, access your Cruddur web app to redirect to the CloudFront distribution URL 
    - or access the Cloudfront distribution URL directly 
  - This will generate logs inside the S3 logs bucket
- Go to **AWS Athena** console
  - Make sure you are using the same region as the created bucket
  - Select the Athena bucket to be used by Athena to store the data
  - Add the following to the Query editor to create a **cruddur** database `create database cruddur;`
  - Click **Run**
  - Select the **+** sign to add a new query tab then add the following to create a table
```sql
CREATE EXTERNAL TABLE IF NOT EXISTS cruddur.cloudfront_logs (
  `date` DATE,
  time STRING,
  location STRING,
  bytes BIGINT,
  request_ip STRING,
  method STRING,
  host STRING,
  uri STRING,
  status INT,
  referrer STRING,
  user_agent STRING,
  query_string STRING,
  cookie STRING,
  result_type STRING,
  request_id STRING,
  host_header STRING,
  request_protocol STRING,
  request_bytes BIGINT,
  time_taken FLOAT,
  xforwarded_for STRING,
  ssl_protocol STRING,
  ssl_cipher STRING,
  response_result_type STRING,
  http_version STRING,
  fle_status STRING,
  fle_encrypted_fields INT,
  c_port INT,
  time_to_first_byte FLOAT,
  x_edge_detailed_result_type STRING,
  sc_content_type STRING,
  sc_content_len BIGINT,
  sc_range_start BIGINT,
  sc_range_end BIGINT
)
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY '\t'
LOCATION 's3://YourS3LogsBucket'
TBLPROPERTIES ( 'skip.header.line.count'='2' );
```
  - **Run** the query
  - Add another query tab to query the data from the table using the following
```sql
SELECT * FROM "cruddur"."cloudfront_logs" limit 10;
```
  - **Run** the query to display the data  
  - You will see useful data such as: Date/time, Location, Request_IP, Method, status, and Host_Header ..

>> Table fields description Ref. https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/AccessLogs.html#access-logs-choosing-s3-bucket
  

### Latest 5 logs Lambda Function

We will reduce the number of log file inside the S3 logs buckt by creating a lambda function that will keep the latest 5 logs generated by CloudFront. The function will be triggered once a new logs file is generated

- Go to **AWS Lambda** console
- Click **Create function**
  - **Function name:** CF-Latest-logs
  - **Runtime:** Pyhton 3.10
  - **Architecture:** x86_64
  - Click *Create function**
-   Replace the lambda function code with the following
```python
import boto3
from datetime import datetime

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket_name = '<YourBucketName>' # replace the value <YourBucketName>
    folder_name = '<LogsFolder>' # replace the value <LogsFolder>
    last_5_objects = []
    
    # Get a list of all objects in the folder
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)['Contents']
    
    # Sort the objects by last modified date, with the most recent objects first
    objects.sort(key=lambda x: x['LastModified'], reverse=True)
    
    # Keep the last recent 5 objects
    for i in range(5):
        if i < len(objects):
            last_5_objects.append(objects[i]['Key'])
    
    # Delete all objects in the folder except the last recent 5 objects
    for obj in objects:
        if obj['Key'] not in last_5_objects:
            s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
    
    return {
        'statusCode': 200,
        'body': 'Objects deleted from S3 folder except the last recent 5 objects'
    }
 ```
 - Click **Deploy**
 
 #### Add S3 Bucket Permissions
 - Go to **Configuration** tab inside the Lambda function
 - Select **Permissions** fromt he left-side menu
 - Click the **Role name** to add new permissions
 - Click **Add permissions** then **Create inline policy**
 - Click on **JSON** tab then replace the content with the following
 ```json
 {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::cf-logs-awsbc.flyingresnova.com/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::cf-logs-awsbc.flyingresnova.com"
            ]
        }
    ]
}
```
- Click **Review policy** 
- Enter a **Name** then click **Create policy**

#### Trigger Lambda Function

- Go to **AWS S3** console
- Select the CloudFront logs bucket you have created previously 
- Click on **Properties**
- Click **Create event notification** under **Event notifications** 
  - **Event name:** cf-latest-logs
  - **Event types:** select **All object create events**
  - **Destination:** select Lambda function
  - Select the lambda function "CF-Latest-logs" from the drop-down menu
  - Click on **Save changes**


  

[Back to Top](#Week-9)
