# Terraform Configuration for AIG130 Project 2 AWS Deployment

This directory contains Terraform configuration files to automatically provision all AWS resources needed for the Bitcoin Price Prediction ML Pipeline.

## 📋 What This Terraform Configuration Creates

### Core Resources
- **ECR Repository**: For storing Docker images
- **ECS Cluster**: Fargate-based cluster for running containers
- **ECS Task Definition**: Container configuration with S3 environment variables
- **IAM Roles**: Task execution role and task role with S3 access
- **Security Group**: Network security for ECS tasks
- **CloudWatch Log Group**: For container logs

### Optional Resources
- **GitHub Actions IAM User**: For CI/CD automation (optional, enabled by default)

### Referenced Resources
- **S3 Bucket**: References your existing S3 bucket (not created by Terraform)
- **VPC & Subnets**: Uses default VPC and subnets

## 📦 Prerequisites

1. **AWS CLI installed and configured**
   ```bash
   aws --version
   aws configure
   ```

2. **Terraform installed** (version >= 1.0)
   ```bash
   terraform --version
   ```

   Install Terraform:
   ```bash
   # macOS
   brew install terraform

   # Linux
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   ```

3. **S3 Bucket already created** (as you mentioned)
   - Bucket name: `aig130-p2-ml-data-bucket`
   - Data file uploaded: `data/btc_1h_data_2018_to_2025.csv`

4. **AWS Credentials configured** with appropriate permissions
   - EC2, ECS, ECR, IAM, CloudWatch, S3 access

## 🚀 Quick Start

### Step 1: Initialize Terraform

Navigate to the terraform directory and initialize:

```bash
cd terraform
terraform init
```

This downloads the AWS provider and sets up the backend.

### Step 2: Review the Plan

See what resources will be created:

```bash
terraform plan
```

Review the output carefully. You should see:
- 1 ECR repository
- 1 ECS cluster
- 1 ECS task definition
- 2 IAM roles (execution role + task role)
- 2 IAM policies
- 1 Security group
- 1 CloudWatch log group
- 1 IAM user (GitHub Actions, optional)

### Step 3: Apply the Configuration

Create all resources:

```bash
terraform apply
```

Type `yes` when prompted.

This will take 2-3 minutes to complete.

### Step 4: View Outputs

After successful apply, Terraform will display important outputs:

```bash
# To see outputs again at any time
terraform output

# To see a specific output
terraform output ecr_repository_url

# To see sensitive outputs (like GitHub Actions secret key)
terraform output -json github_actions_secret_access_key
```

## 📝 Configuration Customization

### Option 1: Use Default Values

The `variables.tf` file contains sensible defaults that match your existing setup. You can use it as-is.

### Option 2: Create a `terraform.tfvars` File

Create a file named `terraform.tfvars` in the `terraform/` directory:

```hcl
# terraform.tfvars
aws_region                  = "us-east-1"
project_name                = "aig130-p2"
s3_bucket_name              = "aig130-p2-ml-data-bucket"
s3_data_key                 = "data/btc_1h_data_2018_to_2025.csv"
ecr_repository_name         = "aig130-p2-ml-pipeline-ecr"
ecs_cluster_name            = "aig130-p2-ml-cluster"
ecs_task_definition_name    = "aig130-p2-ml-task"
container_name              = "ml-pipeline-container"
task_cpu                    = "1024"
task_memory                 = "2048"
log_retention_days          = 7
create_github_actions_user  = true
```

### Option 3: Pass Variables via Command Line

```bash
terraform apply -var="aws_region=us-west-2" -var="task_cpu=2048"
```

## 🔑 GitHub Actions Setup

If you created the GitHub Actions user (default), you need to configure GitHub Secrets:

### Get the Credentials

```bash
# Get Access Key ID
terraform output github_actions_access_key_id

# Get Secret Access Key (sensitive)
terraform output -raw github_actions_secret_access_key
```

### Add to GitHub Secrets

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add two secrets:
   - Name: `AWS_ACCESS_KEY_ID`, Value: [from terraform output]
   - Name: `AWS_SECRET_ACCESS_KEY`, Value: [from terraform output]

## 📊 Post-Deployment Steps

### 1. Build and Push Docker Image

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $(terraform output -raw ecr_repository_url)

# Build and push (from project root)
cd ../AIG130_Project2_Docker
docker build -t $(cd ../terraform && terraform output -raw ecr_repository_url):latest .
docker push $(cd ../terraform && terraform output -raw ecr_repository_url):latest
```

Or use the generated command:
```bash
terraform output -raw useful_commands | jq -r .docker_login | bash
terraform output -raw useful_commands | jq -r .docker_build_and_push | bash
```

### 2. Run the ML Pipeline

```bash
# Get the command from outputs
terraform output useful_commands

# Or run directly
aws ecs run-task \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --task-definition $(terraform output -raw ecs_task_definition_family) \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$(terraform output -json subnet_ids | jq -r 'join(",")')]],securityGroups=[$(terraform output -raw security_group_id)],assignPublicIp=ENABLED}"
```

### 3. View Logs

```bash
# Follow logs in real-time
aws logs tail $(terraform output -raw cloudwatch_log_group_name) --follow

# Or filter by time
aws logs tail $(terraform output -raw cloudwatch_log_group_name) --since 1h
```

### 4. List Running Tasks

```bash
aws ecs list-tasks --cluster $(terraform output -raw ecs_cluster_name)
```

## 🔄 Updating Infrastructure

### Modify Configuration

1. Edit `main.tf`, `variables.tf`, or create/edit `terraform.tfvars`
2. Review changes:
   ```bash
   terraform plan
   ```
3. Apply changes:
   ```bash
   terraform apply
   ```

### Update Task Definition

The task definition is managed by Terraform. To update it:

1. Modify the `aws_ecs_task_definition` resource in `main.tf`
2. Run `terraform apply`

Alternatively, your GitHub Actions workflow will automatically update it on push.

## 🗑️ Destroying Resources

To remove all created resources:

```bash
# Preview what will be destroyed
terraform plan -destroy

# Destroy all resources
terraform destroy
```

**⚠️ Warning**: This will:
- Delete the ECR repository and all images
- Delete the ECS cluster and task definitions
- Delete IAM roles and policies
- Delete CloudWatch logs
- Delete the GitHub Actions user

**Note**: The S3 bucket will NOT be deleted (it's only referenced, not managed by Terraform).

## 📂 File Structure

```
terraform/
├── main.tf           # Main resource definitions
├── variables.tf      # Variable declarations
├── outputs.tf        # Output definitions
├── terraform.tfvars  # Variable values (optional, create this)
├── README.md         # This file
└── .terraform/       # Created by terraform init (gitignored)
```

## 🔧 Troubleshooting

### Issue: "Error creating ECR repository: RepositoryAlreadyExistsException"

**Solution**: The repository already exists. Either:
1. Import the existing repository:
   ```bash
   terraform import aws_ecr_repository.ml_pipeline aig130-p2-ml-pipeline-ecr
   ```
2. Or delete the existing repository:
   ```bash
   aws ecr delete-repository --repository-name aig130-p2-ml-pipeline-ecr --force
   terraform apply
   ```

### Issue: "Error: NoSuchBucket: The specified bucket does not exist"

**Solution**: Create the S3 bucket first:
```bash
aws s3 mb s3://aig130-p2-ml-data-bucket
aws s3 cp ../AIG130_Project2_Docker/data/btc_1h_data_2018_to_2025.csv \
  s3://aig130-p2-ml-data-bucket/data/btc_1h_data_2018_to_2025.csv
```

### Issue: "Error: error configuring Terraform AWS Provider: no valid credential sources"

**Solution**: Configure AWS credentials:
```bash
aws configure
```
Or set environment variables:
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### Issue: Task fails with "CannotPullContainerError"

**Solution**: Make sure you've built and pushed a Docker image to ECR:
```bash
# Check if image exists
aws ecr describe-images --repository-name aig130-p2-ml-pipeline-ecr

# If not, build and push
cd ../AIG130_Project2_Docker
docker build -t $(cd ../terraform && terraform output -raw ecr_repository_url):latest .
docker push $(cd ../terraform && terraform output -raw ecr_repository_url):latest
```

## 💰 Cost Estimation

Estimated monthly costs (assuming 30 runs):

| Resource | Cost per Month |
|----------|---------------|
| ECR Storage (~500 MB) | $0.05 |
| ECS Fargate (30 runs × 10 min) | ~$2.70 |
| CloudWatch Logs | ~$0.25 |
| S3 Storage | ~$0.001 |
| **Total** | **~$3.00/month** |

Note: First 12 months on AWS Free Tier may be cheaper.

## 📚 Additional Resources

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS ECR Documentation](https://docs.aws.amazon.com/ecr/)
- [Terraform CLI Documentation](https://www.terraform.io/docs/cli/index.html)

## 🎯 Next Steps After Terraform Apply

1. ✅ Build and push Docker image to ECR
2. ✅ Configure GitHub Secrets (if using CI/CD)
3. ✅ Test manual ECS task run
4. ✅ Push to GitHub to trigger automated deployment
5. ✅ Monitor CloudWatch logs for successful execution

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Terraform plan output carefully
3. Check AWS CloudWatch logs for runtime errors
4. Review IAM permissions

---

**Created for**: AIG130 Project 2 - Bitcoin Price Prediction ML Pipeline
**Author**: Zhihuai Wang
**Last Updated**: 2025-11-23
