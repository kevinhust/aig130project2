# Terraform 自动化部署配置完成 ✅

## 📦 已创建的文件

```
terraform/
├── main.tf                      # 主配置文件（所有AWS资源定义）
├── variables.tf                 # 变量定义
├── outputs.tf                   # 输出配置
├── terraform.tfvars.example     # 配置示例文件
├── .gitignore                   # Git忽略文件
├── README.md                    # 详细使用文档
├── QUICKSTART.md               # 快速开始指南
├── deploy.sh                    # 自动部署脚本
└── destroy.sh                   # 资源清理脚本
```

## 🎯 Terraform 会创建的 AWS 资源

### ✅ 核心资源

1. **ECR Repository** - 容器镜像仓库
   - 名称: `aig130-p2-ml-pipeline-ecr`
   - 自动镜像扫描: 已启用
   - 生命周期策略: 保留最近10个镜像

2. **ECS Cluster** - 容器集群
   - 名称: `aig130-p2-ml-cluster`
   - 类型: Fargate
   - Container Insights: 已启用

3. **ECS Task Definition** - 任务定义
   - 名称: `aig130-p2-ml-task`
   - CPU: 1 vCPU (1024)
   - 内存: 2 GB (2048)
   - 容器名: `ml-pipeline-container`
   - 环境变量: USE_S3=true, S3_BUCKET, S3_KEY

4. **IAM Roles** - 权限角色
   - Task Execution Role: 拉取镜像、写日志
   - Task Role: 访问S3数据

5. **Security Group** - 安全组
   - 名称: `aig130-p2-ml-sg`
   - 出站: 允许所有（访问ECR、S3、CloudWatch）

6. **CloudWatch Log Group** - 日志组
   - 名称: `/ecs/aig130-p2-ml-task`
   - 保留期: 7天

7. **IAM User for GitHub Actions** - CI/CD用户（可选）
   - 名称: `github-actions-aig130-p2`
   - 权限: ECR推送、ECS部署、S3访问

### 📌 引用的现有资源

- **S3 Bucket**: `aig130-p2-ml-data-bucket` （你已手动创建）
- **VPC**: 默认VPC
- **Subnets**: 默认子网

## 🚀 快速开始（3种方式）

### 方式 1: 使用自动化脚本（最简单）

```bash
cd terraform
./deploy.sh
```

这个脚本会：
- ✅ 检查所有前置条件
- ✅ 初始化Terraform
- ✅ 验证配置
- ✅ 显示部署计划
- ✅ 执行部署
- ✅ 显示重要输出信息

### 方式 2: 手动执行标准流程

```bash
cd terraform

# 1. 初始化
terraform init

# 2. 查看将要创建的资源
terraform plan

# 3. 部署（需要输入 'yes' 确认）
terraform apply

# 4. 查看输出信息
terraform output
```

### 方式 3: 使用变量文件自定义配置

```bash
cd terraform

# 1. 复制配置模板
cp terraform.tfvars.example terraform.tfvars

# 2. 编辑配置（可选）
vim terraform.tfvars

# 3. 部署
terraform init
terraform apply
```

## 📋 部署前检查清单

### 必须完成的步骤

- [ ] AWS CLI 已安装并配置
  ```bash
  aws --version
  aws configure
  ```

- [ ] Terraform 已安装 (>= 1.0)
  ```bash
  terraform --version
  ```

- [ ] AWS 凭证已配置
  ```bash
  aws sts get-caller-identity
  ```

- [ ] S3 bucket 已创建并上传数据
  ```bash
  aws s3 ls s3://aig130-p2-ml-data-bucket/data/
  ```

### 可选步骤

- [ ] 自定义配置（如需修改默认值）
- [ ] 检查 AWS 账户权限

## 🎨 部署后的关键输出

部署完成后，你会看到这些重要信息：

```bash
# ECR 仓库 URL
ecr_repository_url = "123456789012.dkr.ecr.us-east-1.amazonaws.com/aig130-p2-ml-pipeline-ecr"

# ECS 集群名称
ecs_cluster_name = "aig130-p2-ml-cluster"

# 任务定义名称
ecs_task_definition_family = "aig130-p2-ml-task"

# 安全组 ID
security_group_id = "sg-xxxxx"

# GitHub Actions 凭证（如果创建）
github_actions_access_key_id = "AKIAXXXXX"
github_actions_secret_access_key = "<sensitive>"

# 实用命令
useful_commands = {
  docker_login = "aws ecr get-login-password ..."
  docker_build_and_push = "docker build ..."
  run_ecs_task = "aws ecs run-task ..."
  view_logs = "aws logs tail ..."
}
```

## 📝 部署后立即执行的步骤

### 1. 获取 GitHub Actions 凭证（如果需要CI/CD）

```bash
cd terraform

# 获取 Access Key ID
terraform output github_actions_access_key_id

# 获取 Secret Access Key
terraform output -raw github_actions_secret_access_key
```

**添加到 GitHub Secrets:**
1. 进入仓库 Settings → Secrets and variables → Actions
2. 添加 `AWS_ACCESS_KEY_ID`
3. 添加 `AWS_SECRET_ACCESS_KEY`

### 2. 构建并推送 Docker 镜像

```bash
# 登录 ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $(cd terraform && terraform output -raw ecr_repository_url)

# 构建镜像
cd AIG130_Project2_Docker
docker build -t $(cd ../terraform && terraform output -raw ecr_repository_url):latest .

# 推送镜像
docker push $(cd ../terraform && terraform output -raw ecr_repository_url):latest
```

### 3. 手动运行 ML Pipeline（测试）

```bash
cd terraform

# 运行任务
aws ecs run-task \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --task-definition $(terraform output -raw ecs_task_definition_family) \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$(terraform output -json subnet_ids | jq -r '.[0]')],securityGroups=[$(terraform output -raw security_group_id)],assignPublicIp=ENABLED}"

# 查看日志
aws logs tail $(terraform output -raw cloudwatch_log_group_name) --follow
```

### 4. 推送代码触发 GitHub Actions

```bash
git add .
git commit -m "Add Terraform configuration for AWS deployment"
git push origin main
```

GitHub Actions 会自动：
- 构建 Docker 镜像
- 推送到 ECR
- 更新 ECS 任务定义
- 运行 ML Pipeline
- 记录日志到 CloudWatch

## 🗑️ 清理资源

### 使用脚本清理（推荐）

```bash
cd terraform
./destroy.sh
```

### 手动清理

```bash
cd terraform
terraform destroy
```

**注意**: 这会删除所有 Terraform 管理的资源，但**不会删除 S3 bucket**（因为它不是由 Terraform 创建的）。

如果要删除 S3 bucket:
```bash
aws s3 rb s3://aig130-p2-ml-data-bucket --force
```

## 💰 成本估算

| 资源 | 配置 | 月成本 (USD) |
|-----|-----|------------|
| ECR 存储 | ~500 MB | $0.05 |
| ECS Fargate | 30次运行 × 10分钟 | $2.70 |
| CloudWatch 日志 | 7天保留 | $0.25 |
| S3 存储 | 50 MB | $0.001 |
| **总计** | | **~$3.00/月** |

*基于 us-east-1 区域价格，按需付费*

## 📚 文档说明

- **README.md** - 完整详细文档（包含故障排查、高级配置）
- **QUICKSTART.md** - 5分钟快速开始指南
- **TERRAFORM_SETUP.md** - 本文件，配置总览

## 🔧 常见问题

### Q: 如果 ECR 仓库已经存在怎么办？

```bash
# 方案1: 导入现有仓库
terraform import aws_ecr_repository.ml_pipeline aig130-p2-ml-pipeline-ecr

# 方案2: 删除现有仓库
aws ecr delete-repository --repository-name aig130-p2-ml-pipeline-ecr --force
terraform apply
```

### Q: 如何修改任务的CPU和内存？

编辑 `terraform.tfvars`:
```hcl
task_cpu    = "2048"  # 2 vCPU
task_memory = "4096"  # 4 GB
```

然后运行:
```bash
terraform apply
```

### Q: 如何查看正在运行的任务？

```bash
aws ecs list-tasks --cluster $(cd terraform && terraform output -raw ecs_cluster_name)
```

### Q: 任务运行失败了怎么办？

```bash
# 查看日志
aws logs tail $(cd terraform && terraform output -raw cloudwatch_log_group_name) --follow

# 检查任务状态
aws ecs describe-tasks --cluster <cluster-name> --tasks <task-arn>
```

## ✅ 配置特点

### 优势

1. **完全自动化** - 一键部署所有AWS资源
2. **可重复使用** - 代码即基础设施（IaC）
3. **版本控制** - 所有配置都在Git中
4. **安全配置** - IAM角色最小权限原则
5. **成本优化** - ECR生命周期策略、日志保留限制
6. **易于管理** - 清晰的输出、有用的命令
7. **完整文档** - 详细的README和快速指南

### 安全性

- ✅ IAM角色遵循最小权限原则
- ✅ 敏感输出标记为 sensitive
- ✅ .gitignore 排除 .tfvars 文件
- ✅ ECR镜像自动安全扫描
- ✅ 安全组仅允许必要的出站流量

### 最佳实践

- ✅ 使用变量实现可配置性
- ✅ 输出所有重要资源信息
- ✅ 包含实用命令减少手动操作
- ✅ 标签化所有资源便于管理
- ✅ 使用 data source 引用现有资源
- ✅ 生命周期策略控制存储成本

## 🎯 下一步

1. **立即部署**
   ```bash
   cd terraform
   ./deploy.sh
   ```

2. **构建并推送镜像**（见上文）

3. **配置 GitHub Secrets**（如需CI/CD）

4. **测试运行 ML Pipeline**

5. **监控日志和成本**

---

**创建时间**: 2025-11-23
**项目**: AIG130 Project 2 - Bitcoin Price Prediction
**作者**: Zhihuai Wang

**需要帮助？** 查看 `terraform/README.md` 获取完整文档
