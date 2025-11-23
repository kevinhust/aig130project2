#!/bin/bash

# Terraform Destroy Script for AIG130 Project 2
# This script safely destroys all Terraform-managed AWS resources

set -e  # Exit on error

echo "=========================================="
echo "AIG130 Project 2 - AWS Resource Cleanup"
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

# Check if Terraform is initialized
if [ ! -d ".terraform" ]; then
    echo -e "${RED}Error: Terraform not initialized. Run 'terraform init' first${NC}"
    exit 1
fi

echo -e "${YELLOW}⚠ WARNING: This will destroy all AWS resources managed by Terraform!${NC}"
echo ""
echo "Resources that will be DELETED:"
echo "  • ECR Repository (and all Docker images)"
echo "  • ECS Cluster"
echo "  • ECS Task Definition"
echo "  • IAM Roles and Policies"
echo "  • Security Group"
echo "  • CloudWatch Log Group (and all logs)"
echo "  • GitHub Actions IAM User (if created)"
echo ""
echo -e "${GREEN}Resources that will be PRESERVED:${NC}"
echo "  • S3 Bucket (not managed by Terraform)"
echo "  • VPC and Subnets (default VPC)"
echo ""

# Ask for confirmation
read -p "Are you absolutely sure you want to destroy all resources? (type 'yes' to confirm) " -r
echo

if [[ $REPLY != "yes" ]]; then
    echo "Destruction cancelled"
    exit 0
fi

# Second confirmation
echo ""
echo -e "${RED}FINAL WARNING: This action cannot be undone!${NC}"
read -p "Type the project name 'aig130-p2' to confirm: " -r
echo

if [[ $REPLY != "aig130-p2" ]]; then
    echo "Confirmation failed. Destruction cancelled"
    exit 0
fi

echo ""
echo "Creating destruction plan..."
terraform plan -destroy -out=destroy.tfplan

echo ""
read -p "Review the plan above. Proceed with destruction? (yes/no) " -r
echo

if [[ $REPLY == "yes" ]]; then
    echo ""
    echo "Destroying resources..."
    terraform apply destroy.tfplan

    # Clean up plan file
    rm -f destroy.tfplan

    echo ""
    echo -e "${GREEN}=========================================="
    echo "Resources Destroyed Successfully!"
    echo -e "==========================================${NC}"
    echo ""
    echo "What was removed:"
    echo "  ✓ ECR Repository"
    echo "  ✓ ECS Cluster"
    echo "  ✓ ECS Task Definition"
    echo "  ✓ IAM Roles and Policies"
    echo "  ✓ Security Group"
    echo "  ✓ CloudWatch Logs"
    echo "  ✓ GitHub Actions User"
    echo ""
    echo "What remains:"
    echo "  • S3 Bucket: aig130-p2-ml-data-bucket"
    echo "  • Terraform state files (local)"
    echo ""
    echo "To completely clean up:"
    echo "  1. Delete S3 bucket (if no longer needed):"
    echo "     aws s3 rb s3://aig130-p2-ml-data-bucket --force"
    echo ""
    echo "  2. Remove Terraform state files:"
    echo "     rm -rf .terraform terraform.tfstate*"
    echo ""
else
    echo "Destruction cancelled"
    rm -f destroy.tfplan
    exit 0
fi
