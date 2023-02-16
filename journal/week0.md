# Week 0  
## **Billing and Architecture**

- [**AWS Setup**](#AWS-Setup)

    1. [AWS account](#AWS-account)
    2. [AWS CLI](#AWS-CLI)
    3. [AWS Billing Alarm](#AWS-Billing-Alarm)
    4. [AWS budget](#AWS-budget)
      
- [**Diagrams**](#Diagrams)

    1. [Conceptual Diagram](#Conceptual-Diagram)
    2. [Logical Diagram](#Logical-Diagram)
      
- [**Homework Challenges**](#Homework-Challenges)

    1. [EventBridge rule and Health Dashboard](#EventBridge-rule-and-Health-Dashboard)

## AWS Setup

### AWS account 
- Created MFA for the root user
- Created OU and enabled SCP "as a best prectice"
- Created SCP Policy to restrict root access to some of the major services:` "ec2:*","s3:*","rds:*","lambda:*","apigateway:*"`
- Created new username and enabled MFA
- Attached Administrator and billing permissions 
```json
$ aws iam list-attached-user-policies --user-name bashbc
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
```json
$ aws iam list-access-keys --user-name bashbc
{
    "AccessKeyMetadata": [
        {
            "UserName": "bashbc",
            "AccessKeyId": "****************FJXP",
            "Status": "Active",
            "CreateDate": "2023-02-01T08:42:26+00:00"
        }
    ]
}
```
```
 Name                    Value             Type    Location
      ----                    -----             ----    --------
   profile                   bashbc              env    ['AWS_PROFILE', 'AWS_DEFAULT_PROFILE']
access_key     ****************FJXP shared-credentials-file
secret_key     ****************Om6d shared-credentials-file
    region                us-east-1      config-file    ~/.aws/config
```

### AWS CLI
[Back to top](#Week-0)

- Installed **AWS CLI** on my local machine
- Updated .gitpod.yml to install AWS CLI on **Gitpod**
- Updated _Env_ using `gp env` with the required keys and region then added auto-prompt
```
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ env | grep AWS
AWS_PROFILE=bashbc
AWS_DEFAULT_REGION=us-east-1
AWS_CLI_AUTO_PROMPT=on-partial
AWS_SECRET_ACCESS_KEY=****************Om6d
AWS_ACCESS_KEY_ID=****************FJXP
```

```
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ aws sts get-caller-identity
{
    "UserId": "**************UAANOM",
    "Account": "********4680",
    "Arn": "arn:aws:iam::********4680:user/bashbc"
}
```

### AWS Billing Alarm
[Back to top](#Week-0)

1- **Billing Alerts** is enabled under **Billing Preferences**

2- Enabled _Free Tier Usage Alerts_

3- Created **SNS** topic for **Billing alarm**
```
 aws sns list-subscriptions-by-topic --topic-arn arn:aws:sns:us-east-1:********4680:5USD_Alarms_Topic
{
    "Subscriptions": [
        {
            "SubscriptionArn": "arn:aws:sns:us-east-1:********4680:5USD_Alarms_Topic:f6194315-****-****-****-0dc5c70e7206",
            "Owner": "********4680",
            "Protocol": "email",
            "Endpoint": "b*********@gmail.com",
            "TopicArn": "arn:aws:sns:us-east-1:********4680:5USD_Alarms_Topic"
        }
    ]
}
```
3- Created **CloudWatch Alarm**
- Billing alarm based on "Total Estimated Charge" **Metric**
<img width="1000" height="200" alt="image" src="https://user-images.githubusercontent.com/91587569/218409066-25669ce9-50df-4cdd-bbb5-39e78be3fce2.png">

### AWS budget
[Back to top](#Week-0)

- Created new monthly budget up to 5$ with 70% and 100% alerts

<img width="800" alt="image" src="https://user-images.githubusercontent.com/91587569/218413070-e6bfa3ca-701f-4465-b1c8-6b8e55554315.png">
<img width="800" alt="image" src="https://user-images.githubusercontent.com/91587569/219297977-94229613-f110-412f-9d79-225aa4166e77.png">


------------------------------------------------------------

## Diagrams
[Back to top](#Week-0)

### Conceptual Diagram
[**>>>Lucid Diagram link<<<**](https://lucid.app/lucidchart/74082cf6-c0c6-47e7-9b9e-f83b876e4cb7/edit?viewport_loc=-11%2C-65%2C1899%2C949%2C0_0&invitationId=inv_62050072-7316-4fc9-9d31-c386a15ce3f2)

![conceptual-diagram-1](https://user-images.githubusercontent.com/91587569/218745388-df375c03-9c90-42f2-ac79-0f4d75af2113.jpg)



### Logical Diagram
[Back to top](#Week-0)

[**>>>Lucid Diagram link<<<**](https://lucid.app/lucidchart/e5acf940-a099-4d9c-9fc0-88449ae6e8b0/edit?viewport_loc=-67%2C-45%2C1899%2C949%2C0_0&invitationId=inv_af632fe7-5697-4f34-a0a6-93316babc2fa)

![logical-diagram-1](https://user-images.githubusercontent.com/91587569/218745437-be6175c5-a960-4ff4-a310-aea584201349.jpg)

----------------------------------------------------

## Homework Challenges
[Back to top](#Week-0)

### EventBridge rule and Health Dashboard
- This rule will monitor AWS services health and send notification using SNS when there is a service health issue

**EventBridge rule**
```
aws events list-rules
{
    "Rules": [
        {
            "Name": "HC",
            "Arn": "arn:aws:events:us-east-1:********4680:rule/HC",
            "EventPattern": "{\"source\":[\"aws.health\"],\"detail-type\":[\"AWS Health Event\"],\"detail\":{\"service\":[\"*\"],\"eventTypeCategory\":[\"issue\"]}}",
            "State": "ENABLED",
            "Description": "health check",
            "EventBusName": "default"
        }
    ]
}
```

**SNS topic**
```
aws sns list-subscriptions-by-topic --topic-arn arn:aws:sns:us-east-1:********4680:HC
{
    "Subscriptions": [
        {
            "SubscriptionArn": "arn:aws:sns:us-east-1:********4680:HC:e45fc931-****-****-****-350bf9e13e32",
            "Owner": "********4680",
            "Protocol": "email",
            "Endpoint": "b************@gmail.com",
            "TopicArn": "arn:aws:sns:us-east-1:********4680:HC"
        }
    ]
}
```


### CodeCommit Repo setup
- Created new repo in **CodeCommit**
- Generated HTTPS Git credentials in **IAM**
<img width="800" alt="image" src="https://user-images.githubusercontent.com/91587569/219358485-aeaff976-2381-4123-be07-f3a473126c53.png">

- Generated SSH key for **CodeCommit**
```bash
$ ssh-keygen -t rsa -b 4096 -C b******@gmail.com
Generating public/private rsa key pair.
Enter file in which to save the key (/c/Users/***/.ssh/id_rsa): /c/Users/***/.ssh/codecommit_rsa
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /c/Users/***/.ssh/codecommit_rsa
Your public key has been saved in /c/Users/***/.ssh/codecommit_rsa.pub
The key fingerprint is:
SHA256:************************/MuwONy+TYVbbmI7vOY b******@gmail.com
The key's randomart image is:
+---[RSA 4096]----+
|o+.              |
|+..              |
|+   .            |
| . . . .         |
|o.. o o S        |
|+.  . B          |
|.+o+.* o         |
|=.=.*@+=         |
|.o.***E          |
+----[SHA256]-----+

$ ssh  git-codecommit.us-east-1.amazonaws.com
Enter passphrase for key '/c/Users/*****/.ssh/codecommit_rsa':
You have successfully authenticated over SSH. You can use Git to interact with AWS CodeCommit. Interactive shells are not supported.Connection to git-codecommit.us-east-1.amazonaws.com closed by remote host.
Connection to git-codecommit.us-east-1.amazonaws.com closed.

```
- Cloned the repo to my local machine
```Shell
$ git clone ssh://******FCH2@git-codecommit.us-east-1.amazonaws.com/v1/repos/cloud-bc repo-bc/
Cloning into 'repo-bc'...******FCH2@git-codecommit.us-east-1.amazonaws.com/v1/repos/cloud-bc repo-bc/
Enter passphrase for key '/c/Users/******/.ssh/codecommit_rsa':
warning: You appear to have cloned an empty repository.
```
>> This preparation might be useful during CI\CD stage in week 9
