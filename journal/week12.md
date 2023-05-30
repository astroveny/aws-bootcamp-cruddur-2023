# Week 12 


- [Frontend Sync](#Frontend-Sync)
  - [CloudFront Distribution ID script](#CloudFront-Distribution-ID-script)
  - [Create Sync Env](#Create-Sync-Env)
  - [Sync script](#Sync-Script)
  - [](#)
- [Reconnect Database](#Reconnect-Database)
  - [Env Vars Update](#Env-Vars-Update)
  - [Update The RDS SG Rule](#Update-The-RDS-SG-Rule)
  - [Database Schema and Migration](#Database-Schema-and-Migration)
  - [Update Frontend Template](#Update-Frontend-Template)
- [Post Confirmation Lambda Function Update](#Post-Confirmation-Lambda-Function-Update)
  - [Lambda Security Group](#Lambda-Security-Group)
  - [Lambda Configuration Update](#Lambda-Configuration-Update)
  - [Lambda Function Update](#Lambda-Function-Update)
  - [](#)
- [Refactor Create Activity](#Refactor-Create-Activity)
  - [Update App.py](#Update-Apppy)
  - [Update create.sql](#Update-createsql)
  - [Update create_activity.py](#Update-create_activitypy)
  - [Update ActivityForm.js](#Update-ActivityFormjs)
- [Refactor JWT Using Decorators](#Refactor-JWT-Using-Decorators)
  - [Update cognito_jwt_token.py](#Update-cognito_jwt_tokenpy)
  - [Update app.py](#Update-apppy)
  - [](#)
  - [](#)
- [Refactor Backend App Modules](#Refactor-Backend-App-Modules)
  - [Create model_json() function](#Create-model_json()-function)
  - [Rollbar Module](#Rollbar-Module)
  - [Xray Module](#Xray-Module)
  - [Honeycomb Module](#Honeycomb-Module)
  - [CORS Module](#CORS-Module)
  - [CloudWatch Module](#CloudWatch-Module)
  - [Update App.py](#Update-Apppy)
- [Refactor Backend App Routes](#Refactor-Backend-App-Routes)
  - [Helper Module](#Helper-Module)
  - [Activities Route](#Activities-Route)
  - [Users Route](#Users-Route)
  - [Messages Route](#Messages-Route)  
  - [General Route](#General-Route)
  - [Update App.py](#Update-Apppy)
- [Fixes](#Fixes)
  - [Fix ReplyForm.js popup close](#Fix-ReplyFormjs-popup-close)
  - [](#)
  - [](#)
  - [](#)

## Frontend Sync

### CloudFront Distribution ID script
[Back to Top](#Week-12)

- This script will retrieve the CloudFront distribution ID
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

---
  
### Create Sync Env
[Back to Top](#Week-12)

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
---
  
### Sync Script
[Back to Top](#Week-12)

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

### Env Vars Update
[Back to Top](#Week-12)

- Update the PROD_CONNECTION_URL to use the new Database endpoint URL
- Update the DB_SG_ID to use the new Security Group ID
- Update the DB_SG_RULE_ID to use the new Security Group Rule ID
- Make sure $GITPOD_IP has the new Gitpod session IP, otherwise run
`export GITPOD_IP="$(curl ifconfig.me)"`

---
  
### Update The RDS SG Rule
[Back to Top](#Week-12)

- Go to AWS EC2 console then select Security Group from the left-side menu
- Select the RDS security group then edit the inboud rules
- add a new rule> Type: Postgres - Source: MyIP - Description: GITPOD
- Once the new rule is added, then run the following scirpt to update SG with the Gitpod IP
`./bin/aws/rds-update-sg-rule`

--- 
  
### Database Schema and Migration
[Back to Top](#Week-12)

- Run `./bin/db/db-schema-load prod` to load the schema into the production database
- Connect to the database to verify the new tables `./bin/db/db-connect prod`
- run `\dt` to list the tables
- Run the migration tool to update the users table
`CONNECTION_URL=$PROD_CONNECTION_URL ./bin/db/migrate`
- Connect to the database again then run `\d users;` to verify the new column "bio" is added


---
---
  
## Post Confirmation Lambda Function Update
[Back to Top](#Week-12)

We will update the Lambda code, Security Group, and the configuration (Env Vars and VPC)

### Lambda Security Group
- Go to AWS EC2 console, select Security Groups
- Create a new security group for Lambda **"CognitoLambdaSG"**
- Inboud rules: none
- Next, go to the RDS security group **"CrdDbAlbSG"**
- Edit Inboud Rules, then add a new rule
- **Type:** PostgreSQL - **Source:** CognitoLambdaSG - **Description:** COGNITOPOSTCONF

---
  
### Lambda Configuration Update
[Back to Top](#Week-12)

- Go to AWS Lambda console then select **"cruddur-post-confirmation"** function
- Edit the Lambda Env vars under Configuration
- update **"CONNECTION_URL"** with the new RDS instance endpoint
- Edit **VPC** then replace the VPC with the new CrdNetVPC
- Edit the subnets and chose all public subnets
- Edit the security group and chose the new security group **"CognitoLambdaSG"**
- save the changes 

---
  
### Lambda Function Update
[Back to Top](#Week-12)

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


---
---


## Refactor Create Activity

### Update App.py 
[Back to Top](#Week-12)

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

---
  
### Update create.sql
[Back to Top](#Week-12)

- Edit `backend-flask/db/sql/activities/create.sql `
- Replace `users.handle` with `users.cognito_user_id`
- Replace `handle` with `cognito_user_id`

---
  
### Update create_activity.py
[Back to Top](#Week-12)

- Edit `backend-flask/services/create_activity.py`
- Replace all `user_handle` with `cognito_user_id`
- Replace all `handle` with `cognito_user_id`

---
  
### Update ActivityForm.js
[Back to Top](#Week-12)

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
  

  

## Refactor JWT Using Decorators


### Update cognito_jwt_token.py
[Back to Top](#Week-12)

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

---
  
### Update app.py
[Back to Top](#Week-12)

- Refactor the function for each API endpoint route to validate user access using the new `jwt_required` created inside `cognito_jwt_token.py`
- Edit and update [backend-flask/app.py](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/ca7eb79f611305b6358d1c0b8dcc55a55db04e12/backend-flask/app.py)

---
---

## Refactor Backend App Modules

- Refactor app.py to deattach some external models into their own library
- But first we will refactor the repeated retun mpdel error into a function

### Create model_json() function
[Back to Top](#Week-12)

- Edit backend-flask/app.py then add the following function
```python
def model_json(model):
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200
```
- Repalce the `if model['errors']` statement with the new function `return model_json(model)`

---
  
### Rollbar Module
[Back to Top](#Week-12)

- Create a file `backend-flask/lib/rollbar.py`
- Add the following code 
```python
from flask import current_app as app
from flask import got_request_exception
from time import strftime
import os
import rollbar
import rollbar.contrib.flask

def init_rollbar():
  rollbar_access_token = os.getenv('ROLLBAR_ACCESS_TOKEN')
  rollbar.init(
      # access token
      rollbar_access_token,
      # environment name
      'production',
      # server root directory, makes tracebacks prettier
      root=os.path.dirname(os.path.realpath(__file__)),
      # flask already sets up logging
      allow_logging_basic_config=False)
  # send exceptions from `app` to rollbar, using flask's signal system.
  got_request_exception.connect(rollbar.contrib.flask.report_exception, app)
  return rollbar
```
---  

### Xray Module
[Back to Top](#Week-12)

- Create a file `backend-flask/lib/xray.py`
- Add the following code
```python
import os
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

def init_xray(app):
  xray_url = os.getenv("AWS_XRAY_URL")
  xray_recorder.configure(service='backend-flask', dynamic_naming=xray_url)
  XRayMiddleware(app, xray_recorder)
```
---
  
###  Honeycomb Module
[Back to Top](#Week-12)

- Create file `backend-flask/lib/honeycomb.py`
- Add the following code
```python
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)

# OTEL ----------
# Show this in the logs within the backend-flask app (STDOUT)
#simple_processor = SimpleSpanProcessor(ConsoleSpanExporter())
#provider.add_span_processor(simple_processor)

trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

def init_honeycomb(app):
  FlaskInstrumentor().instrument_app(app)
  RequestsInstrumentor().instrument()
```
---
  
### CORS Module
[Back to Top](#Week-12)

- Create a file `backend-flask/lib/cors.py`
- Add the following code
```python
from flask_cors import CORS
import os

def init_cors(app):
  frontend = os.getenv('FRONTEND_URL')
  backend = os.getenv('BACKEND_URL')
  origins = [frontend, backend]
  cors = CORS(
    app, 
    resources={r"/api/*": {"origins": origins}},
    headers=['Content-Type', 'Authorization'], 
    expose_headers='Authorization',
    methods="OPTIONS,GET,HEAD,POST"
  )
```
---
  
###  CloudWatch Module
[Back to Top](#Week-12)

- Create a file `backend-flask/lib/cloudwatch.py`
- Add the following code
```python
import watchtower
import logging
from flask import request

# Configuring Logger to Use CloudWatch
# LOGGER = logging.getLogger(__name__)
# LOGGER.setLevel(logging.DEBUG)
# console_handler = logging.StreamHandler()
# cw_handler = watchtower.CloudWatchLogHandler(log_group='cruddur')
# LOGGER.addHandler(console_handler)
# LOGGER.addHandler(cw_handler)
# LOGGER.info("test log")

def init_cloudwatch(response):
  timestamp = strftime('[%Y-%b-%d %H:%M]')
  LOGGER.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
  return response
```
---
  
### Update App.py
[Back to Top](#Week-12)

- Updte app.py to import the new modules & initialize them
```python
#Import the modules
from lib.rollbar import init_rollbar
from lib.xray import init_xray
from lib.cors import init_cors
from lib.cloudwatch import init_cloudwatch
from lib.honeycomb import init_honeycomb
from aws_xray_sdk.core import xray_recorder

## initalization --------
init_xray(app)
with app.app_context():
  rollbar = init_rollbar()
init_honeycomb(app)
init_cors(app)
```
- Remove previous library import for each of (Rollbar, Xray, Honeycomb, CloudWatch)
- Remove all previous functions related to (Rollbar, Xray, Honeycomb, CloudWatch)

---
---

## Refactor Backend App Routes
[Back to Top](#Week-12)

We will refactor the app.py routes by creating seperate routes modules files then move out all routes to the relevent modules. we will start by creating activities.py for all activities routes, messages.py for all messages routes, users.py for all users routes and lastly general.py for the rest of the routes.

But first we will deattach the model_json() to an external module.

### Helper Module
[Back to Top](#Week-12)

- Create `backend-flask/lib/helpers.py`
- Move the the following from app.py to helpers.py
```python
def model_json(model):
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200
```
- Update app.py to import model_json from helpers module `from lib.helpers import model_json`

--- 
  
### Activities Route
[Back to Top](#Week-12)

- Create a new dir: `backend-flask/routes`
- Create `backend-flask/routes/activities.py`
- Add this [code](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/7c38821f9751f262c15b86ef1d44ffc35fedbcd8/backend-flask/routes/activities.py)

---
  
### Users Route
[Back to Top](#Week-12)

- Create `backend-flask/routes/users.py`
- Add this [code](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/7c38821f9751f262c15b86ef1d44ffc35fedbcd8/backend-flask/routes/users.py)

---
  
### Messages Route
[Back to Top](#Week-12)

- Create `backend-flask/routes/messages.py`
- Add this [code](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/7c38821f9751f262c15b86ef1d44ffc35fedbcd8/backend-flask/routes/messages.py)

---
  
### General Route
[Back to Top](#Week-12)

- Create `backend-flask/routes/general.py`
- Add this [code](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/7c38821f9751f262c15b86ef1d44ffc35fedbcd8/backend-flask/routes/general.py)

---
  
### Update App.py
[Back to Top](#Week-12)

- Edit `backend-flask/app.py` 
- Replace the content with the following code
```python
from flask import Flask
from flask import request, g 
import os
import sys

from lib.rollbar import init_rollbar
from lib.xray import init_xray
from lib.cors import init_cors
from lib.cloudwatch import init_cloudwatch
from lib.honeycomb import init_honeycomb
from lib.helpers import model_json

import routes.general
import routes.activities
import routes.users
import routes.messages


app = Flask(__name__)


## initalization --------
init_xray(app)
init_honeycomb(app)
init_cors(app)
with app.app_context():
  g.rollbar = init_rollbar(app)

# load routes -----------
routes.general.load(app)
routes.activities.load(app)
routes.users.load(app)
routes.messages.load(app)

if __name__ == "__main__":
  app.run(debug=True)
``` 

---
---
  
## Fixes
### Fix ReplyForm.js popup close
[Back to Top](#Week-12)

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
---
  
### Update Frontend Template
[Back to Top](#Week-12)

- Edit `aws/cfn/frontend/template.yaml`
- Add the following
```yml
CustomErrorResponses:
          - ErrorCode: 403
            ResponseCode: 200
            ResponsePagePath: /index.html
```
- Deploy the stack by running `./bin/cfn/frontend`

---
  
### Service Config.toml update
[Back to Top](#Week-12)

- Add the following to `aws/cfn/service/config.toml`
```
[parameters]
EnvFrontendUrl = '<YourDomainName>'
EnvBackendUrl = 'api.<YourDomainName>'
```

---
---

## Replies Feature 

### Update ReplyForm.js

- Add Access Token and pass the uuid for the message 
- Updated [frontend-react-js/src/components/ReplyForm.js]()

### Update Backend Activities Route

- Edit `backend-flask/routes/activities.py`
- Update the **reply route** with the following
```python
 @app.route("/api/activities/<string:activity_uuid>/reply", methods=['POST','OPTIONS'])
  @cross_origin()
  @jwt_required()
  def data_activities_reply(activity_uuid):
    message = request.json['message']
    model = CreateReply.run(message, g.cognito_user_id, activity_uuid)
    return model_json(model)
```

### Update Backend Create Activity Service

- Edit `backend-flask/services/create_reply.py`
- Replace `user_handle` with `cognito_user_id`
- Add a new function `create_reply` to create a message with the uuid
- The final code should be like this [create_reply.py]()

### Reply SQL file

- Create a new SQL file `backend-flask/db/sql/activities/reply.sql`
- Add the following query
```sql
INSERT INTO public.activities (
  user_uuid,
  message,
  reply_to_activity_uuid
)
VALUES (
  (SELECT uuid 
    FROM public.users 
    WHERE users.cognito_user_id = %(cognito_user_id)s
    LIMIT 1
  ),
  %(message)s,
  %(reply_to_activity_uuid)s
) RETURNING uuid;
```

### Update Object SQL file

- Edit `backend-flask/db/sql/activities/object.sql`
- Add this to the query after SELECT `activities.reply_to_activity_uuid`


