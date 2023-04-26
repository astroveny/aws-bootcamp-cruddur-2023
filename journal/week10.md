# Week 10 


## CloudFormation Part 1


## CloudFormation 

- Create a new S3 bucket to contain CloudFormation artifacts
```bash
aws s3 mb s3://cfn-artifacts-UniqueName
export CFN_BUCKET="cfn-artifacts-UniqueName"
gp env CFN_BUCKET="cfn-artifacts-UniqueName"
```


### CloudFormation Cluster Template

- Create dir `aws/cfn` 
- Create yaml file [template.yaml](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/e227d138298d39ab37a4e393ea5fbbbdcdad0bcb/aws/cfn/template.yaml)
- Create stack deployment bash script
  - Create dir: bin/cfn
  - Create bash file [cluster-deploy](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/e227d138298d39ab37a4e393ea5fbbbdcdad0bcb/bin/cfn/cluster-deploy)
- run `cluster-deploy` to deploy the stack
- Install `cfn-lint` to validate the CloudFormation template   
  `pip install cfn-lint`
- Run the following to validate the template
`cfn-lint aws/cfn/template.yaml`

### CloudFormation Guard

AWS CloudFormation Guard is an open-source general-purpose policy-as-code evaluation tool. It provides developers with a simple-to-use, yet powerful and expressive domain-specific language (DSL) to define policies and enables developers to validate JSON- or YAML- formatted structured data with those policies.
It will verify if resources are configured as per the policy you have set 

#### Install cfn-fuard

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


