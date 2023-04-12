#! /bin/bash

#aws reinstall 
cd /workspace
sudo ./aws/install
aws configure set format  json

cd $THEIA_WORKSPACE_ROOT/thumbing-serverless-cdk
npm install aws-cdk -g
cd $THEIA_WORKSPACE_ROOT

#psql reinstall
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc|sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |sudo tee  /etc/apt/sources.list.d/pgdg.list
sudo apt update
sudo apt install -y postgresql-client-13 libpq-dev

# RDS update SG with gitpod IP
export GITPOD_IP="$(curl ifconfig.me)"
source "$THEIA_WORKSPACE_ROOT/backend-flask/bin/rds/rds-update-sg-rule"

cd $THEIA_WORKSPACE_ROOT