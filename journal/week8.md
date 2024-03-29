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
  - [Create Lambda files](#Create-indexjs)
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

[6. Cloudfront CDN Setup](#6-Cloudfront-CDN-Setup)  
  - [Create CloudFront Distribution](#Create-CloudFront-Distribution)
  - [Add S3 Bucket Policy](#Add-S3-Bucket-Policy)
  - [Create Hosted Zone Record](#Create-Hosted-Zone-Record)

[7. Implement Users Profile Page](#7-Implement-Users-Profile-Page)
  - [Create User show.sql](#Create-User-showsql)
  - [Updatde user_activities.py](#Updatde-user_activitiespy)
  - [Update UserFeedPage.js](#Update-UserFeedPagejs)
  - [Create EditProfileButton.js](#Create-EditProfileButtonjs)
  - [Update Activity Feed](#Update-Activity-Feed)
  - [Create Profile Heading](#Create-Profile-Heading)

[8. Profile Form](#8-Profile-Form)
  - [Frontend Absolute Import](#Frontend-Absolute-Import)
  - [Create ProfileForm.js](#Create-ProfileFormjs)
  - [Update UserFeedPage.js](#Update-UserFeedPagejs)
  - [Create Popup CSS](#Create-Popup-CSS)
  
[9. Backend Update Endpoint](#9-Backend-Update-Endpoint)
  - [Create Update Profile](#Create-Update-Profile)
  - [Create Update SQL file](#Create-Update-SQL-file)
  
[10. Migration](#10-Migration)
  - [Migration Task](#Migration-Task)
  - [Migrate and Rollback](#Migrate-and-Rollback)
    - [Migrate script](#Migrate-script)
    - [Rollback script](#Rollback-script)
  
[11. Avatar Upload Feature](#11-Avatar-Upload-Feature)
  - [Create Upload Lambda script](#Create-Upload-Lambda-script)
  - [Create Upload Lambda funtion](#Create-Upload-Lambda-funtion)
  - [S3 Presigned URL Policy](#S3-Presigned-URL-Policy)
  - [JWT Verification Lambda script](#JWT-Verification-Lambda-script)
  - [Create Authorizer Lambda function](#)
  - [API Gateway](#API-Gateway)
  - [S3 upload function](#S3-upload-function)
  - [Upload Bucket CORS](#Upload-Bucket-CORS)

[12. Render Avatar via CloudFront](#12-Render-Avatar-via-CloudFront)  
  - [Profile Avatar](#Profile-Avatar)

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
- Create file [index.js](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/4ce259273f69fdc6a1ce2c376726fa2162a25eaf/aws/lambdas/process-images/index.js)
### Create test.js
- This test code will have hardcoded values for testing 
- Create file [aws/lambdas/process-images/test.js](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/4ce259273f69fdc6a1ce2c376726fa2162a25eaf/aws/lambdas/process-images/test.js)

### Create s3-image-processing.js 
- Create file [aws/lambdas/process-images/s3-image-processing.js](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/4ce259273f69fdc6a1ce2c376726fa2162a25eaf/aws/lambdas/process-images/s3-image-processing.js)

### Create example.json
- Create json file [aws/lambdas/process-images/example.json](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/4ce259273f69fdc6a1ce2c376726fa2162a25eaf/aws/lambdas/process-images/example.json)

### Create Init file
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

## 7. Implement Users Profile Page

### Create User show.sql
[Back to Top](#Week-8)

- Go to `backend-flask/db/sql/users`
- Create new SWL file [**show.sql**](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/94e7712ee3dbe38c5d28cc6ae5947d4e3f3a9ecc/backend-flask/db/sql/users/show.sql)

### Updatde user_activities.py
[Back to Top](#Week-8)

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
[Back to Top](#Week-8)

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


### Create EditProfileButton.js
[Back to Top](#Week-8)

- create JS file [frontend-react-js/src/components/EditProfileButton.js](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/775776a06119a7032049ac10ff9129bca943552f/frontend-react-js/src/components/EditProfileButton.js)
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
[Back to Top](#Week-8)

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
[Back to Top](#Week-8)

Create a new profile heading section then import it to UserFeedPage.js

- Create new JS file [frontend-react-js/src/components/ProfileHeading.js](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/43f0d4bc57c249584624f1bbabae347594e63d5c/frontend-react-js/src/components/ProfileHeading.js)
- Create new CSS file [frontend-react-js/src/components/ProfileHeading.css](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/43f0d4bc57c249584624f1bbabae347594e63d5c/frontend-react-js/src/components/ProfileHeading.css)
- Update UserFeedPage.js with the following:
```python
import ProfileHeading from '../components/ProfileHeading';

const [poppedProfile, setPoppedProfile] = React.useState([]);
  
<div className='activity_feed'>
  <ProfileHeading setPopped={setPoppedProfile} profile={profile} />
  <ActivityFeed activities={activities} />
</div>  
```

----
----

## 8. Profile Form

### Frontend Absolute Import
[Back to Top](#Week-8)

We will create jsconfig file which will set the "include" src dir as the root level for all files, this mean that we can move the js file anywhere within source yet it will affet route.

- Create JS file `frontend-react-js/jsconfig.json`
- Add the following code
```js
{
  "compilerOptions": {
    "baseUrl": "src"
  },
  "include": ["src"]
}
```
- Restart the application to take effect


### Create ProfileForm.js
[Back to Top](#Week-8)

- Create JS file [frontend-react-js/src/components/ProfileForm.js](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/43f0d4bc57c249584624f1bbabae347594e63d5c/frontend-react-js/src/components/ProfileForm.js)
- Create CSS file [frontend-react-js/src/components/ProfileForm.css](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/43f0d4bc57c249584624f1bbabae347594e63d5c/frontend-react-js/src/components/ProfileForm.css)


### Update UserFeedPage.js
[Back to Top](#Week-8)

- Edit `frontend-react-js/src/pages/UserFeedPage.js`
- Add the following code
```js
import ProfileForm from '../components/ProfileForm';

<ProfileForm 
          profile={profile}
          popped={poppedProfile} 
          setPopped={setPoppedProfile} 
        />
```

### Create Popup CSS
[Back to Top](#Week-8)

1. Edit `frontend-react-js/src/components/ReplyForm.css`
2. Delete class`.popup_form_wrap` and `.popup_form` 
3. Create CSS file [`frontend-react-js/src/components/Popup.css`](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/43f0d4bc57c249584624f1bbabae347594e63d5c/frontend-react-js/src/components/Popup.css)
4. Update App.js to import Popup.css `import './components/Popup.css';`

----
----

## 9. Backend Update Endpoint

We will create a new **Update endpoint** then add the route to the backend app

### Create Update Profile
[Back to Top](#Week-8)

- Create python file [backend-flask/services/update_profile.py](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/43f0d4bc57c249584624f1bbabae347594e63d5c/backend-flask/db/sql/users/update.sql)
- Add **Update Endpoint** to **app.py**
  - Add the following code to add the endpoint and import the service
  ```python
  from services.update_profile import *

  @app.route("/api/profile/update", methods=['POST','OPTIONS'])
  @cross_origin()
  def data_update_profile():
    bio          = request.json.get('bio',None)
    display_name = request.json.get('display_name',None)
    access_token = extract_access_token(request.headers)
    try:
      claims = cognito_jwt_token.verify(access_token)
      cognito_user_id = claims['sub']
      model = UpdateProfile.run(
        cognito_user_id=cognito_user_id,
        bio=bio,
        display_name=display_name
      )
      if model['errors'] is not None:
        return model['errors'], 422
      else:
        return model['data'], 200
    except TokenVerifyError as e:
      # unauthenicatied request
      app.logger.debug(e)
      return {}, 401
  ```

### Create Update SQL file 
[Back to Top](#Week-8)
  
- Create SQL file `backend-flask/db/sql/users/update.sql`
- Add the following code
```sql
UPDATE public.users 
SET 
  bio = %(bio)s,
  display_name= %(display_name)s
WHERE 
  users.cognito_user_id = %(cognito_user_id)s
RETURNING handle;
```
----
----

## 10. Migration 

We will create a migration script that will generate ans start a migration task to update the database.

### Migration Task
[Back to Top](#Week-8)

- Create a **migration script** that will generate a python script to do a migration task
- Create dir: `bin/generate`
  - Create bash file [bin/generate/migration](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/main/bin/generate/migration) and make it executable  
- Create output dir: `backend-flask/db/migrations`
  - Create keep file: .keep
- Run `./bin/generate/migration add_bio_column`
- This will generate python file (timestamp_add_bio_column.py) under `backend-flask/db/migrations`
- Edit the file
- add a migration SQL command `    ALTER TABLE public.users ADD COLUMN bio text;`
- add a rollback SQL command `    ALTER TABLE public.users DROP COLUMN bio;`

### Migrate and Rollback

Create Migrate & Rollback script to start a migration task or roll back the task 

#### Migrate script 
[Back to Top](#Week-8)

- Migrate script will start the migration process by starting the migration task
- Create **migrate script** [bin/db/migrate](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/main/bin/db/migrate)
- update `backend-flask/db/schema.sql` to create new table "schema_information " to log last_successful_run
- Add the following code
```sql
CREATE TABLE IF NOT EXISTS public.schema_information (
  id integer UNIQUE,
  last_successful_run text
);
INSERT INTO public.schema_information (id, last_successful_run)
VALUES(1, '0')
ON CONFLICT (id) DO NOTHING;
```
- Run Migrate `./bin/db/migrate` which will start the migration task
- `===>>> running migration:  16817640553749738_add_bio_column`

#### Rollback script
[Back to Top](#Week-8)

- Create **rollback script** [bin/db/rollback](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/main/bin/db/rollback)
- Update `backend-flask/lib/db.py` functions: query_commit, query_array_json, query_object_json, query_value
- add `verbose=True` and `if verbose:`, as shown in the below example
```python

def query_commit(self,sql,params={},verbose=True):
    if verbose:
      self.print_sql('commit with returning',sql,params)
```

## 11. Avatar Upload Feature 

In this section we will add S3 upload function to the ProfileForm.js that will call an api endpoint (created using API gateway) which will validated the authorization using authorizer lambda function then triger the Upload lambda function to upload the avatar.


### Create Upload Lambda script
[Back to Top](#Week-8)

- Go to dir: aws/lambdas
- Create new dir: cruddur-upload-avatar
- create ruby file [**function.rb**](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/b939c66cf2bea5b2a0752ccc330527fe7aedd0e6/aws/lambdas/cruddur-upload-avatar/function.rb)
- Generate Gemfile inside dir: cruddur-upload-avatar `bundle init`
- Edit the Gemfile then add: 
```
gem "aws-sdk-s3"
gem "ox"
gem "jwt"
```
- Install the sdk by running the following `bundle install`
- Test the function by running the following to obtain the signed URL
```bash
$ bundle exec ruby function.rb 
{}
{:statusCode=>200, :body=>"{\"url\":\"https://cruddur-uploaded-avatars.s3.amazonaws.com/mock.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIATNYETYVMCNREFJXP%2F20230419%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20230419T111926Z&X-Amz-Expires=300&X-Amz-SignedHeaders=host&X-Amz-Signature=201d13f4972d6f5923a9f95465ed08ac014c0b9c2ee4366972ea0a235d67f6e\"}"}
```
- Create Lambda layer script to load the gem
- create dir: bin/lambda-layers then create bash file [ruby-jwt](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/d64ac9a4df7fe5d0789022e4e75741ce6b47830c/bin/lambda-layers/ruby-jwt)
- make the file executable then run it
- This will create a customer layer called **jwt**


### Create Upload Lambda funtion
[Back to Top](#Week-8)

- Go to AWS Lambda console
- Click on **Create function**
- fill in the details:
- **Basic Information/Fnction name:** CruddurAvatarUpload
- **Basic Information/Runtime:** Ruby 2.7
- **Basic Information/Architecture:** x86_64
- **Basic Information/Execution role:** Create a new role with basic Lambda permissions
- Click on **Create function**
- Copy the code from the ruby script then paste it into the lambda code
- change the lambfa function file name to **function.rb**
- Change Runtime Settings > handler = **function.handler**
- Select **Add layer** then chose **Custom layers**
- Select the **jwt** layer created in the previous step the click **Add**
- Select **Configuration** tab then click on **Environment variables**
- Click on Edit then add: 
  - Key: UPLOADS_BUCKET_NAME
  - Value: YourDomainName-cruddur-uploaded-avatars


### S3 Presigned URL Policy
[Back to Top](#Week-8)

- Click on the function created previously then select **Configuration** tab
- Select **Permissions** then click on the **Role name** URL
- Select **Add permissions** then click **Create inline policy**
- Fill in the details
  - Service: S3
  - Actions: PutObject
  - Resources: Specific > bucket-ARN/*
- Click **Review policy** then Enter the Policy name: 
- Click **Create Policy** 
- Click on the policy then copy the content
- Create a new policy file `aws/policies/s3-upload-avatar-presigned-url-policy.json`
- Paste the policy content 


### JWT Verification Lambda script
[Back to Top](#Week-8)

- Create dir: `aws/lambdas/lambda-authorizer`
- Create JS file [**index.js**](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/5fa333548640d4686fbb9f2f17cd2c0040c2bd25/aws/lambdas/lambda-authorizer/index.js) inside lambda-authorizer
- Run `npm  i aws-jwt-verify`
- Download the contect of dir: lambda-authorizer to your machine then compress it to a zip file

### Create Authorizer Lambda function
[Back to Top](#Week-8)

- Go to AWS Lambda console
- Click on **Create function**
- fill in the details:
- **Basic Information/Fnction name:** CruddurApiGatewayLambdaAuthorizer
- **Basic Information/Runtime:** Node.js 18.x
- **Basic Information/Architecture:** x86_64
- Click on **Create function**
- Click on **Upload from** under **Code** tab
- Select the lambda-authorizer.zip file created in the previous step
- Click on **Deploy**
- Select **Configuration** tab then click on **Environment variables**
- Click **Edit** then add the _Cognito User Pool_ Env vars (USER_POOL_ID, CLIENT_ID)
  

### API Gateway
[Back to Top](#Week-8)

- Go to AWS API Gteway console
- Click on **Build** for API HTTP
- Click **Add Integration** then chose **Lambda**
- Add the **CruddurAvatarUpload Lambda ARN**
- Enter **API name** e.g.: api-cruddur then click **Next**
- Inside **Configure routes** select **Method** as POST - **Resource path:** /avatars/key_upload - **Integration target** CruddurAvatarUpload
- Add route, **Method** as OPTIONS - **Resource path:** /{proxy+} - **Integration target** CruddurAvatarUpload
- Next, then click on **Create**
- Click on **Authorization** on the left side menu
- Select **Manage authorizers** tab then click **Create**
  - **Authorizer type:** Lambda
  - **Name:** CruddurJWTAuthorizer
  - Select Lambda CruddurApiGatewayLambdaAuthorizer
  - **Response mode:** Simple
  - Disable **Authorizer caching** then click **Create**
- Select **Attach authorizers to routes** tab then Click on **POST**
- Select **CruddurJWTAuthorizer** then click **Attach authorizer**
- Click on **Stage** from the left-side menu then select **default**
- Note the **Invoke URL** to be used in the next step with "/avatars/key_upload"


### S3 upload function
[Back to Top](#Week-8)

We will create s3upload & s3uploadkey functions inside ProfileForm.js this will use the API invoke URL to invoke lambda CruddurAvatarUpload which will generate presigned URL to be used to upload the avatar. Lambda function CruddurApiGatewayLambdaAuthorizer will be invoked to validate and authorize user access to upload the avatar.

- Go to dir: frontend-react-js
- Install @aws-sdk/client-s3: `npm i @aws-sdk/client-s3 --save`
- Update [frontend-react-js/src/components/ProfileForm.js](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/d64ac9a4df7fe5d0789022e4e75741ce6b47830c/frontend-react-js/src/components/ProfileForm.js) with the new code
- Update `frontend-react-js/src/components/ProfileForm.css` with the following
```css
.profile_popup .upload {
  color: white;
  background: green;
}
```
- Edit erb/frontend-react-js.env.erb then add the following
```ruby
REACT_APP_FRONTEND_URL=https://3000-<%= ENV['GITPOD_WORKSPACE_ID'] %>.<%= ENV['GITPOD_WORKSPACE_CLUSTER_HOST'] %>
REACT_APP_API_GATEWAY_ENDPOINT_URL=	https://YourApiInvokeUrl
```

### Upload Bucket CORS
[Back to Top](#Week-8)

We will update the CORS for the upload bucket

- Go to AWS S3 console then select bucket: YourDomainName-cruddur-uploaded-avatars
- Click on Permissions the edit CORS
- add the following
```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["PUT"],
        "AllowedOrigins": ["https://*.gitpod.io"],
        "ExposeHeaders": [
            "x-amz-server-side-encryption",
            "x-amz-request-id",
            "x-amz-is-2"
            ],
            "MaxAgeSeconds": 30000
    }]
```
- copy the content to `aws/s3/cors.json`

---
---

## 12. Render Avatar via CloudFront

We will create Profile avatar component that will render avatar via CloudFront, we will then update relative components.

### Profile Avatar 
[Back to Top](#Week-8) 

- Create [frontend-react-js/src/components/ProfileAvatar.js](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/fcd0db806bd948e7c75af700a7f70487ac9e38c1/frontend-react-js/src/components/ProfileAvatar.js)
- Create frontend-react-js/src/components/ProfileAvatar.css
- Update setUser() in **frontend-react-js/src/lib/CheckAuth.js** with the following code
`cognito_user_uuid: cognito_user.attributes.sub,`
- Update className="banner" **frontend-react-js/src/components/ProfileHeading.js** with the following code
  - REMOVE `<div className="avatar"> .. </div>`
```js
import ProfileAvatar from 'components/ProfileAvatar'

  <ProfileAvatar id={props.profile.cognito_user_uuid} />
```
- Update **frontend-react-js/src/components/ProfileHeading.css** with the following code
  - REPLACE `.profile_heading .avatar {` with `.profile_heading .profile-avatar {`
  - REMOVE `} .profile_heading .avatar img {`
- Update **frontend-react-js/src/components/ProfileInfo.js** with the following code
```js
import ProfileAvatar from 'components/ProfileAvatar'

///REPLACE <div className="profile-avatar"></div>
<ProfileAvatar id={props.user.cognito_user_uuid} />
```
- Update 'if (res.status === 200)' **frontend-react-js/src/pages/UserFeedPage.js** with the following
`console.log('setprofile',resJson.profile)`
- Edit **backend-flask/db/sql/users/show.sql** 
- add the following to SELECT cognito_user_uuid 
`users.cognito_user_id as cognito_user_uuid,`

[Back to Top](#Week-8)
