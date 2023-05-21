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

