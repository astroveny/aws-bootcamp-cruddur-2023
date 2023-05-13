# Week 10 


## CloudFormation Part 1

[1. CloudFormation Setup](#1-CloudFormation-Setup)
  - [CloudFormation Demo Cluster Template](#CloudFormation-Demo-Cluster-Template)
    - [CloudFormation Validation tool](#CloudFormation-Validation-tool)
  - [CloudFormation Guard](#CloudFormation-Guard)
    - [Install cfn-guard](#Install-cfn-guard)
    - [Create Policy Rules](#Create-Policy-Rules)
 
[2. Networking Template](#2-Networking-Template)
  - [Networking Description](#Networking-Description)
  - [Networking Parameters](#Networking-Parameters)
  - [Networking Resources](#Networking-Resources)
    - [VPC](#VPC)
    - [IGW](#IGW)
    - [Public Route Table](#Public-Route-Table)
    - [Private Route Table](#Private-Route-Table)
    - [Subnet](#Subnet)
    - [Subnet Association](#Subnet-Association)
  - [Networking Output](#Networking-Output)
    

[3. Cluster Template](#3-Cluster-Template)
  - [Cluster Description](#Cluster-Description)
  - [Cluster Parameters](#Cluster-Parameters)
  - [Cluster Resources](#Cluster-Resources)
    - [Fargate Cluster](#Fargate-Cluster)
    - [ALB Load Balancer](#ALB-Load-Balancer)
    - [HTTPS Listener](#HTTPS-Listener)
    - [HTTP Listener](#HTTP-Listener)
    - [Backend Listener Rule](#Backend-Listener-Rule)
    - [ALB Security Group](#ALB-Security-Group)
    - [Service Security Group](#Service-Security-Group)
    - [Backend Target Group](#Backend-Target-Group)
    - [Frontend Target Group](#Frontend-Target-Group)
  - [Cluster Output](#Cluster-Output)
  
[4. Service Template](#4-Service-Template)
  - [Service Description](#Service-Description)
  - [Service Parameters](#Service-Parameters)
  - [Service Resources](#Service-Resources)
    - [ECS Backend Service](#ECS-Backend-Service)
    - [Task Definition](#Task-Definition)
    - [Service Execution Policy](#Service-Execution-Policy)
    - [Task Role](#Task-Role)
    
[5. Database Template](#5-Database-Template)
  - [Database Description](#Database-Description)
  - [Database Parameters](#Database-Parameters)
  - [Database Resources](#Database-Resources)
    - [RDS Security Group](#RDS-Security-Group)
    - [DB Subnet Group](#DB-Subnet-Group)
    - [Postgres Database](#Postgres-Database)
  
[6. CloudFormation Deployment](#6-CloudFormation-Deployment)
  - [Toml Config](#Toml-Config)
  - [Deployment Scripts](#Deployment-Scripts)
    - [Networking Deployment Script](#Networking-Deployment-Script)
    - [Cluster Deployment Script](#Cluster-Deployment-Script)
    - [Service Deployment Script](#Service-Deployment-Script)
    - [Database Deployment Script](#Database-Deployment-Script)
    
---

## 1. CloudFormation Setup
[Back to top](#Week-10)

- Create a new S3 bucket to contain CloudFormation artifacts
```bash
aws s3 mb s3://cfn-artifacts-UniqueName
export CFN_BUCKET="cfn-artifacts-UniqueName"
gp env CFN_BUCKET="cfn-artifacts-UniqueName"
```

---
### CloudFormation Demo Cluster Template
[Back to top](#Week-10)

- Create dir `aws/cfn` 
- Create yaml file [template.yaml](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/e227d138298d39ab37a4e393ea5fbbbdcdad0bcb/aws/cfn/template.yaml)
- Create a stack deployment bash script
  - Create dir: bin/cfn
  - Create bash file [cluster-deploy](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/e227d138298d39ab37a4e393ea5fbbbdcdad0bcb/bin/cfn/cluster-deploy)
- run `cluster-deploy` to deploy the stack
- Go to AWS CloudFormation console, 
- Select the stack created previously, then click on **Change sets** tab
- Select the change set name then click **Execute change set**

#### CloudFormation Validation tool

- Install `cfn-lint` to validate the CloudFormation template   
  `pip install cfn-lint`
- Run the following to validate the template
`cfn-lint aws/cfn/template.yaml`

---
### CloudFormation Guard

AWS CloudFormation Guard is an open-source general-purpose policy-as-code evaluation tool. It provides developers with a simple-to-use, yet powerful and expressive domain-specific language (DSL) to define policies and enables developers to validate JSON- or YAML- formatted structured data with those policies.
It will verify if resources are configured as per the policy you have set 

#### Install cfn-guard

- First we need to install cfn-guard using Cargos which is a Rust package manager 
- Run the following command   
`cargo install cfn-guard`

#### Create Policy Rules

- Create a policy rules file [aws/cfn/task-definition.guard](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/e227d138298d39ab37a4e393ea5fbbbdcdad0bcb/aws/cfn/task-definition.guard)
- To validate the creation of Fargate cluster we will create new policy rules
- Create policy guard file `aws/cfn/ecs-cluster.guard`
```
let aws_ecs_cluster_resources = Resources.*[ Type == 'AWS::ECS::Cluster' ]
rule aws_ecs_cluster when %aws_ecs_cluster_resources !empty {
  %aws_ecs_cluster_resources.Properties.CapacityProviders == ["FARGATE"]
  %aws_ecs_cluster_resources.Properties.ClusterName == "MyCluster"
}
```

---
---

## 2. Networking Template
[Back to top](#Week-10)

We will start by creating the parameters to be referenced as we build the template.yaml file, then we will create the resources staring with VPC, IGW, Routing Table, Subnets and other related resources.

### Networking Description 
[Back to top](#Week-10)

- We will add description of the template at the top of the file
```yml
Description: |
  The base networking components for our stack:
  - VPC
    - sets DNS hostnames for EC2 instances
    - Only IPV4, IPV6 is disabled
  - InternetGateway
  - Route Table
    - route to the IGW
    - route to Local
  - 6 Subnets Explicity Associated to Route Table
    - 3 Public Subnets numbered 1 to 3
    - 3 Private Subnets numbered 1 to 3
```

---

### Networking Parameters
[Back to top](#Week-10)    
[Top of Networking Template](#2-Networking-Template)

- We will creat parameters to refernce Availability Zones and CIDR block for subnets in the template file
- Create a new dir: aws/cfn/networking
- Create a new template file inside dir: networking, `template.yaml`
- Add the following to create Availability Zone parameters 
```yml 
Parameters:
    AZ1:
      Type: AWS::EC2::AvailabilityZone::Name
      Default: us-east-1a
    AZ2:
      Type: AWS::EC2::AvailabilityZone::Name
      Default: us-east-1b
    AZ3:
      Type: AWS::EC2::AvailabilityZone::Name
      Default: us-east-1c
```
- Add the following to create subnet CIDR blocks
```yml
SubnetCidrBlocks: 
      Description: "Comma-delimited list of CIDR blocks for our private public subnets"
      Type: CommaDelimitedList
      Default: >
        10.0.0.0/24, 
        10.0.4.0/24, 
        10.0.8.0/24, 
        10.0.12.0/24,
        10.0.16.0/24,
        10.0.20.0/24
``` 

---

### Networking Resources
[Back to top](#Week-10)

#### VPC  
[Back to top](#Week-10)    
[Top of Networking Template](#2-Networking-Template)

>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html
- Add the **VPC** resourece and the properties

  ```yml
  Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties: 
      CidrBlock: !Ref VpcCidrBlock
      EnableDnsHostnames: true
      EnableDnsSupport: true
      InstanceTenancy: default
      Tags:
        - Key: Name 
        Value: !Sub "${AWS::StackName}VPC"
  ```
- Creta a stack networking deployment script [bin/cfn/networking-deploy]()
- Make the script executable then run it `./bin/cfn/networking-deploy`
- This will create the CloudFormation stack 

#### IGW
[Back to top](#Week-10)    
[Top of Networking Template](#2-Networking-Template)

>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-internetgateway.html

- Edit the template `aws/cfn/networking/template.yaml`
- Add the Internet Gateway **IGW** resource and properties
```yml
IGW:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value:  !Sub "${AWS::StackName}IGW"  
```
- Add the following to attach the IGW
```yml
 AttachIGW:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId:
          Ref: VPC #reference method-1
      InternetGatewayId: !Ref IGW #reference method-2
```

#### Public Route Table
[Back to top](#Week-10)     
[Top of Networking Template](#2-Networking-Template)

>>Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-routetable.html

- Create a **Public Route Table** by adding the following
```yml
PubRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId:  !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub "${AWS::StackName}PublicRT"
```

#### Private Route Table
[Back to top](#Week-10)   
[Top of Networking Template](#2-Networking-Template)

>>Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-routetable.html

- Create a **Private Route Table** by adding the following
```yml
PrivRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId:  !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub "${AWS::StackName}PrivateRT"   
```

- Create a **Route to IGW** by adding the following
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html
```yml
RouteToIGW:
    Type: AWS::EC2::Route
    DependsOn: AttachIGW
    Properties:
      RouteTableId: !Ref PubRouteTable
      GatewayId: !Ref IGW
      DestinationCidrBlock: 0.0.0.0/0
```

#### Subnet
[Back to top](#Week-10)   
[Top of Networking Template](#2-Networking-Template)

>>Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html

- Create **Subnet** by adding the following
```yml
SubnetPub1:
    Type: AWS::EC2::Subnet
    Properties:
      AvailabilityZone: !Ref AZ1
      CidrBlock: !Select [0, !Ref SubnetCidrBlocks]
      EnableDns64: false
      MapPublicIpOnLaunch: true #public subnet
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub "${AWS::StackName}SubnetPub1"
```
- Create 2 more **Public subnets** using the above but change the following
```yml
# Public subnet 2
SubnetPub1: # change to:  SubnetPub2
      AvailabilityZone: !Ref AZ1 # change to: !Ref AZ2
      CidrBlock: !Select [0, !Ref SubnetCidrBlocks] # change index to 1
        Value: !Sub "${AWS::StackName}SubnetPub1" # change to: SubnetPub2
```
```yml
# Public subnet 3
SubnetPub: # change to:  SubnetPub3
      AvailabilityZone: !Ref AZ1 # change to: !Ref AZ3
      CidrBlock: !Select [0, !Ref SubnetCidrBlocks] # change index to 2
        Value: !Sub "${AWS::StackName}SubnetPub1" # change to: SubnetPub3
```
- Create 3 more **Private subnets** using the above "SubnetPub1" but change the following

```yml
# Private subnet 1
SubnetPub1: # change to:  SubnetPriv1
      CidrBlock: !Select [0, !Ref SubnetCidrBlocks] # change index to 3
      MapPublicIpOnLaunch: true # change to: false #private subnet
        Value: !Sub "${AWS::StackName}SubnetPub1" # change to: SubnetPriv1
```
```yml
# Private subnet 2
SubnetPub1: # change to:  SubnetPriv2
      AvailabilityZone: !Ref AZ1 # change to: !Ref AZ2
      CidrBlock: !Select [0, !Ref SubnetCidrBlocks] # change index to 4
      MapPublicIpOnLaunch: true # change to: false #private subnet
        Value: !Sub "${AWS::StackName}SubnetPub1" # change to: SubnetPriv2
```
```yml
# Private subnet 3
SubnetPub1: # change to:  SubnetPriv3
      AvailabilityZone: !Ref AZ1 # change to: !Ref AZ3
      CidrBlock: !Select [0, !Ref SubnetCidrBlocks] # change index to 5
      MapPublicIpOnLaunch: true # change to: false #private subnet
        Value: !Sub "${AWS::StackName}SubnetPub1" # change to: SubnetPriv3
```

#### Subnet Association
[Back to top](#Week-10)    
[Top of Networking Template](#2-Networking-Template)

- We will associate the public subnets with the public route table
- Create 3 resources using the following and change the subnet details respectivley 
```yml
  SubnetPub1RTAssociation: # change to reflect the subnet name
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref SubnetPub1 # change to reflect the subnet name
      RouteTableId: !Ref PubRouteTable   
```
- Next, we will associate the private subnets with the private route table
- Create 3 resources using the following and change the subnet details respectivley 
```yml
SubnetPriv1RTAssociation: #change to reflect the subnet name
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref SubnetPriv1 #change to reflect the subnet name
      RouteTableId: !Ref PrivRouteTable    
```
---
### Networking Output 
[Back to top](#Week-10)    
[Top of Networking Template](#2-Networking-Template)

- Add the following to output the resources in the CloudFormation Output
```yml
Outputs:
  VpcId:
    Value: !Ref VPC
    Export:
      Name: !Sub "${AWS::StackName}VpcId"
  VpcCidrBlock:
    Value: !GetAtt VPC.CidrBlock
    Export:
      Name: !Sub "${AWS::StackName}VpcCidrBlock"
  SubnetCidrBlocks:
    Value: !Join [",", !Ref SubnetCidrBlocks]
    Export:
      Name: !Sub "${AWS::StackName}SubnetCidrBlocks"
  PublicSubnetIds:
    Value: !Join 
      - ","
      - - !Ref SubnetPub1
        - !Ref SubnetPub2
        - !Ref SubnetPub3
    Export:
      Name: !Sub "${AWS::StackName}PuplicSubnetIds"
  
  PrivateSubnetIds:
    Value: !Join 
      - ","
      - - !Ref SubnetPriv1
        - !Ref SubnetPriv2
        - !Ref SubnetPriv3
    Export:
      Name: !Sub "${AWS::StackName}PrivateSubnetIds"
  AvailabilityZones:
    Value: !Join 
      - ","
      - - !Ref AZ1
        - !Ref AZ2
        - !Ref AZ3
    Export:
      Name: !Sub "${AWS::StackName}AvailabilityZones"
```

---
---

## 3. Cluster Template

### Cluster Description
[Back to top](#Week-10)

We will start by creating new cluster template.yaml file then add the stack description, Parameters and Resources.

- Create a new dir: aws/cfn/cluster
- Create a new template file inside dir: cluster, [template.yaml]()
- Add the following description
```yml
Description: |
  The networking and cluster configuration to support fargate containers
  - ECS Fargate Cluster
  - Application Load Balancer (ALB)
    - ipv4
    - internet facing
    - certificate attached from Amazon Certification Manager (ACM)
  - ALB Security Group
  - HTTPS Listener 
    - send naked domain to frontend target group
    - send api. subdomain to backend target group
  - HTTP Listener
    - redirect to HTTPS listener
  - Backend Target group
  - Frontend Target group
```

---

### Cluster Parameters
[Back to top](#Week-10)    
[Top of Cluster Template](#3-Cluster-Template)

- Add the following Parameters to be referenced while creating resources
```yml
NetworkingStack:
    Type: String
    Description: This is our base layer of networking components eg. VPC, Subnets
    Default: CrdNet
# >> Frontend 
FrontendPort:
  Type: Number
  Default: 3000
# Health Check
FrontendHealthCheckPath: 
  Type: String
  Defualt: "/"
FrontendHealthCheckPort: 
  Type: String
  Defualt: 80
FrontendHealthCheckProtocol: 
  Type: String
  Defualt: HTTP
FrontendHealthCheckTimeoutSeconds: 
  Type: Number
  Defualt: 5
FrontendHealthyThresholdCount: 
  Type: Number
  Defualt: 2
FrontendHealthCheckIntervalSeconds: 
  Type: Number
  Defualt: 10
FrontendUnhealthyThresholdCount:
  Type: Number
  Default: 2
  
# >> Backend 
BackendPort:
  Type: Number
  Default: 4567
# Health Check
BackendHealthCheckPath: 
  Type: String
  Defualt: "/api/health-check"
BackendHealthCheckPort: 
  Type: String
  Defualt: 80
BackendHealthCheckProtocol: 
  Type: String
  Defualt: HTTP
BackendHealthCheckTimeoutSeconds: 
  Type: Number
  Defualt: 5
BackendHealthyThresholdCount: 
  Type: Number
  Defualt: 2
BackendHealthCheckIntervalSeconds: 
  Type: Number
  Defualt: 10
BackendUnhealthyThresholdCount:
  Type: Number
  Default: 2  
```
---

### Cluster Resources

#### Fargate Cluster
[Back to top](#Week-10)    
[Top of Cluster Template](#3-Cluster-Template)

>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-cluster.html
- Add the following to create a Fargate cluster 

```yml
ECSCluster: #LogicalName
    Type: 'AWS::ECS::Cluster'
    Properties:
      ClusterName: !Sub "${AWS::StackName}FargateCluster"
      CapacityProviders:
        - FARGATE
    ClusterSettings:
        - Name: containerInsights
          Value: enabled
    Configuration:
      ExecuteCommandConfiguration:
        # KmsKeyId: !Ref KmsKeyId
        Logging: DEFAULT
    ServiceConnectDefaults:
      Namespace: cruddur  
```

#### ALB Load Balancer
[Back to top](#Week-10)     
[Top of Cluster Template](#3-Cluster-Template)

>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-loadbalancer.html
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-loadbalancer-loadbalancerattributes.html
- Add the following to create an ALB Load Balancer
```yml
ALB:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties: 
      Name: !Sub "${AWS::StackName}ALB"
      Type: application
      IpAddressType: ipv4
      Schema: internet-facing
      SecurityGroups:
        - !GetAtt ALBSG.GroupId
      Subnets:
        Fn::Split:
          - ","
          - Fn::ImportValue:
              !Sub "${NetworkingStack}PublicSubnetIds"
      LoadBalancerAttributes:
        - Key: routing.http2.enabled
          Value: true
        - Key: routing.http.preserve_host_header.enabled
          Value: false
        - Key: deletion_protection.enabled
          Value: true
        - Key: load_balancing.cross_zone.enabled
          Value: true
        - Key: access_logs.s3.enabled
          Value: false
```

#### HTTPS Listener
[Back to top](#Week-10)   
[Top of Cluster Template](#3-Cluster-Template)

>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-listener.html
- Next, we will create Listeners, add the following to create HTTPS listener
```yml
HTTPSListener:
    Type: "AWS::ElasticLoadBalancingV2::Listener"
    Properties: 
      Protocol: HTTPS
      Port: 443
      LoadBalancerArn: !Ref ALB
      Certificates:
        - CertificateArn: !Ref CertificateArn 
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref FrontendTG 
```

#### HTTP Listener
[Back to top](#Week-10)    
[Top of Cluster Template](#3-Cluster-Template)

>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-listener.html
- Create HTTP listener by adding the following
```yml
 HTTPListener: 
    Type: "AWS::ElasticLoadBalancingV2::Listener"
    Properties:    
      Protocol: HTTP
      Port: 80
      LoadBalancerArn: !Ref ALB
      DefaultActions:
        - Type: "redirect"
          RedirectConfig:
            Protocol: "HTTPS"
            Port: 443
            Host: "#{host}"
            Path: "/#{path}"
            Query: "#{query}"
            StatusCode: "HTTP_301"
```

#### Backend Listener Rule
[Back to top](#Week-10)    
[Top of Cluster Template](#3-Cluster-Template)

>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-listenerrule.html
- We will create a backend listener rule to forward traffic to api. subdomain by adding the following
```yml
ApiALBListernerRule:
    Type: AWS::ElasticLoadBalancingV2::ListenerRule
    Properties:
      Conditions: 
        - Field: host-header
          HostHeaderConfig: 
            Values: 
              - api.awsbc.flyingresnova.com
      Actions: 
        - Type: forward
          TargetGroupArn: !Ref BackendTG
      ListenerArn: !Ref HTTPSListener
      Priority: 1
```

#### ALB Security Group
[Back to top](#Week-10)    
[Top of Cluster Template](#3-Cluster-Template)

>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html
- Add the following to create an ALB Security Group  
```yml
ALBSG:
  Type: AWS::EC2::SecurityGroup
  Properties:
    GroupName: !Sub "${AWS::StackName}ALBSG"
    GroupDescription: Public facing SG for our Cruddur ALB
    VpcId:
        Fn::ImportValue:
          !Sub ${NetworkingStack}VpcId
    SecurityGroupIngress:
      - IpProtocol: tcp
        FromPort: 443
        ToPort: 443
        CidrIp: 0.0.0.0/0
        Description: INTERNET HTTPS
      - IpProtocol: tcp
        FromPort: 80
        ToPort: 80
        CidrIp: 0.0.0.0/0
        Description: INTERNET HTTP
```
#### Service Security Group
[Back to top](#Week-10)    
[Top of Cluster Template](#3-Cluster-Template)

>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html
- Add the following to create a Security Group for the backend service
```yml
ServiceSG:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}ServSG"
      GroupDescription: Public Facing SG for our Cruddur ALB
      VpcId:
        Fn::ImportValue:
          !Sub ${NetworkingStack}VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          SourceSecurityGroupId: !GetAtt ALBSG.GroupId
          FromPort: !Ref BackendPort
          ToPort: !Ref BackendPort
          Description: ALB to backend
```

#### Backend Target Group
[Back to top](#Week-10)     
[Top of Cluster Template](#3-Cluster-Template)

>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-targetgroup.html
- We will create a backend Target Group by adding the following
```yml
BackendTG:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub "${AWS::StackName}BackendTG"
      Port: !Ref BackendPort
      TargetType: ip
      HealthCheckEnabled: true
      HealthCheckProtocol: !Ref BackendHealthCheckProtocol
      HealthCheckIntervalSeconds: !Ref BackendHealthCheckIntervalSeconds
      HealthCheckPath: !Ref BackendHealthCheckPath
      HealthCheckPort: !Ref BackendPort
      HealthCheckTimeoutSeconds: !Ref BackendHealthCheckTimeoutSeconds
      HealthyThresholdCount: !Ref BackendHealthyThresholdCount
      UnhealthyThresholdCount: !Ref BackendUnhealthyThresholdCount
      IpAddressType: ipv4
      Matcher: 
        HttpCode: 200
      Protocol: HTTP
      ProtocolVersion: HTTP2
      TargetGroupAttributes: 
        - Key: deregistration_delay.timeout_seconds
          Value: 0
      VpcId:
        Fn::ImportValue:
          !Sub ${NetworkingStack}VpcId # cross-stack references using parameter 'NetworkingStack' & export from the other stack 
```

#### Frontend Target Group
[Back to top](#Week-10)   
[Top of Cluster Template](#3-Cluster-Template)

>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-targetgroup.html
- We will create a frontend Target Group by adding the following
```yml
FrontendTG:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub "${AWS::StackName}FrontendTG"
      Port: !Ref FrontendPort
      TargetType: ip
      HealthCheckEnabled: true
      HealthCheckProtocol: !Ref FrontendHealthCheckProtocol
      HealthCheckIntervalSeconds: !Ref FrontendHealthCheckIntervalSeconds
      HealthCheckPath: !Ref FrontendHealthCheckPath
      HealthCheckPort: !Ref FrontendPort
      HealthCheckTimeoutSeconds: !Ref FrontendHealthCheckTimeoutSeconds
      HealthyThresholdCount: !Ref FrontendHealthyThresholdCount
      UnhealthyThresholdCount: !Ref FrontendUnhealthyThresholdCount
      IpAddressType: ipv4
      Matcher: 
        HttpCode: 200
      Protocol: HTTP
      ProtocolVersion: HTTP2
      TargetGroupAttributes: 
        - Key: deregistration_delay.timeout_seconds
          Value: 0
      VpcId:
        Fn::ImportValue:
          !Sub ${NetworkingStack}VpcId
```

---

### Cluster Output
[Back to top](#Week-10)   
[Top of Cluster Template](#3-Cluster-Template)

- Add the following to create output
```yml
Outputs:
  ClusterName:
    Value: !Ref FargateCluster
    Export:
      Name: !Sub "${AWS::StackName}ClusterName"
  ALBSecurityGroupId:
    Value: !GetAtt ALBSG.GroupId
    Export:
      Name: !Sub "${AWS::StackName}ALBSecurityGroupId"
  FrontendTGArn:
    Value: !Ref FrontendTG
    Export:
      Name: !Sub "${AWS::StackName}FrontendTGArn"
  BackendTGArn:
    Value: !Ref BackendTG
    Export:
      Name: !Sub "${AWS::StackName}BackendTGArn"
  ServiceSecurityGroupId:
    Value: !GetAtt ServiceSG.GroupId
    Export:
      Name: !Sub "${AWS::StackName}ServiceSecurityGroupId"
```


---
---

## 4. Service Template

Backend Service template to create ECS backend service and task definition 

### Service Description
[Back to top](#Week-10)

- Add the following template description
```yml
 Task Definition
  Fargate Service
  Execution Role
  Task Role
```  
---
### Service Parameters
[Back to top](#Week-10)  
[Top of Service Template](#4-Service-Template)
  
- Add the following parameters as reference to create resources in the next step
```yml
Parameters:
  NetworkingStack:
    Type: String
    Description: This is our base layer of networking components eg. VPC, Subnets
    Default: CrdNet
  ClusterStack:
    Type: String
    Description: This is our cluster layer eg. ECS Cluster, ALB
    Default: CrdCluster
  ContainerPort:
    Type: Number
    Default: 4567
  ServiceCpu:
    Type: String
    Default: '256'
  ServiceMemory:
    Type: String
    Default: '512'
  ServiceName:
    Type: String
    Default: backend-flask
  ContainerName:
    Type: String
    Default: backend-flask
  TaskFamily:
    Type: String
    Default: backend-flask
  EcrImage:
    Type: String
    Default: '<YourAwsAccount>.dkr.ecr.<YourRegion>.amazonaws.com/backend-flask'
  EnvOtelServiceName:
    Type: String
    Default: backend-flask
  EnvOtelExporterOtlpEndpoint:
    Type: String
    Default: https://api.honeycomb.io
  EnvAWSCognitoUserPoolId:
    Type: String
    Default: <YourCognitoUserPoolId>
  EnvCognitoUserPoolClientId:
    Type: String
    Default: <YourCognitoUserPoolClientId>
  EnvFrontendUrl:
    Type: String
    Default: "*"
  EnvBackendUrl:
    Type: String
    Default: "*"
  SecretsAWSAccessKeyId:
    Type: String
    Default: 'arn:aws:ssm:<YourRegion>:<YourAwsAccount>:parameter/cruddur/backend-flask/AWS_ACCESS_KEY_ID'
  SecretsSecretAccessKey:
    Type: String
    Default: 'arn:aws:ssm:<YourRegion>:<YourAwsAccount>:parameter/cruddur/backend-flask/AWS_SECRET_ACCESS_KEY'
  SecretsConnectionUrl:
    Type: String
    Default: 'arn:aws:ssm:<YourRegion>:<YourAwsAccount>:parameter/cruddur/backend-flask/CONNECTION_URL'
  SecretsRollbarAccessToken:
    Type: String
    Default: 'arn:aws:ssm:<YourRegion>:<YourAwsAccount>:parameter/cruddur/backend-flask/ROLLBAR_ACCESS_TOKEN'
  SecretsOtelExporterOltpHeaders:
    Type: String
    Default: 'arn:aws:ssm:<YourRegion>:<YourAwsAccount>:parameter/cruddur/backend-flask/OTEL_EXPORTER_OTLP_HEADERS'
```
---
### Service Resources

#### ECS Backend Service
[Back to top](#Week-10)    
[Top of Service Template](#4-Service-Template)

- Create a Fargate Service by adding the following
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html
```yml
FargateService:
    Type: AWS::ECS::Service
    Properties:
      Cluster:
        Fn::ImportValue:
          !Sub "${ClusterStack}ClusterName"
      DeploymentController:
        Type: ECS
      DesiredCount: 1
      EnableECSManagedTags: true
      EnableExecuteCommand: true
      HealthCheckGracePeriodSeconds: 0
      LaunchType: FARGATE
      LoadBalancers:
        - TargetGroupArn:
            Fn::ImportValue:
              !Sub "${ClusterStack}BackendTGArn"
          ContainerName: 'backend-flask'
          ContainerPort: !Ref ContainerPort
      NetworkConfiguration:
        AwsvpcConfiguration:
          AssignPublicIp: ENABLED
          SecurityGroups:
            - !GetAtt ServiceSG.GroupId
          Subnets:
            Fn::Split:
              - ","
              - Fn::ImportValue:
                  !Sub "${NetworkingStack}PublicSubnetIds"
      PlatformVersion: LATEST
      PropagateTags: SERVICE
      ServiceConnectConfiguration:
        Enabled: true
        Namespace: "cruddur"
        # TODO - If you want to log
        # LogConfiguration
        Services:
          - DiscoveryName: backend-flask
            PortName: backend-flask
            ClientAliases:
              - Port: !Ref ContainerPort
      #ServiceRegistries:
      #  - RegistryArn: !Sub 'arn:aws:servicediscovery:${AWS::Region}:${AWS::AccountId}:service/srv-cruddur-backend-flask'
      #    Port: !Ref ContainerPort
      #    ContainerName: 'backend-flask'
      #    ContainerPort: !Ref ContainerPort
      ServiceName: !Ref ServiceName
      TaskDefinition: !Ref TaskDefinition
```

#### Task Definition
[Back to top](#Week-10)    
[Top of Service Template](#4-Service-Template)

- Add the following to create a Task Definition
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-taskdefinition.html
```yml
TaskDefinition:
    Type: 'AWS::ECS::TaskDefinition'
    Properties:
      Family: !Ref TaskFamily
      ExecutionRoleArn: !GetAtt ExecutionRole.Arn
      TaskRoleArn: !GetAtt TaskRole.Arn
      NetworkMode: 'awsvpc'
      Cpu: !Ref ServiceCpu
      Memory: !Ref ServiceMemory
      RequiresCompatibilities:
        - 'FARGATE'
      ContainerDefinitions:
        - Name: 'xray'
          Image: 'public.ecr.aws/xray/aws-xray-daemon'
          Essential: true
          User: '1337'
          PortMappings:
            - Name: 'xray'
              ContainerPort: 2000
              Protocol: 'udp'
        - Name: 'backend-flask'
          Image: !Ref EcrImage 
          Essential: true
          HealthCheck:
            Command:
              - 'CMD-SHELL'
              - 'python /backend-flask/bin/health-check'
            Interval: 30
            Timeout: 5
            Retries: 3
            StartPeriod: 60
          PortMappings:
            - Name: !Ref ContainerName
              ContainerPort: !Ref ContainerPort
              Protocol: 'tcp'
              AppProtocol: 'http'
          LogConfiguration:
            LogDriver: 'awslogs'
            Options:
              awslogs-group: 'cruddur'
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: !Ref ServiceName
          Environment:
            - Name: 'OTEL_SERVICE_NAME'
              Value: !Ref EnvOtelServiceName
            - Name: 'OTEL_EXPORTER_OTLP_ENDPOINT'
              Value: !Ref EnvOtelExporterOtlpEndpoint
            - Name: 'AWS_COGNITO_USER_POOL_ID'
              Value: !Ref EnvAWSCognitoUserPoolId
            - Name: 'AWS_COGNITO_USER_POOL_CLIENT_ID'
              Value: !Ref EnvCognitoUserPoolClientId
            - Name: 'FRONTEND_URL'
              Value: !Ref EnvFrontendUrl
            - Name: 'BACKEND_URL'
              Value: !Ref EnvBackendUrl
            - Name: 'AWS_DEFAULT_REGION'
              Value: !Ref AWS::Region
          Secrets:
            - Name: 'AWS_ACCESS_KEY_ID'
              ValueFrom: !Ref SecretsAWSAccessKeyId
            - Name: 'AWS_SECRET_ACCESS_KEY'
              ValueFrom: !Ref SecretsSecretAccessKey
            - Name: 'CONNECTION_URL'
              ValueFrom: !Ref SecretsConnectionUrl
            - Name: 'ROLLBAR_ACCESS_TOKEN'
              ValueFrom: !Ref SecretsRollbarAccessToken
            - Name: 'OTEL_EXPORTER_OTLP_HEADERS'
              ValueFrom: !Ref SecretsOtelExporterOltpHeaders
```

#### Service Execution Policy
[Back to top](#Week-10)    
[Top of Service Template](#4-Service-Template)

- Create a service execution policy by adding the following
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html
```yml
ExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: CruddurServiceExecutionRole
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: 'Allow'
            Principal:
              Service: 'ecs-tasks.amazonaws.com'
            Action: 'sts:AssumeRole'
      Policies:
        - PolicyName: 'cruddur-execution-policy'
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Sid: 'VisualEditor0'
                Effect: 'Allow'
                Action:
                  - 'ecr:GetAuthorizationToken'
                  - 'ecr:BatchCheckLayerAvailability'
                  - 'ecr:GetDownloadUrlForLayer'
                  - 'ecr:BatchGetImage'
                  - 'logs:CreateLogStream'
                  - 'logs:PutLogEvents'
                Resource: '*'
              - Sid: 'VisualEditor1'
                Effect: 'Allow'
                Action:
                  - 'ssm:GetParameters'
                  - 'ssm:GetParameter'
                Resource: !Sub 'arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter/cruddur/${ServiceName}/*'
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/CloudWatchLogsFullAccess
```

#### Task Role
[Back to top](#Week-10)    
[Top of Service Template](#4-Service-Template)

- Add the follfowing to create a Task Role
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html
```yml
TaskRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: CruddurServiceTaskRole
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: 'Allow'
            Principal:
              Service: 'ecs-tasks.amazonaws.com'
            Action: 'sts:AssumeRole'
      Policies:
        - PolicyName: 'cruddur-task-policy'
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Sid: 'VisualEditor0'
                Effect: 'Allow'
                Action:
                  - ssmmessages:CreateControlChannel
                  - ssmmessages:CreateDataChannel
                  - ssmmessages:OpenControlChannel
                  - ssmmessages:OpenDataChannel
                Resource: '*'
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/CloudWatchLogsFullAccess
        - arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess
```

---
---

## 5. Database Template

- Create a new dir: `aws/cfn/db`
- Inside db dir: create database CloudFormation template file `template.yaml`

### Database Description
[Back to top](#Week-10)

- Add the following templarte description 
```yml
Description: |
  The primary Postgres RDS Database for the application
  - RDS Instance
  - Database Security Group
  - DBSubnetGroup
```
---
### Database Parameters
[Back to top](#Week-10)

- Add the following to created the required parameters for this repmplate
```yml
Parameters:
  NetworkingStack:
    Type: String
    Description: This is our base layer of networking components eg. VPC, Subnets
    Default: CrdNet
  ClusterStack:
    Type: String
    Description: This is our FargateCluster
    Default: CrdCluster
  BackupRetentionPeriod:
    Type: Number
    Default: 0
  DBInstanceClass:
    Type: String
    Default: db.t4g.micro
  DBInstanceIdentifier:
    Type: String
    Default: cruddur-instance
  DBName:
    Type: String
    Default: cruddur
  DeletionProtection:
    Type: String
    AllowedValues:
      - true
      - false
    Default: true
  EngineVersion:
    Type: String
    #  DB Proxy only supports very specific versions of Postgres
    #  https://stackoverflow.com/questions/63084648/which-rds-db-instances-are-supported-for-db-proxy
    Default: '15.2'
  MasterUsername:
    Type: String
  MasterUserPassword:
    Type: String
    NoEcho: true
``` 
---
### Database Resources

#### RDS Security Group
[Back to top](#Week-10)

- Add the following to create a security group for the RDS instance
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html
```yml
RDSPostgresSG:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}AlbSG"
      GroupDescription: Public Facing SG for our Cruddur ALB
      VpcId:
        Fn::ImportValue:
          !Sub ${NetworkingStack}VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          SourceSecurityGroupId:
            Fn::ImportValue:
              !Sub ${ClusterStack}ServiceSecurityGroupId
          FromPort: 5432
          ToPort: 5432
          Description: ALB HTTP
```

#### DB Subnet Group
[Back to top](#Week-10)

>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbsubnetgroup.html
- Add the following to create a database subnet group 
```yml
DBSubnetGroup:
    # 
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupName: !Sub "${AWS::StackName}DBSubnetGroup"
      DBSubnetGroupDescription: !Sub "${AWS::StackName}DBSubnetGroup"
      SubnetIds: { 'Fn::Split' : [ ','  , { "Fn::ImportValue": { "Fn::Sub": "${NetworkingStack}PublicSubnetIds" }}] }
```

#### Postgres Database
[Back to top](#Week-10)

>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbinstance.html
- Add ther following to create a Postgres database 
```yml
Database:
    Type: AWS::RDS::DBInstance
    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html
    DeletionPolicy: 'Snapshot'
    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-updatereplacepolicy.html
    UpdateReplacePolicy: 'Snapshot'
    Properties:
      AllocatedStorage: '20'
      AllowMajorVersionUpgrade: true
      AutoMinorVersionUpgrade: true
      BackupRetentionPeriod: !Ref  BackupRetentionPeriod
      DBInstanceClass: !Ref DBInstanceClass
      DBInstanceIdentifier: !Ref DBInstanceIdentifier
      DBName: !Ref DBName
      DBSubnetGroupName: !Ref DBSubnetGroup
      DeletionProtection: !Ref DeletionProtection
      EnablePerformanceInsights: true
      Engine: postgres
      EngineVersion: !Ref EngineVersion

# Must be 1 to 63 letters or numbers.
# First character must be a letter.
# Can't be a reserved word for the chosen database engine.
      MasterUsername:  !Ref MasterUsername
      # Constraints: Must contain from 8 to 128 characters.
      MasterUserPassword: !Ref MasterUserPassword
      PubliclyAccessible: true
      VPCSecurityGroups:
        - !GetAtt RDSPostgresSG.GroupId  
```

---
---

## 6. CloudFormation Deployment 

We will create a toml configuration file that contains attribute and parameters to be used in the each deployment script. Once each script is executed it will load the attribute and parameters to the respective CloudFormation template.  

### Toml Config
[Back to top](#Week-10)

- Install cfn-toml by running the following `gem install cfn-toml`
- add the above command to the gitpod.yml
- Create a **Cluster** example config.toml file `aws/cluster/config.toml.example`
  - add the following 
  ```yml
  [deploy]
  bucket = ''
  region = ''
  stack_name = ''

  [parameters]
  CertificateArn = ''
  NetworkingStack = ''
  ```
  - Copy config.toml.example config.toml then enter the values
  - add config.toml to the .gitignore 
- Repeat the above steps to creat a **Networking**, **Service**, **Database** config.toml inside dir: aws/cfn/networking   

  - **Networking** config.toml
  ```yml
  [deploy]
    bucket = ''
    region = ''
    stack_name = ''
  ```
  - **Service** config.toml inside 
  ```yml
  [deploy]
    bucket = ''
    region = ''
    stack_name = ''
  ```
  - **Database** config.toml
  ```yml
  [deploy]
    bucket = ''
    region = ''
    stack_name = ''

    [parameters]
    NetworkingStack = 'CrdNet'
    ClusterStack = 'CrdCluster'
    MasterUsername = ''
  ```
---
### Deployment Scripts 
[Back to top](#Week-10)

#### Networking Deployment Script 
[Back to top](#Week-10)

- Update `bin/cfn/networking-deploy` with the following
```bash
CONFIG_PATH="/workspace/aws-bootcamp-cruddur-2023/aws/cfn/networking/config.toml"

BUCKET=$(cfn-toml key deploy.bucket -t $CONFIG_PATH)
REGION=$(cfn-toml key deploy.region -t $CONFIG_PATH)
STACK_NAME=$(cfn-toml key deploy.stack_name -t $CONFIG_PATH)

# REPLACE the existing aws cli with the followng
aws cloudformation deploy \
  --stack-name $STACK_NAME \
  --s3-bucket $CFN_BUCKET \
  --s3-prefix networking \
  --region $REGION \
  --template-file "$CFN_PATH" \
  --no-execute-changeset \
  --tags group=cruddur-networking \
  --capabilities CAPABILITY_NAMED_IAM
```
  
#### Cluster Deployment Script
[Back to top](#Week-10)

- Update `bin/cfn/cluster-deploy` with the following
```bash
CONFIG_PATH="/workspace/aws-bootcamp-cruddur-2023/aws/cfn/cluster/config.toml"

BUCKET=$(cfn-toml key deploy.bucket -t $CONFIG_PATH)
REGION=$(cfn-toml key deploy.region -t $CONFIG_PATH)
STACK_NAME=$(cfn-toml key deploy.stack_name -t $CONFIG_PATH)
PARAMETERS=$(cfn-toml params v2 -t $CONFIG_PATH)

# REPLACE the existing aws cli with the followng
aws cloudformation deploy \
  --stack-name $STACK_NAME \
  --s3-bucket $CFN_BUCKET \
  --s3-prefix cluster \
  --region $REGION \
  --template-file "$CFN_PATH" \
  --no-execute-changeset \
  --tags group=cruddur-cluster \
  --parameter-overrides $PARAMETERS \
  --capabilities CAPABILITY_NAMED_IAM
```
- Run the script `./bin/cfn/cluster-deploy` to deploy the stack
- Update The Hosted Zone main A record and the api A record with the new ALB URL
  
#### Service Deployment Script
[Back to top](#Week-10)

- Create `bin/cfn/service-deploy` then add the following
```bash
! /usr/bin/env bash
set -e # stop the execution of the script if it fails

CFN_PATH="/workspace/aws-bootcamp-cruddur-2023/aws/cfn/service/template.yaml"
CONFIG_PATH="/workspace/aws-bootcamp-cruddur-2023/aws/cfn/service/config.toml"
echo $CFN_PATH

cfn-lint $CFN_PATH

BUCKET=$(cfn-toml key deploy.bucket -t $CONFIG_PATH)
REGION=$(cfn-toml key deploy.region -t $CONFIG_PATH)
STACK_NAME=$(cfn-toml key deploy.stack_name -t $CONFIG_PATH)
#PARAMETERS=$(cfn-toml params v2 -t $CONFIG_PATH)

aws cloudformation deploy \
  --stack-name $STACK_NAME \
  --s3-bucket $CFN_BUCKET \
  --s3-prefix backend-service \
  --region $REGION \
  --template-file "$CFN_PATH" \
  --no-execute-changeset \
  --tags group=cruddur-backend-flask \
  --capabilities CAPABILITY_NAMED_IAM
  #--parameter-overrides $PARAMETERS \
```

  
#### Database Deployment Script
[Back to top](#Week-10)

- Create `bin/cfn/db-deploy` then add the following
```bash
#! /usr/bin/env bash
set -e # stop the execution of the script if it fails

CFN_PATH="/workspace/aws-bootcamp-cruddur-2023/aws/cfn/db/template.yaml"
CONFIG_PATH="/workspace/aws-bootcamp-cruddur-2023/aws/cfn/db/config.toml"
echo $CFN_PATH

cfn-lint $CFN_PATH

BUCKET=$(cfn-toml key deploy.bucket -t $CONFIG_PATH)
REGION=$(cfn-toml key deploy.region -t $CONFIG_PATH)
STACK_NAME=$(cfn-toml key deploy.stack_name -t $CONFIG_PATH)
PARAMETERS=$(cfn-toml params v2 -t $CONFIG_PATH)

aws cloudformation deploy \
  --stack-name $STACK_NAME \
  --s3-bucket $CFN_BUCKET \
  --s3-prefix db \
  --region $REGION \
  --template-file "$CFN_PATH" \
  --no-execute-changeset \
  --tags group=cruddur-cluster \
  --parameter-overrides $PARAMETERS MasterUserPassword=$DB_PASSWORD \
  --capabilities CAPABILITY_NAMED_IAM
```
- Add the DB password as Env var in Gitpod
```bash
export DB_PASSWORD="YourDbPassword"
gp env  DB_PASSWORD="YourDbPassword"
```
