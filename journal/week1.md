# Week 1 
## **App Containerization**
- [**Containerize Backend**](#Containerize-Backend)
  1. [Backend Dockerfile](#Backend-Dockerfile)
  2. [Build container](#Build-container)
  3. [Run The Continer](#Run-The-Continer)
  4. [Container Status and Image details](#Container-Status-and-Image-details)
  5. [Test Backend Server Access](#Test-Backend-Server-Access)
  6. [Continer logs to verify access status](#Continer-logs-to-verify-access-status)
  7. [Verify Container Env variables using Bash](#Verify-Container-Env-variables-using-Bash)

- [**Containerize Frontend**](#Containerize-Frontend)
  1. [Install NPM](#Install-NPM)
  2. [Frontend Dockerfile](#Frontend-Dockerfile)
  3. [Update gitpod.yml to install npm](#Update-gitpodyml-to-install-npm)

- [**Multiple Containers**](#Multiple-Containers)
  1. [Create and Build Docker Compose file](#Create-and-Build-Docker-Compose-file)

- [**Create The Notification Feature**](#Create-The-Notification-Feature)
  1. [Add PATH and GET operation to OpenAPI file](#1-Add-PATH-and-GET-operation-to-OpenAPI-file)
  2. [Update the Backend app to with the NEW endpoint](#2-Update-the-Backend-app-with-the-NEW-endpoint)
  3. [Update the Frontend app with the new notifications page](#3-Update-the-Frontend-app-with-the-new-notifications-page)

- [**Postgres and DynamoDB Local Setup**](#Postgres-and-DynamoDB-Local-Setup)
  1.  [Update Docker Compose](#Update-Docker-Compose)
  2.  [Run Docker Compose ](#Run-Docker-Compose)
  3.  [DynamoDB test](#DynamoDB-test)
  4.  [Postgres test](#Postgres-test)

- [**Homework Challenges**](#Homework-Challenges)
  1.  [Docker HUB](#Docker-HUB)
  2.  [Docker on Local machine](#Docker-on-Local-machine)
  3.  [Docker on AWS EC2](#Docker-on-AWS-EC2)
  4.  [Run Dockerfile CMD as an external script](#Run-Dockerfile-CMD-as-an-external-script)
  5.  [Snyk Security Vulnerability Platform](#Snyk-Security-Vulnerability-Platform)


## Containerize Backend
- IDE used is Gitpod 

### Backend Dockerfile 
- Created Dockerfile inside dir: **backend-flask**

### Build container
[Back to top](#Week-1)

>> **NOTE:** output has been reduced!

- Build the _container_ using **Dockerfile**
- Image name: _backend-flask_; Dockerfile location: ./backend-flask


```bash
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ docker build -t backend-flask ./backend-flask
Sending build context to Docker daemon   34.3kB
Step 1/8 : FROM python:3.10-slim-buster
3.10-slim-buster: Pulling from library/python
29cd48154c03: Pull complete 
2c59e55cfd71: Pull complete 
3b4b58298de0: Pull complete 
6239e464c1ab: Pull complete 
047dd5665bb1: Pull complete 
Digest: sha256:6e96825731607f9d49d382e302a78e994d60db2871f3447152f56621069e6114
Status: Downloaded newer image for python:3.10-slim-buster
 ---> b5d627f77479
Step 2/8 : WORKDIR /backend-flask
 ---> Running in 1232727f5d99
Removing intermediate container 1232727f5d99
 ---> 579b4a5547dd
Step 3/8 : COPY requirements.txt requirements.txt
 ---> 0a9906a8099d
Step 4/8 : RUN pip3 install -r requirements.txt
 ---> Running in c3b5d83290d9
Collecting flask
  Downloading Flask-2.2.3-py3-none-any.whl (101 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 101.8/101.8 kB 4.8 MB/s eta 0:00:00
Collecting flask-cors
  Downloading Flask_Cors-3.0.10-py2.py3-none-any.whl (14 kB)
Collecting Werkzeug>=2.2.2
  Downloading Werkzeug-2.2.3-py3-none-any.whl (233 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 233.6/233.6 kB 21.0 MB/s eta 0:00:00
Collecting Jinja2>=3.0
  Downloading Jinja2-3.1.2-py3-none-any.whl (133 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 133.1/133.1 kB 61.1 MB/s eta 0:00:00
Collecting itsdangerous>=2.0
  Downloading itsdangerous-2.1.2-py3-none-any.whl (15 kB)
Collecting click>=8.0
  Downloading click-8.1.3-py3-none-any.whl (96 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 96.6/96.6 kB 39.7 MB/s eta 0:00:00
Collecting Six
  Downloading six-1.16.0-py2.py3-none-any.whl (11 kB)
Collecting MarkupSafe>=2.0
  Downloading MarkupSafe-2.1.2-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (25 kB)
Installing collected packages: Six, MarkupSafe, itsdangerous, click, Werkzeug, Jinja2, flask, flask-cors
Successfully installed Jinja2-3.1.2 MarkupSafe-2.1.2 Six-1.16.0 Werkzeug-2.2.3 click-8.1.3 flask-2.2.3 flask-cors-3.0.10 itsdangerous-2.1.2

...

Removing intermediate container c3b5d83290d9
 ---> 6b554427850a
Step 5/8 : COPY . .
 ---> 39790a1cc628
Step 6/8 : ENV FLASK_ENV=development
 ---> Running in 09eac9d13d28
Removing intermediate container 09eac9d13d28
 ---> dd33c83e82db
Step 7/8 : EXPOSE ${PORT}
 ---> Running in fd0039c86f49
Removing intermediate container fd0039c86f49
 ---> c867aca63d24
Step 8/8 : CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567"]
 ---> Running in d20916157ad9
Removing intermediate container d20916157ad9
 ---> 6a2d3dbb41d2
Successfully built 6a2d3dbb41d2
Successfully tagged backend-flask:latest
```

### Run The Continer
[Back to top](#Week-1)

- Run the container using -e flag to pass the Env var FRONTEND_URL & BACKEND_URL
- Option --rm will cleanup after the container is stop running
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ docker run --rm -p 4567:4567 -it -e FRONTEND_URL='*' -e BACKEND_URL='*' backend-flask
'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:4567
 * Running on http://172.17.0.2:4567
Press CTRL+C to quit
 * Restarting with stat
'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
 * Debugger is active!
 * Debugger PIN: 103-669-471
 ```
 - To run the container in the background, use option -d
 ```bash
 docker container run --rm -p 4567:4567 -d backend-flask
 ```
 - Check if the port is open "solid circle" on the vscode port tab
 <img width="750" height="80" alt="image" src="https://user-images.githubusercontent.com/91587569/219940187-d27e87e8-4c35-489a-80d6-b6e9672d1154.png">

### Container Status and Image details
[Back to top](#Week-1)

- Verify the running processes 
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ docker ps
CONTAINER ID   IMAGE           COMMAND                  CREATED          STATUS          PORTS                                       NAMES
92b6c6200789   backend-flask   "python3 -m flask ru…"   16 minutes ago   Up 16 minutes   0.0.0.0:4567->4567/tcp, :::4567->4567/tcp   wonderful_almeida
```
- Check the Image details
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ docker images
REPOSITORY      TAG                IMAGE ID       CREATED          SIZE
backend-flask   latest             6a2d3dbb41d2   52 minutes ago   129MB
python          3.10-slim-buster   b5d627f77479   10 days ago      118MB
```

### Test Backend Server Access 
[Back to top](#Week-1)

- Used Curl command to access the backend URL link

>> **NOTE:** output has been reduced!
```json
gitpod /workspace/aws-bootcamp-cruddur-2023/frontend-react-js (main) $ curl -X GET http://localhost:4567/api/activities/home -H "Accept: application/json" -H "Content-Type: application/json"
[
  {
    "created_at": "2023-02-17T09:59:20.762944+00:00",
    "expires_at": "2023-02-24T09:59:20.762944+00:00",
    "handle": "Andrew Brown",
    "likes_count": 5,
    "message": "Cloud is fun!",
    "replies": [
 ...
  {
    "created_at": "2023-02-19T08:59:20.762944+00:00",
    "expires_at": "2023-02-19T21:59:20.762944+00:00",
    "handle": "Garek",
    "likes": 0,
    "message": "My dear doctor, I am just simple tailor",
    "replies": [],
    "uuid": "248959df-3079-4947-b847-9e0892d1bab4"
  }
]
```

### Continer logs to verify access status 
[Back to top](#Week-1)

- run the `docker logs` command using the container ID

```bash
gitpod /workspace/aws-bootcamp-cruddur-2023/frontend-react-js (main) $ docker logs 92b6c6200789 -f

 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:4567
 * Running on http://172.17.0.2:4567
Press CTRL+C to quit
 * Restarting with stat
...

 * Debugger is active!
 * Debugger PIN: 103-669-471
172.17.0.1 - - [19/Feb/2023 09:59:20] "GET /api/activities/home HTTP/1.1" 200 -
172.17.0.1 - - [19/Feb/2023 10:05:16] "GET /api/activities/home HTTP/1.1" 200 -
192.168.158.136 - - [19/Feb/2023 10:07:25] "GET / HTTP/1.1" 404 -
192.168.158.136 - - [19/Feb/2023 10:07:26] "GET /favicon.ico HTTP/1.1" 404 -
192.168.158.136 - - [19/Feb/2023 10:07:48] "GET /api/activities/home HTTP/1.1" 200 -
```

### Verify Container Env variables using Bash
[Back to top](#Week-1)

- Access the Container bash shell
  - Run this command `docker ps` to get the **Container ID** or **Name**
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ docker ps
CONTAINER ID   IMAGE           COMMAND                  CREATED             STATUS             PORTS                                       NAMES
92b6c6200789   backend-flask   "python3 -m flask ru…"   About an hour ago   Up About an hour   0.0.0.0:4567->4567/tcp, :::4567->4567/tcp   wonderful_almeida
```
  - Use either the **Container ID** or the **Name**
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ docker exec -it 92b6c6200789 /bin/bash
root@92b6c6200789:/backend-flask# ls
Dockerfile  README.md  __pycache__  app.py  openapi-3.0.yml  requirements.txt  services
```
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ docker exec -it wonderful_almeida /bin/bash
root@92b6c6200789:/backend-flask# ls
Dockerfile  README.md  __pycache__  app.py  openapi-3.0.yml  requirements.txt  service
```

-------------------------------------------------
## Containerize Frontend

### Install NPM 
[Back to top](#Week-1)

- Go to dir: frontend dir then run the `npm i` command to install NPM  
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023/frontend-react-js (main) $ npm i
npm WARN deprecated w3c-hr-time@1.0.2: Use your platform's native performance.now() and performance.timeOrigin.
npm WARN deprecated stable@0.1.8: Modern JS already guarantees Array#sort() is a stable sort, so this library is deprecated. See the compatibility table on MDN: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#browser_compatibility
npm WARN deprecated svgo@1.3.2: This SVGO version is no longer supported. Upgrade to v2.x.x.

added 1471 packages, and audited 1472 packages in 19s

225 packages are looking for funding
  run `npm fund` for details

8 high severity vulnerabilities

To address issues that do not require attention, run:
  npm audit fix

To address all issues (including breaking changes), run:
  npm audit fix --force

Run `npm audit` for details.
npm notice 
npm notice New major version of npm available! 8.19.3 -> 9.5.0
npm notice Changelog: https://github.com/npm/cli/releases/tag/v9.5.0
npm notice Run npm install -g npm@9.5.0 to update!
npm notice 
```

### Frontend Dockerfile 
[Back to top](#Week-1)

- Created Dockerfile inside dir: **frontend-react-js**

### Update gitpod.yml to install npm
[Back to top](#Week-1)

```yml
- name: dependencies
    init: |
      cd $THEIA_WORKSPACE_ROOT/frontend-react-js
      npm i
      cd $THEIA_WORKSPACE_ROOT
```

-----------------------------------
## Multiple Containers

### Create and Build Docker Compose file
[Back to top](#Week-1)

- Created docker-compose.yml file at the root dir:
- This compose file will build images using the dockerfile inside backend-flask and frontend-react-js
- Run the below compose command to build all coontainers in the compose file
 - `docker compose -f "docker-compose.yml" up -d --build` 
>> **NOTE:** output has been reduced!

```bash
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ docker compose -f "docker-compose.yml" up -d --build
[+] Building 42.2s (18/18) FINISHED                                                                                                                                    
 => [aws-bootcamp-cruddur-2023-backend-flask internal] load build definition from Dockerfile                                                                      0.0s
 => => transferring dockerfile: 669B                                                                                                                              0.0s
 => [aws-bootcamp-cruddur-2023-frontend-react-js internal] load build definition from Dockerfile                                                                  0.0s
 => => transferring dockerfile: 175B                                                                                                                              0.0s
 => [aws-bootcamp-cruddur-2023-backend-flask internal] load .dockerignore                                                                                         0.0s
 => => transferring context: 2B                                                                                                                                   0.0s
 => [aws-bootcamp-cruddur-2023-frontend-react-js internal] load .dockerignore                                                                                     0.0s
 => => transferring context: 2B                                                                                                                                   0.0s
 => [aws-bootcamp-cruddur-2023-backend-flask internal] load metadata for docker.io/library/python:3.10-slim-buster                                                0.0s
 => [aws-bootcamp-cruddur-2023-backend-flask 1/5] FROM docker.io/library/python:3.10-slim-buster                                                                  0.1s
 => [aws-bootcamp-cruddur-2023-backend-flask internal] load build context                                                                                         0.0s
 => => transferring context: 20.15kB                                                                                                                              0.0s
 => [aws-bootcamp-cruddur-2023-frontend-react-js internal] load metadata for docker.io/library/node:16.18                                                         0.9s
 => [aws-bootcamp-cruddur-2023-backend-flask 2/5] WORKDIR /backend-flask                                                                                          0.0s
 => [aws-bootcamp-cruddur-2023-backend-flask 3/5] COPY requirements.txt requirements.txt                                                                          0.0s
 => [aws-bootcamp-cruddur-2023-backend-flask 4/5] RUN pip3 install -r requirements.txt                                                                           10.3s
 => [aws-bootcamp-cruddur-2023-frontend-react-js internal] load build context                                                                                    12.0s
 => => transferring context: 239.36MB                                                                                                                            11.9s
 => [aws-bootcamp-cruddur-2023-frontend-react-js 1/4] FROM docker.io/library/node:16.18@sha256:7f404d09ceb780c51f4fac7592c46b8f21211474aacce25389eb0df06aaa7472  26.5s
 => => resolve docker.io/library/node:16.18@sha256:7f404d09ceb780c51f4fac7592c46b8f21211474aacce25389eb0df06aaa7472                                               0.0s
  ...
  => [aws-bootcamp-cruddur-2023-backend-flask 5/5] COPY . .                                                                                                        0.3s
 => [aws-bootcamp-cruddur-2023-frontend-react-js] exporting to image                                                                                              8.4s
 => => exporting layers                                                                                                                                           7.0s
 => => writing image sha256:04592910d79bcf83505bfc0cfa529089e1549fada0e4e6d35a9fd673463de700                                                                      0.0s
 => => naming to docker.io/library/aws-bootcamp-cruddur-2023-backend-flask                                                                                        0.0s
 => => writing image sha256:cd73f0808316f3c0ca186ba2908228c76af236c8567b8bc17dc1a411ac9e5654                                                                      0.0s
 => => naming to docker.io/library/aws-bootcamp-cruddur-2023-frontend-react-js                                                                                    0.0s
 => [aws-bootcamp-cruddur-2023-frontend-react-js 2/4] COPY . /frontend-react-js                                                                                   4.2s
 => [aws-bootcamp-cruddur-2023-frontend-react-js 3/4] WORKDIR /frontend-react-js                                                                                  0.0s
 => [aws-bootcamp-cruddur-2023-frontend-react-js 4/4] RUN npm install                                                                                             3.5s
[+] Running 3/3
 ⠿ Network aws-bootcamp-cruddur-2023_default                Created                                                                                               0.0s
 ⠿ Container aws-bootcamp-cruddur-2023-backend-flask-1      Started                                                                                               0.5s
 ⠿ Container aws-bootcamp-cruddur-2023-frontend-react-js-1  Started                                                                                               0.6s
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ 
```

- The application can be accessed using the frontend link
<img width="750" height="400" alt="image" src="https://user-images.githubusercontent.com/91587569/219944324-216bcb55-98dd-40b7-827e-b7a5cbe6c375.png">

- Frontend and backend ports are open
<img width="750" height="120" alt="image" src="https://user-images.githubusercontent.com/91587569/219944209-7f8e47a9-0012-4200-89aa-24a44ba9d166.png">


### Create The Notification Feature

#### **1. Add PATH and GET operation to OpenAPI file**
[Back to top](#Week-1)

- Open openapi-3.0.yml under /backend-flask
- Used OpenAPI vscode extension to add NEW APTH `/api/activities/notifications` inside openapi-3.0.yml
- Added GET operation
```yml
  /api/activities/notifications:
    get:
      description: 'Return a feed of activity for all of those I follow'
      tags:
        - activities
      parameters: []
      responses:
        '200':
          description: Resturns an array of activities 
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Activity'
```                  
- Commit and push to github repo

#### **2. Update the Backend app with the NEW endpoint**
[Back to top](#Week-1)

>> **NOTE:** output has been reduced!


- Create new notifications service by creating python file under dir: services (_notifications_activities.py_)
- Copy the content of _home_activities.py_ to _notifications_activities.py_
- Change the class name **NotificationsActivities**  
- Change the handle and the message


```python
from datetime import datetime, timedelta, timezone
class NotificationsActivities:
  def run():
    now = datetime.now(timezone.utc).astimezone()
    results = [{
      'uuid': '68f126b0-1ceb-4a33-88be-d90fa7109eee',
      'handle':  'Coco',
      'message': 'Remember Meeeee!',
    ... 
```
- Update **app.py** by adding a new route with notifications PATH & GET method for the notification service
```python
@app.route("/api/activities/notifications", methods=['GET'])
def data_notifications():
  data = NotificationsActivities.run()
  return data, 200
```
- Commit & push to Github

#### **3. Update the Frontend app with the new notifications page**
[Back to top](#Week-1)

>> **NOTE:** output has been reduced!

- Create new files for the notifications page under /frontend-react-js/src/pages (_NotificationsFeedPage.js; NotificationsFeedPage.css_)
- Update **App.js** to import the notifications page and add route
```js
import HomeFeedPage from './pages/HomeFeedPage';
import NotificationsFeedPage from './pages/NotificationsFeedPage';
...
const router = createBrowserRouter([
 ...
  {
    path: "/notifications",
    element: <NotificationsFeedPage />
  },
  ```
- Copy the conent from _HomeFeePage.js_ to _NotificationsFeedPage.js_
- Change css file to `./NotificationsFeedPage.css`
- Change `HomeFeedPage()` to `NotificationsFeedPage()`
- Change bacnkend_url to `/api/activities/notifications`
- Change the ActivityFeed title to `Notifications`
- Commit & push to Github

```js
import './NotificationsFeedPage.css';
import React from "react";
... 
// [TODO] Authenication
import Cookies from 'js-cookie'

export default function NotificationsFeedPage() {
  const [activities, setActivities] = React.useState([]);
...
  const loadData = async () => {
    try {
      const backend_url = `${process.env.REACT_APP_BACKEND_URL}/api/activities/notifications`
      const res = await fetch(backend_url, {
        method: "GET"
      });
...
  return (
    <article>
      <DesktopNavigation user={user} active={'home'} setPopped={setPopped} />
      ...
        <ActivityFeed 
          title="Notifications" 
          setReplyActivity={setReplyActivity} 
          setPopped={setPoppedReply} 
          activities={activities} 
        />
      </div>
      <DesktopSidebar user={user} />
    </article>
  );
}
```

![noti-page](https://user-images.githubusercontent.com/91587569/220592422-f979394a-93a7-4dc3-b8a7-7e7d0f2c6c7a.png)



### Postgres and DynamoDB Local Setup
[Back to top](#Week-1)

#### Update Docker Compose 
[Back to top](#Week-1)

- Updated `docker-compose.yml` with Postgres and DynamoDB service
- Updated `gitpod.yml` to install Postgres client

#### Run Docker Compose 
[Back to top](#Week-1)

- Run `docker compose up -d` to _start the containers_
- Check _Containers status_
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ docker ps
CONTAINER ID   IMAGE                                         COMMAND                  CREATED          STATUS          PORTS                                       NAMES
3594a1f6f050   aws-bootcamp-cruddur-2023-backend-flask       "python3 -m flask ru…"   42 minutes ago   Up 42 minutes   0.0.0.0:4567->4567/tcp, :::4567->4567/tcp   aws-bootcamp-cruddur-2023-backend-flask-1
fe92db498a14   aws-bootcamp-cruddur-2023-frontend-react-js   "docker-entrypoint.s…"   42 minutes ago   Up 42 minutes   0.0.0.0:3000->3000/tcp, :::3000->3000/tcp   aws-bootcamp-cruddur-2023-frontend-react-js-1
0f4a18bd5591   postgres:13-alpine                            "docker-entrypoint.s…"   42 minutes ago   Up 42 minutes   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   aws-bootcamp-cruddur-2023-db-1
dd099412103f   amazon/dynamodb-local:latest                  "java -jar DynamoDBL…"   42 minutes ago   Up 42 minutes   0.0.0.0:8000->8000/tcp, :::8000->8000/tcp   dynamodb-local
```
- Open the **ports**

<img  alt="image" src="https://user-images.githubusercontent.com/91587569/220661323-84d6bb43-43cb-49e4-8847-65a9dc530eaa.png">

#### DynamoDB test
[Back to top](#Week-1)

- Create new table, Create new item and List tables

```json
gitpod /workspace $ aws dynamodb create-table --endpoint-url http://localhost:8000 --table-name Music --attribute-definitions AttributeName=Artist,AttributeType=S \
         AttributeName=SongTitle,AttributeType=S \
     --key-schema AttributeName=Artist,KeyType=HASH AttributeName=SongTitle,KeyType=RANGE \
     --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 \
     --table-class STANDARD
{
    "TableDescription": {
        "AttributeDefinitions": [
            {
                "AttributeName": "Artist",
                "AttributeType": "S"
            },
            {
                "AttributeName": "SongTitle",
                "AttributeType": "S"
            }
        ],
        "TableName": "Music",
```

```json
gitpod /workspace $ aws dynamodb put-item --endpoint-url http://localhost:8000 --table-name Music \
     --item \
         '{"Artist": {"S": "No One You Know"}, "SongTitle": {"S": "Call Me Today"}, "AlbumTitle": {"S": "Somewhat Famous"}}' \
     --return-consumed-capacity TOTAL  
{
    "ConsumedCapacity": {
        "TableName": "Music",
        "CapacityUnits": 1.0
    }
}
```

```json
gitpod /workspace $ aws dynamodb list-tables --endpoint-url http://localhost:8000
{
    "TableNames": [
        "Music"
    ]
}
```

#### Postgres test
[Back to top](#Week-1)

- Connect using Postgres vscode ext and using `psql`
```sql
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ psql -U postgres -h localhost
Password for user postgres: 
psql (13.10 (Ubuntu 13.10-1.pgdg20.04+1))
Type "help" for help.

postgres-# \l
                                 List of databases
   Name    |  Owner   | Encoding |  Collate   |   Ctype    |   Access privileges   
-----------+----------+----------+------------+------------+-----------------------
 postgres  | postgres | UTF8     | en_US.utf8 | en_US.utf8 | 
 template0 | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
           |          |          |            |            | postgres=CTc/postgres
 template1 | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
           |          |          |            |            | postgres=CTc/postgres
(3 rows)

postgres-# \q
```

<img  alt="image" src="https://user-images.githubusercontent.com/91587569/220658100-8b954577-6dbe-4652-8b50-d27da9bc4ff9.png">


-------------------------------------------
## Homework Challenges


### Docker HUB
[Back to top](#Week-1)

- Connected my Docker ID on **Docker HUB** to the Registries  
- **Run** `docker image push` to push images to **Docker HUB**

>> **NOTE:** output has been reduced!
```bash
Executing task: docker image push astroveny/aws-bootcamp-cruddur-2023-backend-flask:latest 

The push refers to repository [docker.io/astroveny/aws-bootcamp-cruddur-2023-backend-flask]
001a2d96d6f8: Mounted from astroveny/aws-cloud-bootcamp 
...
63b3cf45ece8: Mounted from astroveny/aws-cloud-bootcamp 
latest: digest: sha256:8155931b69d8c34cda11b8179dee945035ab2d256b48443dea6192a14d44820d size: 2203
 *  Terminal will be reused by tasks, press any key to close it. 
 ```
```bash
 Executing task: docker image push astroveny/aws-bootcamp-cruddur-2023-frontend-react-js:latest 

The push refers to repository [docker.io/astroveny/aws-bootcamp-cruddur-2023-frontend-react-js]
27b2d1768a0d: Pushed 
5f70bf18a086: Pushed 
...
3943af3b0cbd: Mounted from library/node 
latest: digest: sha256:5fe6c9b699f542e358a25fea6ba9415503ae24ebafaa747a8e23b8ec32a8d030 size: 2844
```
- _List all Images_ by running this command
```bash
itpod /workspace/aws-bootcamp-cruddur-2023 (main) $ docker image ls
REPOSITORY                                              TAG       IMAGE ID       CREATED             SIZE
astroveny/aws-bootcamp-cruddur-2023-frontend-react-js   latest    0de30b6fd9d1   About an hour ago   1.15GB
aws-bootcamp-cruddur-2023-frontend-react-js             latest    0de30b6fd9d1   About an hour ago   1.15GB
astroveny/aws-bootcamp-cruddur-2023-backend-flask       latest    588e2bf137b2   About an hour ago   129MB
aws-bootcamp-cruddur-2023-backend-flask                 latest    588e2bf137b2   About an hour ago   129MB
```

### Docker on Local machine
[Back to top](#Week-1)

- Connected **Docker HUB** to the local docker using vscode Docker extension 
<img width="300" alt="image" src="https://user-images.githubusercontent.com/91587569/220380760-6f87df63-2280-4d8e-a7fb-f1b913dfbec3.png">

- **Pull** Images from **Docker HUB**
```bash
Executing task in folder Temp: docker image pull astroveny/aws-bootcamp-cruddur-2023-backend-flask:latest 

latest: Pulling from astroveny/aws-bootcamp-cruddur-2023-backend-flask
29cd48154c03: Pull complete
...
95fad5820345: Pull complete
Digest: sha256:8155931b69d8c34cda11b8179dee945035ab2d256b48443dea6192a14d44820d
Status: Downloaded newer image for astroveny/aws-bootcamp-cruddur-2023-backend-flask:latest
docker.io/astroveny/aws-bootcamp-cruddur-2023-backend-flask:latest
```
- **Run** the Backend-flask container
```bash
$ docker run --rm -p 4567:4567 -it -e FRONTEND_URL='*' -e BACKEND_URL='*' -d astroveny/aws-bootcamp-cruddur-2023-backend-flask:latest 
382f7187efe990fcaf6b9c7398fa002a1f6f822a50a127db53aaccf92d1af3a5
```

- **Test Backend Server Access** - 

>> **NOTE:** output has been reduced!
```json
$ curl -X GET http://localhost:4567/api/activities/home -H "Accept: application/json" -H "Contencurl -X GET http://localhost:4567/api/activit-Type: application/json"
[
  {
    "created_at": "2023-02-19T14:49:14.867118+00:00",
    "expires_at": "2023-02-26T14:49:14.867118+00:00",
    "handle": "Andrew Brown",
    "likes_count": 5,
    "message": "Cloud is fun!",
    "replies": [
      {
...
  {
    "created_at": "2023-02-21T13:49:14.867118+00:00",
    "expires_at": "2023-02-22T02:49:14.867118+00:00",
    "handle": "Garek",
    "likes": 0,
    "message": "My dear doctor, I am just simple tailor",
    "replies": [],
    "uuid": "248959df-3079-4947-b847-9e0892d1bab4"
  }
]
```

- Check the **logs** output
```bash
$ docker logs 382f7187efe9 -f
 * Debugger is active!
 * Debugger PIN: 126-737-939
172.17.0.1 - - [21/Feb/2023 14:47:22] "GET /api/activities/home HTTP/1.1" 200 -
172.17.0.1 - - [21/Feb/2023 14:49:14] "GET /api/activities/home HTTP/1.1" 200 -
```

### Docker on AWS EC2
[Back to top](#Week-1)

>> **NOTE:** output has been reduced!

#### Create EC2 instance

- Launched new t2.micro instance "Container-engine" using the below:
  - AMI: Amazon Linux 2 Kernel 5.10
  - created new key pair
  - default VPC - subnet us-east-1a
  - created new security group: CE-SG
  - enabled auto-assign public IP
<img  alt="image" src="https://user-images.githubusercontent.com/91587569/221221470-2bfdbbf6-f848-4815-ba06-8abe586bb75e.png">

- Security Group Inbound rules: enabled _external access_ to **SSH** to access the instance and port **4567** to access the backend
<img  alt="image" src="https://user-images.githubusercontent.com/91587569/221222022-85962f69-bb9f-4586-ba6c-26a8d78433c7.png">
>> NOTE: Terminated the instance & deleted the SG after the lab has been completed
#### Prepare Gitpod
- created new dir "aws" under the repo root
- uploaded the key pair to the new dir (right-click the vscode Explorer then click upload)
>> NOTE: deleted dir aws and the key pair after the lab has been completed

#### Connect to the Instance
- Connected to the instance via SSH using the public IP and the key pair

`gitpod /workspace/aws-bootcamp-cruddur-2023/aws (main) $ sudo ssh -i keypair.pem ec2-user@34.205.4.197`


#### Install Docker
- Run the below command to install docker on the instance
```bash
[ec2-user@ip-172-31-10-129 ~]$ sudo yum update
[ec2-user@ip-172-31-10-129 ~]$ sudo yum install docker
```
- Run the docker daemon
```bash
[ec2-user@ip-172-31-10-129 ~]$ sudo systemctl start docker.service
[ec2-user@ip-172-31-10-129 ~]$ docker ps
Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.24/containers/json": dial unix /var/run/docker.sock: connect: permission denied
```
- Add ec2-user to the docker group 
```bash
[ec2-user@ip-172-31-10-129 ~]$ sudo usermod -a -G docker ec2-user
[ec2-user@ip-172-31-10-129 ~]$ id ec2-user
uid=1000(ec2-user) gid=1000(ec2-user) groups=1000(ec2-user),4(adm),10(wheel),190(systemd-journal),992(docker)
[ec2-user@ip-172-31-10-129 ~]$ newgrp docker
[ec2-user@ip-172-31-10-129 ~]$ docker ps
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

#### Connect to Docker HUB and Pull the container
- Connect to Docker HUB
```bash
[ec2-user@ip-172-31-10-129 ~]$ docker login -u astroveny
Password: 
...
Login Succeeded
```
- Pull the image
```bash
[ec2-user@ip-172-31-10-129 ~]$ docker image pull astroveny/aws-bootcamp-cruddur-2023-backend-flask:latest 
latest: Pulling from astroveny/aws-bootcamp-cruddur-2023-backend-flask
```

#### Run the container
```bash
[ec2-user@ip-172-31-10-129 ~]$ docker run  --rm -p 4567:4567 -it -e FRONTEND_URL='*' -e BACKEND_URL='*' -d astroveny/aws-bootcamp-cruddur-2023-backend-flask:latest 
845cfdb7e4e59eb74f94cb02bff87f371658c8cfac1bc024fdb986952e279467
[ec2-user@ip-172-31-10-129 ~]$ docker ps
CONTAINER ID   IMAGE                                                      COMMAND                  CREATED          STATUS          PORTS                                       NAMES
845cfdb7e4e5   astroveny/aws-bootcamp-cruddur-2023-backend-flask:latest   "python3 -m flask ru…"   23 seconds ago   Up 22 seconds   0.0.0.0:4567->4567/tcp, :::4567->4567/tcp   unruffled_chatterjee
```

#### Test access to the Backend
```json
[ec2-user@ip-172-31-10-129 ~]$ curl -X GET http://ec2-34-205-4-197.compute-1.amazonaws.com:4567/api/activities/home -H "Accept: application/json" 
[
  {
    "created_at": "2023-02-22T15:23:58.473125+00:00",
    "expires_at": "2023-03-01T15:23:58.473125+00:00",
    "handle": "Andrew Brown",
    "likes_count": 5,
    "message": "Cloud is fun!",
    "replies": [
...
  {
    "created_at": "2023-02-24T14:23:58.473125+00:00",
    "expires_at": "2023-02-25T03:23:58.473125+00:00",
    "handle": "Garek",
    "likes": 0,
    "message": "My dear doctor, I am just simple tailor",
    "replies": [],
    "uuid": "248959df-3079-4947-b847-9e0892d1bab4"
  }
]
```
<img alt="image" src="https://user-images.githubusercontent.com/91587569/221227838-74080644-79b6-434b-9f6d-338bd075cbbf.png">

#### Container Logs verification
```bash
[ec2-user@ip-172-31-10-129 ~]$ docker logs 845cfdb7e4e5
...
87.200.181.26 - - [24/Feb/2023 15:20:53] "GET /api/activities/home HTTP/1.1" 200 -
172.31.10.129 - - [24/Feb/2023 15:23:58] "GET /api/activities/home HTTP/1.1" 200 -
```

### Run Dockerfile CMD as an external script
[Back to top](#Week-1)

1. Create new dir "extcmd" under backend-flask
2. Created Dockerfile & flaskapp.sh files inside extcmd
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ tree extcmd/
extcmd/
├── Dockerfile
└── flaskapp.sh
```
4. [Dockerfile content](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/main/backend-flask/extcmd/Dockerfile)
5. [flaskapp.sh content](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/main/backend-flask/extcmd/flaskapp.sh)
6. Build the image and point to the new Dockerfile
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ docker build -t ext-backend-flask -f extcmd/Dockerfile .
...
 ---> 283f168e3baf
Step 9/9 : CMD ./flaskapp.sh
 ---> Running in f7b23a6d3f48
Removing intermediate container f7b23a6d3f48
 ---> 69e4bcc710d0
Successfully built 69e4bcc710d0
Successfully tagged ext-backend-flask:latest
```
8. Run the container using the new image
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ docker run --rm -p 4567:4567 -it -e FRONTEND_URL='*' -e BACKEND_URL='*' -d ext-backend-flask 
```
10. Check the container status
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ docker ps
CONTAINER ID   IMAGE               COMMAND                  CREATED          STATUS          PORTS                                       NAMES
91e04fb5fe60   ext-backend-flask   "/bin/sh -c ./flaska…"   12 seconds ago   Up 10 seconds   0.0.0.0:4567->4567/tcp, :::4567->4567/tcp   relaxed_buck
```
12. Open the port
<img  alt="image" src="https://user-images.githubusercontent.com/91587569/220949583-cc87a0e1-361e-4a84-8edf-0508faa13602.png">

14. Access the backend app URL
<img width="600" height="200" alt="image" src="https://user-images.githubusercontent.com/91587569/220949646-4c955c09-2c8a-476d-bd16-dd3d48520011.png">




### Snyk Security Vulnerability Platform

- Intigrate with Github: create Snyk account using Github
- Import and Scan the Repo from Github
![Snyk-dashboard](https://user-images.githubusercontent.com/91587569/221202095-9b4b5d9d-a85a-4b6e-8bb7-beda86979d3b.jpg)

[Back to top](#Week-1)
