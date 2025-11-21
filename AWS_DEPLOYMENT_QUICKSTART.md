# AWS Deployment Quick Start Guide
# AIG130 Project 2 - Bitcoin Price Prediction ML Pipeline

This is a quick reference guide for deploying your ML pipeline to AWS. For detailed instructions, see `AWS_DEPLOYMENT_GUIDE.md`.

---

## What Was Changed

### 1. Code Updates for S3 Support

**Files Modified:**
- `AIG130_Project2_Docker/requirements.txt` - Added boto3 for AWS S3 access
- `AIG130_Project2_Docker/config.py` - Added S3 configuration from environment variables
- `AIG130_Project2_Docker/src/data_loader.py` - Added S3 data loading capability
- `AIG130_Project2_Docker/Dockerfile` - Commented out local data copy (data now loads from S3)

**How it works:**
- When `USE_S3=true` environment variable is set, the pipeline loads data from S3
- When `USE_S3=false` or not set, it loads from local file (for local testing)
- S3 bucket and key are configured via environment variables

### 2. New Files Created

- `.github/workflows/deploy.yml` - GitHub Actions workflow for automated deployment
- `AWS_DEPLOYMENT_GUIDE.md` - Comprehensive deployment documentation
- `AWS_DEPLOYMENT_QUICKSTART.md` - This file

---

## Prerequisites Checklist

Before deploying, ensure you have:

- [ ] AWS Account with admin access
- [ ] AWS CLI installed (`aws --version` should work)
- [ ] GitHub repository pushed to `main` branch
- [ ] Local Docker installation for testing

---

## Deployment Steps (TL;DR)

### Step 1: Configure AWS CLI (5 minutes)

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter region: us-east-1
# Enter output format: json
```

### Step 2: Run AWS Setup Script (10 minutes)

You can either run the commands manually from `AWS_DEPLOYMENT_GUIDE.md` Section 1, or use this condensed script:

```bash
# Set your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $ACCOUNT_ID"

# 1. Create IAM roles
bash setup_iam_roles.sh  # See below for script contents

# 2. Create S3 bucket and upload data
aws s3 mb s3://aig130-p2-ml-data-bucket --region us-east-1
aws s3 cp AIG130_Project2_Docker/data/btc_1h_data_2018_to_2025.csv \
  s3://aig130-p2-ml-data-bucket/data/btc_1h_data_2018_to_2025.csv

# 3. Create ECR repository
aws ecr create-repository \
  --repository-name aig130-p2-ml-pipeline-ecr \
  --region us-east-1 \
  --image-scanning-configuration scanOnPush=true

# 4. Create ECS cluster
aws ecs create-cluster \
  --cluster-name aig130-p2-ml-cluster \
  --region us-east-1

# 5. Create log group
aws logs create-log-group \
  --log-group-name /ecs/aig130-p2-ml-task \
  --region us-east-1

# 6. Create and register task definition
# (See AWS_DEPLOYMENT_GUIDE.md Step 6 for full task definition)
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json \
  --region us-east-1

# 7. Get VPC info for security group
VPC_ID=$(aws ec2 describe-vpcs \
  --filters "Name=isDefault,Values=true" \
  --query "Vpcs[0].VpcId" \
  --output text \
  --region us-east-1)

# Create security group
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
  --group-name aig130-p2-ml-sg \
  --description "Security group for AIG130 P2 ML ECS tasks" \
  --vpc-id ${VPC_ID} \
  --region us-east-1 \
  --query 'GroupId' \
  --output text)

echo "✅ AWS Setup Complete!"
echo "Security Group ID: $SECURITY_GROUP_ID"
```

### Step 3: Configure GitHub Secrets (2 minutes)

Go to your GitHub repository:
**Settings → Secrets and variables → Actions → New repository secret**

Add these secrets:

1. `AWS_ACCESS_KEY_ID` - Your AWS access key
2. `AWS_SECRET_ACCESS_KEY` - Your AWS secret key

```bash
# Or use GitHub CLI:
gh secret set AWS_ACCESS_KEY_ID
gh secret set AWS_SECRET_ACCESS_KEY
```

### Step 4: Deploy (Automatic)

Push to main branch to trigger deployment:

```bash
git add .
git commit -m "Setup AWS deployment with ECR, ECS, and S3"
git push origin main
```

Watch the deployment at: `https://github.com/YOUR_USERNAME/aig130project2/actions`

---

## Local Testing Before AWS Deployment

### Test 1: Build Docker Image Locally

```bash
cd AIG130_Project2_Docker

# Uncomment the data COPY line in Dockerfile first:
# Line 54: COPY --chown=appuser:appuser data/btc_1h_data_2018_to_2025.csv ./data/

docker build -t aig130-ml-local:test .
docker run --rm aig130-ml-local:test
```

### Test 2: Test with S3 (Requires AWS credentials)

```bash
# Set AWS credentials as environment variables
docker run --rm \
  -e USE_S3=true \
  -e S3_BUCKET=aig130-p2-ml-data-bucket \
  -e S3_KEY=data/btc_1h_data_2018_to_2025.csv \
  -e AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY \
  -e AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY \
  -e AWS_DEFAULT_REGION=us-east-1 \
  aig130-ml-local:test
```

---

## Monitoring and Debugging

### View ECS Task Logs

```bash
# View recent logs
aws logs tail /ecs/aig130-p2-ml-task --since 1h --region us-east-1

# Follow logs in real-time
aws logs tail /ecs/aig130-p2-ml-task --follow --region us-east-1
```

### Check Running Tasks

```bash
# List running tasks
aws ecs list-tasks \
  --cluster aig130-p2-ml-cluster \
  --region us-east-1

# Get task details
TASK_ARN=<task-arn-from-above>
aws ecs describe-tasks \
  --cluster aig130-p2-ml-cluster \
  --tasks $TASK_ARN \
  --region us-east-1
```

### Verify S3 Data

```bash
# Check if data file exists in S3
aws s3 ls s3://aig130-p2-ml-data-bucket/data/ --human-readable

# Download data file to verify
aws s3 cp s3://aig130-p2-ml-data-bucket/data/btc_1h_data_2018_to_2025.csv ./verify.csv
```

### Check ECR Images

```bash
# List images in ECR
aws ecr describe-images \
  --repository-name aig130-p2-ml-pipeline-ecr \
  --region us-east-1 \
  --query 'imageDetails[*].[imageTags[0],imagePushedAt]' \
  --output table
```

---

## Cost Estimate

Based on running 1 task per day for 10 minutes:

| Service | Cost/Month |
|---------|------------|
| S3 Storage (50 MB) | $0.01 |
| ECR Storage (500 MB) | $0.05 |
| ECS Fargate (1 vCPU, 2 GB) | $2.00 |
| CloudWatch Logs (5 GB) | $0.25 |
| **Total** | **~$2.50/month** |

**To reduce costs:**
- Use FARGATE_SPOT (70% cheaper)
- Reduce CloudWatch log retention to 3-7 days
- Use ECR lifecycle policies to auto-delete old images

---

## Common Issues and Solutions

### Issue: "CannotPullContainerError"

**Solution:** Check that the ECR repository exists and task execution role has permissions

```bash
aws ecr describe-repositories --repository-names aig130-p2-ml-pipeline-ecr --region us-east-1
aws iam list-attached-role-policies --role-name aig130-p2-ecs-task-execution-role
```

### Issue: "AccessDenied" when accessing S3

**Solution:** Verify task role has S3 permissions

```bash
aws iam get-role-policy \
  --role-name aig130-p2-ecs-task-role \
  --policy-name aig130-p2-s3-access-policy
```

### Issue: GitHub Actions fails at ECR login

**Solution:** Verify GitHub Secrets are set correctly

```bash
gh secret list
# Should show:
# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY
```

### Issue: Task runs out of memory

**Solution:** Increase memory in task definition

Edit `task-definition.json`:
```json
{
  "cpu": "2048",
  "memory": "4096"
}
```

Then re-register:
```bash
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json \
  --region us-east-1
```

---

## Manual Task Execution (Testing)

To manually run a task (useful for testing):

```bash
# Get VPC configuration
SUBNETS=$(aws ec2 describe-subnets \
  --filters "Name=default-for-az,Values=true" \
  --query 'Subnets[*].SubnetId' \
  --output text \
  --region us-east-1 | tr '\t' ',')

SECURITY_GROUP=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=aig130-p2-ml-sg" \
  --query 'SecurityGroups[0].GroupId' \
  --output text \
  --region us-east-1)

# Run task
aws ecs run-task \
  --cluster aig130-p2-ml-cluster \
  --task-definition aig130-p2-ml-task \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SECURITY_GROUP],assignPublicIp=ENABLED}" \
  --region us-east-1
```

---

## Cleanup (Delete All Resources)

**WARNING:** This will delete all AWS resources and data. Only run if you want to completely remove the deployment.

```bash
# Delete ECS cluster (must have no tasks running)
aws ecs delete-cluster --cluster aig130-p2-ml-cluster --region us-east-1

# Delete ECR repository
aws ecr delete-repository \
  --repository-name aig130-p2-ml-pipeline-ecr \
  --force \
  --region us-east-1

# Delete S3 bucket
aws s3 rm s3://aig130-p2-ml-data-bucket --recursive
aws s3 rb s3://aig130-p2-ml-data-bucket

# Delete CloudWatch log group
aws logs delete-log-group \
  --log-group-name /ecs/aig130-p2-ml-task \
  --region us-east-1

# Delete security group
SECURITY_GROUP=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=aig130-p2-ml-sg" \
  --query 'SecurityGroups[0].GroupId' \
  --output text \
  --region us-east-1)
aws ec2 delete-security-group --group-id $SECURITY_GROUP --region us-east-1

# Detach and delete IAM policies and roles
# (See AWS_DEPLOYMENT_GUIDE.md for detailed cleanup)
```

---

## Architecture Diagram (Text)

```
┌─────────────────┐
│  GitHub Repo    │
│  (Push to main) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GitHub Actions  │
│ - Build Docker  │
│ - Push to ECR   │
│ - Upload to S3  │
│ - Deploy to ECS │
└────────┬────────┘
         │
    ┌────┴────┬────────────┬────────────┐
    │         │            │            │
    ▼         ▼            ▼            ▼
┌─────┐  ┌─────┐      ┌─────┐      ┌─────┐
│ ECR │  │ S3  │      │ ECS │      │ IAM │
│     │  │     │      │     │      │     │
│Image│  │Data │      │Task │      │Roles│
└─────┘  └─────┘      └──┬──┘      └─────┘
                          │
                          ▼
                    ┌───────────┐
                    │CloudWatch │
                    │   Logs    │
                    └───────────┘
```

---

## Next Steps

After successful deployment:

1. **Monitor Logs:** Watch task execution in CloudWatch
2. **Optimize Costs:** Consider FARGATE_SPOT for 70% savings
3. **Add Notifications:** Set up SNS alerts for task failures
4. **Model Versioning:** Save trained models to S3 with git SHA tags
5. **Scheduled Runs:** Use EventBridge to run tasks on a schedule
6. **Experiment Tracking:** Integrate MLflow or Weights & Biases

---

## Project Reflection Points

For your AIG130 project report, highlight:

1. **Cloud-Native Transformation:**
   - Evolution from local scripts to containerized cloud deployment
   - Demonstrates understanding of modern ML deployment practices

2. **DevOps Integration:**
   - Automated CI/CD pipeline with GitHub Actions
   - Infrastructure as Code with task definitions and policies

3. **Data Management:**
   - Separation of data and code using S3
   - Environment-based configuration (local vs. cloud)

4. **Scalability:**
   - Serverless architecture with Fargate
   - Ability to run parallel experiments
   - Cost-efficient pay-per-use model

5. **Security:**
   - IAM roles with least privilege
   - No hardcoded credentials
   - Encrypted data in transit and at rest

6. **Reproducibility:**
   - Docker ensures consistent environment
   - Version-controlled infrastructure
   - Anyone with AWS access can replicate

---

## Resources

- **Full Guide:** `AWS_DEPLOYMENT_GUIDE.md`
- **AWS Documentation:** https://docs.aws.amazon.com/ecs/
- **GitHub Actions:** https://docs.github.com/en/actions
- **Docker Best Practices:** https://docs.docker.com/develop/dev-best-practices/

---

**Questions or Issues?**

Check the troubleshooting section in `AWS_DEPLOYMENT_GUIDE.md` or refer to AWS documentation.

Good luck with your deployment!
