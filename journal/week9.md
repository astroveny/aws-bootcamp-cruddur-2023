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


### Edit Pipeline

- Click on **Edit** at the top
- Select **Add stage** after Edit:Deploy
- Type **Stage name:** bake-image
  - Click **Add action group**
  - **Action name:** build
  - **Action provider:** CodeBuild 
  - **Input artifacts:** SourceArtifact
  - **Project name:** click **Create Project**
    - This will open a CodeBuild page to create build project
    - **Project configuration/Project name:** cruddur-backend-flask-bake-image
    - **Environment/Environment image:** Managed image
      - **Operating system:** Amazon Linux 2
      - **Runtime:** Standard 
      - **Image:** chose the latest 
      - **Environment type:** Linux
      - Enable **Privileged** 
      - **Additional configuration/Timeout:** 20 minutes
      - **VPC:** Default
      - **Subnets:** a, b, and c
      - **Security groups:** Default
    - **Buildspec/Buildspec name:** [backend-flask/buildspec.yml](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/095945593f55d6a40b9fcf28a11fea92ebd1e08d/backend-flask/buildspec.yml)
    - **Logs/Group name:** /cruddur/build/backend-flask
    - **Stream name:** backend-flask
    - Click **Continue to CodePipeline**
    - Click **Done**
