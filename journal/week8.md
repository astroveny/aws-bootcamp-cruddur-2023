# Week 8 

## Serverless Image Processing


## CDK Setup
[Back to Top](#Week-8)

We will Install AWS CDK CLI then initialize CDK using type script as the used lanuage. Then we will update the stack file with the required resources and Env variables to creat a CloudFormation stack that will build the Image Processing Serverless solution.


### CDK Initialization
[Back to Top](#Week-8)

- Create a new dir: `thumbing-serverless-cdk` in the TLD 
- Install AWS CDK CLI: cd to the dir: then run `npm install aws-cdk -g`
- Add the CDK CLI install to gitpod task
```yml
  - name: cdk
    before: |
      npm install aws-cdk -g
  ```    
- Iitialize a new cdk project inside the new dir:
`cdk init app --language typescript`   


### Bootstrapping
[Back to Top](#Week-8)

Bootstrapping is the process of provisioning resources required by AWS CDK before you can deploy the app into AWS environment. Those recourses are S3 bucket to store files & IAM roles to grant required permissions to perform deployments. This has to be done per account per region 

- Run the following command to start bootstap  
`cdk bootstrap "aws://$AWS_ACCOUNT_ID/$AWS_DEFAULT_REGION"`
- This will create a CloudFormation stack "CDKToolkit"

### CDK Build and Deploy v1
[Back to Top](#Week-8)

- Run the following to build the stack based on the stack file we updated previously   
` npm run build` 
- Run the follwoing to synthesize the CloudFormation stack  
`cdk synth`
- Deploy the stack by running the following  
` cdk deploy`

### Load The Env Vars
[Back to Top](#Week-8)

We will add the Env variables to be used with each service function. 

- Add the following to the stack file
```ts
const dotenv = require('dotenv');
dotenv.config();

const bucketName: string = process.env.THUMBING_BUCKET_NAME as string;
const folderInput: string = process.env.THUMBING_S3_FOLDER_INPUT as string;
const folderOutput: string = process.env.THUMBING_S3_FOLDER_OUTPUT as string;
const webhookUrl: string = process.env.THUMBING_WEBHOOK_URL as string;
const topicName: string = process.env.THUMBING_TOPIC_NAME as string;
const functionPath: string = process.env.THUMBING_FUNCTION_PATH as string;
console.log('bucketName',bucketName)
console.log('folderInput',folderInput)
console.log('folderOutput',folderOutput)
console.log('webhookUrl',webhookUrl)
console.log('topicName',topicName)
console.log('functionPath',functionPath)
```
- Create new Env file `thumbing-serverless-cdk/.env.example` then add the following
```bash
THUMBING_BUCKET_NAME="assets.YourDomainName.com"
THUMBING_S3_FOLDER_INPUT="avatars/original/"
THUMBING_S3_FOLDER_OUTPUT="avatars/processed/"
THUMBING_WEBHOOK_URL="https://api.YourDomainName.com/webhooks/avatar"
THUMBING_TOPIC_NAME="cruddur-webhook-avatar"
THUMBING_FUNCTION_PATH="/workspace/aws-bootcamp-cruddur-2023/aws/lambdas/process-images/"
```
- Install using the following   
`npm i dotenv`
- Go to TLD dir: aws then create dir: `process-images`

### Add S3 Bucket function
[Back to Top](#Week-8)

We will start adding the requird resources by adding an S3 bucket that will be used to upload and store the processed images/Avatar

- Define an S3 bucket by updating **thumbing-serverless-cdk-stack.ts** inside dir: lib 
- Add the S3 Bucket function using the following code
```ts
const bucket = this.createBucket(bucketName)

createBucket(bucketName: string): s3.IBucket {
  const logicalName: string = 'ThumbingBucket';
  const bucket = new s3.Bucket(this, logicalName , {
    bucketName: bucketName,
    removalPolicy: cdk.RemovalPolicy.DESTROY,
  });
  return bucket;
}
```

### Create Lambda Function
[Back to Top](#Week-8)

We will create a Lambda function to process the images inside the S3 bucket 

- Add the following code to the stack file to create a lambda function 
```ts
import * as lambda from 'aws-cdk-lib/aws-lambda';

const lambda = this.createLambda(folderInput,folderOutput,functionPath,bucketName)

createLambda(folderIntput: string, folderOutput: string, functionPath: string, bucketName: string): lambda.IFunction {
  const logicalName = 'ThumbLambda';
  const code = lambda.Code.fromAsset(functionPath)
  const lambdaFunction = new lambda.Function(this, logicalName, {
    runtime: lambda.Runtime.NODEJS_18_X,
    handler: 'index.handler',
    code: code,
    environment: {
      DEST_BUCKET_NAME: bucketName,
      FOLDER_INPUT: folderIntput,
      FOLDER_OUTPUT: folderOutput,
      PROCESS_WIDTH: '512',
      PROCESS_HEIGHT: '512'
    }
  });
  return lambdaFunction;
}
```
## Lambda Processing Images


### Create index.js
[Back to Top](#Week-8)

- Go to dir: aws/lambda/process-images
- Create file `index.js` then enter the following
```js
const process = require('process');
const {getClient, getOriginalImage, processImage, uploadProcessedImage} = require('./s3-image-processing.js')
const path = require('path');

const bucketName = process.env.DEST_BUCKET_NAME
const folderInput = process.env.FOLDER_INPUT
const folderOutput = process.env.FOLDER_OUTPUT
const width = parseInt(process.env.PROCESS_WIDTH)
const height = parseInt(process.env.PROCESS_HEIGHT)

client = getClient();

exports.handler = async (event) => {
  const srcBucket = event.Records[0].s3.bucket.name;
  const srcKey = decodeURIComponent(event.Records[0].s3.object.key.replace(/\+/g, ' '));
  console.log('srcBucket',srcBucket)
  console.log('srcKey',srcKey)

  const dstBucket = bucketName;

  filename = path.parse(srcKey).name
  const dstKey = `${folderOutput}/${filename}.jpg`
  console.log('dstBucket',dstBucket)
  console.log('dstKey',dstKey)

  const originalImage = await getOriginalImage(client,srcBucket,srcKey)
  const processedImage = await processImage(originalImage,width,height)
  await uploadProcessedImage(client,dstBucket,dstKey,processedImage)
};
```
### Create test.js
[Back to Top](#Week-8)

- This test code will have hardcoded values for testing 
- Create file `test.js` then enter the following
```js
const {getClient, getOriginalImage, processImage, uploadProcessedImage} = require('./s3-image-processing.js')

async function main(){
  client = getClient()
  const srcBucket = 'cruddur-thumbs'
  const srcKey = 'avatar/original/data.jpg'
  const dstBucket = 'cruddur-thumbs'
  const dstKey = 'avatar/processed/data.png'
  const width = 256
  const height = 256

  const originalImage = await getOriginalImage(client,srcBucket,srcKey)
  console.log(originalImage)
  const processedImage = await processImage(originalImage,width,height)
  await uploadProcessedImage(client,dstBucket,dstKey,processedImage)
}

main()
```

### Create s3-image-processing.js 
[Back to Top](#Week-8)

- Create file `s3-image-processing.js` then enter the following
```js
const sharp = require('sharp');
const { S3Client, PutObjectCommand, GetObjectCommand } = require("@aws-sdk/client-s3");

function getClient(){
  const client = new S3Client();
  return client;
}

async function getOriginalImage(client,srcBucket,srcKey){
  console.log('get==')
  const params = {
    Bucket: srcBucket,
    Key: srcKey
  };
  console.log('params',params)
  const command = new GetObjectCommand(params);
  const response = await client.send(command);

  const chunks = [];
  for await (const chunk of response.Body) {
    chunks.push(chunk);
  }
  const buffer = Buffer.concat(chunks);
  return buffer;
}

async function processImage(image,width,height){
  const processedImage = await sharp(image)
    .resize(width, height)
    .jpeg()
    .toBuffer();
  return processedImage;
}

async function uploadProcessedImage(client,dstBucket,dstKey,image){
  console.log('upload==')
  const params = {
    Bucket: dstBucket,
    Key: dstKey,
    Body: image,
    ContentType: 'image/jpeg'
  };
  console.log('params',params)
  const command = new PutObjectCommand(params);
  const response = await client.send(command);
  console.log('repsonse',response);
  return response;
}

module.exports = {
  getClient: getClient,
  getOriginalImage: getOriginalImage,
  processImage: processImage,
  uploadProcessedImage: uploadProcessedImage
}
```
### Create example.json
[Back to Top](#Week-8)

- Create json file `example.json with the following
```json
{
  "Records": [
    {
      "eventVersion": "2.0",
      "eventSource": "aws:s3",
      "awsRegion": "ca-central-1",
      "eventTime": "1970-01-01T00:00:00.000Z",
      "eventName": "ObjectCreated:Put",
      "userIdentity": {
        "principalId": "EXAMPLE"
      },
      "requestParameters": {
        "sourceIPAddress": "127.0.0.1"
      },
      "responseElements": {
        "x-amz-request-id": "EXAMPLE123456789",
        "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "testConfigRule",
        "bucket": {
          "name": "assets.cruddur.com",
          "ownerIdentity": {
            "principalId": "EXAMPLE"
          },
          "arn": "arn:aws:s3:::assets.cruddur.com"
        },
        "object": {
          "key": "avatars/original/data.jpg",
          "size": 1024,
          "eTag": "0123456789abcdef0123456789abcdef",
          "sequencer": "0A1B2C3D4E5F678901"
        }
      }
    }
  ]
}
```
### Create Init file
[Back to Top](#Week-8)

- Run the following inside dir: process-images to create init package.json  
` npm init -y`

### Install Sharp JS

- Install "sharp"  using the following command    
`npm i sharp`
- This will create dir: node_modules 

### Install AWS SDK S3 client

- Run the following command to installt he AWS SDK S3 client   
`npm i @aws-sdk/client-s3`

### Deploy Lambda 
[Back to Top](#Week-8)

- Go to the CDK dir: thumbing-serverless-cdk
- run the following to synthesize the stack 
`cdk synth`
- run the following to deploy the stack then andyer "y" to deploy the changes
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023/thumbing-serverless-cdk (main) $ cdk deploy
bucketName cruddur-thumbs
folderInput avatar/original/
folderOutput avatar/processed/
webhookUrl https://api.awsbc.flyingresnova.com/webhooks/avatar
topicName cruddur-webhook-avatar
functionPath /workspace/aws-bootcamp-cruddur-2023/aws/lambdas/process-images/

✨  Synthesis time: 5s

ThumbingServerlessCdkStack: building assets...

[0%] start: Building 8a45b127810ec03277632694d64bfdbb6b24a5872307dc333c0555bdb72d:current_account-current_region
[0%] start: Building 738f4b12e1b6e16969f08f1e7ac69e943db292e58fe785e2e6046ab6021b:current_account-current_region
[50%] success: Built 8a45b127810ec03277632694d64bfdbb6b24a5872307dc333c0555bdb72d:current_account-current_region
[100%] success: Built 738f4b12e1b6e16969f08f1e7ac69e943db292e58fe785e2e6046ab6021b:current_account-current_region

ThumbingServerlessCdkStack: assets built

This deployment will make potentially sensitive changes according to your current security approval level (--require-approval broadening).
Please confirm you intend to make the following modifications:

IAM Statement Changes
┌───┬────────────────────────────────┬────────┬────────────────┬──────────────────────────────┬───────────┐
│   │ Resource                       │ Effect │ Action         │ Principal                    │ Condition │
├───┼────────────────────────────────┼────────┼────────────────┼──────────────────────────────┼───────────���
│ + │ ${ThumbLambda/ServiceRole.Arn} │ Allow  │ sts:AssumeRole │ Service:lambda.amazonaws.com │           │
└───┴────────────────────────────────┴────────┴────────────────┴──────────────────────────────┴───────────┘
IAM Policy Changes
┌───┬────────────────────────────┬────────────────────────────────────────────────────────────────────────────────┐
│   │ Resource                   │ Managed Policy ARN                                                             │
├───┼────────────────────────────┼────────────────────────────────────────────────────────────────────────────────┤
│ + │ ${ThumbLambda/ServiceRole} │ arn:${AWS::Partition}:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole │
└───┴────────────────────────────┴────────────────────────────────────────────────────────────────────────────────┘
(NOTE: There may be security-related changes not in this list. See https://github.com/aws/aws-cdk/issues/1299)

Do you wish to deploy these changes (y/n)? y
ThumbingServerlessCdkStack: deploying... [1/1]
[0%] start: Publishing 8a45b127810ec03277632694d64bfdbb6b24a5872307dc333c0555bdb72d:current_account-current_region
[0%] start: Publishing 738f4b12e1b6e16969f08f1e7ac69e943db292e58fe785e2e6046ab6021b:current_account-current_region
[50%] success: Published 738f4b12e1b6e16969f08f1e7ac69e943db292e58fe785e2e6046ab6021b:current_account-current_region
[100%] success: Published 8a45b127810ec03277632694d64bfdbb6b24a5872307dc333c0555bdb72d:current_account-current_region
ThumbingServerlessCdkStack: creating CloudFormation changeset...

 ✅  ThumbingServerlessCdkStack

✨  Deployment time: 48.33s

Stack ARN:
arn:aws:cloudformation:us-east-1:235696014680:stack/ThumbingServerlessCdkStack/8dd4af60-xxxx-xxxx-xxxx-0acbf22c9d87

✨  Total time: 53.33s
```
 

## S3 Event Notification

### Create S3 Event Notification to Lambda

- Go to the lib dir inside CDK dir: thumbing-serverless-cdk 
- Update the stack file to add S3 event notification function 
```ts
this.createS3NotifyToLambda(folderInput,laombda,bucket)

createS3NotifyToLambda(prefix: string, lambda: lambda.IFunction, bucket: s3.IBucket): void {
  const destination = new s3n.LambdaDestination(lambda);
    bucket.addEventNotification(s3.EventType.OBJECT_CREATED_PUT,
    destination,
    {prefix: prefix}
  )
}
```

>> NOTE: due to a wrong bucket name Env vars assigned in the shell previously, we have created the wrong bucket name, so we will destroy the stack, change the stack file to import the bucket manually then re-deploy the stack 


### Update Stack File to Import Bucket Name

- Edit `lib/thumbing-serverless-cdk-stack.ts `
- Remove the the creat bucket function 
- Add the following code to import the existing bucket name (from .env)
```ts
const bucket = this.importBucket(bucketName)

//import bucket
    importBucket(bucketName: string): s3.IBucket {
      const bucket = s3.Bucket.fromBucketName(this,"AssetsBucket",bucketName);
       return bucket; 
    }
```

### Create Bucket Policy

- Add the following function to create a bucket policy
```ts
import * as iam from 'aws-cdk-lib/aws-iam';


const s3ReadWritePolicy = this.createPolicyBucketAccess(bucket.bucketArn)
lambda.addToRolePolicy(s3ReadWritePolicy);


createPolicyBucketAccess(bucketArn: string){
    const s3ReadWritePolicy = new iam.PolicyStatement({
      actions: [
        's3:GetObject',
        's3:PutObject',
      ],
      resources: [
        `${bucketArn}/*`,
      ]
    });
    return s3ReadWritePolicy;
  }
```

- Run `cdk deploy`


## S3 Event Notification to SNS

### Create SNS Topic

- Edit `lib/thumbing-serverless-cdk-stack.ts `
- Add the following code to create SNS topic
```ts
import * as sns from 'aws-cdk-lib/aws-sns';

const snsTopic = this.createSnsTopic(topicName)

createSnsTopic(topicName: string): sns.ITopic{
  const logicalName = "Topic";
  const snsTopic = new sns.Topic(this, logicalName, {
    topicName: topicName
  });
  return snsTopic;
}
```

### Create an SNS Subscription

- Add the following code to create SNS Subscription.
```ts
import * as subscriptions from 'aws-cdk-lib/aws-sns-subscriptions';


this.createSnsSubscription(snsTopic,webhookUrl)

createSnsSubscription(snsTopic: sns.ITopic, webhookUrl: string): sns.Subscription {
  const snsSubscription = snsTopic.addSubscription(
    new subscriptions.UrlSubscription(webhookUrl)
  )
  return snsSubscription;
}
```

### Create S3 Event Notification to SNS

- Add the following code to create S3 notification to SNS
```ts
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';

this.createS3NotifyToSns(folderOutput,snsTopic,bucket)

createS3NotifyToSns(prefix: string, snsTopic: sns.ITopic, bucket: s3.IBucket): void {
  const destination = new s3n.SnsDestination(snsTopic)
  bucket.addEventNotification(
    s3.EventType.OBJECT_CREATED_PUT, 
    destination,
    {prefix: prefix}
  );
}
```

### Create Policy

- Add the following code to create SNS policy
```ts
const snsPublishPolicy = this.createPolicySnSPublish(snsTopic.topicArn)

lambda.addToRolePolicy(snsPublishPolicy);

createPolicySnSPublish(topicArn: string){
    const snsPublishPolicy = new iam.PolicyStatement({
      actions: [
        'sns:Publish',
      ],
      resources: [
        topicArn
      ]
    });
    return snsPublishPolicy;
  }
```


## Avatar Utility Scripts

### Avatar Build

- Go to TLD then bin
- Create dir: avatar then create build file inside avatar then add the following
```bash
#! /usr/bin/bash

ABS_PATH=$(readlink -f "$0")
SERVERLESS_PATH=$(dirname $ABS_PATH)
BIN_PATH=$(dirname $SERVERLESS_PATH)
PROJECT_PATH=$(dirname $BIN_PATH)
SERVERLESS_PROJECT_PATH="$PROJECT_PATH/thumbing-serverless-cdk"

cd $SERVERLESS_PROJECT_PATH

npm install
rm -rf node_modules/sharp
SHARP_IGNORE_GLOBAL_LIBVIPS=1 npm install --arch=x64 --platform=linux --libc=glibc sharp
```
- Make build file executable then run it


### Avatar Clear

- This script will remove the data file from the bucket
- Create a clear script using the following code
```bash
#! /usr/bin/bash

ABS_PATH=$(readlink -f "$0")
SERVERLESS_PATH=$(dirname $ABS_PATH)
DATA_FILE_PATH="$SERVERLESS_PATH/files/data.jpg"

aws s3 rm "s3://assets.$DOMAIN_NAME/avatars/original/data.jpg"
aws s3 rm "s3://assets.$DOMAIN_NAME/avatars/processed/data.jpg"
```

### Avata Upload

- This script will upload the data file to the bucket
- Create upload script using the following code
```bash
#! /usr/bin/bash

ABS_PATH=$(readlink -f "$0")
SERVERLESS_PATH=$(dirname $ABS_PATH)
DATA_FILE_PATH="$SERVERLESS_PATH/files/data.jpg"

aws s3 cp "$DATA_FILE_PATH" "s3://assets.$DOMAIN_NAME/avatars/data.jpg"
```
---
---

## Cloudfront CDN Setup

We will use CDN to store the files to avoid downloading the files every time 

### Create CloudFront Distribution 

- Go to AWS CloudFront console then click on Create a distribution 
- In the **Origin** section, browse the S3 bucket as the **Origin domain**
- Select "Origin access control settings (recommended)" as the **Origin access**
- Click **Create control setting**, keep the S3 bucket then click **Create** 
- In the next section **Default cache behavior** select **Yes** to "Compress objects automatically"
- Select **Redirect HTTP to HTTPS** under **Viewer protocol policy**
- Under **Cache key and origin requests** select **Cache policy and origin request policy (recommended)**
- Select **CachingOptimized** as **Cache policy**
- Select **CORS-S3Orign** as **Origin request policy - optional**
- Select **SimpleCORS** as **Response headers policy - optional**
- In the **Settings** section, enter assets.YourDomainNAme as **Alternate domain name (CNAME) - optional**
- Select the ACM certificate created previously as **Custom SSL certificate - optional**
- Enter **Serve Assets for Cruddur** in the **Description** field 

  
### Add S3 Bucket Policy

- Add the following policy to the bucket policy 
```json
{
        "Version": "2008-10-17",
        "Id": "PolicyForCloudFrontPrivateContent",
        "Statement": [
            {
                "Sid": "AllowCloudFrontServicePrincipal",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudfront.amazonaws.com"
                },
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::ARN/*",
                "Condition": {
                    "StringEquals": {
                      "AWS:SourceArn": "arn:aws:cloudfront_ARN"
                    }
                }
            }
        ]
      }
```
  
### Create Hosted Zone Record

- Go to AWS Route 53 console
- Click on the hosted zones then select your domain name
- Click on **Create record**
- Enter **assets** as the **Record name**
- Select **A record** as the **Record type**
- Enable **Alias**
- Select **Alias CloudFront distribution**
- Browse to select the distribution URL
- Click **Create records**
- Test access to the **assets** URL using the browser 

---

## Add S3 Bucket

We will add a new S3 bukcet to the stack to be used as a temporary location to upload the files 

### Update Env Variables

- Edit thumbing-serverless-cdk/.env.cdk
- Add new bucket Env var `UPLOADS_BUCKET_NAME="YourDomainName-cruddur-uploaded-avatars"`
- Replace the exiting bucket variable with `ASSETS_BUCKET_NAME="assets.YourDomainName.com"`
- Run `cp .env.cdk .env`

### Add Upload Bucket to The Stack

- Edit `thumbing-serverless-cdk/lib/thumbing-serverless-cdk-stack.ts`
- Add the following code
```ts
    const uploadsBucketName: string = process.env.UPLOADS_BUCKET_NAME as string;

    console.log('uploadsBucketName',) 

    const uploadsBucket = this.createBucket(uploadsBucketName);

    // create policies
    const s3UploadsReadWritePolicy = this.createPolicyBucketAccess(uploadsBucket.bucketArn)

    lambda.addToRolePolicy(s3UploadsReadWritePolicy);

```
- Add the function name `uploadsBucketName` to lambda function 


### Update imported bucketName 

- Repalce imported bucketName with assetsBucketName
```ts
    const assetsBucketName: string = process.env.ASSETS_BUCKET_NAME as string;

    console.log('assetsBucketName',assetsBucketName)

    const assetsBucket = this.importBucket(assetsBucketName)

    this.createS3NotifyToLambda(folderInput,lambda,assetsBucket)


    const s3AssetsReadWritePolicy = this.createPolicyBucketAccess(assetsBucket.bucketArn)

    lambda.addToRolePolicy(s3AssetsReadWritePolicy);
    //import bucket
    importBucket(bucketName: string): s3.IBucket {
      const bucket = s3.Bucket.fromBucketName(this,"AssetsBucket",bucketName);
       return bucket; 
    }


```
### Update createLambda()

- Replace the code with the following
```ts
// create lambda
    const lambda = this.createLambda(
      functionPath, 
      uploadsBucketName, 
      assetsBucketName, 
      folderInput, 
      folderOutput
    );


    createLambda(functionPath: string, uploadsBucketName: string, assetsBucketName: string, folderInput: string, folderOutput: string): lambda.IFunction {
const lambdaFunction = new lambda.Function(this, 'ThumbLambda', {
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset(functionPath),
      environment: {
        DEST_BUCKET_NAME: assetsBucketName,
        FOLDER_INPUT: folderInput,
        FOLDER_OUTPUT: folderOutput,
        PROCESS_WIDTH: '512',
        PROCESS_HEIGHT: '512'
      }
    });
    return lambdaFunction;
  }
```
- Run `cdk deploy
