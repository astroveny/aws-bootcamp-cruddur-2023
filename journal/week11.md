# Week 11 


## CloudFormation Part 2




## 1.1 DynamoDB Template


- Create a new dir: ddb
- Create a new template file inside dir: ddb, [template.yaml]

### DynamoDB Description

- Add the following description
```yml
Description: | 
  - DynamoDB Table
  - DynamoDB Stream
```
---
### DynaoDB Parameters

- Add the following Parameters to be referenced while creating resources
```yml
Parameters:
  PythonRuntime:
    Type: String
    Default: python3.9
  MemorySize:
    Type: String
    Default:  128
  Timeout:
    Type: Number
    Default: 3
  DeletionProtectionEnabled:
    Type: String
    Default: false
```

---
### DynamoDB Resources 

#### DynamoDB Table

- Add the following to create a DynamoDB Table
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html
```yml
DynamoDBTable:
    Type: AWS::DynamoDB::Table
    Properties: 
      AttributeDefinitions: 
        - AttributeName: message_group_uuid
          AttributeType: S
        - AttributeName: pk
          AttributeType: S
        - AttributeName: sk
          AttributeType: S
      TableClass: STANDARD 
      KeySchema: 
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: sk
          KeyType: RANGE
      ProvisionedThroughput: 
        ReadCapacityUnits: 5
        WriteCapacityUnits: 5
      BillingMode: PROVISIONED
      DeletionProtectionEnabled: !Ref DeletionProtectionEnabled
      GlobalSecondaryIndexes:
        - IndexName: message-group-sk-index
          KeySchema:
            - AttributeName: message_group_uuid
              KeyType: HASH
            - AttributeName: sk
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
          ProvisionedThroughput: 
            ReadCapacityUnits: 5
            WriteCapacityUnits: 5
      StreamSpecification:
        StreamViewType: NEW_IMAGE
```

#### Process DynamoDB Stream

- Add the following to create a DynamoDB Stream
>> Ref. https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-function.html
```yml
ProcessDynamoDBStream:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      PackageType: Zip
      Handler: lambda_handler
      Runtime: !Ref PythonRuntime
      Role: !GetAtt ExecutionRole.Arn
      MemorySize: !Ref MemorySize
      Timeout: !Ref Timeout
      Events:
        Stream:
          Type: DynamoDB
          Properties:
            Stream: !GetAtt DynamoDBTable.StreamArn
            # TODO - Does our Lambda handle more than record?
            BatchSize: 1
            # https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-property-function-dynamodb.html#sam-function-dynamodb-startingposition
            # TODO - This this the right value?
            StartingPosition: LATEST
```

#### Lambda Log Group

- Add the following to create a Lambda Log Group
```yml
LambdaLogGroup:
    Type: "AWS::Logs::LogGroup"
    Properties:
      LogGroupName: "/aws/lambda/cruddur-messaging-stream00"
      RetentionInDays: 14
```


#### Lambda Log Stream

- Add the following to create a Lambda Log Stream
```yml
LambdaLogStream:
    Type: "AWS::Logs::LogStream"
    Properties:
      LogGroupName: !Ref LambdaLogGroup
      LogStreamName: "LambdaExecution"
```


#### Execution Role

- Add the following to create an Execution Role
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html
```yml
ExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: CruddurDdbStreamExecRole
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: 'Allow'
            Principal:
              Service: 'lambda.amazonaws.com'
            Action: 'sts:AssumeRole'
      Policies:
        - PolicyName: "LambdaExecutionPolicy"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: "Allow"
                Action: "logs:CreateLogGroup"
                Resource: !Sub "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:*"
              - Effect: "Allow"
                Action:
                  - "logs:CreateLogStream"
                  - "logs:PutLogEvents"
                Resource: !Sub "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:${LambdaLogGroup}:*"
              - Effect: "Allow"
                Action:
                  - "ec2:CreateNetworkInterface"
                  - "ec2:DeleteNetworkInterface"
                  - "ec2:DescribeNetworkInterfaces"
                Resource: "*"
              - Effect: "Allow"
                Action:
                  - "lambda:InvokeFunction"
                Resource: "*"
              - Effect: "Allow"
                Action:
                  - "dynamodb:DescribeStream"
                  - "dynamodb:GetRecords"
                  - "dynamodb:GetShardIterator"
                  - "dynamodb:ListStreams"
                Resource: "*"
```


## 1.2 SAM Setup

### Install SAM

- Add the folowing to gitpod.yaml
```yml
  - name: aws-sam
      init: |
        cd /workspace
        wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip
        unzip aws-sam-cli-linux-x86_64.zip -d sam-installation
        sudo ./sam-installation/install
        cd $THEIA_WORKSPACE_ROOT
```
- Use the above commands to install SAM in your current workspace session

- 


### SAM Build Script 

- Move the cruddur-messaging-stream.py to`ddb/function/lambda_function.py`
- Create a **config.toml** file inside dir: ddb then add the follwing
```
version=0.1
[default.build.parameters]
region = "us-east-1"

[default.package.parameters]
region = "us-east-1"

[default.deploy.parameters]
region = "us-east-1"
```


- Create a **build** script file then add the following
```bash
#! /usr/bin/env bash
set -e # stop the execution of the script if it fails

FUNC_DIR="/workspace/aws-bootcamp-cruddur-2023/ddb/function/"
TEMPLATE_PATH="/workspace/aws-bootcamp-cruddur-2023/ddb/template.yaml"
CONFIG_PATH="/workspace/aws-bootcamp-cruddur-2023/ddb/config.toml"

sam validate -t $TEMPLATE_PATH

echo "== build"
# https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-build.html
# --use-container
# use container is for building the lambda in a container
# it's still using the runtimes and its not a custom runtime
sam build \
--use-container \
--config-file $CONFIG_PATH \
--template $TEMPLATE_PATH \
--base-dir $FUNC_DIR
#--parameter-overrides
```
### SAM Package Script 

- Create a **package** script file then add the following
```bash
#! /usr/bin/env bash
set -e # stop the execution of the script if it fails

ARTIFACT_BUCKET="cfn-artifacts-awsbc.flyingresnova.com"
TEMPLATE_PATH="/workspace/aws-bootcamp-cruddur-2023/.aws-sam/build/template.yaml"
OUTPUT_TEMPLATE_PATH="/workspace/aws-bootcamp-cruddur-2023/.aws-sam/build/packaged.yaml"
CONFIG_PATH="/workspace/aws-bootcamp-cruddur-2023/ddb/config.toml"

echo "== package"
# https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-package.html
sam package \
  --s3-bucket $ARTIFACT_BUCKET \
  --config-file $CONFIG_PATH \
  --output-template-file $OUTPUT_TEMPLATE_PATH \
  --template-file $TEMPLATE_PATH \
  --s3-prefix "ddb"
```

### SAM Deploy Script 

- Create a **deploy** script file then add the following
```bash
#! /usr/bin/env bash
set -e # stop the execution of the script if it fails

PACKAGED_TEMPLATE_PATH="/workspace/aws-bootcamp-cruddur-2023/.aws-sam/build/packaged.yaml"
CONFIG_PATH="/workspace/aws-bootcamp-cruddur-2023/aws/cfn/ddb/config.toml"

echo "== deploy"
# https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-deploy.html
sam deploy \
  --template-file $PACKAGED_TEMPLATE_PATH  \
  --config-file $CONFIG_PATH \
  --stack-name "CrdDdb" \
  --tags group=cruddur-ddb \
  --no-execute-changeset \
  --capabilities "CAPABILITY_NAMED_IAM"
```

### Run SAM Scripts

- Run the build script to place all build artifacts in .aws-sam for subsquent steps in the workflow
- Run the package script to package the SAM application by creating a zip file of the code
- Run the deploy script to deploy the SAM application using CloudFormation 

---
---

## 2.1 CICD Template

- Before we create the termplate, we need to create a new **artifacts bucket**
- Run the following to create the new bucket
`aws s3api create-bucket --bucket <ArtifactsBucketName> --region us-east-1`
- Create a new dir: `aws/cfn/cicd` as a base direcotry 
- Create a template.yaml file inside `aws/cfn/cicd`

### Description

- Add the following template description 
```yml
AWSTemplateFormatVersion: 2010-09-09
Description: |
  - CodeStar Connection V2 Github
  - CodePipeline
  - Codebuild
```

### Parameters

- Add the following Parameters to be referenced while creating resources
```yml
Parameters:
  GitHubBranch:
    Type: String
    Default: prod
  GithubRepo:
    Type: String
    Default: 'astroveny/aws-bootcamp-cruddur-2023'
  ClusterStack:
    Type: String
  ServiceStack:
    Type: String
  ArtifactBucketName:
    Type: String
```

### Resources

#### CodeBuild Bake Image Stack

- Add the following to create a CodeBuild Bake Image Stack
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stack.html
```yml
CodeBuildBakeImageStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: nested/codebuild.yaml
```

#### CodeStar Connection

- Add the following to create a CodeStar Connection
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarconnections-connection.html
```yml
CodeStarConnection:
    Type: AWS::CodeStarConnections::Connection
    Properties:
      ConnectionName: !Sub ${AWS::StackName}-connection
      ProviderType: GitHub
```

#### Pipeline

- Add the following to create a Pipeline
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html
>> Ref. https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference-ECS.html

```yml
Pipeline:
    Type: AWS::CodePipeline::Pipeline
    Properties:
      ArtifactStore:
        Location: !Ref ArtifactBucketName
        Type: S3
      RoleArn: !GetAtt CodePipelineRole.Arn
      Stages:
        - Name: Source
          Actions:
            - Name: ApplicationSource
              RunOrder: 1
              ActionTypeId:
                Category: Source
                Provider: CodeStarSourceConnection
                Owner: AWS
                Version: '1'
              OutputArtifacts:
                - Name: Source
              Configuration:
                ConnectionArn: !Ref CodeStarConnection
                FullRepositoryId: !Ref GithubRepo
                BranchName: !Ref GitHubBranch
                #OutputArtifactFormat: "CODE_ZIP"
        - Name: Build
            Actions:
              - Name: BuildContainerImage
                RunOrder: 1
                ActionTypeId:
                  Category: Build
                  Owner: AWS
                  Provider: CodeBuild
                  Version: '1'
                InputArtifacts:
                  - Name: Source
                OutputArtifacts:
                  - Name: ImageDefinitions
                Configuration:
                  ProjectName: !GetAtt CodeBuildBakeImageStack.Outputs.CodeBuildProjectName
                  BatchEnabled: false
        - Name: Deploy
          Actions:
            - Name: Deploy
              RunOrder: 1
              ActionTypeId:
                Category: Deploy
                Provider: ECS
                Owner: AWS
                Version: '1'
              InputArtifacts:
                - Name: ImageDefinitions
              Configuration:
                # In Minutes
                DeploymentTimeout: "10"
                ClusterName:
                  Fn::ImportValue:
                    !Sub ${ClusterStack}ClusterName
                ServiceName:
                  Fn::ImportValue:
                    !Sub ${ServiceStack}ServiceName
```

#### CodePipeline Role

- Add the following to create a CodePipeline Role
```yml
CodePipelineRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Statement:
        - Action: ['sts:AssumeRole']
          Effect: Allow
          Principal:
            Service: [codepipeline.amazonaws.com]
        Version: '2012-10-17'
      Path: /
      Policies:
        - PolicyName: !Sub ${AWS::StackName}EcsDeployPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Action:
                - ecs:DescribeServices
                - ecs:DescribeTaskDefinition
                - ecs:DescribeTasks
                - ecs:ListTasks
                - ecs:RegisterTaskDefinition
                - ecs:UpdateService
                Effect: Allow
                Resource: "*"
        - PolicyName: !Sub ${AWS::StackName}CodeStarPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Action:
                - codestar-connections:UseConnection
                Effect: Allow
                Resource:
                  !Ref CodeStarConnection
        - PolicyName: !Sub ${AWS::StackName}CodePipelinePolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Action:
                - s3:*
                - logs:CreateLogGroup
                - logs:CreateLogStream
                - logs:PutLogEvents
                - cloudformation:*
                - iam:PassRole
                - iam:CreateRole
                - iam:DetachRolePolicy
                - iam:DeleteRolePolicy
                - iam:PutRolePolicy
                - iam:DeleteRole
                - iam:AttachRolePolicy
                - iam:GetRole
                - iam:PassRole
                Effect: Allow
                Resource: '*'
        - PolicyName: !Sub ${AWS::StackName}CodePipelineBuildPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Action:
                - codebuild:StartBuild
                - codebuild:StopBuild
                - codebuild:RetryBuild
                - codebuild:BatchGetBuilds
                - codebuild:UpdateProject
                - codebuild:CreateProject
                Effect: Allow
                Resource: !Join
                  - ''
                  - - 'arn:aws:codebuild:'
                    - !Ref AWS::Region
                    - ':'
                    - !Ref AWS::AccountId
                    - ':project/'
                    - !GetAtt CodeBuildBakeImageStack.Outputs.CodeBuildProjectName
```


---

## 2.2 CodeBuild Template

- Create a new dir: `aws/cfn/cicd/nested`
- Create a codebuild.yaml file inside `aws/cfn/cicd/nested` 

### Description

- Add the following template description 
```yml
Description: |
  Codebuild used for baking container images
  - Codebuild Project
  - Codebuild Project Role
```

### Parameters

- Add the following Parameters to be referenced while creating resources
```yml
Parameters:
  LogGroupPath:
    Type: String
    Description: "The log group path for CodeBuild"
    Default: "/cruddur/codebuild/bake-service"
  LogStreamName:
    Type: String
    Description: "The log group path for CodeBuild"
    Default: "backend-flask"
  CodeBuildImage:
    Type: String
    Default: aws/codebuild/amazonlinux2-x86_64-standard:4.0
  CodeBuildComputeType:
    Type: String
    Default: BUILD_GENERAL1_SMALL
  CodeBuildTimeoutMins:
    Type: Number
    Default: 5
  BuildSpec:
    Type: String
    Default: 'buildspec.yaml'
  Default: "backend-flask/buildspec.yml"
  ArtifactBucketName: 
    Type: String
    Default: codepipeline-artifacts-awsbc.flyingresnova.com  
  GitHubBranch:
    Type: String
    Default: prod 
  GithubRepo:
    Type: String
    Default: 'https://github.com/astroveny/aws-bootcamp-cruddur-2023.git'
```

### Resources

#### CodeBuild

- Add the following to create a CodeBuild
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html
```yml
CodeBuild:
    Type: AWS::CodeBuild::Project
    Properties:
      QueuedTimeoutInMinutes: !Ref CodeBuildTimeoutMins
      ServiceRole: !GetAtt CodeBuildRole.Arn
      # PrivilegedMode is needed to build Docker images
      # even though we have No Artifacts, CodePipeline Demands both to be set as CODEPIPLINE
      Artifacts:
        Type: NO_ARTIFACTS
      Environment:
        ComputeType: !Ref CodeBuildComputeType
        Image: !Ref CodeBuildImage
        Type: LINUX_CONTAINER
        PrivilegedMode: true
      TimeoutInMinutes: 20
      LogsConfig:
        CloudWatchLogs:
          GroupName: !Ref LogGroupPath
          Status: ENABLED
          StreamName: !Ref LogStreamName
      Source:
        Type: GITHUB
        Location: !Ref GithubRepo
        GitCloneDepth: 1
        ReportBuildStatus: true
        BuildSpec: !Ref BuildSpec
        Auth:
          Type: OAUTH
      Triggers:
        BuildType: BUILD
        Webhook: true
        FilterGroups:
          - - Type: EVENT
              Pattern: PULL_REQUEST_MERGED
      SourceVersion: !Ref GitHubBranch
```

#### CodeBuild Role

- Add the following to create a CodeBuild Role
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html
```yml
CodeBuildRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Statement:
        - Action: ['sts:AssumeRole']
          Effect: Allow
          Principal:
            Service: [codebuild.amazonaws.com]
        Version: '2012-10-17'
      Path: /
      Policies:
        - PolicyName: !Sub ${AWS::StackName}ECRPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Action:
                - ecr:BatchCheckLayerAvailability
                - ecr:CompleteLayerUpload
                - ecr:GetAuthorizationToken
                - ecr:InitiateLayerUpload
                - ecr:BatchGetImage
                - ecr:GetDownloadUrlForLayer
                - ecr:PutImage
                - ecr:UploadLayerPart
                Effect: Allow
                Resource: "*"
        - PolicyName: !Sub ${AWS::StackName}VPCPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Action:
                - ec2:CreateNetworkInterface
                - ec2:DescribeDhcpOptions
                - ec2:DescribeNetworkInterfaces
                - ec2:DeleteNetworkInterface
                - ec2:DescribeSubnets
                - ec2:DescribeSecurityGroups
                - ec2:DescribeVpcs
                Effect: Allow
                Resource: "*"
              - Action:
                - ec2:CreateNetworkInterfacePermission
                Effect: Allow
                Resource: "*"
        - PolicyName: !Sub ${AWS::StackName}Logs
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Action:
                - logs:CreateLogGroup
                - logs:CreateLogStream
                - logs:PutLogEvents
                Effect: Allow
                Resource:
                  - !Sub arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:${LogGroupPath}*
                  - !Sub arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:${LogGroupPath}:*
                  
        - PolicyName: !Sub ${AWS::StackName}S3Policy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Action:
                  - s3:GetObject
                  - s3:ListBucket
                  - s3:DeleteObject
                  - s3:PutObject
                Effect: Allow
                #Resource: !Sub "arn:aws:s3:::${ArtifactBucketName}/*"
                Resource: "arn:aws:s3:::codepipeline-artifacts-awsbc.flyingresnova.com/*"          
              - Action:
                  - s3:ListBucket
                Effect: Allow
                #Resource: !Sub "arn:aws:s3:::${ArtifactBucketName}"
                Resource: "arn:aws:s3:::codepipeline-artifacts-awsbc.flyingresnova.com"
```

### Outputs

- Add the following to generate the outputs
```yml
Outputs:
  CodeBuildProjectName:
    Description: "CodeBuildProjectName"
    Value: !Ref CodeBuild
```



---

## 2.3 CICD Deployment

### Config.toml

- Create config.toml file inside dir: `aws/cfn/cicd` then add the following
```
[deploy]
bucket = 'YourCfnArtifactsBucket'
region = 'us-east-1'
stack_name = 'CrdCicd'

[parameters]
ServiceStack = 'CrdSrvBackendFlask'
ClusterStack = 'CrdCluster'
GitHubBranch = 'prod'
GithubRepo = 'astroveny/aws-bootcamp-cruddur-2023'
ArtifactBucketName = "codepipeline-cruddur-artifacts"
```

### CICD Deployment Script

- Create cicd-deploy script file inside dir: `bin/cfn/` then add the following
```bash
#! /usr/bin/env bash
#set -e # stop the execution of the script if it fails

CFN_PATH="/workspace/aws-bootcamp-cruddur-2023/aws/cfn/cicd/template.yaml"
CONFIG_PATH="/workspace/aws-bootcamp-cruddur-2023/aws/cfn/cicd/config.toml"
PACKAGED_PATH="/workspace/aws-bootcamp-cruddur-2023/tmp/packaged-template.yaml"
PARAMETERS=$(cfn-toml params v2 -t $CONFIG_PATH)
echo $CFN_PATH

cfn-lint $CFN_PATH

BUCKET=$(cfn-toml key deploy.bucket -t $CONFIG_PATH)
REGION=$(cfn-toml key deploy.region -t $CONFIG_PATH)
STACK_NAME=$(cfn-toml key deploy.stack_name -t $CONFIG_PATH)

# package
# -----------------
echo ">>>> packaging CFN to S3 <<<<"
aws cloudformation package \
  --template-file $CFN_PATH \
  --s3-bucket $BUCKET \
  --s3-prefix cicd-package \
  --region $REGION \
  --output-template-file "$PACKAGED_PATH"

aws cloudformation deploy \
  --stack-name $STACK_NAME \
  --s3-bucket $BUCKET \
  --s3-prefix cicd \
  --region $REGION \
  --template-file "$PACKAGED_PATH" \
  --no-execute-changeset \
  --tags group=cruddur-cicd \
  --parameter-overrides $PARAMETERS \
  --capabilities CAPABILITY_NAMED_IAM
```
- Run the cicid-deploy script to create the stack
- Go to **AWS CloudFormation** console then select **CrdCicd**
- Click on **Change sets** then **Execute change sets**
- Once the stack is completed, Go to **AWS CodePipeline**
- The pipeline will fail due to the missing connection to Github repo
- Click on **Connections** under **Settings** on the left-side menu 
- Select **CrdCicd-connection** then click on ** Update pending connection**
- From the pop-up window, select the Github Repo you have registered before
