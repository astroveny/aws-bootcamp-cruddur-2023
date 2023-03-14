# Week 4 

## Postgres and RDS

[1. Provision RDS Instance Postgres Engine](#1-Provision-RDS-Instance-Postgres-Engine)  

[2. Postgres DB Setup](#2-Postgres-DB-Setup)

-   [Connect and create DB](#Connect-and-create-DB)
-   [Env Variables](#Env-Variables)
    



### 1. Provision RDS Instance Postgres Engine
[Back to top](#Week-4)

- First, we will provision the RDS instance as it will take time to be created.
- Run the following command to create the RDs instance using Postgres engine.
>> **NOTE:** output has been reduced!
```json
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ aws rds create-db-instance --db-instance-identifier cruddur-db-instance --db-instance-class db.t3.micro \
>   --engine postgres --engine-version 14.6 --master-username root --master-user-password YourPasswordHere --allocated-storage 20 --availability-zone us-east-1a \
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


### 2. Postgres DB Setup
[Back to top](#Week-4)

#### Connect and create DB

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

#### Env Variables
[Back to top](#Week-4)

- Create ENV variable Connection URL for local `CONNECTION_URL` and production DB `PROD_CONNECTION_URL`
- The following will use localhost as local DB URL, and RDS DB endpoint as production URL
```bash
export CONNECTION_URL='postgresql://postgresUSER:USERpassword@localhost:5432/cruddur'
gp env CONNECTION_URL='postgresql://postgresUSER:USERpassword@localhost:5432/cruddur'

export PROD_CONNECTION_URL='postgresql://DBUSER:DBpassword@DB-instance-name.xxxxxxxx.us-east-1.rds.amazonaws.com'
gp env PROD_CONNECTION_URL='postgresql://DBUSER:DBpassword@DB-instance-name.xxxxxxxx.us-east-1.rds.amazonaws.com'
```


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



#### Create Bash Scripts
[Back to top](#Week-4)

- Create these files `db-create`  `db-drop`  `db-schema-load` under backend-flask/bin 
- update **db-create** with the following
```bash
echo 'DB-create'
NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<<"$CONNECTION_URL")
psql $NO_DB_CONNECTION_URL -c "CREATE database cruddur;"
```
- update **db-drop** with the following
```bash
echo 'DB-drop'
NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<<"$CONNECTION_URL")
psql $NO_DB_CONNECTION_URL -c "drop database cruddur;"
```
- update **db-schema-load** with the following
```bash
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-schema-load"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

schemaload_path=$(realpath "$0")
schema_path=($(sed 's/bin\/db-schema-load//' <<<"$schemaload_path")db/schema.sql)
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

- Create **db-connect** and add the following code
```bash
#! /usr/bin/bash

psql $CONNECTION_URL
```

- run **'db-connect'** `./bin/db-connect` then type \dt to list the tables 
```sql
cruddur=# \dt
           List of relations
 Schema |    Name    | Type  |  Owner   
--------+------------+-------+----------
 public | activities | table | postgres
 public | users      | table | postgres
``` 

- Create **db-seed**, add the following code then make it executable
```bash
#! /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-seed-load"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"


seedload_path=$(realpath "$0")
seed_path=($(sed 's/bin\/db-seed//' <<<"$seedload_path")db/seed.sql)

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
