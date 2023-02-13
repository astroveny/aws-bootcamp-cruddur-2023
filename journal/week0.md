# Week 0 — Billing and Architecture

## AWS - Setup

### AWS account 
- Created new username and enabled MFA
- Attached Administrator and billing permissions 
```
aws iam list-attached-user-policies --user-name bashbc
{
    "AttachedPolicies": [
        {
            "PolicyName": "AdministratorAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AdministratorAccess"
        },
        {
            "PolicyName": "Billing",
            "PolicyArn": "arn:aws:iam::aws:policy/job-function/Billing"
        },
        {
            "PolicyName": "AWSBudgetsActionsWithAWSResourceControlAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSBudgetsActionsWithAWSResourceControlAccess"
        }
    ]
}
```
- Generated new access keys
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
- Installed **AWS CLI** on my local machine
- Updated .gitpod.yml to install AWS CLI on **Gitpod**
- Updated _Env_ and added new _profile_ as the defualt profile
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

2- Created **SNS** topic for **Billing alarm**
```
{
    "Topics": [
        {
            "TopicArn": "arn:aws:sns:us-east-1:********4680:5USD_Alarms_Topic"
        }
    ]
}
```
3- Created **CloudWatch Alarm**

<img width="701" alt="image" src="https://user-images.githubusercontent.com/91587569/218409066-25669ce9-50df-4cdd-bbb5-39e78be3fce2.png">

### AWS budget
- Created new monthly budget up to 5$ with 70% and 100% alerts

<img width="500" alt="image" src="https://user-images.githubusercontent.com/91587569/218413070-e6bfa3ca-701f-4465-b1c8-6b8e55554315.png">



## Diagrams


### Conceptual Diagram
![Untitled Diagram drawio](https://user-images.githubusercontent.com/91587569/218457059-fe8bdd06-aa7f-4e2a-aece-353a94663935.png)


### Architectual Diagram
