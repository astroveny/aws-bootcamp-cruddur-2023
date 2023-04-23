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

To speed up the deployment, we have to udpate the loadbalancer health check time, deregistration time and Task definition container stop time
The following changes, reduced the pipeline process from  around **30 minutes to 8 minutes**

- Loadbalancer - Target Group
  - list target groups and relevant ARN   
  `aws elbv2 describe-target-groups --query "TargetGroups[*].[TargetGroupName, TargetGroupArn]" --output table`
  - update target group health check interval to 10 seconds and threshold to 2
  `aws elbv2 modify-target-group --target-group-arn <target-group-arn> --health-check-interval-seconds 10 --healthy-threshold-count 2`
  - update deregistration_delay.timeout_seconds to 10 seconds 
  ` aws elbv2 modify-target-group-attributes --target-group-arn <target-group-arn> --attributes Key=deregistration_delay.timeout_seconds,Value=10`
- Task Definition
  - update the following
    "interval": 10,
    "retries": 2,
  - Add task definition ECS_CONTAINER_STOP_TIMEOUT to 6
  `"environment":` `{"name": "ECS_CONTAINER_STOP_TIMEOUT", "value": "6"}`