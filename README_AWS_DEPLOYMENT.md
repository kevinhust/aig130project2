# AWS Deployment for AIG130 Project 2
# Bitcoin Price Prediction ML Pipeline

Welcome to the AWS deployment guide for your Bitcoin price prediction ML pipeline!

This README provides an overview of the deployment setup and links to detailed documentation.

---

## Quick Links

📚 **Documentation Files:**

1. **[DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)** ⭐ **START HERE**
   - Overview of all changes
   - What was created and modified
   - Architecture and deployment flow
   - Cost analysis and optimization
   - 20 pages of comprehensive information

2. **[AWS_DEPLOYMENT_QUICKSTART.md](./AWS_DEPLOYMENT_QUICKSTART.md)** 🚀 **Quick Reference**
   - TL;DR deployment steps
   - Common commands
   - Troubleshooting guide
   - Monitoring and debugging
   - 12 pages of quick reference

3. **[AWS_DEPLOYMENT_GUIDE.md](./AWS_DEPLOYMENT_GUIDE.md)** 📖 **Detailed Guide**
   - Step-by-step AWS setup instructions
   - Complete GitHub Actions workflow
   - Testing and validation procedures
   - Best practices and rationale
   - 29 pages of detailed instructions

4. **[.github/workflows/deploy.yml](./.github/workflows/deploy.yml)** ⚙️ **CI/CD Workflow**
   - GitHub Actions automation
   - Builds, tests, and deploys automatically
   - Triggered on push to `main` branch

---

## What's New?

### 🎯 Deployment Capabilities

Your ML pipeline now supports:

✅ **Automated Cloud Deployment** - Push to GitHub → Auto-deploy to AWS
✅ **Serverless Execution** - ECS Fargate (no servers to manage)
✅ **Cloud Data Storage** - Training data in S3
✅ **Container Registry** - Docker images in ECR
✅ **Monitoring** - CloudWatch logs for all executions
✅ **Security** - IAM roles, no hardcoded credentials
✅ **Cost Efficient** - ~$2.80/month for daily runs

### 📝 Files Created (4 new files)

1. `.github/workflows/deploy.yml` - GitHub Actions CI/CD workflow
2. `AWS_DEPLOYMENT_GUIDE.md` - Comprehensive deployment guide
3. `AWS_DEPLOYMENT_QUICKSTART.md` - Quick reference guide
4. `DEPLOYMENT_SUMMARY.md` - Overview and analysis

### 🔧 Files Modified (4 files)

1. `AIG130_Project2_Docker/requirements.txt` - Added boto3
2. `AIG130_Project2_Docker/config.py` - Added S3 configuration
3. `AIG130_Project2_Docker/src/data_loader.py` - Added S3 loading
4. `AIG130_Project2_Docker/Dockerfile` - Made data copy optional

### ✨ Features Added

- **S3 Data Loading:** Download training data from S3 bucket
- **Environment-Based Config:** USE_S3 flag controls local vs. cloud
- **Backward Compatible:** Existing local workflow unchanged
- **Automated Deployment:** GitHub Actions handles entire pipeline

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GITHUB REPOSITORY                     │
│  ┌─────────────┐    ┌──────────────┐   ┌─────────────┐ │
│  │ Source Code │    │ Dockerfile   │   │ .github/    │ │
│  │ (Python ML) │    │ (Container)  │   │ workflows/  │ │
│  └─────────────┘    └──────────────┘   └─────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │ Push to main
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  GITHUB ACTIONS (CI/CD)                  │
│  1. Build Docker Image                                   │
│  2. Push to ECR                                          │
│  3. Upload Data to S3                                    │
│  4. Deploy to ECS                                        │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┬────────────────┐
         ▼                       ▼                ▼
┌─────────────────┐    ┌──────────────────┐   ┌──────────┐
│  AWS ECR        │    │  AWS S3          │   │ AWS ECS  │
│  (Docker Image) │    │  (Training Data) │   │ (Fargate)│
│                 │    │                  │   │          │
│  Image:latest   │    │  BTC CSV file    │   │ ML Task  │
│  Image:sha123   │    │  50 MB           │   │ Runs     │
└─────────────────┘    └──────────────────┘   └────┬─────┘
                                                    │
                                                    ▼
                                            ┌───────────────┐
                                            │  CloudWatch   │
                                            │  Logs         │
                                            │  Monitoring   │
                                            └───────────────┘
```

---

## Cost Breakdown

### Monthly Cost (1 task/day, 10 min/run)

| Service | Cost/Month |
|---------|------------|
| S3 Storage | $0.001 |
| ECR Storage | $0.050 |
| ECS Fargate | $2.000 |
| CloudWatch | $0.750 |
| **Total** | **$2.80** |

### Optimized (FARGATE_SPOT + log retention)

| Service | Cost/Month |
|---------|------------|
| S3 Storage | $0.001 |
| ECR Storage | $0.050 |
| ECS Fargate SPOT | $0.600 |
| CloudWatch | $0.550 |
| **Total** | **$1.20** |

---

## Deployment Workflow

### 1️⃣ One-Time Setup (30 minutes)

**Prerequisites:**
- AWS Account
- AWS CLI installed
- GitHub repository

**Steps:**
```bash
# 1. Configure AWS CLI
aws configure

# 2. Run AWS setup commands
# See AWS_DEPLOYMENT_GUIDE.md Section 1

# 3. Configure GitHub Secrets
# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY

# 4. Push to GitHub
git push origin main
```

### 2️⃣ Every Deployment (Automatic)

```bash
# Make changes to your code
vim AIG130_Project2_Docker/main.py

# Commit and push
git add .
git commit -m "Update model parameters"
git push origin main

# GitHub Actions automatically:
# ✅ Builds Docker image
# ✅ Pushes to ECR
# ✅ Uploads data to S3
# ✅ Runs ECS task
# ✅ Logs to CloudWatch
```

---

## Testing Locally

### Test 1: Local Docker (No AWS)

```bash
cd AIG130_Project2_Docker

# Uncomment data COPY in Dockerfile first (line 54)
# Then build and run
docker build -t ml-pipeline:local .
docker run --rm ml-pipeline:local
```

### Test 2: Local Docker with S3 (AWS credentials required)

```bash
# Upload data to S3
aws s3 cp data/btc_1h_data_2018_to_2025.csv \
  s3://aig130-p2-ml-data-bucket/data/btc_1h_data_2018_to_2025.csv

# Run with S3
docker run --rm \
  -e USE_S3=true \
  -e S3_BUCKET=aig130-p2-ml-data-bucket \
  -e S3_KEY=data/btc_1h_data_2018_to_2025.csv \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_DEFAULT_REGION=us-east-1 \
  ml-pipeline:local
```

---

## Monitoring and Debugging

### View Logs

```bash
# View recent logs
aws logs tail /ecs/aig130-p2-ml-task --since 1h --region us-east-1

# Follow logs in real-time
aws logs tail /ecs/aig130-p2-ml-task --follow --region us-east-1
```

### Check Task Status

```bash
# List running tasks
aws ecs list-tasks --cluster aig130-p2-ml-cluster --region us-east-1

# Get task details
aws ecs describe-tasks \
  --cluster aig130-p2-ml-cluster \
  --tasks <TASK_ARN> \
  --region us-east-1
```

### Verify GitHub Actions

Go to: https://github.com/YOUR_USERNAME/aig130project2/actions

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| GitHub Actions fails at ECR login | Check GitHub Secrets are set correctly |
| Task fails with "CannotPullContainerError" | Verify ECR repository exists and task execution role has permissions |
| Task fails with S3 access denied | Check task role has S3 read permissions |
| Task runs out of memory | Increase memory in task definition (edit task-definition.json) |

### Quick Diagnostics

```bash
# Check all resources exist
aws s3 ls s3://aig130-p2-ml-data-bucket/data/
aws ecr describe-repositories --repository-names aig130-p2-ml-pipeline-ecr
aws ecs describe-clusters --clusters aig130-p2-ml-cluster
aws logs describe-log-groups --log-group-name-prefix /ecs/aig130-p2-ml-task

# Check IAM roles
aws iam get-role --role-name aig130-p2-ecs-task-execution-role
aws iam get-role --role-name aig130-p2-ecs-task-role
```

---

## Security Features

✅ **No Hardcoded Credentials:** All credentials via IAM roles or GitHub Secrets
✅ **Least Privilege IAM:** Roles have minimum required permissions
✅ **Encrypted Storage:** S3 and ECR encryption at rest
✅ **Network Isolation:** ECS tasks in VPC with security group
✅ **Container Security:** Non-root user, minimal image, vulnerability scanning
✅ **Secrets Management:** GitHub Secrets encrypted, never exposed in logs

---

## Scalability

### Horizontal Scaling (Run Multiple Tasks)

```bash
# Run 5 parallel experiments
for i in {1..5}; do
  aws ecs run-task \
    --cluster aig130-p2-ml-cluster \
    --task-definition aig130-p2-ml-task \
    --launch-type FARGATE \
    --network-configuration "..." &
done
```

### Vertical Scaling (Increase Resources)

Edit `task-definition.json`:
```json
{
  "cpu": "4096",      // 4 vCPU (from 1024)
  "memory": "8192"    // 8 GB  (from 2048)
}
```

---

## Project Value

### For AIG130 Project Report

This deployment demonstrates:

1. **Modern ML Engineering:** Cloud-native deployment with CI/CD
2. **DevOps Skills:** GitHub Actions, Docker, AWS infrastructure
3. **Scalability:** From laptop to cloud-scale processing
4. **Reproducibility:** Containerization ensures consistent results
5. **Cost Awareness:** ~$1-3/month for production deployment
6. **Security:** IAM roles, encrypted storage, least privilege
7. **Professional Skills:** Real-world deployment practices

### Technical Skills Demonstrated

- Docker containerization
- CI/CD pipeline implementation
- AWS cloud services (ECR, ECS, S3, IAM, CloudWatch)
- Infrastructure as Code
- Environment-based configuration
- Security best practices
- Cost optimization

---

## Next Steps

### Immediate (Required)

1. Read `DEPLOYMENT_SUMMARY.md` for overview
2. Follow `AWS_DEPLOYMENT_GUIDE.md` Section 1 for AWS setup
3. Configure GitHub Secrets
4. Push to GitHub and monitor first deployment

### Optional Enhancements

- **Model Serving:** Deploy Flask API for predictions
- **Scheduled Runs:** EventBridge cron for daily retraining
- **Notifications:** SNS alerts on success/failure
- **Experiment Tracking:** MLflow integration
- **GPU Support:** Switch to EC2-based ECS or SageMaker
- **Model Versioning:** Save models to S3 with git SHA

---

## Documentation Structure

```
📁 aig130project2/
├── 📄 README_AWS_DEPLOYMENT.md (THIS FILE)
│   └── Overview and quick links
│
├── 📄 DEPLOYMENT_SUMMARY.md ⭐ START HERE
│   ├── Executive summary
│   ├── All changes explained
│   ├── Architecture diagrams
│   ├── Cost analysis
│   └── Security and scalability
│
├── 📄 AWS_DEPLOYMENT_QUICKSTART.md 🚀 QUICK REFERENCE
│   ├── TL;DR deployment steps
│   ├── Common commands
│   ├── Troubleshooting
│   └── Monitoring
│
├── 📄 AWS_DEPLOYMENT_GUIDE.md 📖 DETAILED GUIDE
│   ├── Step-by-step AWS setup
│   ├── IAM roles and policies
│   ├── Complete workflow YAML
│   ├── Testing procedures
│   └── Best practices
│
├── 📁 .github/workflows/
│   └── 📄 deploy.yml
│       └── GitHub Actions CI/CD workflow
│
└── 📁 AIG130_Project2_Docker/
    ├── 📄 requirements.txt (MODIFIED - added boto3)
    ├── 📄 config.py (MODIFIED - S3 support)
    ├── 📄 Dockerfile (MODIFIED - optional data)
    └── 📁 src/
        └── 📄 data_loader.py (MODIFIED - S3 loading)
```

---

## Support and Resources

### Documentation
- **Deployment Summary:** [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)
- **Quick Start:** [AWS_DEPLOYMENT_QUICKSTART.md](./AWS_DEPLOYMENT_QUICKSTART.md)
- **Full Guide:** [AWS_DEPLOYMENT_GUIDE.md](./AWS_DEPLOYMENT_GUIDE.md)

### AWS Documentation
- [Amazon ECS](https://docs.aws.amazon.com/ecs/)
- [Amazon ECR](https://docs.aws.amazon.com/ecr/)
- [Amazon S3](https://docs.aws.amazon.com/s3/)
- [AWS Fargate](https://docs.aws.amazon.com/fargate/)

### GitHub
- [GitHub Actions](https://docs.github.com/en/actions)
- [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

## Quick Commands Reference

```bash
# View logs
aws logs tail /ecs/aig130-p2-ml-task --follow

# List tasks
aws ecs list-tasks --cluster aig130-p2-ml-cluster

# Check S3 data
aws s3 ls s3://aig130-p2-ml-data-bucket/data/

# Check ECR images
aws ecr list-images --repository-name aig130-p2-ml-pipeline-ecr

# Run manual task
aws ecs run-task \
  --cluster aig130-p2-ml-cluster \
  --task-definition aig130-p2-ml-task \
  --launch-type FARGATE

# Check GitHub Actions
# Go to: https://github.com/YOUR_USERNAME/aig130project2/actions
```

---

## Summary

Your Bitcoin price prediction ML pipeline is now configured for production AWS deployment with:

✅ Automated CI/CD via GitHub Actions
✅ Serverless execution with ECS Fargate
✅ Cloud storage with S3
✅ Container registry with ECR
✅ Monitoring with CloudWatch
✅ Secure IAM-based authentication
✅ ~$1-3/month cost for daily runs
✅ 100% backward compatible with local development

**Total Documentation:** 1,500+ lines across 4 comprehensive guides

**Ready to deploy?** Start with [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)

---

**Good luck with your deployment!** 🚀
