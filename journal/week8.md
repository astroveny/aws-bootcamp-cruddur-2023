# Week 8 

## Serverless Image Processing


## CDK Setup

We will Install AWS CDK CLI then initialize CDK using type script as the used lanuage. Then we will update the stack file with the required resources and Env variables to creat a CloudFormation stack that will build the Image Processing Serverless solution.


### CDK Initialization
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

### Add S3 Bucket
We will start adding the requird resources by adding an S3 bucket that will be used to upload and store the processed images/Avatar

- Define an S3 bucket by updating **thumbing-serverless-cdk-stack.ts** inside dir: lib with the folloing code
```ts
import * as s3 from 'aws-cdk-lib/aws-s3';

const bucketName: string = process.env.THUMBING_BUCKET_NAME as string;

const bucket = new s3.Bucket(this, 'ThumbingBucket', {
  bucketName: bucketName,
  removalPolicy: cdk.RemovalPolicy.DESTROY,
});
```
- Update Env variables with the following
```bash
export THUMBING_BUCKET_NAME="cruddur-thumbs"
gp env THUMBING_BUCKET_NAME="cruddur-thumbs"
```

### Bootstrapping

Bootstrapping is the process of provisioning resources required by AWS CDK before you can deploy the app into AWS environment. Those recourses are S3 bucket to store files & IAM roles to grant required permissions to perform deployments. This has to be done per account per region 

- Run the following command to start bootstap  
`cdk bootstrap "aws://$AWS_ACCOUNT_ID/$AWS_DEFAULT_REGION"`
- This will create a CloudFormation stack "CDKToolkit"

### CDK Build and Deploy v1

- Run the following to build the stack based on the stack file we updated previously   
` npm run build` 
- Run the follwoing to synthesize the CloudFormation stack  
`cdk synth`
- Deploy the stack by running the following  
` cdk deploy`

### Load The Env Vars

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

### Update S3 Bucket function

- Refactor the S3 Bucket function using the following code
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