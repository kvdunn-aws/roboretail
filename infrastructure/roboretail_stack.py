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

        # ========== VPC - Use Default or Create Simple One ==========
        
        # Option 1: Use existing default VPC (cheapest)
        vpc = ec2.Vpc.from_lookup(self, "VPC", is_default=True)
        
        # ========== Security Group ==========
        
        # Single security group for the instance
        sg = ec2.SecurityGroup(
            self, "InstanceSG",
            vpc=vpc,
            security_group_name="roboretail-sg",
            description="Security group for RoboRetail instance",
            allow_all_outbound=True
        )
        
        # Allow HTTP from anywhere
        sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow HTTP from internet"
        )
        
        # Allow Flask app port
        sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(5000),
            "Allow Flask app from internet"
        )
        
        # Allow SSH (for debugging)
        sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(22),
            "Allow SSH from internet"
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

        # ========== EC2 Instance ==========
        
        # Single t3.micro instance (free tier eligible)
        instance = ec2.Instance(
            self, "Instance",
            instance_name="roboretail-instance",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=sg,
            role=role,
            user_data=user_data,
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
            self, "InstanceId",
            value=instance.instance_id,
            description="EC2 Instance ID"
        )
        
        CfnOutput(
            self, "PublicIP",
            value=instance.instance_public_ip,
            description="Public IP address"
        )
        
        CfnOutput(
            self, "AppURL",
            value=f"http://{instance.instance_public_ip}:5000",
            description="Application URL"
        )
        
        CfnOutput(
            self, "SSHCommand",
            value=f"ssh -i <key.pem> ec2-user@{instance.instance_public_ip}",
            description="SSH command (requires key pair)"
        )
