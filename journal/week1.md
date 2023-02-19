# Week 1 
## ** App Containerization**


## Containerize Backend
- We will perform the below steps on Gitpod workspace

### Backend Dockerfile 
- Created Dockerfile inside **backend-flask**

### Build container
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

### Run Continer

- Run the container using -g flag to pass the Env var FRONTEND_URL & BACKEND_URL
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
 - To tun the container in the background, use option -d
 ```bash
 docker container run --rm -p 4567:4567 -d backend-flask
 ```
 - Check if the port is open "solid circle" on the vscode port tab
 <img width="750" height="80" alt="image" src="https://user-images.githubusercontent.com/91587569/219940187-d27e87e8-4c35-489a-80d6-b6e9672d1154.png">

### Container Status and Image details
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


## Containerize Frontend

### Install NPM under frontend dir

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
