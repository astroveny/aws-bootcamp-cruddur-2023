# Week 8 

## Serverless Image Processing - CDK deployment


[1. CDK Setup](#1-CDK-Setup)
  - [CDK Initialization](#CDK-Initialization)
  - [Bootstrapping](#Bootstrapping)
  - [Load The Env Vars](#Load-The-Env-Vars)
  - [Create S3 Uploads Bucket ](#Create-S3-Uploads-Bucket )
  - [Import S3 Assets Bucket](#Import-S3-Assets-Bucket)
  - [CDK Build and Deploy ](#CDK-Build-and-Deploy)

[2. Lambda Processing Images](#2-Lambda-Processing-Images)
  - [Create Lambda Function](#Create-Lambda-Function)
  - [Create index.js](#Create-indexjs)
  - [Create test.js](#Create-testjs)
  - [Create s3-image-processing.js](#Create-s3-image-processingjs)
  - [Create example.json](#Create-examplejson)
  - [Create Init file](#Create-Init-file)
  - [Install Sharp JS](#Install-Sharp-JS)
  - [Install AWS SDK S3 client](#Install-AWS-SDK-S3-client)
  - [Deploy Lambda](#Deploy-Lambda)

[3. Lambda Trigger](#3-Lambda-Trigger)
  - [Create S3 Event Notification to Lambda](#Create-S3-Even-Notification-to-Lambda)
  - [Create Bucket Policy](#Create-Bucket-Policy)

[4. SNS Notification](#4-SNS-Notification)
  - [Create SNS Topic](#Create-SNS-Topic)
  - [Create an SNS Subscription](#Create-an-SNS-Subscription)
  - [Create S3 Event Notification to SNS](#Create-S3-Event-Notification-to-SNS)
  - [Create SNS Policy](#Create-SNS-Policy)

[5. Avatar Utility Scripts](#5-Avatar-Utility-Scripts)
  - [Avatar Build](#Avatar-Build)
  - [Avatar Clear](#Avatar-Clear)
  - [Avatar Upload](#Avatar-Upload)

[6. Cloudfront CDN Setup](#6.-Cloudfront-CDN-Setup)  
  - [Create CloudFront Distribution](#Create-CloudFront-Distribution)
  - [Add S3 Bucket Policy](#Add-S3-Bucket-Policy)
  - [Create Hosted Zone Record](#Create-Hosted-Zone-Record)

---
---

## 1. CDK Setup
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
UPLOADS_BUCKET_NAME="YourDomainName-cruddur-uploaded-avatars"
ASSETS_BUCKET_NAME="assets.YourDomainName.com"
THUMBING_S3_FOLDER_INPUT=""
THUMBING_S3_FOLDER_OUTPUT="avatars"
THUMBING_WEBHOOK_URL="https://api.YourDomainName.com/webhooks/avatar"
THUMBING_TOPIC_NAME="cruddur-assets"
THUMBING_FUNCTION_PATH="/workspace/aws-bootcamp-cruddur-2023/aws/lambdas/process-images/"
```
- Install using the following   
`npm i dotenv`
- Go to TLD dir: aws then create dir: `process-images`

### Create S3 Uploads Bucket 
[Back to Top](#Week-8)

We will start adding the requird resources by adding an S3 bucket that will be used to upload images/Avatar

- Define an S3 bucket by updating **thumbing-serverless-cdk-stack.ts** inside dir: lib 
- Add the S3 Bucket function using the following code
```ts
const uploadsBucketName: string = process.env.UPLOADS_BUCKET_NAME as string;

console.log('uploadsBucketName',) 

const uploadsBucket = this.createBucket(uploadsBucketName);

// Create a bucket
createBucket(bucketName: string): s3.IBucket {
    const bucket = new s3.Bucket(this, 'UploadsBucket' , {
    bucketName: bucketName,
    removalPolicy: cdk.RemovalPolicy.DESTROY,
    });
  return bucket;
}
```

### Import S3 Assets Bucket 

Once images are uploaded to the uploads bucket, the bucket will trigger the lambda function to process the images then store them in the asset bucket.

- Go to AWS S3 console then click on create bucket
- Type the **Bucket name:**  assets.YourDomainName.com
- Chose your **AWS Region** then click on **Create bucket**
- Edit `lib/thumbing-serverless-cdk-stack.ts `
- Add the following code to import the existing bucket name (from .env)
```ts
const assetsBucketName: string = process.env.ASSETS_BUCKET_NAME as string;

console.log('assetsBucketName',assetsBucketName)


const assetsBucket = this.importBucket(assetsBucketName)

//import bucket
    importBucket(bucketName: string): s3.IBucket {
      const bucket = s3.Bucket.fromBucketName(this,"AssetsBucket",bucketName);
       return bucket; 
    }
```

### CDK Build and Deploy 
[Back to Top](#Week-8)

- Use the following to build the stack based on the stack file we updated previously   
` npm run build` 
- Use the follwoing to synthesize the CloudFormation stack  
`cdk synth`
- Deploy the stack by using the following  
` cdk deploy`

---
---

## 2. Lambda Processing Images

### Create Lambda Function
[Back to Top](#Week-8)

We will create a Lambda function to process the images inside the S3 bucket 

- Add the following code to the stack file to create a lambda function 
```ts
import * as lambda from 'aws-cdk-lib/aws-lambda';

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
  const dstKey = `${folderOutput}/${filename}.png`
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
- run the following to deploy the stack then answer "y" to deploy the changes   
`cdk deploy`  

---
---

## 3. Lambda Trigger 

### Create S3 Event Notification to Lambda
[Back to Top](#Week-8)

- Go to the lib dir inside CDK dir: thumbing-serverless-cdk 
- Update the stack file to add S3 event notification function 
```ts
this.createS3NotifyToLambda(folderInput,lambda,uploadsBucket)

createS3NotifyToLambda(prefix: string, lambda: lambda.IFunction, bucket: s3.IBucket): void {
  const destination = new s3n.LambdaDestination(lambda);
    bucket.addEventNotification(s3.EventType.OBJECT_CREATED_PUT,
    destination
    
  )
}
```

### Create Bucket Policy
[Back to Top](#Week-8)

- This bucket policy will allow lambda to perform GetObject & PutObject
- Add the following code to create a bucket policy
```ts
import * as iam from 'aws-cdk-lib/aws-iam';


const s3UploadsReadWritePolicy = this.createPolicyBucketAccess(uploadsBucket.bucketArn)
const s3AssetsReadWritePolicy = this.createPolicyBucketAccess(assetsBucket.bucketArn)

lambda.addToRolePolicy(s3UploadsReadWritePolicy);
lambda.addToRolePolicy(s3AssetsReadWritePolicy);


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

---
---

## 4. SNS Notification 

### Create SNS Topic
[Back to Top](#Week-8)

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
[Back to Top](#Week-8)

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
[Back to Top](#Week-8)

- Add the following code to create S3 notification to SNS
```ts
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';

this.createS3NotifyToSns(folderOutput,snsTopic,assetsBucket)

createS3NotifyToSns(prefix: string, snsTopic: sns.ITopic, bucket: s3.IBucket): void {
  const destination = new s3n.SnsDestination(snsTopic)
  bucket.addEventNotification(
    s3.EventType.OBJECT_CREATED_PUT, 
    destination,
    {prefix: prefix}
  );
}
```

### Create SNS Policy
[Back to Top](#Week-8)

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

- Run `cdk deploy`

---
---

## 5. Avatar Utility Scripts

### Avatar Build
[Back to Top](#Week-8)

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
[Back to Top](#Week-8)

- This script will remove the data file from the bucket
- Create a clear script using the following code
```bash
#! /usr/bin/bash

ABS_PATH=$(readlink -f "$0")
SERVERLESS_PATH=$(dirname $ABS_PATH)
DATA_FILE_PATH="$SERVERLESS_PATH/files/data.jpg"

aws s3 rm "s3://YourDomainName-cruddur-uploaded-avatars/data.png"
aws s3 rm "s3://assets.$DOMAIN_NAME/avatars/data.jpg"
```

### Avatar Upload
[Back to Top](#Week-8)

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

## 6. Cloudfront CDN Setup

We will use CDN to store the files to avoid downloading the files every time 

### Create CloudFront Distribution 
[Back to Top](#Week-8)

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
[Back to Top](#Week-8)

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
[Back to Top](#Week-8)

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
---

## Implement Users Profile Page

### Create User show.sql

- Go to `backend-flask/db/sql/users`
- Create new SWL file **show.sql** then add the following code
```sql
SELECT 
  (SELECT COALESCE(row_to_json(object_row),'{}'::json) FROM (
    SELECT
      users.uuid,
      users.cognito_user_id as cognito_user_uuid,
      users.handle,
      users.display_name,
      (
       SELECT 
        count(true) 
       FROM public.activities
       WHERE
        activities.user_uuid = users.uuid
       ) as cruds_count
  ) object_row) as profile,
  (SELECT COALESCE(array_to_json(array_agg(row_to_json(array_row))),'[]'::json) FROM (
    SELECT
      activities.uuid,
      users.display_name,
      users.handle,
      activities.message,
      activities.created_at,
      activities.expires_at
    FROM public.activities
    WHERE
      activities.user_uuid = users.uuid
    ORDER BY activities.created_at DESC 
    LIMIT 40
  ) array_row) as activities
FROM public.users
WHERE
  users.handle = %(handle)s
```

### Updatde user_activities.py
- Edit `backend-flask/services/user_activities.py`
- Add `from lib.db import db`
- Replace `if user_handle` with the following code
```python
if user_handle == None or len(user_handle) < 1:
      model['errors'] = ['blank_user_handle']
    else:
      print("else:")
      sql = db.template('users','show')
      results = db.query_object_json(sql,{'handle': user_handle})
      model['data'] = results
```

### Update UserFeedPage.js

- Edit `frontend-react-js/src/pages/UserFeedPage.js`
- Add the following code to map activities as expected
- Replace the commented code with the code below it
```js
//import Cookies from 'js-cookie'
import {checkAuth, getAccessToken} from '../lib/CheckAuth';

//Add to export default function UserFeedPage()
  const [profile, setProfile] = React.useState([]);
  const [poppedProfile, setPoppedProfile] = React.useState([]);

//const backend_url = `${process.env.REACT_APP_BACKEND_URL}/api/activities/${title}`
const backend_url = `${process.env.REACT_APP_BACKEND_URL}/api/activities/@${params.handle}`
      await getAccessToken()
      const access_token = localStorage.getItem("access_token")
   //Add to  const res = await fetch  
      headers: {
          Authorization: `Bearer ${access_token}`
        },

 //setActivities(resJson)
 setProfile(resJson.profile)
setActivities(resJson.activities)     

// Remove const checkAuth = async ()
// checkAuth();
checkAuth(setUser);
```

- Test access to the  profile tab using frontend-URL/@handle


### Creat EditProfileButton.js

- create JS file `frontend-react-js/src/components/EditProfileButton.js`
- Add the following code
```js
import './EditProfileButton.css';

export default function EditProfileButton(props) {
  const pop_profile_form = (event) => {
    event.preventDefault();
    props.setPopped(true);
    return false;
  }

  return (
    <button onClick={pop_profile_form} className='profile-edit-button' href="#">Edit Profile</button>
  );
}
```
- Create CSS file `frontend-react-js/src/components/EditProfileButton.css`
- Add the following code
```css
.profile-edit-button {
  border: solid 1px rgba(255,255,255,0.5);
  padding: 12px 20px;
  font-size: 18px;
  background: none;
  border-radius: 999px;
  color: rgba(255,255,255,0.8);
  cursor: pointer;
}

.profile-edit-button:hover {
  background: rgba(255,255,255,0.3)
}
```

### Update Activity Feed

1. Edit `frontend-react-js/src/components/ActivityFeed.js`
  - Replace the ruturn of the **ActivityFeed()** function with the following
    ```js
    <div className='activity_feed_collection'>
          {props.activities.map(activity => {
          return  <ActivityItem setReplyActivity={props.setReplyActivity} setPopped={props.setPopped} key={activity.uuid} activity={activity} />
          })}
    ```
2. Edit `frontend-react-js/src/pages/HomeFeedPage.js`
    - Replace class ActivityFeed with the following
    ```js
    <div className='activity_feed'>
          <div className='activity_feed_heading'>
            <div className='title'>Home</div>
          </div>
          <ActivityFeed 
            setReplyActivity={setReplyActivity} 
            setPopped={setPoppedReply} 
            activities={activities} 
          />
        </div>
    ```
3. Edit `frontend-react-js/src/pages/NotificationsFeedPage.js`
    - Replace class ActivityFeed with the following
    ```js
    <div className='activity_feed'>
          <div className='activity_feed_heading'>
            <div className='title'>Notifications</div>
          </div>
          <ActivityFeed 
            setReplyActivity={setReplyActivity} 
            setPopped={setPoppedReply} 
            activities={activities} 
          />
        </div>
    ``` 


### Create Profile Heading

Create new profile heading section then embedded into UserFeedPage.js


- Create new JS file `frontend-react-js/src/components/ProfileHeading.js`
- Add the following code
```js
import './ProfileHeading.css';
import EditProfileButton from '../components/EditProfileButton';

export default function ProfileHeading(props) {
  const backgroundImage = 'url("https://assets.YourDomainName.com/banners/banner.jpg")';
  const styles = {
    backgroundImage: backgroundImage,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
  };
  return (
  <div className='activity_feed_heading profile_heading'>
    <div className='title'>{props.profile.display_name}</div>
    <div className="cruds_count">{props.profile.cruds_count} Cruds</div>
    <div class="banner" style={styles} >
      <div className="avatar">
        <img src="https://assets.YourDomainName.com/avatars/data.jpg"></img>
      </div>
    </div>
    <div class="info">
      <div class='id'>
        <div className="display_name">{props.profile.display_name}</div>
        <div className="handle">@{props.profile.handle}</div>
      </div>
      <EditProfileButton setPopped={props.setPopped} />
    </div>

  </div>
  );
}
```

- Create new CSS file `frontend-react-js/src/components/ProfileHeading.css`
- Add the following code
```css
.profile_heading {
  padding-bottom: 0px;
}
.profile_heading .avatar {
  position: absolute;
  bottom:-74px;
  left: 16px;
}
.profile_heading .avatar img {
  width: 148px;
  height: 148px;
  border-radius: 999px;
  border: solid 8px var(--fg);
}

.profile_heading .banner {
  position: relative;
  height: 200px;
}

.profile_heading .info {
  display: flex;
  flex-direction: row;
  align-items: start;
  padding: 16px;
}

.profile_heading .info .id {
  padding-top: 70px;
  flex-grow: 1;
}

.profile_heading .info .id .display_name {
  font-size: 24px;
  font-weight: bold;
  color: rgb(255,255,255);
}
.profile_heading .info .id .handle {
  font-size: 16px;
  color: rgba(255,255,255,0.7);
}
```

- Update UserFeedPage.js with the following code
```js
// import ProfileHeading
import ProfileHeading from '../components/ProfileHeading';

//Create  
  const [poppedProfile, setPoppedProfile] = React.useState([]);


// Replace: <ActivityFeed title={title} activities={activities} />
<div className='activity_feed'>
          <ProfileHeading setPopped={setPoppedProfile} profile={profile} />
          <ActivityFeed activities={activities} />
        </div>
```