# Week 5 

## DynamoDB and Serverless Caching



  
## DynamoDB Utility scripts

We will create new bash utility scripts for dynamoDB, we will start by creating 'schema-load' to define and create the table then we will create 'drop' and 'list-tables' scripts to be able to drop and list existing tables. Next we will seed data consist of messages along with uuid details using script 'seed', we can then view the content using scripts 'scan' which will scan the table, 'get-conversation' which will get specific messages based on specific criteria and finally 'list-conversations' which lists all messages also based on specific criteria.

- Go to backend-flask/bin and create new dir: `ddb`

### Schema-load script
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
- Let's create [script seed](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/main/backend-flask/bin/ddb/seed to input data to the table using uuid from the postgres DB
- Before we run `./seed` we need to make sure that cruddur DB and data are available after running `./backend-flask/bin/db/db-setup`
- Run `./seed` to seed data (messages using uuid)

### Scan script
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

- Then we create access patterns scripts to fetch the data based on each pattern, create dir: patterns inside dir: ddb

  #### get-conversation script
  - Create script `get-conversation` to get conversation using operators like 'begin_with' or 'between'
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

  #### list-conversations scripts
  - Create script `list-conversations` to list conversations, then make it executable 
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
