# RoboRetail Infrastructure - MINIMAL VERSION

## Philosophy
**Minimal, cheap infrastructure for security testing - not production.**

## What We Have

**Single EC2 Instance:**
- t3.micro (free tier eligible!)
- Public IP
- SQLite database (on instance)
- Local file storage
- No load balancer, no RDS, no S3

## Cost

**Original:** $257/month  
**New:** $0-8/month (97% savings!)

- t3.micro: $0 (free tier) or $8/month
- Everything else: $0

## Components

- ✅ 1x EC2 t3.micro instance
- ✅ Default VPC (no cost)
- ✅ Security group (ports 80, 5000, 22 open)
- ✅ IAM role (SSM access)
- ✅ User data script

## Removed

- ❌ Custom VPC
- ❌ ALB ($25/month saved)
- ❌ NAT Gateway ($35/month saved)
- ❌ RDS ($120/month saved)
- ❌ S3 bucket
- ❌ Auto Scaling
- ❌ CloudWatch Logs
- ❌ Secrets Manager

## Application Changes

1. **Database:** SQLite instead of PostgreSQL
2. **Storage:** Local filesystem instead of S3
3. **Secrets:** Hardcoded (intentionally insecure!)

## Deployment

```bash
cd infrastructure
cdk deploy
```

Outputs:
- Instance ID
- Public IP
- App URL: http://<ip>:5000

## Perfect For

✅ Security testing  
✅ Vulnerability scanning  
✅ Cost-effective  
✅ Simple to deploy  
✅ Easy to destroy
