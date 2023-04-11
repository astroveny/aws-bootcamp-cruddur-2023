# Week 8 

## Serverless Image Processing


## CDK Setup

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