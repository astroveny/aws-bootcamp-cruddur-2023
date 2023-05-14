# Week 11 


## CloudFormation Part 2




## DynamoDB Template


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


## SAM Setup

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
