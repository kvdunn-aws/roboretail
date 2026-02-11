from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    CfnOutput,
    RemovalPolicy,
)
from constructs import Construct


class RoboRetailStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ========== VPC - ISOLATED (NOT INTERNET ACCESSIBLE) ==========
        
        # Create isolated VPC - NO internet access
        vpc = ec2.Vpc(
            self, "RoboRetailVPC",
            vpc_name="roboretail-isolated-vpc",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            max_azs=1,
            nat_gateways=0,  # NO NAT Gateway - no internet access
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Isolated",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ]
        )
        
        # ========== Security Group - INTERNAL ONLY ==========
        
        # Security group - NO internet access, VPC-internal only
        sg = ec2.SecurityGroup(
            self, "InstanceSG",
            vpc=vpc,
            security_group_name="roboretail-isolated-sg",
            description="Security group for isolated RoboRetail instance",
            allow_all_outbound=False  # NO outbound internet
        )
        
        # Allow HTTP only from within VPC
        sg.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block),
            ec2.Port.tcp(80),
            "Allow HTTP from VPC only"
        )
        
        # Allow Flask app port only from within VPC
        sg.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block),
            ec2.Port.tcp(5000),
            "Allow Flask from VPC only"
        )
        
        # Allow SSH only from within VPC (for Session Manager)
        sg.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block),
            ec2.Port.tcp(22),
            "Allow SSH from VPC only"
        )

        # ========== IAM Role ==========
        
        # Simple EC2 role
        role = iam.Role(
            self, "InstanceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
            ]
        )

        # ========== User Data Script ==========
        
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "#!/bin/bash",
            "yum update -y",
            "yum install -y python3.11 python3-pip git postgresql15",
            "",
            "# Clone application",
            "cd /home/ec2-user",
            "git clone https://github.com/kvdunn-aws/roboretail.git",
            "cd roboretail",
            "chown -R ec2-user:ec2-user /home/ec2-user/roboretail",
            "",
            "# Install dependencies (when available)",
            "pip3 install flask gunicorn psycopg2-binary boto3 || true",
            "",
            "# Create simple startup script",
            "cat > /home/ec2-user/start-app.sh << 'EOF'",
            "#!/bin/bash",
            "cd /home/ec2-user/roboretail",
            "export FLASK_APP=app.py",
            "export FLASK_ENV=development",
            "python3 -m flask run --host=0.0.0.0 --port=5000",
            "EOF",
            "chmod +x /home/ec2-user/start-app.sh",
            "",
            "echo 'Setup complete. Run /home/ec2-user/start-app.sh to start app'"
        )

        # ========== EC2 Instance - ISOLATED (NO PUBLIC IP) ==========
        
        # Single t3.micro instance in ISOLATED subnet (NO public IP)
        instance = ec2.Instance(
            self, "Instance",
            instance_name="roboretail-isolated-instance",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            security_group=sg,
            role=role,
            user_data=user_data,
            associate_public_ip_address=False,  # NO public IP - isolated
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/xvda",
                    volume=ec2.BlockDeviceVolume.ebs(
                        volume_size=8,
                        delete_on_termination=True
                    )
                )
            ]
        )

        # ========== Outputs ==========
        
        CfnOutput(
            self, "VPCId",
            value=vpc.vpc_id,
            description="Isolated VPC ID"
        )
        
        CfnOutput(
            self, "InstanceId",
            value=instance.instance_id,
            description="EC2 Instance ID (access via Session Manager only)"
        )
        
        CfnOutput(
            self, "PrivateIP",
            value=instance.instance_private_ip,
            description="Private IP address (VPC-internal only)"
        )
        
        CfnOutput(
            self, "AppURL",
            value=f"http://{instance.instance_private_ip}:5000",
            description="Application URL (accessible from within VPC only)"
        )
        
        CfnOutput(
            self, "SessionManagerCommand",
            value=f"aws ssm start-session --target {instance.instance_id}",
            description="Connect via AWS Session Manager (no SSH key needed)"
        )
