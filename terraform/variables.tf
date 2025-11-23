variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for resource naming and tagging"
  type        = string
  default     = "aig130-p2"
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "prod"
}

# S3 Configuration
variable "s3_bucket_name" {
  description = "Name of the existing S3 bucket for ML data"
  type        = string
  default     = "aig130-p2-ml-data-bucket"
}

variable "s3_data_key" {
  description = "S3 key path for the training data file"
  type        = string
  default     = "data/btc_1h_data_2018_to_2025.csv"
}

# ECR Configuration
variable "ecr_repository_name" {
  description = "Name of the ECR repository"
  type        = string
  default     = "aig130-p2-ml-pipeline-ecr"
}

# ECS Configuration
variable "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
  default     = "aig130-p2-ml-cluster"
}

variable "ecs_task_definition_name" {
  description = "Name of the ECS task definition"
  type        = string
  default     = "aig130-p2-ml-task"
}

variable "container_name" {
  description = "Name of the container in the task definition"
  type        = string
  default     = "ml-pipeline-container"
}

variable "task_cpu" {
  description = "CPU units for the ECS task (1024 = 1 vCPU)"
  type        = string
  default     = "1024"
}

variable "task_memory" {
  description = "Memory for the ECS task in MB"
  type        = string
  default     = "2048"
}

# CloudWatch Configuration
variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 7
}

# GitHub Actions Configuration
variable "create_github_actions_user" {
  description = "Whether to create an IAM user for GitHub Actions"
  type        = bool
  default     = true
}
