# Week 9 

## CI/CD with CodePipeline, CodeBuild and CodeDeploy


## 1. CodePipeline 

### Create Pipeline

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


### Create CodeBuild Build Project

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
  
  
### Add Build Stage

- Click on **Edit** at the top
- Select **Add stage** before **Deploy** stage
- Type **Stage name:** Build
  - Click **Add action group**
  - **Action name:**  bake-image
  - **Action provider:** CodeBuild 
  - **Input artifacts:** SourceArtifact
  - **Project name:** cruddur-backend-flask-bake-image
  - **Build type:** Single build
  - Click **Done**
  
  
### Create ECR Policy

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

### Test CodeBuild Build Run

- After updating Github main branch, go to **Pull Requests** tab
- Click **New pull request**
- Select base **prod** <- compare **main** 
- Click **Create pull request** then commit the changes 
- This will trigger a CodeBuild build run
- once build is completed successfully, backend-flask ECR repo gets updated 
