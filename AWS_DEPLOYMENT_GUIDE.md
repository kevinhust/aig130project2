# AWS Deployment Guide for AIG130 Project 2
# Bitcoin Price Prediction ML Pipeline - ECR + ECS + S3 Deployment

---

## Section 1: AWS Setup Instructions

### Prerequisites
- AWS Account with appropriate permissions
- AWS CLI installed locally (`brew install awscli` or download from AWS)
- GitHub repository: `aig130project2`
- Docker installed locally for testing

### Step 1: Configure AWS CLI

```bash
# Configure AWS CLI with your credentials
aws configure

# You will be prompted for:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region name: us-east-1
# - Default output format: json
```

### Step 2: Create IAM Roles and Policies

#### 2.1 Create ECS Task Execution Role (for ECS to pull images and logs)

```bash
# Create trust policy file for ECS tasks
cat > ecs-task-execution-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create the role
aws iam create-role \
  --role-name aig130-p2-ecs-task-execution-role \
  --assume-role-policy-document file://ecs-task-execution-trust-policy.json

# Attach AWS managed policy for ECS task execution
aws iam attach-role-policy \
  --role-name aig130-p2-ecs-task-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

#### 2.2 Create ECS Task Role (for your application to access S3)

```bash
# Create trust policy for task role
cat > ecs-task-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create the task role
aws iam create-role \
  --role-name aig130-p2-ecs-task-role \
  --assume-role-policy-document file://ecs-task-trust-policy.json

# Create S3 access policy for your specific bucket
cat > s3-access-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::aig130-p2-ml-data-bucket",
        "arn:aws:s3:::aig130-p2-ml-data-bucket/*"
      ]
    }
  ]
}
EOF

# Create and attach the policy
aws iam create-policy \
  --policy-name aig130-p2-s3-access-policy \
  --policy-document file://s3-access-policy.json

# Get your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Attach the policy to the task role
aws iam attach-role-policy \
  --role-name aig130-p2-ecs-task-role \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/aig130-p2-s3-access-policy
```

#### 2.3 Create IAM User for GitHub Actions

```bash
# Create a user for GitHub Actions
aws iam create-user --user-name github-actions-aig130-p2

# Create access key for the user (SAVE THESE CREDENTIALS!)
aws iam create-access-key --user-name github-actions-aig130-p2
# Output will contain AccessKeyId and SecretAccessKey - save these for GitHub Secrets

# Create policy for GitHub Actions (ECR, ECS, S3 access)
cat > github-actions-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecs:UpdateService",
        "ecs:DescribeServices",
        "ecs:DescribeTaskDefinition",
        "ecs:RegisterTaskDefinition",
        "ecs:RunTask",
        "ecs:DescribeTasks"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::aig130-p2-ml-data-bucket",
        "arn:aws:s3:::aig130-p2-ml-data-bucket/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:PassRole"
      ],
      "Resource": [
        "arn:aws:iam::*:role/aig130-p2-ecs-task-execution-role",
        "arn:aws:iam::*:role/aig130-p2-ecs-task-role"
      ]
    }
  ]
}
EOF

# Create and attach the policy
aws iam create-policy \
  --policy-name aig130-p2-github-actions-policy \
  --policy-document file://github-actions-policy.json

aws iam attach-user-policy \
  --user-name github-actions-aig130-p2 \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/aig130-p2-github-actions-policy
```

### Step 3: Create S3 Bucket

```bash
# Create S3 bucket for storing training data
aws s3 mb s3://aig130-p2-ml-data-bucket --region us-east-1

# Enable versioning (optional but recommended)
aws s3api put-bucket-versioning \
  --bucket aig130-p2-ml-data-bucket \
  --versioning-configuration Status=Enabled

# Upload the BTC data file
aws s3 cp \
  AIG130_Project2_Docker/data/btc_1h_data_2018_to_2025.csv \
  s3://aig130-p2-ml-data-bucket/data/btc_1h_data_2018_to_2025.csv

# Verify the upload
aws s3 ls s3://aig130-p2-ml-data-bucket/data/
```

### Step 4: Create ECR Repository

```bash
# Create ECR repository for Docker images
aws ecr create-repository \
  --repository-name aig130-p2-ml-pipeline-ecr \
  --region us-east-1 \
  --image-scanning-configuration scanOnPush=true

# Get the repository URI (save this for later)
aws ecr describe-repositories \
  --repository-names aig130-p2-ml-pipeline-ecr \
  --region us-east-1 \
  --query 'repositories[0].repositoryUri' \
  --output text

# Example output: 123456789012.dkr.ecr.us-east-1.amazonaws.com/aig130-p2-ml-pipeline-ecr
```

### Step 5: Create ECS Cluster

```bash
# Create ECS cluster (Fargate)
aws ecs create-cluster \
  --cluster-name aig130-p2-ml-cluster \
  --region us-east-1 \
  --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy \
    capacityProvider=FARGATE,weight=1,base=0

# Verify cluster creation
aws ecs describe-clusters \
  --clusters aig130-p2-ml-cluster \
  --region us-east-1
```

### Step 6: Create ECS Task Definition

```bash
# Get your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create task definition JSON
cat > task-definition.json << EOF
{
  "family": "aig130-p2-ml-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::${ACCOUNT_ID}:role/aig130-p2-ecs-task-execution-role",
  "taskRoleArn": "arn:aws:iam::${ACCOUNT_ID}:role/aig130-p2-ecs-task-role",
  "containerDefinitions": [
    {
      "name": "ml-pipeline-container",
      "image": "${ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/aig130-p2-ml-pipeline-ecr:latest",
      "essential": true,
      "environment": [
        {
          "name": "USE_S3",
          "value": "true"
        },
        {
          "name": "S3_BUCKET",
          "value": "aig130-p2-ml-data-bucket"
        },
        {
          "name": "S3_KEY",
          "value": "data/btc_1h_data_2018_to_2025.csv"
        },
        {
          "name": "AWS_DEFAULT_REGION",
          "value": "us-east-1"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/aig130-p2-ml-task",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs",
          "awslogs-create-group": "true"
        }
      }
    }
  ]
}
EOF

# Register the task definition
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json \
  --region us-east-1
```

### Step 7: Create CloudWatch Log Group (Optional but Recommended)

```bash
# Create log group for ECS tasks
aws logs create-log-group \
  --log-group-name /ecs/aig130-p2-ml-task \
  --region us-east-1

# Set retention policy (optional, saves costs)
aws logs put-retention-policy \
  --log-group-name /ecs/aig130-p2-ml-task \
  --retention-in-days 7 \
  --region us-east-1
```

### Step 8: Create VPC and Security Group (if needed)

```bash
# Get default VPC ID
VPC_ID=$(aws ec2 describe-vpcs \
  --filters "Name=isDefault,Values=true" \
  --query "Vpcs[0].VpcId" \
  --output text \
  --region us-east-1)

# Get subnets in the default VPC
SUBNETS=$(aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=${VPC_ID}" \
  --query "Subnets[*].SubnetId" \
  --output text \
  --region us-east-1)

# Create security group for ECS tasks
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
  --group-name aig130-p2-ml-sg \
  --description "Security group for AIG130 P2 ML ECS tasks" \
  --vpc-id ${VPC_ID} \
  --region us-east-1 \
  --query 'GroupId' \
  --output text)

# Allow outbound traffic (required for pulling from ECR and accessing S3)
aws ec2 authorize-security-group-egress \
  --group-id ${SECURITY_GROUP_ID} \
  --ip-permissions IpProtocol=-1,FromPort=-1,ToPort=-1,IpRanges='[{CidrIp=0.0.0.0/0}]' \
  --region us-east-1

echo "VPC_ID: ${VPC_ID}"
echo "SUBNETS: ${SUBNETS}"
echo "SECURITY_GROUP_ID: ${SECURITY_GROUP_ID}"
# Save these values for the GitHub Actions workflow
```

### Step 9: Run ECS Task Manually (Testing)

```bash
# Run task manually to test
aws ecs run-task \
  --cluster aig130-p2-ml-cluster \
  --task-definition aig130-p2-ml-task \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[${SUBNETS}],securityGroups=[${SECURITY_GROUP_ID}],assignPublicIp=ENABLED}" \
  --region us-east-1

# Check task status
aws ecs list-tasks \
  --cluster aig130-p2-ml-cluster \
  --region us-east-1

# View task logs (replace TASK_ID with actual task ID)
aws logs tail /ecs/aig130-p2-ml-task --follow --region us-east-1
```

### Step 10: (Optional) Create ECS Service for Continuous Running

**Note:** For batch ML tasks, you typically DON'T need a service. Services are for long-running applications (like web servers). For ML training, use `run-task` instead (which GitHub Actions will do). Skip this step unless you want a continuously running service.

```bash
# Only if you want a service that keeps tasks running:
aws ecs create-service \
  --cluster aig130-p2-ml-cluster \
  --service-name aig130-p2-ml-service \
  --task-definition aig130-p2-ml-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[${SUBNETS}],securityGroups=[${SECURITY_GROUP_ID}],assignPublicIp=ENABLED}" \
  --region us-east-1
```

---

## Section 2: GitHub Actions Workflow YAML File

Create `.github/workflows/deploy.yml` in your repository:

```yaml
name: Deploy ML Pipeline to AWS ECS

on:
  push:
    branches:
      - main
  workflow_dispatch: # Allows manual triggering

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: aig130-p2-ml-pipeline-ecr
  ECS_CLUSTER: aig130-p2-ml-cluster
  ECS_TASK_DEFINITION: aig130-p2-ml-task
  CONTAINER_NAME: ml-pipeline-container
  S3_BUCKET: aig130-p2-ml-data-bucket
  S3_DATA_KEY: data/btc_1h_data_2018_to_2025.csv

jobs:
  deploy:
    name: Build and Deploy to AWS
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Upload training data to S3
        run: |
          # Check if file exists in S3
          if aws s3 ls s3://${{ env.S3_BUCKET }}/${{ env.S3_DATA_KEY }} 2>&1 | grep -q 'PRE\|csv'; then
            echo "Data file already exists in S3, skipping upload"
          else
            echo "Uploading data file to S3..."
            aws s3 cp AIG130_Project2_Docker/data/btc_1h_data_2018_to_2025.csv \
              s3://${{ env.S3_BUCKET }}/${{ env.S3_DATA_KEY }}
            echo "Data file uploaded successfully"
          fi

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, tag, and push Docker image to ECR
        id: build-image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          # Build Docker image
          cd AIG130_Project2_Docker
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest

          # Push to ECR
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

          # Output image URI for next steps
          echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT

      - name: Download current task definition
        run: |
          aws ecs describe-task-definition \
            --task-definition ${{ env.ECS_TASK_DEFINITION }} \
            --query 'taskDefinition' \
            --region ${{ env.AWS_REGION }} > task-definition.json

      - name: Fill in the new image ID in the Amazon ECS task definition
        id: task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: task-definition.json
          container-name: ${{ env.CONTAINER_NAME }}
          image: ${{ steps.build-image.outputs.image }}

      - name: Deploy Amazon ECS task definition
        uses: aws-actions/amazon-ecs-deploy-task-definition@v2
        with:
          task-definition: ${{ steps.task-def.outputs.task-definition }}
          cluster: ${{ env.ECS_CLUSTER }}
          wait-for-service-stability: false

      - name: Run ECS task for ML pipeline execution
        id: run-task
        run: |
          # Get VPC configuration
          SUBNETS=$(aws ec2 describe-subnets \
            --filters "Name=default-for-az,Values=true" \
            --query 'Subnets[*].SubnetId' \
            --output text \
            --region ${{ env.AWS_REGION }} | tr '\t' ',')

          SECURITY_GROUP=$(aws ec2 describe-security-groups \
            --filters "Name=group-name,Values=aig130-p2-ml-sg" \
            --query 'SecurityGroups[0].GroupId' \
            --output text \
            --region ${{ env.AWS_REGION }})

          # Run the task
          TASK_ARN=$(aws ecs run-task \
            --cluster ${{ env.ECS_CLUSTER }} \
            --task-definition ${{ env.ECS_TASK_DEFINITION }} \
            --launch-type FARGATE \
            --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SECURITY_GROUP],assignPublicIp=ENABLED}" \
            --region ${{ env.AWS_REGION }} \
            --query 'tasks[0].taskArn' \
            --output text)

          echo "Task ARN: $TASK_ARN"
          echo "task-arn=$TASK_ARN" >> $GITHUB_OUTPUT

          # Wait for task to start
          echo "Waiting for task to start..."
          aws ecs wait tasks-running \
            --cluster ${{ env.ECS_CLUSTER }} \
            --tasks $TASK_ARN \
            --region ${{ env.AWS_REGION }} || true

      - name: Display task execution status
        run: |
          echo "✅ Deployment successful!"
          echo "Task ARN: ${{ steps.run-task.outputs.task-arn }}"
          echo ""
          echo "To view logs, run:"
          echo "aws logs tail /ecs/${{ env.ECS_TASK_DEFINITION }} --follow --region ${{ env.AWS_REGION }}"
          echo ""
          echo "To check task status, run:"
          echo "aws ecs describe-tasks --cluster ${{ env.ECS_CLUSTER }} --tasks ${{ steps.run-task.outputs.task-arn }} --region ${{ env.AWS_REGION }}"
```

---

## Section 3: GitHub Secrets Configuration Guide

### Required Secrets

Navigate to your GitHub repository and add the following secrets:
**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

1. **AWS_ACCESS_KEY_ID**
   - Value: The Access Key ID from Step 2.3 (GitHub Actions IAM user)
   - Example: `AKIAIOSFODNN7EXAMPLE`

2. **AWS_SECRET_ACCESS_KEY**
   - Value: The Secret Access Key from Step 2.3
   - Example: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

3. **(Optional) AWS_ACCOUNT_ID**
   - Value: Your 12-digit AWS account ID
   - Only needed if you want to reference it in workflows
   - Example: `123456789012`

### Why GitHub Secrets are Secure

1. **Encryption at Rest**: Secrets are encrypted using libsodium sealed boxes before being stored
2. **Encryption in Transit**: Secrets are transmitted over HTTPS/TLS
3. **Access Control**: Only workflows in the repository can access these secrets
4. **Masking in Logs**: Secret values are automatically masked in workflow logs (shown as ***)
5. **No API Access**: Secrets cannot be retrieved via GitHub API
6. **Audit Logging**: GitHub logs all secret access events

### How to Add Secrets

```bash
# Via GitHub CLI (if you have gh installed)
gh secret set AWS_ACCESS_KEY_ID
gh secret set AWS_SECRET_ACCESS_KEY

# Or via GitHub Web UI:
# 1. Go to: https://github.com/YOUR_USERNAME/aig130project2/settings/secrets/actions
# 2. Click "New repository secret"
# 3. Name: AWS_ACCESS_KEY_ID
# 4. Value: [paste your access key]
# 5. Click "Add secret"
# 6. Repeat for AWS_SECRET_ACCESS_KEY
```

### Verifying Secrets

```bash
# List secrets (values are hidden)
gh secret list

# Output example:
# AWS_ACCESS_KEY_ID       Updated 2025-11-20
# AWS_SECRET_ACCESS_KEY   Updated 2025-11-20
```

---

## Section 4: Testing and Validation Steps

### Local Testing (Before AWS Deployment)

#### 4.1 Test Docker Build Locally

```bash
cd AIG130_Project2_Docker

# Build the image
docker build -t aig130-ml-local:test .

# Run locally (with local data)
docker run --rm aig130-ml-local:test

# Expected output: Training logs, model metrics, completion message
```

#### 4.2 Test S3 Access Locally

```bash
# Install AWS CLI if not already installed
pip install boto3 awscli

# Test S3 download
aws s3 cp s3://aig130-p2-ml-data-bucket/data/btc_1h_data_2018_to_2025.csv ./test_download.csv

# Verify file
ls -lh test_download.csv
md5 test_download.csv
```

### AWS Testing (Manual)

#### 4.3 Test ECR Push Manually

```bash
# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com

# Build and tag image
cd AIG130_Project2_Docker
docker build -t aig130-p2-ml-pipeline-ecr:manual-test .
docker tag aig130-p2-ml-pipeline-ecr:manual-test \
  ${ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/aig130-p2-ml-pipeline-ecr:manual-test

# Push to ECR
docker push ${ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/aig130-p2-ml-pipeline-ecr:manual-test

# Verify image in ECR
aws ecr describe-images \
  --repository-name aig130-p2-ml-pipeline-ecr \
  --region us-east-1
```

#### 4.4 Test ECS Task Execution

```bash
# Get VPC configuration
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" \
  --query "Vpcs[0].VpcId" --output text --region us-east-1)

SUBNETS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=${VPC_ID}" \
  --query "Subnets[*].SubnetId" --output text --region us-east-1 | tr '\t' ',')

SECURITY_GROUP=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=aig130-p2-ml-sg" \
  --query 'SecurityGroups[0].GroupId' --output text --region us-east-1)

# Run task
TASK_ARN=$(aws ecs run-task \
  --cluster aig130-p2-ml-cluster \
  --task-definition aig130-p2-ml-task \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SECURITY_GROUP],assignPublicIp=ENABLED}" \
  --region us-east-1 \
  --query 'tasks[0].taskArn' \
  --output text)

echo "Task ARN: $TASK_ARN"

# Monitor task status
aws ecs describe-tasks \
  --cluster aig130-p2-ml-cluster \
  --tasks $TASK_ARN \
  --region us-east-1 \
  --query 'tasks[0].lastStatus'

# View logs (wait 30 seconds after task starts)
aws logs tail /ecs/aig130-p2-ml-task --follow --region us-east-1
```

### GitHub Actions Testing

#### 4.5 Test GitHub Actions Workflow

```bash
# Method 1: Push to main branch (triggers automatically)
git add .
git commit -m "Test AWS deployment workflow"
git push origin main

# Method 2: Manual trigger (workflow_dispatch)
# Go to: https://github.com/YOUR_USERNAME/aig130project2/actions
# Select "Deploy ML Pipeline to AWS ECS" workflow
# Click "Run workflow" → Select branch: main → Click "Run workflow"

# Monitor the workflow
# https://github.com/YOUR_USERNAME/aig130project2/actions
```

#### 4.6 Verify Deployment

```bash
# Check latest task definition
aws ecs describe-task-definition \
  --task-definition aig130-p2-ml-task \
  --region us-east-1 \
  --query 'taskDefinition.revision'

# Check running tasks
aws ecs list-tasks \
  --cluster aig130-p2-ml-cluster \
  --region us-east-1

# Check S3 data file
aws s3 ls s3://aig130-p2-ml-data-bucket/data/ --human-readable

# View CloudWatch logs
aws logs tail /ecs/aig130-p2-ml-task --since 1h --region us-east-1
```

### Validation Checklist

- [ ] Local Docker build succeeds
- [ ] Local Docker run produces expected output
- [ ] S3 bucket created and data uploaded
- [ ] ECR repository created
- [ ] Manual ECR push succeeds
- [ ] IAM roles and policies created
- [ ] ECS cluster created
- [ ] ECS task definition registered
- [ ] Manual ECS task run succeeds
- [ ] Task logs appear in CloudWatch
- [ ] GitHub Secrets configured
- [ ] GitHub Actions workflow file created
- [ ] GitHub Actions workflow runs successfully
- [ ] ECS task accesses S3 data successfully
- [ ] ML pipeline completes without errors

---

## Section 5: Best Practices, Rationale, and Enhancements

### Why ECR + ECS + S3?

#### ECR (Elastic Container Registry)
- **Benefits:**
  - Native integration with AWS services
  - Automatic encryption at rest and in transit
  - Image scanning for vulnerabilities
  - Lifecycle policies for cost optimization
  - No need to manage Docker Hub rate limits

- **vs. Docker Hub:**
  - Better security and compliance
  - Faster pulls within AWS (same region)
  - No public exposure by default

#### ECS with Fargate
- **Benefits:**
  - Serverless - no EC2 instances to manage
  - Pay only for compute time used (per second billing)
  - Automatic scaling
  - Built-in load balancing (if needed)
  - Integration with CloudWatch for monitoring

- **vs. EC2-based ECS:**
  - No server maintenance
  - No underutilized resources
  - Automatic patching and security updates

- **vs. Lambda:**
  - No 15-minute timeout limit (Fargate tasks can run for hours)
  - More memory and CPU options (up to 30 GB RAM, 4 vCPU)
  - Better for ML workloads

#### S3 for Data Storage
- **Benefits:**
  - Durable (99.999999999% durability)
  - Scalable (unlimited storage)
  - Cost-effective (pennies per GB)
  - Versioning support
  - Fine-grained access control
  - Lifecycle policies for archival

- **vs. Embedding in Docker:**
  - Separates data from code
  - Easier data updates without rebuilding images
  - Multiple versions/datasets supported
  - Lower Docker image size

### Cost Considerations

#### Estimated Monthly Costs (Assumptions: 1 task run per day, 10 minutes per run)

1. **S3 Storage:**
   - BTC CSV file (~50 MB): $0.01/month
   - Requests: negligible

2. **ECR Storage:**
   - Docker images (~500 MB): $0.05/month
   - Data transfer: free within region

3. **ECS Fargate:**
   - CPU: 1 vCPU × 10 min × 30 runs = ~$1.50/month
   - Memory: 2 GB × 10 min × 30 runs = ~$0.50/month
   - **Total ECS: ~$2.00/month**

4. **CloudWatch Logs:**
   - Log storage (5 GB/month): $0.25/month
   - Log ingestion: negligible

**Total Estimated Cost: ~$2.50/month** (for daily runs)

**Cost Optimization Tips:**
- Use FARGATE_SPOT for 70% discount (for non-critical tasks)
- Set CloudWatch log retention to 7 days
- Use ECR lifecycle policies to delete old images
- Use smaller Docker images (multi-stage builds)
- Monitor with AWS Cost Explorer

### Scalability Benefits

1. **Horizontal Scaling:**
   - Run multiple tasks in parallel
   - Process multiple datasets simultaneously
   - Example: 10 concurrent tasks for different models

2. **Vertical Scaling:**
   - Adjust CPU/memory in task definition
   - Example: 4 vCPU + 8 GB RAM for larger datasets

3. **Auto Scaling:**
   - Use ECS auto-scaling with CloudWatch metrics
   - Scale based on CPU, memory, or custom metrics

4. **Geographic Distribution:**
   - Deploy to multiple AWS regions
   - Reduce latency for global teams

### Reproducibility and Deployment Enhancements

1. **Version Control:**
   - Docker images tagged with git SHA
   - S3 versioning for datasets
   - Task definition revisions tracked

2. **Immutable Infrastructure:**
   - Containers are ephemeral and reproducible
   - No manual configuration drift
   - Environment variables for configuration

3. **CI/CD Integration:**
   - Automated builds on every commit
   - Automated testing before deployment
   - Rollback capability (previous task definitions)

4. **Monitoring and Observability:**
   - CloudWatch Logs for debugging
   - CloudWatch Metrics for performance
   - AWS X-Ray for tracing (optional)

5. **Security:**
   - IAM roles with least privilege
   - No hardcoded credentials
   - Encrypted data at rest and in transit
   - Network isolation with VPC

### Additional Enhancements for Your Project

1. **Model Artifact Storage:**
   - Save trained models to S3 (not just in container)
   - Example: `s3://aig130-p2-ml-data-bucket/models/model_${GIT_SHA}.pkl`

2. **Result Visualization:**
   - Upload plots to S3
   - Create static website to view results
   - Example: S3 bucket with public read for plots

3. **Notification System:**
   - Use SNS to email on task completion/failure
   - Slack integration via webhooks

4. **Parameter Store:**
   - Use AWS Systems Manager Parameter Store for configs
   - Example: model hyperparameters, feature engineering settings

5. **Experiment Tracking:**
   - Integrate MLflow or Weights & Biases
   - Store experiment metadata in DynamoDB

6. **Scheduled Runs:**
   - Use EventBridge (CloudWatch Events) for cron jobs
   - Example: Daily retraining at 2 AM

7. **GPU Support:**
   - Currently Fargate doesn't support GPUs
   - If needed, use EC2-based ECS with GPU instances
   - Or use AWS SageMaker for GPU training

### Project Reflection Points

**For Your Report/Documentation:**

1. **Deployment Evolution:**
   - Local development → Dockerization → AWS deployment
   - Demonstrates understanding of cloud-native practices

2. **DevOps Skills:**
   - CI/CD pipeline implementation
   - Infrastructure as Code (task definitions, policies)
   - Automated testing and deployment

3. **Scalability Demonstration:**
   - From single-machine to cloud-scale
   - Ability to handle larger datasets or more frequent runs

4. **Cost Awareness:**
   - Understanding cloud economics
   - Optimization strategies

5. **Security Best Practices:**
   - IAM roles, no hardcoded secrets
   - Least privilege access

6. **Reproducibility:**
   - Anyone with AWS access can replicate
   - Fully automated deployment

---

## Troubleshooting Common Issues

### Issue 1: Task Fails with "CannotPullContainerError"

**Solution:**
```bash
# Check ECR permissions
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com

# Verify image exists
aws ecr describe-images --repository-name aig130-p2-ml-pipeline-ecr --region us-east-1

# Check task execution role has AmazonECSTaskExecutionRolePolicy
aws iam list-attached-role-policies --role-name aig130-p2-ecs-task-execution-role
```

### Issue 2: Task Fails with S3 Access Denied

**Solution:**
```bash
# Verify task role has S3 permissions
aws iam get-role-policy --role-name aig130-p2-ecs-task-role --policy-name s3-access-policy

# Test S3 access with task role
aws sts assume-role --role-arn arn:aws:iam::${ACCOUNT_ID}:role/aig130-p2-ecs-task-role --role-session-name test
```

### Issue 3: GitHub Actions Fails at ECR Login

**Solution:**
```bash
# Verify GitHub Secrets are set correctly
gh secret list

# Check IAM user permissions
aws iam list-attached-user-policies --user-name github-actions-aig130-p2
```

### Issue 4: Task Runs Out of Memory

**Solution:**
Update task definition with more memory:
```json
{
  "cpu": "2048",
  "memory": "4096"
}
```

### Issue 5: High Costs

**Solution:**
```bash
# Switch to Fargate Spot (in task definition or run-task command)
--capacity-provider-strategy capacityProvider=FARGATE_SPOT,weight=1

# Reduce CloudWatch log retention
aws logs put-retention-policy --log-group-name /ecs/aig130-p2-ml-task --retention-in-days 3
```

---

## Quick Reference Commands

```bash
# View running tasks
aws ecs list-tasks --cluster aig130-p2-ml-cluster --region us-east-1

# Stop a task
aws ecs stop-task --cluster aig130-p2-ml-cluster --task <TASK_ARN> --region us-east-1

# View logs
aws logs tail /ecs/aig130-p2-ml-task --follow --region us-east-1

# Update task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json --region us-east-1

# Delete all resources (cleanup)
aws ecs delete-cluster --cluster aig130-p2-ml-cluster --region us-east-1
aws ecr delete-repository --repository-name aig130-p2-ml-pipeline-ecr --force --region us-east-1
aws s3 rb s3://aig130-p2-ml-data-bucket --force
aws iam delete-role --role-name aig130-p2-ecs-task-execution-role
aws iam delete-role --role-name aig130-p2-ecs-task-role
```

---

## Next Steps

1. Complete AWS setup (Sections 1-10)
2. Add GitHub Secrets (Section 3)
3. Create `.github/workflows/deploy.yml` (Section 2)
4. Update code for S3 support (see below)
5. Push to GitHub and watch automatic deployment
6. Monitor logs and validate results

---

**End of AWS Deployment Guide**
