# Week 0 — Billing and Architecture

## AWS - Setup

### AWS account 
- Created MFA for the root user
- Created OU and enabled SCP "as a best prectice"
- Created SCP Policy to restrict root access to some of the major services:` "ec2:*","s3:*","rds:*","lambda:*","apigateway:*"`
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

2- Enabled _Free Tier Usage Alerts_

3- Created **SNS** topic for **Billing alarm**
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

<img width="1000" height="200" alt="image" src="https://user-images.githubusercontent.com/91587569/218409066-25669ce9-50df-4cdd-bbb5-39e78be3fce2.png">

### AWS budget
- Created new monthly budget up to 5$ with 70% and 100% alerts

<img width="800" alt="image" src="https://user-images.githubusercontent.com/91587569/218413070-e6bfa3ca-701f-4465-b1c8-6b8e55554315.png">

------------------------------------------------------------

## Diagrams

### Conceptual Diagram
[**>>>Lucid Diagram link<<<**](https://lucid.app/lucidchart/74082cf6-c0c6-47e7-9b9e-f83b876e4cb7/edit?viewport_loc=-11%2C-65%2C1899%2C949%2C0_0&invitationId=inv_62050072-7316-4fc9-9d31-c386a15ce3f2)

![conceptual-diagram-1](https://user-images.githubusercontent.com/91587569/218745388-df375c03-9c90-42f2-ac79-0f4d75af2113.jpg)



### Logical Diagram
[**>>>Lucid Diagram link<<<**](https://lucid.app/lucidchart/e5acf940-a099-4d9c-9fc0-88449ae6e8b0/edit?viewport_loc=-67%2C-45%2C1899%2C949%2C0_0&invitationId=inv_af632fe7-5697-4f34-a0a6-93316babc2fa)

![logical-diagram-1](https://user-images.githubusercontent.com/91587569/218745437-be6175c5-a960-4ff4-a310-aea584201349.jpg)
