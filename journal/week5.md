# Week 5 

## DynamoDB and Serverless Caching

  [1. DynamoDB Utility scripts](#1-DynamoDB-Utility-scripts)
   -  [Schema-load script](#Schema-load-script)
   -  [List-table script](#List-table-script)
   -  [Drop script](#Drop-script)
   -  [Seed script](#Seed-script)
   -  [Scan script](#Scan-script)
   -  [Access Patterns](#Access-Patterns)
      - [get-conversation script](#get-conversation-script)
      - [list-conversations script](#list-conversations-script)

  
## 1. DynamoDB Utility scripts

We will create new bash utility scripts for dynamoDB, we will start by creating 'schema-load' to define and create the table then we will create 'drop' and 'list-tables' scripts to be able to drop and list existing tables. Next we will seed data consist of messages along with uuid details using script 'seed', we can then view the content using scripts 'scan' which will scan the table, 'get-conversation' which will get specific messages based on specific criteria and finally 'list-conversations' which lists all messages also based on specific criteria.

- Go to backend-flask/bin and create new dir: `ddb`

### Schema-load script
[Back to top](#week-5)
- create script `schema-load` which will define the schema and create the table
```bash
#! /usr/bin/env python3

import boto3
import sys

attrs = {
  'endpoint_url': 'http://localhost:8000'}

if len(sys.argv) == 2:
  if "prod" in sys.argv[1]:
    attrs = {}

dynamodb = boto3.client('dynamodb', **attrs)
table_name = 'cruddur-messages'

# define the schema for the table
table_schema = {
  'AttributeDefinitions': [
    {
      'AttributeName': 'message_group_uuid',
      'AttributeType': 'S'
    },{
      'AttributeName': 'pk',
      'AttributeType': 'S'
    },{
      'AttributeName': 'sk',
      'AttributeType': 'S'
    }
  ],
  'KeySchema': [{
      'AttributeName': 'pk',
      'KeyType': 'HASH'
    },{
      'AttributeName': 'sk',
      'KeyType': 'RANGE'
    }
  ],
  'BillingMode': 'PROVISIONED',
  'ProvisionedThroughput': {
      'ReadCapacityUnits': 5,
      'WriteCapacityUnits': 5
  },
  'GlobalSecondaryIndexes':[{
    'IndexName':'message-group-sk-index',
    'KeySchema':[{
      'AttributeName': 'message_group_uuid',
      'KeyType': 'HASH'
    },{
      'AttributeName': 'sk',
      'KeyType': 'RANGE'
    }],
    'Projection': {
      'ProjectionType': 'ALL'
    },
    'ProvisionedThroughput': {
      'ReadCapacityUnits': 5,
      'WriteCapacityUnits': 5
    },
  }]
}

# create the table
response = dynamodb.create_table(
    TableName=table_name,
    **table_schema
)

# print the response
print(response)
```

### List-table script
[Back to top](#week-5)

- Next, create script `list-tables` to list the current tables
```bash
#! /usr/bin/bash

if [ "$1" = "prod" ]; then
  ENDPOINT_URL=""
else
  ENDPOINT_URL="--endpoint-url=http://localhost:8000"
fi

aws dynamodb list-tables  $ENDPOINT_URL \
  --query TableNames \
  --output table
```

### Drop script
[Back to top](#week-5)

- Create script `drop` to drop the table
```bash
#! /usr/bin/bash

set -e

if [ -z "$1" ]; then #-z checks if $1 exist
  echo "No TABLE_NAME argument supplied eg. bin/rds/describ-table cruddur-messages"
  exit 1
fi
TABLE_NAME=$1

if [ "$2" = "prod" ]; then
  ENDPOINT_URL=""
else
  ENDPOINT_URL="--endpoint-url=http://localhost:8000"
fi

aws dynamodb delete-table  $ENDPOINT_URL \
  --table-name $TABLE_NAME
```
### Seed script 
[Back to top](#week-5)

- Let's create [script seed](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/main/backend-flask/bin/ddb/seed) to input data to the table using uuid from the postgres DB
- Before we run `./seed` we need to make sure that cruddur DB and data are available after running `./backend-flask/bin/db/db-setup`
- Run `./seed` to seed data (messages using uuid)

### Scan script
[Back to top](#week-5)

- For testing we can check the seeded data on the local DynamoDB using this script `scan`
```python
  #!/usr/bin/env python3

import boto3

attrs = {
  'endpoint_url': 'http://localhost:8000'
}
ddb = boto3.resource('dynamodb',**attrs)
table_name = 'cruddur-messages'

table = ddb.Table(table_name)
response = table.scan()

items = response['Items']
for item in items:
  print(item)
```
- Run `./scan` to view the seeded messages for each uuid
>> NOTE: output has been reduced!
```json
{'user_uuid': 'adbebad0-29d8-48ed-9023-2c3e4a671e8c', 'message_group_uuid': '5ae290ed-55d1-47a0-bc6d-fe2bc2700399', 'user_handle': 'buzz', 'sk': '2023-03-23T09:55:59.043951+00:00', 'pk': 'GRP#9e8936ff-3baa-415b-b78f-7b2961ac31d6', 'message': 'this is a filler message', 'user_display_name': 'Buzz Lightyear'}
{'user_uuid': '9e8936ff-3baa-415b-b78f-7b2961ac31d6', 'user_handle': 'woody', 'sk': '2023-03-23T09:55:59.043951+00:00', 'pk': 'MSG#5ae290ed-55d1-47a0-bc6d-fe2bc2700399', 'message_uuid': 'b90ecde4-f47f-44fb-8b2b-5cdecf659d98', 'message': "Have you ever watched Babylon 5? It's one of my favorite TV shows!", 'user_display_name': 'Woody'}
...
{'user_uuid': 'adbebad0-29d8-48ed-9023-2c3e4a671e8c', 'user_handle': 'buzz', 'sk': '2023-03-23T11:38:59.043951+00:00', 'pk': 'MSG#5ae290ed-55d1-47a0-bc6d-fe2bc2700399', 'message_uuid': '04fc3d2c-aa60-4d44-af10-52a6ed434169', 'message': "Definitely. I think his character is a great example of the show's ability to balance humor and heart, and to create memorable and beloved characters that fans will cherish for years to come.", 'user_display_name': 'Buzz Lightyear'}
{'user_uuid': '9e8936ff-3baa-415b-b78f-7b2961ac31d6', 'message_group_uuid': '5ae290ed-55d1-47a0-bc6d-fe2bc2700399', 'user_handle': 'woody', 'sk': '2023-03-23T09:55:59.043951+00:00', 'pk': 'GRP#adbebad0-29d8-48ed-9023-2c3e4a671e8c', 'message': 'this is a filler message', 'user_display_name': 'Woody'}
```

### Access Patterns 
[Back to top](#week-5)

- Then we create access patterns scripts to fetch the data based on each pattern, create dir: patterns inside dir: ddb

  #### get-conversation script
  [Back to top](#week-5)
  
  - Create script `get-conversation` to get conversation using operators like 'begin_with' or 'between'
  ```python
  #!/usr/bin/env python3

  import boto3
  import sys
  import json
  import datetime

  attrs = {
    'endpoint_url': 'http://localhost:8000'
  }

  if len(sys.argv) == 2:
    if "prod" in sys.argv[1]:
      attrs = {}

  dynamodb = boto3.client('dynamodb',**attrs)
  table_name = 'cruddur-messages'

  message_group_uuid = "5ae290ed-55d1-47a0-bc6d-fe2bc2700399"

  year = str(datetime.datetime.now().year)
  # define the query parameters
  query_params = {
    'TableName': table_name,
    'ScanIndexForward': False,
    'Limit': 20,
    'ReturnConsumedCapacity': 'TOTAL',
    'KeyConditionExpression': 'pk = :pk AND begins_with(sk,:year)',
    #'KeyConditionExpression': 'pk = :pk AND sk BETWEEN :start_date AND :end_date',
    'ExpressionAttributeValues': {
      ':year': {'S': year },
      #":start_date": { "S": "2023-03-01T00:00:00.000000+00:00" },
      #":end_date": { "S": "2023-03-19T23:59:59.999999+00:00" },
      ':pk': {'S': f"MSG#{message_group_uuid}"}
    }
  }


  # query the table
  response = dynamodb.query(**query_params)

  # print the items returned by the query
  print(json.dumps(response, sort_keys=True, indent=2))

  # print the consumed capacity
  print(json.dumps(response['ConsumedCapacity'], sort_keys=True, indent=2))

  items = response['Items']
  #items.reverse()
  reversed_array = items[::-1]

  for item in reversed_array:
    sender_handle = item['user_handle']['S']
    message       = item['message']['S']
    timestamp     = item['sk']['S']
    dt_object = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')
    formatted_datetime = dt_object.strftime('%Y-%m-%d %I:%M %p')
    print(f'{sender_handle: <12}{formatted_datetime: <22}{message[:40]}...')
  ```  
  - Run `./patterns/get-converstation` 
  >> NOTE: output has been reduced!
  ```
  woody       2023-03-23 11:19 AM   One thing that really stands out about B...
  buzz        2023-03-23 11:20 AM   I thought the special effects in Babylon...
  ...
  woody       2023-03-23 11:35 AM   I also thought that Zathras was a great ...
  buzz        2023-03-23 11:36 AM   Yes, that's a good point. Babylon 5 was ...
  woody       2023-03-23 11:37 AM   And Zathras was just one example of that...
  buzz        2023-03-23 11:38 AM   Definitely. I think his character is a g...
  ```

  #### list-conversations script
  [Back to top](#week-5)

  - Update db library `backend-flask/lib/db.py` with the following code:
  - Add argument `params` to the following:
  ```python
  def print_sql(self,title,sql,params={}): #line 38
  ...
  print(sql,params) #line 42
  ...
  self.print_sql('array',sql,params) #line 62
  ...
  self.print_sql('json',sql,params) #line 73
  ```
  - Add the followinf query function
  ```python
  def query_value(self,sql,params={}):
      self.print_sql('value',sql,params)
      with self.pool.connection() as conn:
        with conn.cursor() as cur:
          cur.execute(sql,params)
          json = cur.fetchone()
          return json[0]
  ```

  
  - Create script `list-conversations` to list conversations, then make it executable 
  ```python
  #!/usr/bin/env python3

  import boto3
  import sys
  import json
  import os

  current_path = os.path.dirname(os.path.abspath(__file__))
  parent_path = os.path.abspath(os.path.join(current_path, '..', '..', '..'))
  sys.path.append(parent_path)
  from lib.db import db

  attrs = {
    'endpoint_url': 'http://localhost:8000'
  }

  if len(sys.argv) == 2:
    if "prod" in sys.argv[1]:
      attrs = {}

  dynamodb = boto3.client('dynamodb',**attrs)
  table_name = 'cruddur-messages'

  def get_my_user_uuid():
    sql = """
      SELECT 
        users.uuid
      FROM users
      WHERE
        users.handle =%(handle)s
    """
    uuid = db.query_value(sql,{
      'handle':  'woody'
    })
    return uuid

  my_user_uuid = get_my_user_uuid()
  print(f"my-uuid: {my_user_uuid}")

  # define the query parameters
  query_params = {
    'TableName': table_name,
    'KeyConditionExpression': 'pk = :pk',
    'ExpressionAttributeValues': {
      ':pk': {'S': f"GRP#{my_user_uuid}"}
    },
    'ReturnConsumedCapacity': 'TOTAL'
  }

  # query the table
  response = dynamodb.query(**query_params)

  # print the items returned by the query
  print(json.dumps(response, sort_keys=True, indent=2))
  ```
  - Run `./patterns/list-conversations`
  >> NOTE: output has been reduced!
  ```json
     {'handle': 'woody'}
  my-uuid: 9e8936ff-3baa-415b-b78f-7b2961ac31d6
  {
    "ConsumedCapacity": {
      "CapacityUnits": 0.5,
      "TableName": "cruddur-messages"
  ...
   "user_handle": {
          "S": "buzz"
        },
        "user_uuid": {
          "S": "adbebad0-29d8-48ed-9023-2c3e4a671e8c"
  ```



## Implement DynamoDB into the App

### Pattern A

#### DynamoDB library for Flask

- in this section we will create new library [ddb.py](https://github.com/omenking/aws-bootcamp-cruddur-2023/blob/0c0aaa6479c7cd234b6f8506ef013c259f6ff4e5/backend-flask/lib/ddb.py) `backend-flask/lib/ddb.py` 

### Retrieve Cognito users uuid 
- Create new dir: cognito under backend-flask/bin
- Create script `list-users` inside dir: cognito 
```python
#!/usr/bin/env python3

import boto3
import os
import json

userpool_id = os.getenv("AWS_COGNITO_USER_POOL_ID")
client = boto3.client('cognito-idp')
params = {
  'UserPoolId': userpool_id,
  'AttributesToGet': [
      'preferred_username',
      'sub'
  ]
}
response = client.list_users(**params)
users = response['Users']

print(json.dumps(users, sort_keys=True, indent=2, default=str))

dict_users = {}
for user in users:
  attrs = user['Attributes']
  sub    = next((a for a in attrs if a["Name"] == 'sub'), None)
  handle = next((a for a in attrs if a["Name"] == 'preferred_username'), None)
  dict_users[handle['Value']] = sub['Value']

print(json.dumps(dict_users, sort_keys=True, indent=2, default=str))
```
- run list-users `./cognito/list-users
```json
{
  "astroveny": "025b9f07-1df5-4d56-a3cc-73a96c8b0ed8",
  "buzz": "1d190662-71b2-4d5c-8526-60c261889bea",
  "woody": "f68b6dfb-675d-4cc4-894e-770ea3b03eb1"
}
```

- Next we will create new script to import cognito users id into the postgres DB 
- Create [script update_cognito_user_ids](https://github.com/astroveny/aws-bootcamp-cruddur-2023/tree/main/backend-flask/bin/db/update_cognito_user_ids) under bin/db.
- Add the following code to `bin/db/db-setup`: `source "$setup_path/update_cognito_user_ids"`
- Run `update_cognito_user_ids` - _sample output_:
```sql
 SQL STATEMENT-[commit with returning]------

    UPDATE public.users
    SET cognito_user_id = %(sub)s
    WHERE
      users.handle = %(handle)s;
   {'handle': 'woody', 'sub': 'f68b6dfb-675d-4cc4-894e-770ea3b03eb1'}
```

#### Add Cognito user id to Message Groups Service  

- First we will update App.py and replace function `data_message_groups()` with the following code
```python
access_token = extract_access_token(request.headers)
  try:
    claims = cognito_jwt_token.verify(access_token)
    # authenicatied request
    app.logger.debug("authenicated")
    app.logger.debug(claims)
    cognito_user_id = claims['sub']
    model = MessageGroups.run(cognito_user_id=cognito_user_id)
    if model['errors'] is not None:
      return model['errors'], 422
    else:
      return model['data'], 200
  except TokenVerifyError as e:
    # unauthenicatied request
    app.logger.debug(e)
    return {}, 401
```
- Replace the code inside service/message_groups.py with the following 
```python
from datetime import datetime, timedelta, timezone
from lib.ddb import Ddb
from lib.db import db

class MessageGroups:
  def run(cognito_user_id):
    model = {
      'errors': None,
      'data': None
    }

    sql = db.template('users','uuid_from_cognito_user_id')
    my_user_uuid = db.query_value(sql,{
      'cognito_user_id': cognito_user_id
    })

    print(f"UUID: {my_user_uuid}")

    ddb = Ddb.client()
    data = Ddb.list_message_groups(ddb, my_user_uuid)
    print("list_message_groups:",data)

    model['data'] = data
    
  return model
 ```
 - Next we will create the `uuid_from_cognito_user_id` sql file under `db/sql/users` and add the following
 - This will return the uuid from cognito user id
```sql
SELECT
  users.uuid
FROM public.users
WHERE 
  users.cognito_user_id = %(cognito_user_id)s
LIMIT 1
```

#### Add Access token to Frontend pages
- update files `frontend-react-js/src/pages/MessageGroupsPage.js` and `MessageGroupPage.js`
- Add the following code: 
```js
  headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`
        },
```
- Remove the following code:
```js
// [TODO] Authenication
import Cookies from 'js-cookie'
```

- Update `frontend-react-js/src/components/MessageForm.js` headers section with the following
`'Authorization': `Bearer ${localStorage.getItem("access_token")}``

- Decouple the checkAuth function from HomeFeedPage.js by creating Check Auth js file `frontend-react-js/src/lib/CheckAuth.js` then move the following code:
```js
import { Auth } from 'aws-amplify';

const checkAuth = async (setUser) => {
  Auth.currentAuthenticatedUser({
    // Optional, By default is false. 
    // If set to true, this call will send a 
    // request to Cognito to get the latest user data
    bypassCache: false 
  })
  .then((user) => {
    console.log('user',user);
    return Auth.currentAuthenticatedUser()
  }).then((cognito_user) => {
      setUser({
        display_name: cognito_user.attributes.name,
        handle: cognito_user.attributes.preferred_username
      })
  })
  .catch((err) => console.log(err));
};

export default checkAuth;
```
- Next, we will update checkAuth for MessageGroupPage.js and MessageGroupsPage.js
- add `import checkAuth from '../lib/CheckAuth';` 
- remove the checkAuth function, then add `setUser` argument to checkAuth(); inside `React.useEffect`
- Login to the frontend app then go to messages 
  
![image](https://user-images.githubusercontent.com/91587569/227632833-091f01a8-e19b-470d-aea9-976a60dbb80d.png)



  
  ### Pattern B

#### Frontend Router Update 

- First we will update the App.js `MessageGroupPage` router path from `/messages/@:handle` to `/messages/:message_group_uuid`
- Next we will update Pages/MessageGroupPage.js `const backend_url` as the following and remove `const handle`
  ```js 
  const backend_url = `${process.env.REACT_APP_BACKEND_URL}/api/messages/${params.message_group_uuid}`
  ```
- Update components/MessageGroupitem.js `const classes` with the following:
```js 
if (params.message_group_uuid == props.message_group.uuid){
      classes.push('active')}
```
- update the returned path to `to={`/messages/@`+props.message_group.uuid}>`

#### Backend Route update
- Replace App.py `data_messages` with the following:
```python
 access_token = extract_access_token(request.headers)
  try:
    claims = cognito_jwt_token.verify(access_token)
    # authenicatied request
    app.logger.debug("authenicated")
    app.logger.debug(claims)
    cognito_user_id = claims['sub']
    model = MessageGroups.run(cognito_user_id=cognito_user_id)
    if model['errors'] is not None:
      return model['errors'], 422
    else:
      return model['data'], 200
  except TokenVerifyError as e:
    # unauthenicatied request
    app.logger.debug(e)
    return {}, 401
```

- Replace services/messages.py with the following
```python
from datetime import datetime, timedelta, timezone
from lib.ddb import Ddb
from lib.db import db

class Messages:
  def run(message_group_uuid,cognito_user_id):
    model = {
      'errors': None,
      'data': None
    }
    sql = db.template('users','uuid_from_cognito_user_id')
    my_user_uuid = db.query_value(sql,{
      'cognito_user_id': cognito_user_id
    })

    print(f"UUID: {my_user_uuid}")
    ddb = Ddb.client()
    data = Ddb.list_messages(ddb, message_group_uuid)
    print("list_messages")
    print(data)

    model['data'] = data
    return model
``` 

#### Pass message group uuid inside MessageForm.js 
- replace the body content with `body: JSON.stringify(json)`
- then create object json to list message based on handle or uuid
```js
let json = { 'message': message }
      if (params.handle) {
        json.handle = params.handle
      } else {
        json.message_group_uuid = params.message_group_uuid
      }
```
### Pattern D

#### Backend Create Message
- Replace App.py `data_create_message()` with the following code:
```python
message_group_uuid   = request.json.get('message_group_uuid',None)
  user_receiver_handle = request.json.get('handle',None)
  message = request.json['message']
  access_token = extract_access_token(request.headers)
  try:
    claims = cognito_jwt_token.verify(access_token)
    # authenicatied request
    app.logger.debug("authenicated")
    app.logger.debug(claims)
    cognito_user_id = claims['sub']
    if message_group_uuid == None:
      # Create for the first time
      model = CreateMessage.run(
        mode="create",
        message=message,
        cognito_user_id=cognito_user_id,
        user_receiver_handle=user_receiver_handle
      )
    else:
      # Push onto existing Message Group
      model = CreateMessage.run(
        mode="update",
        message=message,
        message_group_uuid=message_group_uuid,
        cognito_user_id=cognito_user_id
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
- Then update [services/create_message.py](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/main/backend-flask/services/create_message.py) to create or update message group based on uuid and handle

- Create db/sql/users/create_message_users.sql and add the following sql code:
```sql
SELECT 
  users.uuid,
  users.display_name,
  users.handle,
  CASE users.cognito_user_id = %(cognito_user_id)s
  WHEN TRUE THEN
    'sender'
  WHEN FALSE THEN
    'recv'
  ELSE
    'other'
  END as kind
FROM public.users
WHERE
  users.cognito_user_id = %(cognito_user_id)s
  OR 
  users.handle = %(user_receiver_handle)s
```
- login to the frontend app then go to **Messages** tab, click on the group message then add new message
- 


### Pattern C

### Frontend New Message Group
- Update App.js with the following code to add new router
```js
import MessageGroupNewPage from './pages/MessageGroupNewPage';

{
    path: "/messages/new/:handle",
    element: <MessageGroupNewPage />
  },
```
- Add new page [MessageGroupNewPage.js](https://github.com/astroveny/aws-bootcamp-cruddur-2023/tree/main/frontend-react-js/src/pages/MessageGroupNewPage.js)
- Add new component MessageGroupNewitem.js
```js
import './MessageGroupItem.css';
import { Link } from "react-router-dom";

export default function MessageGroupNewItem(props) {
  return (

    <Link className='message_group_item active' to={`/messages/new/`+props.user.handle}>
      <div className='message_group_avatar'></div>
      <div className='message_content'>
        <div classsName='message_group_meta'>
          <div className='message_group_identity'>
            <div className='display_name'>{props.user.display_name}</div>
            <div className="handle">@{props.user.handle}</div>
          </div>{/* activity_identity */}
        </div>{/* message_meta */}
      </div>{/* message_content */}
    </Link>
  );
}
```
- Update components/MessageGroupFeed.js with the following code
```js
import MessageGroupNewItem from './MessageGroupNewItem';

 let message_group_new_item;
  if (props.otherUser) {
    message_group_new_item = <MessageGroupNewItem user={props.otherUser} />
  }

{message_group_new_item} //add this inside className='message_group_feed_collection'
```
- Add conditional to components/MessageForm.js redirect if there is new record
```js
        console.log('data:',data)
        if (data.message_group_uuid) {
          console.log('redirect to message group')
          window.location.href = `/messages/${data.message_group_uuid}`
        } else {
          props.setMessages(current => [...current,data]);
        }
```

### Backend Adding Endpoint

- update app.py with new service  and endpoint by adding the following code
```python
from services.users_short import *

@app.route("/api/users/@<string:handle>/short", methods=['GET'])
def data_users_short(handle):
  data = UsersShort.run(handle)
  return data, 200
```

- Add new service users_short.py
```python
from lib.db import db

class UsersShort:
  def run(handle):
    sql = db.template('users','short')
    results = db.query_object_json(sql,{
      'handle': handle
    })
    return results
```
- Create new SQL file short.sql
```sql 
SELECT
  users.uuid,
  users.handle,
  users.display_name
FROM public.users
WHERE 
  users.handle = %(handle)s
  ```

  - Login to the frontend app, go to messages the redirect to /new/Handle ex: /new/astroveny
  - click on the new message group then post a new message and it should appear in the message group

<img width="508" alt="image" src="https://user-images.githubusercontent.com/91587569/227721999-d25f8fcd-551e-4bb7-8d42-32ccd1a9e059.png">

