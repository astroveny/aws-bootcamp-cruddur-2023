# Week 10 


## CloudFormation Part 1


## CloudFormation Setup

- Create a new S3 bucket to contain CloudFormation artifacts
```bash
aws s3 mb s3://cfn-artifacts-UniqueName
export CFN_BUCKET="cfn-artifacts-UniqueName"
gp env CFN_BUCKET="cfn-artifacts-UniqueName"
```


### CloudFormation Demo Cluster Template

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

## CloudFormation Networking



### Networking Template

We will start by creating the parameters to be referenced as we build the template.yaml file, then we will create the resources staring with VPC, IGW, Routing Table, Subnets and other related resources.


#### Parameters

- We will creat parameters to refernce Availability Zones and CIDR block for subnets in the template file
- Create a new dir: aws/cfn/networking
- Create a new template file inside dir: networking, [template.yaml]()
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

#### VPC  
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

#### Output 

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

#### Description 

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

### Cluster Template

#### Description

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

#### Parameters

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

#### Resources

#### Fargate Cluster
- Add the following to create a Fargate cluster 
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-cluster.html
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

- Add the following to create an ALB Load Balancer
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-loadbalancer.html
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-loadbalancer-loadbalancerattributes.html
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

- Next, we will create Listeners, add the following to create HTTPS listener
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-listener.html
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

- Create HTTP listener by adding the following
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-listener.html
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

- We will create a backend listener rule to forward traffic to api. subdomain by adding the following
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-listenerrule.html
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

- Add the following to create an ALB Security Group 
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html 
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

#### Backend Target Group

- We will create a backend Target Group by adding the following
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-targetgroup.html
```yml
BackendTG:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub "${AWS::StackName}BackendTG"
      Port: !Ref BackendPort
      HealthCheckEnabled: true
      HealthCheckProtocol: !Ref BackendHealthCheckProtocol
      HealthCheckIntervalSeconds: !Ref BackendHealthCheckIntervalSeconds
      HealthCheckPath: !Ref BackendHealthCheckPath
      HealthCheckPort: !Ref BackendHealthCheckPort
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

- We will create a frontend Target Group by adding the following
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-targetgroup.html
```yml
FrontendTG:
    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-targetgroup.html
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub "${AWS::StackName}FrontendTG"
      Port: !Ref FrontendPort
      HealthCheckEnabled: true
      HealthCheckProtocol: !Ref FrontendHealthCheckProtocol
      HealthCheckIntervalSeconds: !Ref FrontendHealthCheckIntervalSeconds
      HealthCheckPath: !Ref FrontendHealthCheckPath
      HealthCheckPort: !Ref FrontendHealthCheckPort
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

### CloudFormation Toml Config

We will create a toml configuration file that contains attribute and parameters to be used in the each deployment script. Once each script is executed it will load the attribute and parameters to the respective CloudFormation template.  

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
- Repeat the above steps to creat a **Networking** config.toml inside dir: aws/cfn/networking using the following 
```yml
 [deploy]
  bucket = ''
  region = ''
  stack_name = ''
```
- Update bin/cfn/cluster-deploy with the following
```bash
CONFIG_PATH="/workspace/aws-bootcamp-cruddur-2023/aws/cfn/cluster/config.toml"

BUCKET=$(cfn-toml key deploy.bucket -t $CONFIG_PATH)
REGION=$(cfn-toml key deploy.region -t $CONFIG_PATH)
STACK_NAME=$(cfn-toml key deploy.stack_name -t $CONFIG_PATH)
PARAMETERS=$(cfn-toml params v2 -t $CONFIG_PATH)

# REPLACE the existing aws cli with the followng
aws cloudformation deploy \
  --stack-name $STACK_NAME \
  --s3-bucket $BUCKET \
  --region $REGION \
  --template-file "$CFN_PATH" \
  --no-execute-changeset \
  --tags group=cruddur-cluster \
  --parameter-overrides $PARAMETERS \
  --capabilities CAPABILITY_NAMED_IAM
```
- Update bin/cfn/networking-deploy with the following
```bash
CONFIG_PATH="/workspace/aws-bootcamp-cruddur-2023/aws/cfn/networking/config.toml"

BUCKET=$(cfn-toml key deploy.bucket -t $CONFIG_PATH)
REGION=$(cfn-toml key deploy.region -t $CONFIG_PATH)
STACK_NAME=$(cfn-toml key deploy.stack_name -t $CONFIG_PATH)

# REPLACE the existing aws cli with the followng
aws cloudformation deploy \
  --stack-name $STACK_NAME \
  --s3-bucket $BUCKET \
  --region $REGION \
  --template-file "$CFN_PATH" \
  --no-execute-changeset \
  --tags group=cruddur-networking \
  --capabilities CAPABILITY_NAMED_IAM
```
