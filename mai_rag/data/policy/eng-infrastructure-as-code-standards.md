---
title: Infrastructure as Code Standards (Terraform)
doc_id: eng-infrastructure-as-code-standards
owner: DevOps Leadership
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Infrastructure as Code Standards (Terraform)

## 1. Purpose

All infrastructure—compute, networking, storage, databases—is defined as code via Terraform and version-controlled in GitHub. This ensures repeatable, auditable, and reversible infrastructure changes.

## 2. Repository Structure

All Terraform code lives in `github.com/northwind/infrastructure` with the following layout:

```
infrastructure/
├── README.md
├── terraform.tfvars (git-ignored; per-environment secrets)
├── terraform.tfvars.example (template; committed)
├── backend.tf (remote state config)
├── aws/
│   ├── main.tf (AWS provider configuration)
│   ├── eks.tf (EKS cluster for microservices)
│   ├── rds.tf (PostgreSQL managed database)
│   ├── networking.tf (VPC, subnets, security groups)
│   ├── iam.tf (IAM roles and policies)
│   ├── monitoring.tf (Datadog agent, CloudWatch alarms)
│   ├── variables.tf (input variables)
│   └── outputs.tf (exported values)
├── azure/
│   ├── main.tf (Azure provider)
│   ├── container-apps.tf (AKS cluster for audit service)
│   ├── databases.tf (PostgreSQL Flexible Server)
│   ├── networking.tf (VNets, NSGs)
│   ├── variables.tf
│   └── outputs.tf
├── shared/ (multi-cloud resources)
│   ├── variables.tf
│   └── outputs.tf
├── modules/ (reusable configurations)
│   ├── eks-cluster/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── rds-postgres/
│   ├── security-group/
│   └── iam-role/
└── environments/
    ├── prod.tfvars
    ├── staging.tfvars
    └── dev.tfvars
```

## 3. Terraform Best Practices

### 3.1 State Management

Terraform state is stored remotely in AWS S3 with DynamoDB locking:

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "northwind-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

**Access control**: Only DevOps team has IAM access to state bucket (see **Secrets Management Standard** for credential rotation).

### 3.2 Variable Definition and Secrets

Never hardcode secrets in Terraform files:

```hcl
# ✓ GOOD: Use variables
variable "db_password" {
  type      = string
  sensitive = true  # Don't log this value
}

resource "aws_db_instance" "main" {
  allocated_storage    = 20
  engine              = "postgres"
  instance_class      = "db.t4g.micro"
  db_name             = "northwind"
  username            = "postgres"
  password            = var.db_password  # Passed via terraform.tfvars
}

# ✗ BAD: Never do this
password = "hardcoded_password_12345"
```

Secrets are provided via `terraform.tfvars` (git-ignored):
```hcl
# terraform.tfvars (git-ignored)
db_password = "CorrectHorseBatteryStaple123!"
environment = "prod"
```

Template file for developers:
```hcl
# terraform.tfvars.example (committed)
db_password = "REPLACE_WITH_SECRET"
environment = "prod"
```

## 4. Module Usage

Reusable infrastructure patterns are defined as Terraform modules:

### 4.1 EKS Cluster Module

```hcl
# aws/eks.tf
module "eks_cluster" {
  source = "./modules/eks-cluster"
  
  cluster_name    = "northwind-prod-east"
  cluster_version = "1.28"
  region          = "us-east-1"
  
  node_group_config = {
    desired_size       = 5
    min_size          = 3
    max_size          = 10
    instance_types    = ["t4g.medium"]
  }
  
  tags = {
    Environment = "prod"
    ManagedBy   = "terraform"
  }
}
```

Module output:
```hcl
output "eks_cluster_endpoint" {
  value = module.eks_cluster.cluster_endpoint
}
```

### 4.2 Database Module

```hcl
# aws/rds.tf
module "postgres_db" {
  source = "./modules/rds-postgres"
  
  instance_identifier = "northwind-db-prod"
  allocated_storage   = 100
  instance_class      = "db.t4g.large"
  engine_version      = "15.3"
  
  db_name  = "northwind"
  username = "postgres"
  password = var.db_password  # From tfvars
  
  # High availability
  multi_az            = true
  backup_retention_days = 30
  
  tags = {
    Environment = "prod"
    CriticalityTier = "tier-1"
  }
}
```

## 5. Change Management and Code Review

All Terraform changes follow **Code Review Standards** and **Git Branching & Release Strategy**:

### 5.1 PR Workflow

1. **Feature branch**: `feature/add-new-database-backup` or `infra/update-eks-version`
2. **terraform plan**: Automatic in GitHub Actions
   ```yaml
   - run: terraform plan -out=tfplan
   - run: terraform show tfplan > plan-output.txt
   - # Post plan-output as PR comment
   ```
3. **Code review**: DevOps lead + 1 other engineer approves (see **Code Review Standards**)
4. **Merge to main**: Changes staged for next deployment window
5. **Staged deployment**: Run `terraform apply` in staging first (see **Production Deployment Runbook**)
6. **Production apply**: Manual execution by DevOps lead

### 5.2 Terraform Plan Review Checklist

Reviewers must verify:

- [ ] **Plan output** matches PR description (e.g., "scaling EKS to 10 nodes")
- [ ] **Destructive changes** are intentional (e.g., database deletion requires approval from DBA)
- [ ] **No secrets** in plan output (check for passwords, API keys)
- [ ] **Backward compatibility**: Existing resources not deleted without migration
- [ ] **Monitoring/alarms**: New resources include appropriate observability (see **Observability & Monitoring Standards**)
- [ ] **Tags present**: All resources tagged with Environment, Owner, CostCenter (for billing)

## 6. Modules: Building and Testing

### 6.1 Module Structure

Each module in `modules/` has:
- `main.tf`: Resource definitions
- `variables.tf`: Input variables with validation
- `outputs.tf`: Exported values
- `README.md`: Module documentation
- (Optional) `examples/` directory with usage examples

### 6.2 Input Validation

Always validate inputs:

```hcl
variable "instance_class" {
  type    = string
  default = "db.t4g.micro"
  
  validation {
    condition     = contains(["db.t4g.micro", "db.t4g.small", "db.t4g.large"], var.instance_class)
    error_message = "Instance class must be one of: db.t4g.micro, db.t4g.small, db.t4g.large."
  }
}
```

## 7. Deployment Procedure (Terraform Apply)

Production Terraform changes are applied via a change window:

1. **Approval window**: PR merged to main; DevOps lead schedules apply time
2. **Staging validation**: Run `terraform apply` in staging environment first
3. **Change ticket**: Create ticket in Jira with:
   - What's changing (resource name, parameter)
   - Why (business justification, ticket reference)
   - Rollback plan (e.g., "scale back down to 5 nodes if memory utilization spikes")
4. **Deployment window**: Execute during business hours (see **Production Deployment Runbook**)
   ```bash
   cd infrastructure && terraform apply prod.tfvars
   ```
5. **Monitoring**: DevOps lead monitors for 30 minutes post-apply
6. **Documented**: Change logged in Jira with timestamp and approval chain

## 8. Multi-Environment Configuration

### 8.1 Environment Separation

Each environment (dev, staging, prod) has its own:
- `tfvars` file (dev.tfvars, staging.tfvars, prod.tfvars)
- Isolated AWS/Azure accounts
- Separate Kubernetes clusters
- Distinct database instances

Example environment config:
```hcl
# environments/prod.tfvars
environment      = "prod"
eks_node_count   = 5
db_instance_type = "db.t4g.large"
backup_retention = 30
enable_monitoring = true

# environments/staging.tfvars
environment      = "staging"
eks_node_count   = 2
db_instance_type = "db.t4g.micro"
backup_retention = 7
enable_monitoring = true

# environments/dev.tfvars
environment      = "dev"
eks_node_count   = 1
db_instance_type = "db.t4g.micro"
backup_retention = 1
enable_monitoring = false
```

### 8.2 Terraform Workspace Usage

Workspaces manage state isolation:

```bash
terraform workspace new staging
terraform workspace select staging
terraform apply -var-file=environments/staging.tfvars
```

## 9. Disaster Recovery and Backup

Terraform enables rapid infrastructure recovery:

### 9.1 Disaster Recovery Drill (Quarterly)

1. **Snapshot**: Export current Terraform state as backup
2. **Destroy**: `terraform destroy -var-file=prod.tfvars` on staging clone
3. **Re-create**: Run `terraform apply` to rebuild infrastructure
4. **Validate**: Verify all services online and operational
5. **Document**: Time to recovery (RTO), any issues encountered

### 9.2 State Backup

Terraform state is automatically backed up to S3 (versioning enabled):

```bash
# Manual state backup
terraform state pull > terraform.state.backup
git add terraform.state.backup  # Committed to secure branch
```

## 10. Drift Detection

Periodic drift detection ensures infrastructure matches code:

```bash
# Detect unmanaged changes
terraform plan -refresh-only
# If diff shows changes not in Terraform, investigate (manual change, console modification, etc.)
```

Run drift detection weekly via scheduled GitHub Actions job.

---

**Related policies:**
- See **Container & Kubernetes Standards** for Kubernetes manifests and cluster configuration
- See **Code Review Standards** for Terraform PR review checklist
- See **Secrets Management Standard** for managing sensitive variables
- See **Production Deployment Runbook** for deployment scheduling and runbook
