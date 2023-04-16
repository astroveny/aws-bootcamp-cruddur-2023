# import from dockerhub
FROM 235696014680.dkr.ecr.us-east-1.amazonaws.com/cruddur-python:3.10-slim-buster

#create new dir inside the contianer
WORKDIR /backend-flask

#copy from the host to the container
COPY requirements.txt requirements.txt
#install lib dependency inside the container  
RUN pip3 install -r requirements.txt

#copy . from the host (~/local dir)  to . (local dir) inside the container 
COPY . .

#ephemeral Env vars insde the container 
#ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

EXPOSE ${PORT}

ENV PYTHONBUFFERED=1

#run the command with the options and arguments
#this will run: python3 -m flask run --host=0.0.0.0 --port=4567
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567"]