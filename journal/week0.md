# Week 0 — Billing and Architecture

## AWS - Setup

### AWS account 
- created new username and enabled MFA
- attached Administrator and billing permissions 
- generated new access keys

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

### AWS budget

## Diagrams


### Conceptual Diagram


### Architectual Diagram
