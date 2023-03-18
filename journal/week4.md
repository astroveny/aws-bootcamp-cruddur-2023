# Week 4 

## Postgres and RDS

[1. Provision RDS Instance Postgres Engine](#1-Provision-RDS-Instance-Postgres-Engine)  

[2. Postgres DB Setup](#2-Postgres-DB-Setup)

-   [Connect and create DB](#Connect-and-create-DB)
-   [Env Variables](#Env-Variables)
-   [Create SQL files](#Create-SQL-files)
    -   [Create SQL Schema file ](#Create-SQL-Schema-file)
    -   [Create SQL Seed file](#Create-SQL-Seed-file)
-   [Create Bash Scripts](#Create-Bash-Scripts)
    -   [Create DB db-create script](#Create-DB-db-create-script)
    -   [Drop DB db-drop script](#Drop-DB-db-drop-script)
    -   [Load Schema db-schema-load script ](#Load-Schema-db-schema-load-script )
    -   [Connect to DB db-connect script](#Connect-to-DB-db-connect-script)
    -   [Insert Data db-seed script ](#Insert-Data-db-seed-script)
    -   [Check Open Sessions Script](#Check-Open-Sessions-Script)
-   [Install Postgres Client](#Install-Postgres-Client)
  
[3. Connect Gitpod to RDS instance ](#3-Connect-Gitpod-to-RDS-instance )
-   [Allow Temp Gitpod access](#Allow-Temp-Gitpod-access)
-   [Dynamic Gitpod Access Setup](#Dynamic-Gitpod-Access-Setup)   
    



## 1. Provision RDS Instance Postgres Engine
[Back to top](#Week-4)

- First, we will provision the RDS instance as it will take time to be created.
- Run the following command to create the RDs instance using Postgres engine.
>> **NOTE:** output has been reduced!
```json
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ aws rds create-db-instance --db-instance-identifier cruddur-db-instance --db-instance-class db.t3.micro \
>   --engine postgres --engine-version 14.6 --master-username cruddurroot --master-user-password YourPasswordHere --allocated-storage 20 --availability-zone us-east-1a \
>   --backup-retention-period 0 --port 5432 --no-multi-az --db-name cruddur --storage-type gp2 --publicly-accessible --storage-encrypted \
>   --enable-performance-insights --performance-insights-retention-period 7 --no-deletion-protection

{
    "DBInstance": {
        "DBInstanceIdentifier": "cruddur-db-instance",
        "DBInstanceClass": "db.t3.micro",
        "Engine": "postgres",
        "DBInstanceStatus": "creating",
        "MasterUsername": "root",
        "DBName": "cruddur",
        "AllocatedStorage": 20,
...
        "DBParameterGroups": [
                "DBParameterGroupName": "default.postgres14",
...
        "AvailabilityZone": "us-east-1a",
        "DBSubnetGroup": {
            "DBSubnetGroupName": "default",
            "DBSubnetGroupDescription": "default",
...
            "MasterUserPassword": "****"
        },
        "MultiAZ": false,
        "EngineVersion": "14.6",
                {
                "OptionGroupName": "default:postgres-14",
                "Status": "in-sync"
            }
        ],
        "StorageType": "gp2",
        "StorageEncrypted": true,
        "DbiResourceId": "db-*******************LEYM",
        ...
        "DBInstanceArn": "arn:aws:rds:us-east-1:*******:cruddur-db-instance",
...
```

- Once the instance is created, go to AWS RDS console and **stop the new instance** (this will stop the RDS instance for 4 days)

---
---

## 2. Postgres DB Setup
[Back to top](#Week-4)

### Connect and create DB

- Connect to the Postgres DB `gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ psql -U postgres -h localhost`
- Create local DB named 'cruddur' then list the DB
```sql
postgres=# create database cruddur;
CREATE DATABASE
postgres=# \l
                                 List of databases
   Name    |  Owner   | Encoding |  Collate   |   Ctype    |   Access privileges   
-----------+----------+----------+------------+------------+-----------------------
 cruddur   | postgres | UTF8     | en_US.utf8 | en_US.utf8 | 
 postgres  | postgres | UTF8     | en_US.utf8 | en_US.utf8 | 
 template0 | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
           |          |          |            |            | postgres=CTc/postgres
 template1 | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
           |          |          |            |            | postgres=CTc/postgres
(4 rows)
```
---  
### Env Variables
[Back to top](#Week-4)

- Create ENV variable Connection URL for local `CONNECTION_URL` and production DB `PROD_CONNECTION_URL`
- The following will use localhost as local DB URL, and RDS DB endpoint as production URL
```bash
export CONNECTION_URL='postgresql://postgresUSER:USERpassword@localhost:5432/cruddur'
gp env CONNECTION_URL='postgresql://postgresUSER:USERpassword@localhost:5432/cruddur'

export PROD_CONNECTION_URL='postgresql://DBUSER:DBpassword@DB-instance-name.xxxxxxxx.us-east-1.rds.amazonaws.com'
gp env PROD_CONNECTION_URL='postgresql://DBUSER:DBpassword@DB-instance-name.xxxxxxxx.us-east-1.rds.amazonaws.com'
```

--- 
### Create SQL files


#### Create SQL Schema file 
[Back to top](#Week-4)

The Schema file contains the SQL commands to create new DB schema and define tables

- Create SQL file schema.sql inside backend-flask/db and add the following code
`CREATE EXTENSION "uuid-ossp";`
- Import the script using the following command:

```sql
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ psql cruddur < db/schema.sql -h localhost -U postgres
Password for user postgres: 
CREATE EXTENSION
```
- Update db/schema.sql with the following to create tables to be used in the next step
```sql
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.activities;

CREATE TABLE public.users (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  display_name text,
  handle text,
  cognito_user_id text,
  created_at TIMESTAMP default current_timestamp NOT NULL
);

CREATE TABLE public.activities (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_uuid UUID NOT NULL,
  message text NOT NULL,
  replies_count integer DEFAULT 0,
  reposts_count integer DEFAULT 0,
  likes_count integer DEFAULT 0,
  reply_to_activity_uuid integer,
  expires_at TIMESTAMP,
  created_at TIMESTAMP default current_timestamp NOT NULL
);
``` 
---  
#### Create SQL Seed file
[Back to top](#Week-4)

The Seed file contains SQL commands to seed/enter data based on the DB schema

- Create **db/seed.sql** and add the following code
```sql
-- this file was manually created
INSERT INTO public.users (display_name, handle, cognito_user_id)
VALUES
  ('Woody', 'woody' ,'MOCK'),
  ('Buzz Lightyear', 'buzz' ,'MOCK');

INSERT INTO public.activities (user_uuid, message, expires_at)
VALUES
  (
    (SELECT uuid from public.users WHERE users.handle = 'woody' LIMIT 1),
    'This was imported as seed data!',
    current_timestamp + interval '10 day'
  )
```

---  
### Create Bash Scripts
[Back to top](#Week-4)

- Create these files `db-create`  `db-drop`  `db-schema-load` under backend-flask/bin 

#### Create DB db-create script

- update **db-create** with the following
```bash
echo 'DB-create'
NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<<"$CONNECTION_URL")
psql $NO_DB_CONNECTION_URL -c "CREATE database cruddur;"
```
#### Drop DB db-drop script
[Back to top](#Week-4)

- update **db-drop** with the following
```bash
echo 'DB-drop'
NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<<"$CONNECTION_URL")
psql $NO_DB_CONNECTION_URL -c "drop database cruddur;"
```
#### Load Schema db-schema-load script 
[Back to top](#Week-4)

- update **db-schema-load** with the following
```bash
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-schema-load"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

#schemaload_path=$(realpath "$0")
#schema_path=($(sed 's/bin\/db-schema-load//' <<<"$schemaload_path")db/schema.sql)
schema_path="$(realpath .)/db/schema.sql"
echo $schema_path

if [ "$1" = "prod" ]; then
  echo "loading using production"
  CON_URL=$PROD_CONNECTION_URL
else
  CON_URL=$CONNECTION_URL
fi

psql $CON_URL cruddur < $schema_path
```

- run **db-schema-load** `./bin/db-schema-load`
```sql
ERROR:  extension "uuid-ossp" already exists
NOTICE:  table "users" does not exist, skipping
DROP TABLE
NOTICE:  table "activities" does not exist, skipping
DROP TABLE
CREATE TABLE
CREATE TABLE
```
#### Connect to DB db-connect script
[Back to top](#Week-4)

- Create **db-connect** and add the following code
```bash
#! /usr/bin/bash

psql $CONNECTION_URL
```

- run **'db-connect'** `./bin/db-connect` then type \dt to list the tables 
- enable '\x auto' once connected by running `\x auto`
```sql
cruddur=# \dt
           List of relations
 Schema |    Name    | Type  |  Owner   
--------+------------+-------+----------
 public | activities | table | postgres
 public | users      | table | postgres
``` 

#### Insert Data db-seed script 
[Back to top](#Week-4)

- Create **db-seed**, add the following code then make it executable
```bash
#! /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-seed-load"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"


#seedload_path=$(realpath "$0")
#seed_path=($(sed 's/bin\/db-seed//' <<<"$seedload_path")db/seed.sql)
seed_path="$(realpath .)/db/seed.sql"

echo $seed_path

if [ "$1" = "prod" ]; then
  echo "loading using production"
  CON_URL=$PROD_CONNECTION_URL
else
  CON_URL=$CONNECTION_URL
fi

psql $CON_URL cruddur < $seed_path
```

- Run **'db-seed'** `./bin/db-seed` 
```sql
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ ./bin/db-seed 
== db-seed
/workspace/aws-bootcamp-cruddur-2023/backend-flask/db/seed.sql
INSERT 0 2
INSERT 0 1
```
#### Check Open Sessions Script
[Back to top](#Week-4)

- To check the current Postgres sessions, create file sessions under backend-flask/bin and add the following code
```bash
#! /usr/bin/bash

yellowbg="\033[0;43m"
bred="\033[1;31m"
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-sessions"
printf "${yellowbg}${bred}>>> ${LABEL}${NO_COLOR}\n"

if [ "$1" = "prod" ]; then
  echo "loading using production"
  URL=$PROD_CONNECTION_URL
else
  URL=$CONNECTION_URL
fi

NO_DB_URL=$(sed 's/\/cruddur//g' <<<"$URL")
psql $NO_DB_URL -c "select pid as process_id, \
       usename as user,  \
       datname as db, \
       client_addr, \
       application_name as app,\
       state \
from pg_stat_activity;"
```


#### Setup DB db-setup script 
[Back to top](#Week-4)

- We will create db-setup file under backend-flask/bin to run the previous scripts in order
- add the following code:
```bash
#! /usr/bin/bash

-e # stop if it fails at any point

yellowbg="\033[0;43m"
bgreenbg='\033[1;102m'
bgreen="\033[1;32m"
bred="\033[1;31m"
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-SETUP"
printf "${yellowbg}${bred}>>> ${LABEL}${NO_COLOR}\n"

setup_path="$(realpath .)/bin"

source "$setup_path/db-drop"
echo -e "${bgreenbg}>>> db-drop DONE${NO_COLOR}\n"
source "$setup_path/db-create"
echo -e "${bgreenbg}>>> db-create DONE${NO_COLOR}\n"
source "$setup_path/db-schema-load"
echo -e "${bgreenbg}>>> db-schema-load DONE${NO_COLOR}\n"
source "$setup_path/db-seed"
echo -e "${bgreenbg}>>> db-seed DONE${NO_COLOR}\n"
echo -e "${bgreen}>>> ALL DONE!${NO_COLOR}\n"
```
---

### Install Postgres Client
[Back to top](#Week-4)

- Start by adding the env variables to the docker compose file under backend-flask
`CONNECTION_URL: "${CONNECTION_URL}"`

>> Ref: https://www.psycopg.org/psycopg3/

- Add the following to  backend-flask/requirement.txt
```
psycopg[binary]
psycopg[pool]
```
- install the modules 
```
pip install -r requirements.txt
```
- Create db.py under backend-flask/lib and add the following code:
```python
from psycopg_pool import ConnectionPool
import os

def query_wrap_object(template):
  sql = f'''
  (SELECT COALESCE(row_to_json(object_row),'{{}}'::json) FROM (
  {template}
  ) object_row);
  '''
  return sql
def query_wrap_array(template):
  sql = f'''
  (SELECT COALESCE(array_to_json(array_agg(row_to_json(array_row))),'[]'::json) FROM (
  {template}
  ) array_row);
  '''
  return sql

connection_url = os.getenv("CONNECTION_URL")
pool = ConnectionPool(connection_url)
```

- Update file: backend-flask/services/home_activities.py with the following code:
- 
```python
from lib.db import pool, query_wrap_array
```
  - replace the following code, starting with result=[{ .. until span.set_attribute }]
    ```python
    results = [{
      'uuid': '68f126b0-1ceb-4a33-88be-d90fa7109eee',
      'handle':  'Andrew Brown',
      'message': 'Cloud is fun!',
      ...
    span.set_attribute("app.result_length", len(results))
    ```
  - with the following new code:
  
  ```python 
    sql = query_wrap_array("""
     SELECT
        activities.uuid,
        users.display_name,
        users.handle,
        activities.message,
        activities.replies_count,
        activities.reposts_count,
        activities.likes_count,
        activities.reply_to_activity_uuid,
        activities.expires_at,
        activities.created_at
      FROM public.activities
      LEFT JOIN public.users ON users.uuid = activities.user_uuid
      ORDER BY activities.created_at DESC
      """)
    with pool.connection() as conn:
        with conn.cursor() as cur:
          cur.execute(sql)
          # this will return a tuple
          # the first field being the data
          json = cur.fetchone()
      return json[0]
  ```
---
---

 ## 3. Connect Gitpod to RDS instance 
 [Back to top](#Week-4)

- Go to AWS RDS console then power up the RDS instance 
- Test the connection to RDS DB using env var PROD_CONNECTION_URL by running the following command
`psql $PROD_CONNECTION_URL`
- The above command should time-out since RDS instance' security group has no rule to allow gitpod access
- Press 'ctrl+c' then move to the next step.

### Allow Temp Gitpod access 
[Back to top](#Week-4)

- First we need to get the Gitpod public IP and create a variable for it by running the following command 
```bash
GITPOD_IP=$(curl ifconfig.me)
```
- run `echo $GITPOD_IP` to obtain the current Gitpod  IP
- Next we will create a security group inbound rule to allow Gitpod access to port 5432
  - Go to AWS RDS console, then click on the instance 
  - Click on the instance security group then select 'Inbound Rules' tab
  - click on Edit inbound rules and the following rule
  - Type: Postsgl - Source: the Gitpod IP - Description: Gitpod
- Test the connection to RDS DB again by running this command `psql $PROD_CONNECTION_URL`

### Dynamic Gitpod Access Setup
[Back to top](#Week-4)

Gitpod IP is ephemeral, hence it will change constantly and we would use a dynamic setup to update the RDS security group with the new IP.
for that we will add security group ID and rule as Env variables and use them in a bash script that has aws cli command to update the Gitpod IP.

- Go back to the AWS securty group console and get the security group ID and rule ID
- run the following to add them as Env variables 
```bash
export DB_SG_ID="sg-038xxxxxxxxxxxfda"
gp env DB_SG_ID="sg-038xxxxxxxxxxxfda"
export DB_SG_RULE_ID="sgr-036xxxxxxxxxx1996"
gp env DB_SG_RULE_ID="sgr-036xxxxxxxxxx1996"
```
- then we need to create `rds-update-sg-rule` file inside backend-flask/bin and add the following command
```bash
#1 /usr/bin/bash

yellowbg="\033[0;43m"
bred="\033[1;31m"
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="RDS-UPDATE-SG_RULE"
printf "${yellowbg}${bred}>>> ${LABEL} <<<<${NO_COLOR}\n"

aws ec2 modify-security-group-rules \
    --group-id $DB_SG_ID \
    --security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$GITPOD_IP/32}"
```

