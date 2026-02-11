# RoboRetail Deployment Architecture

**Version:** 1.0  
**Date:** February 11, 2026  
**Cloud Provider:** Amazon Web Services (AWS)

## Overview

This document describes the deployment architecture for RoboRetail on AWS infrastructure. The architecture prioritizes availability, scalability, and security while maintaining cost-effectiveness.

## Architecture Diagram

```
                                    Internet
                                       │
                                       │
                                       ▼
                            ┌──────────────────┐
                            │  Route 53 (DNS)  │
                            └──────────────────┘
                                       │
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                          VPC (10.0.0.0/16)                      │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              Internet Gateway                           │   │
│  └────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              │                                  │
│  ┌───────────────────────────────────────────────────────┐    │
│  │         Application Load Balancer (Public)            │    │
│  │              Availability Zone 1 & 2                  │    │
│  │         Public Subnet A       Public Subnet B         │    │
│  │         (10.0.1.0/24)        (10.0.2.0/24)           │    │
│  └───────────────────────────────────────────────────────┘    │
│                              │                                  │
│                              │                                  │
│  ┌───────────────────────────────────────────────────────┐    │
│  │          Auto Scaling Group (Private)                 │    │
│  │                                                        │    │
│  │  ┌──────────────────┐      ┌──────────────────┐     │    │
│  │  │   EC2 Instance   │      │   EC2 Instance   │     │    │
│  │  │   Flask App      │      │   Flask App      │     │    │
│  │  │   Private Sub A  │      │   Private Sub B  │     │    │
│  │  │  (10.0.10.0/24)  │      │  (10.0.11.0/24)  │     │    │
│  │  └──────────────────┘      └──────────────────┘     │    │
│  │                                                        │    │
│  └───────────────────────────────────────────────────────┘    │
│                              │                                  │
│                              │                                  │
│  ┌───────────────────────────────────────────────────────┐    │
│  │         RDS PostgreSQL (Multi-AZ)                     │    │
│  │                                                        │    │
│  │  ┌──────────────────┐      ┌──────────────────┐     │    │
│  │  │   Primary DB     │      │   Standby DB     │     │    │
│  │  │   Private Sub A  │      │   Private Sub B  │     │    │
│  │  │  (10.0.20.0/24)  │      │  (10.0.21.0/24)  │     │    │
│  │  └──────────────────┘      └──────────────────┘     │    │
│  │                                                        │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐    │
│  │              NAT Gateway (Public Subnet)              │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                                       │
                                       │
                                       ▼
                            ┌──────────────────┐
                            │   S3 Bucket      │
                            │  (User Avatars)  │
                            └──────────────────┘
                                       │
                                       │
                                       ▼
                            ┌──────────────────┐
                            │   CloudWatch     │
                            │  (Logs/Metrics)  │
                            └──────────────────┘
```

## Infrastructure Components

### 1. Network Layer

#### 1.1 VPC (Virtual Private Cloud)
- **CIDR Block:** 10.0.0.0/16
- **Region:** us-west-2 (Oregon)
- **Availability Zones:** 2 (us-west-2a, us-west-2b)

**Purpose:** Isolated network environment for RoboRetail infrastructure.

#### 1.2 Subnets

**Public Subnets (Internet-facing):**
- Public Subnet A: 10.0.1.0/24 (AZ: us-west-2a)
- Public Subnet B: 10.0.2.0/24 (AZ: us-west-2b)
- **Purpose:** Host Application Load Balancer and NAT Gateway

**Private Subnets (Application Tier):**
- Private Subnet A: 10.0.10.0/24 (AZ: us-west-2a)
- Private Subnet B: 10.0.11.0/24 (AZ: us-west-2b)
- **Purpose:** Host EC2 application servers

**Private Subnets (Database Tier):**
- Private Subnet A: 10.0.20.0/24 (AZ: us-west-2a)
- Private Subnet B: 10.0.21.0/24 (AZ: us-west-2b)
- **Purpose:** Host RDS database instances

#### 1.3 Internet Gateway
- **Purpose:** Enable internet access for public subnets
- **Attached to:** VPC

#### 1.4 NAT Gateway
- **Location:** Public Subnet A
- **Purpose:** Enable outbound internet access for private subnets
- **Use Cases:** Package updates, external API calls

#### 1.5 Route Tables

**Public Route Table:**
```
Destination       Target
10.0.0.0/16      local
0.0.0.0/0        igw-xxxxx (Internet Gateway)
```

**Private Route Table:**
```
Destination       Target
10.0.0.0/16      local
0.0.0.0/0        nat-xxxxx (NAT Gateway)
```

### 2. Compute Layer

#### 2.1 Application Load Balancer (ALB)
- **Type:** Application Load Balancer
- **Scheme:** Internet-facing
- **Subnets:** Public Subnet A & B
- **Listeners:**
  - HTTPS (443) → Target Group (Port 5000)
- **SSL Certificate:** AWS Certificate Manager
- **Health Check:**
  - Path: /health
  - Interval: 30 seconds
  - Timeout: 5 seconds
  - Healthy threshold: 2
  - Unhealthy threshold: 3

#### 2.2 EC2 Auto Scaling Group
- **Instance Type:** t3.medium (2 vCPU, 4 GB RAM)
- **AMI:** Amazon Linux 2023
- **Min Instances:** 2
- **Max Instances:** 4
- **Desired Capacity:** 2
- **Subnets:** Private Subnet A & B
- **Health Check Type:** ELB
- **Health Check Grace Period:** 300 seconds

**Scaling Policies:**
- **Scale Up:** CPU > 70% for 5 minutes → Add 1 instance
- **Scale Down:** CPU < 30% for 15 minutes → Remove 1 instance

#### 2.3 EC2 Instance Configuration
- **Operating System:** Amazon Linux 2023
- **Python Version:** 3.11
- **Web Server:** Gunicorn (4 workers)
- **Application:** Flask 3.0
- **Startup Script:** systemd service

**User Data Script:**
```bash
#!/bin/bash
yum update -y
yum install -y python3.11 python3-pip git

# Clone application
cd /opt
git clone https://github.com/kvdunn-aws/roboretail.git
cd roboretail

# Install dependencies
pip3 install -r requirements.txt

# Configure environment
export DB_HOST=<rds-endpoint>
export DB_NAME=roboretail
export DB_USER=app_user
export DB_PASSWORD=<from-secrets-manager>
export S3_BUCKET=roboretail-avatars

# Start application
systemctl enable roboretail
systemctl start roboretail
```

### 3. Database Layer

#### 3.1 RDS PostgreSQL
- **Engine:** PostgreSQL 15.4
- **Instance Class:** db.t3.medium (2 vCPU, 4 GB RAM)
- **Storage:** 100 GB General Purpose SSD (gp3)
- **Multi-AZ:** Enabled (automatic failover)
- **Subnets:** Private Subnet A & B (DB Subnet Group)
- **Backup:**
  - Automated backups: Enabled
  - Retention period: 7 days
  - Backup window: 03:00-04:00 UTC
  - Maintenance window: Sun 04:00-05:00 UTC
- **Encryption:** Enabled (AWS KMS)
- **Performance Insights:** Enabled

**Database Configuration:**
- **Database Name:** roboretail
- **Master Username:** postgres
- **Master Password:** Stored in AWS Secrets Manager
- **Port:** 5432

**Parameter Group Settings:**
- max_connections: 100
- shared_buffers: 1GB
- effective_cache_size: 3GB
- maintenance_work_mem: 256MB

### 4. Storage Layer

#### 4.1 S3 Bucket
- **Bucket Name:** roboretail-avatars-<account-id>
- **Region:** us-west-2
- **Purpose:** Store user profile pictures and exported reports
- **Versioning:** Enabled
- **Encryption:** Server-side encryption (SSE-S3)
- **Lifecycle Policy:**
  - Transition to Glacier after 90 days
  - Delete after 365 days
- **Public Access:** Blocked (access via signed URLs)

**Bucket Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<account-id>:role/RoboRetail-EC2-Role"
      },
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::roboretail-avatars-<account-id>/*"
    }
  ]
}
```

### 5. Security Layer

#### 5.1 Security Groups

**ALB Security Group:**
```
Inbound Rules:
- Type: HTTPS, Port: 443, Source: 0.0.0.0/0
- Type: HTTP, Port: 80, Source: 0.0.0.0/0 (redirect to HTTPS)

Outbound Rules:
- Type: All Traffic, Destination: 0.0.0.0/0
```

**Application Security Group:**
```
Inbound Rules:
- Type: Custom TCP, Port: 5000, Source: ALB Security Group

Outbound Rules:
- Type: PostgreSQL, Port: 5432, Destination: Database Security Group
- Type: HTTPS, Port: 443, Destination: 0.0.0.0/0 (for S3, package updates)
```

**Database Security Group:**
```
Inbound Rules:
- Type: PostgreSQL, Port: 5432, Source: Application Security Group

Outbound Rules:
- None (database doesn't initiate outbound connections)
```

#### 5.2 IAM Roles

**EC2 Instance Role (RoboRetail-EC2-Role):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::roboretail-avatars-*/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:us-west-2:<account-id>:secret:roboretail/db-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:us-west-2:<account-id>:log-group:/aws/roboretail/*"
    }
  ]
}
```

#### 5.3 Secrets Manager
- **Secret Name:** roboretail/db-credentials
- **Secret Value:**
  ```json
  {
    "username": "app_user",
    "password": "<generated-password>",
    "host": "<rds-endpoint>",
    "port": 5432,
    "database": "roboretail"
  }
  ```
- **Rotation:** Enabled (30 days)

### 6. Monitoring & Logging

#### 6.1 CloudWatch Logs
**Log Groups:**
- `/aws/roboretail/application` - Application logs
- `/aws/roboretail/access` - Access logs
- `/aws/roboretail/error` - Error logs

**Retention:** 30 days

#### 6.2 CloudWatch Metrics
**Custom Metrics:**
- API response time
- Database query time
- Failed login attempts
- Order placement rate

**Alarms:**
- High CPU utilization (> 80%)
- High memory utilization (> 85%)
- Database connection errors
- ALB 5xx errors (> 10 in 5 minutes)
- Disk space low (< 20%)

#### 6.3 CloudWatch Dashboards
- **Application Dashboard:** Request rate, latency, errors
- **Infrastructure Dashboard:** CPU, memory, network, disk
- **Database Dashboard:** Connections, queries, replication lag

### 7. DNS & SSL

#### 7.1 Route 53
- **Hosted Zone:** roboretail.com
- **Records:**
  - A record: roboretail.com → ALB
  - CNAME: www.roboretail.com → roboretail.com
  - CNAME: api.roboretail.com → ALB

#### 7.2 AWS Certificate Manager
- **Domain:** *.roboretail.com
- **Validation:** DNS validation
- **Renewal:** Automatic

### 8. Deployment Process

#### 8.1 Infrastructure Deployment (AWS CDK)
```bash
# Install CDK
npm install -g aws-cdk

# Navigate to infrastructure directory
cd infrastructure

# Install dependencies
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap aws://<account-id>/us-west-2

# Deploy infrastructure
cdk deploy RoboRetailStack
```

#### 8.2 Application Deployment
```bash
# SSH to EC2 instance (via Session Manager)
aws ssm start-session --target <instance-id>

# Pull latest code
cd /opt/roboretail
git pull origin main

# Install dependencies
pip3 install -r requirements.txt

# Restart application
sudo systemctl restart roboretail
```

#### 8.3 Database Migration
```bash
# Connect to database
psql -h <rds-endpoint> -U postgres -d roboretail

# Run migration scripts
\i migrations/001_initial_schema.sql
\i migrations/002_sample_data.sql
```

### 9. Disaster Recovery

#### 9.1 Backup Strategy
- **Database:** Automated daily backups (7-day retention)
- **Application:** Infrastructure as Code (CDK) for rapid rebuild
- **User Data:** S3 versioning enabled

#### 9.2 Recovery Procedures
**Database Failure:**
1. RDS automatically fails over to standby (Multi-AZ)
2. Application reconnects automatically
3. Downtime: < 2 minutes

**Application Server Failure:**
1. ALB health check detects failure
2. Traffic routed to healthy instances
3. Auto Scaling launches replacement
4. Downtime: None (multiple instances)

**Region Failure:**
1. Manual failover to backup region (not implemented in v1.0)
2. Restore database from snapshot
3. Deploy infrastructure via CDK
4. Update DNS to point to new region
5. RTO: 4 hours, RPO: 24 hours

### 10. Cost Estimation

**Monthly Costs (Estimated):**
- EC2 (2x t3.medium): $60
- RDS (db.t3.medium Multi-AZ): $120
- ALB: $25
- NAT Gateway: $35
- S3 Storage (100 GB): $2
- Data Transfer: $10
- CloudWatch: $5
- **Total:** ~$257/month

**Cost Optimization:**
- Use Reserved Instances for predictable workloads (30-40% savings)
- Enable S3 Intelligent-Tiering
- Review CloudWatch log retention
- Right-size instances based on metrics

### 11. Performance Targets

**Response Times:**
- Page load: < 2 seconds
- API response: < 500ms
- Database queries: < 100ms

**Throughput:**
- Concurrent users: 100
- Requests per second: 50
- Database connections: 20

**Availability:**
- Target: 99.9% uptime
- Downtime allowance: 43 minutes/month

### 12. Scaling Strategy

**Vertical Scaling (Instance Size):**
- Current: t3.medium
- Next tier: t3.large (4 vCPU, 8 GB RAM)
- Trigger: Sustained CPU > 80%

**Horizontal Scaling (Instance Count):**
- Current: 2-4 instances
- Next tier: 4-8 instances
- Trigger: Request rate > 100 RPS

**Database Scaling:**
- Read replicas for read-heavy workloads
- Upgrade instance class for write-heavy workloads
- Consider Aurora PostgreSQL for > 1000 connections

---

## Appendix

### A. Resource Naming Convention
- VPC: roboretail-vpc
- Subnets: roboretail-public-a, roboretail-private-app-a
- Security Groups: roboretail-alb-sg, roboretail-app-sg
- EC2 Instances: roboretail-app-01, roboretail-app-02
- RDS: roboretail-db
- S3 Bucket: roboretail-avatars-<account-id>

### B. Tags
All resources tagged with:
- Project: RoboRetail
- Environment: Production
- ManagedBy: CDK
- CostCenter: Engineering

### C. Maintenance Windows
- Database: Sunday 04:00-05:00 UTC
- Application: Rolling updates (no downtime)
- Infrastructure: Planned maintenance announced 7 days in advance

---

**Document Version:** 1.0  
**Last Updated:** February 11, 2026  
**Next Review:** May 11, 2026
