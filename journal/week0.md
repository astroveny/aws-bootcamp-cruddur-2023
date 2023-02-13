# Week 0 — Billing and Architecture

## AWS - Setup

### AWS account 
- created new username and enabled MFA
- attached Administrator and billing permissions 
- generated new access keys
```
{
    "Users": [
        {
            "Path": "/",
            "UserName": "bashbc",
            "UserId": "**************UAANOM",
            "Arn": "arn:aws:iam::********4680:user/bashbc",
            "CreateDate": "2023-02-01T08:41:15+00:00",
            "PasswordLastUsed": "2023-02-13T07:27:09+00:00"
        }
    ]
}
```

### AWS CLI
- Installed AWS CLI on my local machine
- Installed AWS CLI on my gitpod
- Added new profile and made it as the defualt profile
```
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ aws sts get-caller-identity
{
    "UserId": "**************UAANOM",
    "Account": "********4680",
    "Arn": "arn:aws:iam::********4680:user/bashbc"
}
```
- Enabled auto-prompt
```
gp env AWS_CLI_AUTO_PROMPT="on-partial"
```

### AWS Billing Alarm
1- **Billing Alerts** is enabled under **Billing Preferences**
2- Created SNS topic for Billing alarm
```
{
    "Topics": [
        {
            "TopicArn": "arn:aws:sns:us-east-1:********4680:5USD_Alarms_Topic"
        }
    ]
}
```
3- Created CloudWatch Alarm

<img width="701" alt="image" src="https://user-images.githubusercontent.com/91587569/218409066-25669ce9-50df-4cdd-bbb5-39e78be3fce2.png">


### AWS budget

## Diagrams


### Conceptual Diagram


### Architectual Diagram
