# RoboRetail Infrastructure - ISOLATED VPC

## CRITICAL: Isolated Deployment

**This infrastructure is ISOLATED from the internet:**
- ❌ NO public IP address
- ❌ NO internet gateway
- ❌ NO NAT gateway
- ❌ NO inbound internet access
- ❌ NO outbound internet access

**Access ONLY via:**
- ✅ AWS Session Manager (SSM)
- ✅ VPC-internal connections only

## Components

**Isolated VPC:**
- CIDR: 10.0.0.0/16
- Single private isolated subnet
- No internet connectivity

**EC2 Instance:**
- t3.micro (free tier eligible)
- Private IP only
- Isolated subnet
- Access via Session Manager

**Security Group:**
- Ports 80, 5000, 22 open ONLY from VPC CIDR
- No outbound internet allowed

## Cost

**$0-8/month:**
- t3.micro: $0 (free tier) or $8/month
- VPC: $0
- Everything else: $0

## Access

**Connect to instance:**
```bash
aws ssm start-session --target <instance-id>
```

**Access application (from within VPC):**
```
http://<private-ip>:5000
```

## Security

✅ Completely isolated from internet  
✅ No public IP  
✅ No internet gateway  
✅ VPC-internal access only  
✅ Perfect for security testing in isolation

