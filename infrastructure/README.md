# RoboRetail Infrastructure

AWS CDK infrastructure code for RoboRetail application.

## Prerequisites

- Python 3.7+
- AWS CLI configured with credentials
- AWS CDK CLI (optional, can use `cdk` via npx)

## Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Infrastructure Components

- **VPC**: 10.0.0.0/16 with public and private subnets across 2 AZs
- **ALB**: Application Load Balancer in public subnets
- **Auto Scaling Group**: 2-4 EC2 t3.medium instances in private subnets
- **RDS PostgreSQL**: Multi-AZ db.t3.medium in isolated subnets
- **S3 Bucket**: For user avatars and exports
- **Security Groups**: ALB, Application, and Database
- **IAM Roles**: EC2 instance role with S3 and Secrets Manager access
- **Secrets Manager**: Database credentials
- **CloudWatch**: Log groups for application and error logs

## Deployment

⚠️ **DO NOT DEPLOY WITHOUT REVIEW**

```bash
# Synthesize CloudFormation template (review only)
cdk synth

# View differences (if stack already exists)
cdk diff

# Deploy infrastructure (after review)
cdk deploy

# Destroy infrastructure (cleanup)
cdk destroy
```

## Outputs

After deployment, CDK will output:
- VPC ID
- ALB DNS name
- Application URL
- Database endpoint
- S3 bucket name
- Database secret ARN

## Cost Estimate

Approximately $257/month:
- EC2 (2x t3.medium): $60
- RDS (db.t3.medium Multi-AZ): $120
- ALB: $25
- NAT Gateway: $35
- S3 + Data Transfer: $12
- CloudWatch: $5

## Security Notes

- All resources deployed in private subnets except ALB
- Database credentials stored in Secrets Manager
- S3 bucket has public access blocked
- Security groups follow least privilege principle
- Encryption enabled for RDS and S3

## Next Steps

1. Review synthesized CloudFormation template
2. Deploy infrastructure
3. Deploy application code to EC2 instances
4. Run database migrations
5. Configure DNS (Route 53)
6. Add SSL certificate (ACM)
