#!/bin/bash

# Terraform Deployment Script for AIG130 Project 2
# This script automates the deployment of AWS infrastructure

set -e  # Exit on error

echo "=========================================="
echo "AIG130 Project 2 - AWS Terraform Deployment"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from terraform directory
if [ ! -f "main.tf" ]; then
    echo -e "${RED}Error: Please run this script from the terraform directory${NC}"
    exit 1
fi

# Check prerequisites
echo "Checking prerequisites..."

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    echo "Install: https://aws.amazon.com/cli/"
    exit 1
fi
echo -e "${GREEN}✓ AWS CLI installed${NC}"

# Check Terraform
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}Error: Terraform is not installed${NC}"
    echo "Install: https://www.terraform.io/downloads"
    exit 1
fi
echo -e "${GREEN}✓ Terraform installed${NC}"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi
echo -e "${GREEN}✓ AWS credentials configured${NC}"

# Check if S3 bucket exists
S3_BUCKET="${S3_BUCKET:-aig130-p2-ml-data-bucket}"
if aws s3 ls "s3://${S3_BUCKET}" &> /dev/null; then
    echo -e "${GREEN}✓ S3 bucket exists: ${S3_BUCKET}${NC}"
else
    echo -e "${YELLOW}⚠ S3 bucket not found: ${S3_BUCKET}${NC}"
    read -p "Do you want to create it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        aws s3 mb "s3://${S3_BUCKET}"
        echo -e "${GREEN}✓ S3 bucket created${NC}"
    else
        echo -e "${RED}Error: S3 bucket is required${NC}"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Starting Terraform Deployment"
echo "=========================================="
echo ""

# Initialize Terraform
echo "Step 1: Initializing Terraform..."
terraform init

# Validate configuration
echo ""
echo "Step 2: Validating configuration..."
terraform validate

# Format check
echo ""
echo "Step 3: Checking formatting..."
terraform fmt -check || terraform fmt

# Plan
echo ""
echo "Step 4: Creating deployment plan..."
terraform plan -out=tfplan

# Ask for confirmation
echo ""
echo -e "${YELLOW}=========================================="
echo "Ready to deploy!"
echo -e "==========================================${NC}"
read -p "Do you want to apply this plan? (yes/no) " -r
echo

if [[ $REPLY == "yes" ]]; then
    # Apply
    echo ""
    echo "Step 5: Applying configuration..."
    terraform apply tfplan

    # Clean up plan file
    rm -f tfplan

    echo ""
    echo -e "${GREEN}=========================================="
    echo "Deployment Complete!"
    echo -e "==========================================${NC}"
    echo ""

    # Display important outputs
    echo "Important Information:"
    echo "----------------------"
    echo ""
    echo "ECR Repository URL:"
    terraform output -raw ecr_repository_url
    echo ""
    echo ""

    echo "ECS Cluster Name:"
    terraform output -raw ecs_cluster_name
    echo ""
    echo ""

    # Check if GitHub Actions user was created
    if terraform output github_actions_access_key_id &> /dev/null; then
        echo -e "${YELLOW}GitHub Actions Credentials (SAVE THESE):${NC}"
        echo "Access Key ID:"
        terraform output -raw github_actions_access_key_id
        echo ""
        echo ""
        echo "Secret Access Key:"
        terraform output -raw github_actions_secret_access_key
        echo ""
        echo ""
        echo -e "${YELLOW}⚠ Important: Add these to your GitHub repository secrets!${NC}"
        echo ""
    fi

    echo "Next Steps:"
    echo "----------"
    echo "1. Build and push Docker image:"
    echo "   cd ../AIG130_Project2_Docker"
    echo "   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin \$(cd ../terraform && terraform output -raw ecr_repository_url)"
    echo "   docker build -t \$(cd ../terraform && terraform output -raw ecr_repository_url):latest ."
    echo "   docker push \$(cd ../terraform && terraform output -raw ecr_repository_url):latest"
    echo ""
    echo "2. Configure GitHub Secrets (if using CI/CD)"
    echo ""
    echo "3. Run the ML pipeline:"
    echo "   See README.md for commands"
    echo ""

else
    echo "Deployment cancelled"
    rm -f tfplan
    exit 0
fi
