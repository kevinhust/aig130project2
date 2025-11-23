# ============================================================
# ECR Outputs
# ============================================================

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.ml_pipeline.repository_url
}

output "ecr_repository_name" {
  description = "Name of the ECR repository"
  value       = aws_ecr_repository.ml_pipeline.name
}

output "ecr_repository_arn" {
  description = "ARN of the ECR repository"
  value       = aws_ecr_repository.ml_pipeline.arn
}

# ============================================================
# ECS Outputs
# ============================================================

output "ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.ml_cluster.id
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.ml_cluster.name
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.ml_cluster.arn
}

output "ecs_task_definition_arn" {
  description = "ARN of the ECS task definition"
  value       = aws_ecs_task_definition.ml_task.arn
}

output "ecs_task_definition_family" {
  description = "Family name of the ECS task definition"
  value       = aws_ecs_task_definition.ml_task.family
}

# ============================================================
# IAM Outputs
# ============================================================

output "ecs_task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value       = aws_iam_role.ecs_task_execution_role.arn
}

output "ecs_task_role_arn" {
  description = "ARN of the ECS task role"
  value       = aws_iam_role.ecs_task_role.arn
}

# ============================================================
# Security Group Outputs
# ============================================================

output "security_group_id" {
  description = "ID of the security group"
  value       = aws_security_group.ml_pipeline_sg.id
}

output "security_group_name" {
  description = "Name of the security group"
  value       = aws_security_group.ml_pipeline_sg.name
}

# ============================================================
# CloudWatch Outputs
# ============================================================

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.ecs_logs.name
}

output "cloudwatch_log_group_arn" {
  description = "ARN of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.ecs_logs.arn
}

# ============================================================
# S3 Outputs
# ============================================================

output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = data.aws_s3_bucket.ml_data_bucket.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = data.aws_s3_bucket.ml_data_bucket.arn
}

# ============================================================
# Network Outputs
# ============================================================

output "vpc_id" {
  description = "ID of the default VPC"
  value       = data.aws_vpc.default.id
}

output "subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

# ============================================================
# GitHub Actions Outputs (if created)
# ============================================================

output "github_actions_user_name" {
  description = "Name of the GitHub Actions IAM user"
  value       = var.create_github_actions_user ? aws_iam_user.github_actions[0].name : null
}

output "github_actions_user_arn" {
  description = "ARN of the GitHub Actions IAM user"
  value       = var.create_github_actions_user ? aws_iam_user.github_actions[0].arn : null
}

output "github_actions_access_key_id" {
  description = "Access key ID for GitHub Actions user (SENSITIVE - store in GitHub Secrets)"
  value       = var.create_github_actions_user ? aws_iam_access_key.github_actions[0].id : null
  sensitive   = false
}

output "github_actions_secret_access_key" {
  description = "Secret access key for GitHub Actions user (SENSITIVE - store in GitHub Secrets)"
  value       = var.create_github_actions_user ? aws_iam_access_key.github_actions[0].secret : null
  sensitive   = true
}

# ============================================================
# Useful Commands
# ============================================================

output "useful_commands" {
  description = "Useful commands for working with the deployed infrastructure"
  value = {
    docker_login = "aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.ml_pipeline.repository_url}"

    docker_build_and_push = "cd ../AIG130_Project2_Docker && docker build -t ${aws_ecr_repository.ml_pipeline.repository_url}:latest . && docker push ${aws_ecr_repository.ml_pipeline.repository_url}:latest"

    run_ecs_task = "aws ecs run-task --cluster ${aws_ecs_cluster.ml_cluster.name} --task-definition ${aws_ecs_task_definition.ml_task.family} --launch-type FARGATE --network-configuration 'awsvpcConfiguration={subnets=[${join(",", aws_subnet.public[*].id)}],securityGroups=[${aws_security_group.ml_pipeline_sg.id}],assignPublicIp=ENABLED}'"

    view_logs = "aws logs tail ${aws_cloudwatch_log_group.ecs_logs.name} --follow"

    list_tasks = "aws ecs list-tasks --cluster ${aws_ecs_cluster.ml_cluster.name}"
  }
}
