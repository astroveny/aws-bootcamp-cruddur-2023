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

#### Route Table
>>Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-routetable.html

- Create a **Route Table** by adding the following
```yml
 RouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId:  !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub "${AWS::StackName}RT"
```
- Create a **Route to IGW** by adding the following
>> Ref. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html
```yml
RouteToIGW:
    Type: AWS::EC2::Route
    DependsOn: AttachIGW
    Properties:
      RouteTableId: !Ref RouteTable
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

- We will associate the subnets with the route table
- Create 6 resources using the following and change the subnet details respectivley 
```yml
  SubnetPub1RTAssociation: # change to reflect the subnet name
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref SubnetPub1 # change to reflect the subnet name
      RouteTableId: !Ref RouteTable   
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
  SubnetIds:
    Value: !Join 
      - ","
      - - !Ref SubnetPub1
        - !Ref SubnetPub2
        - !Ref SubnetPub3
        - !Ref SubnetPriv1
        - !Ref SubnetPriv2
        - !Ref SubnetPriv3
    Export:
      Name: !Sub "${AWS::StackName}SubnetIds"
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

#### Parameters

- Create a new dir: aws/cfn/cluster
- Create a new template file inside dir: cluster, [template.yaml]()

#### Resources

- Add the following to create a Fargate cluster 
```yml
```



#### 