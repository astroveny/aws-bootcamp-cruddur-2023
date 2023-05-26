# Week 12 — 




## Frontend Sync

### CloudFront Distribution get ID script

- Create a bash script `bin/aws/cf-distribution-id-get` to retrieve the distribution id
- Add the following code
```bash
#!/bin/bash

# Set the origin bucket name
origin_bucket_name="awsbc.flyingresnova.com"

# Retrieve the CloudFront distribution ID
distribution_id=$(aws cloudfront list-distributions --query "DistributionList.Items[?Origins.Items[?DomainName=='$origin_bucket_name.s3.amazonaws.com']].Id" --output text)

# Export the CloudFront distribution ID as an environment variable
export DISTRIBUTION_ID=$distribution_id
gp env DISTRIBUTION_ID=$distribution_id

# Print the CloudFront distribution ID
echo "CloudFront Distribution ID: $distribution_id"
```
- Run the script `source bin/aws/cf-distribution-id-get`
- This will export Env var DISTRIBUTION_ID


### Create Sync Env

- Create a new sync erb file `erb/sync.env.erb`
- Add the following Env vars
```
SYNC_S3_BUCKET=<DomainNAme>
SYNC_CLOUDFRONT_DISTRUBTION_ID=<%= ENV['DISTRIBUTION_ID'] %>
SYNC_BUILD_DIR=<%= ENV['THEIA_WORKSPACE_ROOT'] %>/frontend-react-js/build
SYNC_OUTPUT_CHANGESET_PATH=<%=  ENV['THEIA_WORKSPACE_ROOT'] %>/tmp/sync-changeset.json
SYNC_AUTO_APPROVE=false
```
- Edit `bin/frontend/generate-env`
- add the following code
```ruby
File.write(filename, content)

template = File.read 'erb/sync.env.erb'
content = ERB.new(template).result(binding)
filename = "sync.env"
```

### Sync script

- The Sync script will sync data between local frontend dir and the S3 static website bucket
- Create a bash script file [**bin/frontend/sync**](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/13f7e21170d0f1126cd71c1c9129693f23ad725d/bin/frontend/sync) using Ruby
- Install gem `aws_s3_website_sync` and `dotenv`  
`gem install aws_s3_website_sync`  
`gem install dotenv`  
- Run the Sync script: `./bin/frontend/sync`
- This will sync the frontend build with the S3 static website bucket 

---
---

## Reconnect Database

### Env vars update

- Update the PROD_CONNECTION_URL to use the new Database endpoint URL
- Update the DB_SG_ID to use the new Security Group ID
- Update the DB_SG_RULE_ID to use the new Security Group Rule ID
- Make sure $GITPOD_IP has the new Gitpod session IP, otherwise run
`export GITPOD_IP="$(curl ifconfig.me)"`

### Update the RDS SG Rule

- Go to AWS EC2 console then select Security Group from the left-side menu
- Select the RDS security group then edit the inboud rules
- add a new rule> Type: Postgres - Source: MyIP - Description: GITPOD
- Once the new rule is added, then run the following scirpt to update SG with the Gitpod IP
`./bin/aws/rds-update-sg-rule`

### Database Schema and Migration

- Run `./bin/db/db-schema-load prod` to load the schema into the production database
- Connect to the database to verify the new tables `./bin/db/db-connect prod`
- run `\dt` to list the tables
- Run the migration tool to update the users table
`CONNECTION_URL=$PROD_CONNECTION_URL ./bin/db/migrate`
- Connect to the database again then run `\d users;` to verify the new column "bio" is added


### Update Frontend Template

- Edit `aws/cfn/frontend/template.yaml`
- Add the following
```yml
CustomErrorResponses:
          - ErrorCode: 403
            ResponseCode: 200
            ResponsePagePath: /index.html
```
- Deploy the stack by running `./bin/cfn/frontend`


### Post Confirmation Lambda Function Update


#### Lambda Security Group
- Go to AWS EC2 console, select Security Groups
- Create a new security group for Lambda **"CognitoLambdaSG"**
- Inboud rules: none
- Next, go to the RDS security group **"CrdDbAlbSG"**
- Edit Inboud Rules, then add a new rule
- **Type:** PostgreSQL - **Source:** CognitoLambdaSG - **Description:** COGNITOPOSTCONF

#### Lambda Configuration Update
- Go to AWS Lambda console then select **"cruddur-post-confirmation"** function
- Edit the Lambda Env vars under Configuration
- update **"CONNECTION_URL"** with the new RDS instance endpoint
- Edit **VPC** then replace the VPC with the new CrdNetVPC
- Edit the subnets and chose all public subnets
- Edit the security group and chose the new security group **"CognitoLambdaSG"**
- save the changes 

#### Lambda Function Update

- Go to the Code tab the edit the following
- Replace `user_cognito_id` variable with `cognito_user_id`
- Replace `VALUES(%s,%s,%s,%s)` with the following
```python
VALUES(
          %(display_name)s,
          %(email)s,
          %(handle)s,
          %(cognito_user_id)s
        )
```
- Replace the param values with the following
```python
params = {
        'display_name': user_display_name,
        'email': user_email,
        'handle': user_handle,
        'cognito_user_id': cognito_user_id
      }
```
- Deploy the new code

### Service Config.toml update

- Add the following to `aws/cfn/service/config.toml`
```
[parameters]
EnvFrontendUrl = '<YourDomainName>'
EnvBackendUrl = 'api.<YourDomainName>'

---
---


## Refactor Create Activity

### Update App.py 

- Edit `backend-flask/app.py` file 
- Replace the conent of data_activities() function with the following

```python
def data_activities():
  access_token = extract_access_token(request.headers)
  try:
    claims = cognito_jwt_token.verify(access_token)
    cognito_user_id = claims['sub']

    message = request.json['message']
    ttl = request.json['ttl']
    model = CreateActivity.run(message, cognito_user_id, ttl)
    if model['errors'] is not None:
      return model['errors'], 422
    else:
      return model['data'], 200
  except TokenVerifyError as e:
    # unauthenicatied request
    app.logger.debug(e)
    return {}, 401
```

### Update create.sql

- Edit `backend-flask/db/sql/activities/create.sql `
- Replace `users.handle` with `users.cognito_user_id`
- Replace `handle` with `cognito_user_id`

### Update create_activity.py

- Edit `backend-flask/services/create_activity.py`
- Replace all `user_handle` with `cognito_user_id`
- Replace all `handle` with `cognito_user_id`


### Update ActivityForm.js

- Edit `frontend-react-js/src/components/ActivityForm.js`
- Import **getAccessToken** by adding the following
`import {getAccessToken} from '../lib/CheckAuth';`
- Update `const onsubmit` with the following
```js
console.log('onsubmit payload', message)
// add the following
await getAccessToken()
const access_token = localStorage.getItem("access_token")

//REPLACE: 'Accept': 'application/json'
'Authorization': `Bearer ${access_token}`,
```

- This fix will make it possible to create acitivties on the Home page by clicking on Crund button to post a new message

---
---
  
## Fix Bugs
### Fix ReplyForm.js popup close

- Edit `frontend-react-js/src/components/ReplyForm.js`
- Add the following to line 64
```js
 const close = (event)=> {
    if (event.target.classList.contains("reply_popup")) {
      props.setPopped(false)
    }
  }
```
- Replace the following code
```js
//REPLACE: <div className="popup_form_wrap">
//With the following
<div className="popup_form_wrap reply_popup" onClick={close}>
```

## Refactor JWT Using Decorators


### Update cognito_jwt_token.py

- Edit `backend-flask/lib/cognito_jwt_token.py`
- Import the required libraries 
```python
from functools import wraps, partial
from flask import request, g
import os
```
- Add the following code
```python
from functools import wraps, partial
    def jwt_required(f=None, on_error=None):
        if f is None:
            return partial(jwt_required, on_error=on_error)
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cognito_jwt_token = CognitoJwtToken(
                user_pool_id=os.getenv("AWS_COGNITO_USER_POOL_ID"), 
                user_pool_client_id=os.getenv("AWS_COGNITO_USER_POOL_CLIENT_ID"),
                region=os.getenv("AWS_DEFAULT_REGION")
            )
            access_token = extract_access_token(request.headers)
            try:
                claims = cognito_jwt_token.verify(access_token)
                # is this a bad idea using a global?
                g.cognito_user_id = claims['sub']  # storing the user_id in the global g object
            except TokenVerifyError as e:
                # unauthenticated request
                app.logger.debug(e)
                if on_error:
                    on_error(e)
                return {}, 401
            return f(*args, **kwargs)
        return decorated_function
```

### Update app.py

- Edit and update [backend-flask/app.py]()


