# Terraform Quick Start Guide

## 最快 5 分钟部署

### 前置条件检查

```bash
# 检查 AWS CLI
aws --version

# 检查 Terraform
terraform --version

# 检查 AWS 凭证
aws sts get-caller-identity

# 检查 S3 bucket 是否存在
aws s3 ls s3://aig130-p2-ml-data-bucket
```

### 方法 1: 使用自动化脚本（推荐）

```bash
cd terraform
./deploy.sh
```

脚本会自动执行所有步骤，并在最后显示重要信息。

### 方法 2: 手动执行

```bash
cd terraform

# 1. 初始化
terraform init

# 2. 查看计划
terraform plan

# 3. 部署
terraform apply
# 输入 'yes' 确认

# 4. 查看输出
terraform output
```

## 部署后立即可用的命令

部署完成后，运行以下命令获取所有有用的命令：

```bash
terraform output useful_commands
```

### 常用操作

#### 1. 登录 ECR
```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $(terraform output -raw ecr_repository_url)
```

#### 2. 构建并推送镜像
```bash
cd ../AIG130_Project2_Docker
docker build -t $(cd ../terraform && terraform output -raw ecr_repository_url):latest .
docker push $(cd ../terraform && terraform output -raw ecr_repository_url):latest
```

#### 3. 运行 ML Pipeline
```bash
cd terraform
aws ecs run-task \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --task-definition $(terraform output -raw ecs_task_definition_family) \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$(terraform output -json subnet_ids | jq -r '.[0]')],securityGroups=[$(terraform output -raw security_group_id)],assignPublicIp=ENABLED}"
```

#### 4. 查看日志
```bash
aws logs tail $(terraform output -raw cloudwatch_log_group_name) --follow
```

## GitHub Actions 配置

### 获取密钥
```bash
# Access Key ID
terraform output github_actions_access_key_id

# Secret Access Key
terraform output -raw github_actions_secret_access_key
```

### 添加到 GitHub
1. 进入仓库的 Settings → Secrets and variables → Actions
2. 添加两个 secrets：
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

## 销毁资源

```bash
cd terraform
./destroy.sh
```

或手动执行：
```bash
terraform destroy
```

## 故障排查

### 问题: S3 bucket 不存在

```bash
# 创建 bucket
aws s3 mb s3://aig130-p2-ml-data-bucket

# 上传数据
aws s3 cp ../AIG130_Project2_Docker/data/btc_1h_data_2018_to_2025.csv \
  s3://aig130-p2-ml-data-bucket/data/btc_1h_data_2018_to_2025.csv
```

### 问题: ECR 仓库已存在

```bash
# 导入现有仓库
terraform import aws_ecr_repository.ml_pipeline aig130-p2-ml-pipeline-ecr
```

### 问题: 任务无法拉取镜像

```bash
# 检查 ECR 中是否有镜像
aws ecr describe-images --repository-name aig130-p2-ml-pipeline-ecr

# 如果没有，构建并推送
cd ../AIG130_Project2_Docker
docker build -t $(cd ../terraform && terraform output -raw ecr_repository_url):latest .
docker push $(cd ../terraform && terraform output -raw ecr_repository_url):latest
```

## 成本估算

| 资源 | 月成本（USD） |
|-----|------------|
| ECR 存储 | $0.05 |
| ECS Fargate (30次运行) | $2.70 |
| CloudWatch 日志 | $0.25 |
| **总计** | **~$3.00** |

## 文件说明

- `main.tf` - 主要资源定义
- `variables.tf` - 变量声明
- `outputs.tf` - 输出配置
- `README.md` - 详细文档
- `deploy.sh` - 自动部署脚本
- `destroy.sh` - 清理脚本

## 下一步

1. ✅ Terraform 部署完成
2. ⬜ 构建并推送 Docker 镜像
3. ⬜ 配置 GitHub Secrets
4. ⬜ 测试 ECS 任务运行
5. ⬜ 推送代码触发 CI/CD

---

**提示**: 查看 `README.md` 获取完整文档和高级配置选项。
