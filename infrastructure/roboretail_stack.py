from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_s3 as s3,
    aws_iam as iam,
    aws_elasticloadbalancingv2 as elbv2,
    aws_autoscaling as autoscaling,
    aws_secretsmanager as secretsmanager,
    aws_logs as logs,
    CfnOutput,
    RemovalPolicy,
    Duration,
)
from constructs import Construct


class RoboRetailStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ========== VPC and Networking ==========
        
        # Create VPC with public and private subnets across 2 AZs
        vpc = ec2.Vpc(
            self, "RoboRetailVPC",
            vpc_name="roboretail-vpc",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="PrivateApp",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="PrivateDB",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ]
        )

        # ========== Security Groups ==========
        
        # ALB Security Group
        alb_sg = ec2.SecurityGroup(
            self, "ALBSecurityGroup",
            vpc=vpc,
            security_group_name="roboretail-alb-sg",
            description="Security group for Application Load Balancer",
            allow_all_outbound=True
        )
        alb_sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(443),
            "Allow HTTPS from internet"
        )
        alb_sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow HTTP from internet (redirect to HTTPS)"
        )

        # Application Security Group
        app_sg = ec2.SecurityGroup(
            self, "AppSecurityGroup",
            vpc=vpc,
            security_group_name="roboretail-app-sg",
            description="Security group for application servers",
            allow_all_outbound=True
        )
        app_sg.add_ingress_rule(
            alb_sg,
            ec2.Port.tcp(5000),
            "Allow traffic from ALB"
        )

        # Database Security Group
        db_sg = ec2.SecurityGroup(
            self, "DBSecurityGroup",
            vpc=vpc,
            security_group_name="roboretail-db-sg",
            description="Security group for RDS database",
            allow_all_outbound=False
        )
        db_sg.add_ingress_rule(
            app_sg,
            ec2.Port.tcp(5432),
            "Allow PostgreSQL from application"
        )

        # ========== S3 Bucket ==========
        
        # S3 bucket for user avatars and exports
        avatars_bucket = s3.Bucket(
            self, "AvatarsBucket",
            bucket_name=f"roboretail-avatars-{self.account}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
            lifecycle_rules=[
                s3.LifecycleRule(
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(90)
                        )
                    ],
                    expiration=Duration.days(365)
                )
            ]
        )

        # ========== IAM Roles ==========
        
        # EC2 Instance Role
        ec2_role = iam.Role(
            self, "EC2InstanceRole",
            role_name="RoboRetail-EC2-Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            description="IAM role for RoboRetail EC2 instances"
        )

        # Grant S3 access
        avatars_bucket.grant_read_write(ec2_role)

        # Grant CloudWatch Logs access
        ec2_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=[f"arn:aws:logs:{self.region}:{self.account}:log-group:/aws/roboretail/*"]
            )
        )

        # ========== Database Credentials ==========
        
        # Create database credentials in Secrets Manager
        db_credentials = secretsmanager.Secret(
            self, "DBCredentials",
            secret_name="roboretail/db-credentials",
            description="RoboRetail database credentials",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"username":"app_user"}',
                generate_string_key="password",
                exclude_punctuation=True,
                password_length=32
            )
        )

        # Grant EC2 role access to secrets
        db_credentials.grant_read(ec2_role)

        # ========== RDS Database ==========
        
        # RDS PostgreSQL instance
        database = rds.DatabaseInstance(
            self, "Database",
            instance_identifier="roboretail-db",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15_4
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MEDIUM
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            security_groups=[db_sg],
            multi_az=True,
            allocated_storage=100,
            storage_type=rds.StorageType.GP3,
            database_name="roboretail",
            credentials=rds.Credentials.from_secret(db_credentials),
            backup_retention=Duration.days(7),
            deletion_protection=False,
            removal_policy=RemovalPolicy.SNAPSHOT,
            storage_encrypted=True,
            enable_performance_insights=True,
            cloudwatch_logs_exports=["postgresql"],
            parameter_group=rds.ParameterGroup.from_parameter_group_name(
                self, "ParameterGroup",
                "default.postgres15"
            )
        )

        # ========== CloudWatch Log Groups ==========
        
        app_log_group = logs.LogGroup(
            self, "AppLogGroup",
            log_group_name="/aws/roboretail/application",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY
        )

        error_log_group = logs.LogGroup(
            self, "ErrorLogGroup",
            log_group_name="/aws/roboretail/error",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY
        )

        # ========== User Data Script ==========
        
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "#!/bin/bash",
            "set -e",
            "",
            "# Update system",
            "yum update -y",
            "yum install -y python3.11 python3-pip git postgresql15",
            "",
            "# Clone application",
            "cd /opt",
            "git clone https://github.com/kvdunn-aws/roboretail.git",
            "cd roboretail",
            "",
            "# Install dependencies",
            "pip3 install -r requirements.txt || echo 'requirements.txt not yet created'",
            "",
            "# Configure environment variables",
            f"export DB_HOST={database.db_instance_endpoint_address}",
            "export DB_NAME=roboretail",
            "export DB_PORT=5432",
            f"export DB_SECRET_ARN={db_credentials.secret_arn}",
            f"export S3_BUCKET={avatars_bucket.bucket_name}",
            f"export AWS_REGION={self.region}",
            "",
            "# Create systemd service",
            "cat > /etc/systemd/system/roboretail.service << 'EOF'",
            "[Unit]",
            "Description=RoboRetail Flask Application",
            "After=network.target",
            "",
            "[Service]",
            "Type=simple",
            "User=ec2-user",
            "WorkingDirectory=/opt/roboretail",
            f"Environment=DB_HOST={database.db_instance_endpoint_address}",
            "Environment=DB_NAME=roboretail",
            "Environment=DB_PORT=5432",
            f"Environment=DB_SECRET_ARN={db_credentials.secret_arn}",
            f"Environment=S3_BUCKET={avatars_bucket.bucket_name}",
            f"Environment=AWS_REGION={self.region}",
            "ExecStart=/usr/local/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app",
            "Restart=always",
            "",
            "[Install]",
            "WantedBy=multi-user.target",
            "EOF",
            "",
            "# Enable and start service (will fail until app is built)",
            "systemctl daemon-reload",
            "# systemctl enable roboretail",
            "# systemctl start roboretail",
            "",
            "echo 'User data script completed'"
        )

        # ========== Launch Template ==========
        
        launch_template = ec2.LaunchTemplate(
            self, "LaunchTemplate",
            launch_template_name="roboretail-launch-template",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MEDIUM
            ),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            security_group=app_sg,
            role=ec2_role,
            user_data=user_data,
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/xvda",
                    volume=ec2.BlockDeviceVolume.ebs(
                        volume_size=20,
                        volume_type=ec2.EbsDeviceVolumeType.GP3,
                        encrypted=True,
                        delete_on_termination=True
                    )
                )
            ]
        )

        # ========== Application Load Balancer ==========
        
        alb = elbv2.ApplicationLoadBalancer(
            self, "ALB",
            load_balancer_name="roboretail-alb",
            vpc=vpc,
            internet_facing=True,
            security_group=alb_sg,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            )
        )

        # Target Group
        target_group = elbv2.ApplicationTargetGroup(
            self, "TargetGroup",
            target_group_name="roboretail-tg",
            vpc=vpc,
            port=5000,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.INSTANCE,
            health_check=elbv2.HealthCheck(
                path="/health",
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                healthy_threshold_count=2,
                unhealthy_threshold_count=3
            ),
            deregistration_delay=Duration.seconds(30)
        )

        # HTTP Listener (redirect to HTTPS in production)
        alb.add_listener(
            "HTTPListener",
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            default_action=elbv2.ListenerAction.forward([target_group])
        )

        # ========== Auto Scaling Group ==========
        
        asg = autoscaling.AutoScalingGroup(
            self, "ASG",
            auto_scaling_group_name="roboretail-asg",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            launch_template=launch_template,
            min_capacity=2,
            max_capacity=4,
            desired_capacity=2,
            health_check=autoscaling.HealthCheck.elb(
                grace=Duration.seconds(300)
            ),
            update_policy=autoscaling.UpdatePolicy.rolling_update(
                max_batch_size=1,
                min_instances_in_service=1,
                pause_time=Duration.minutes(5)
            )
        )

        # Attach ASG to target group
        asg.attach_to_application_target_group(target_group)

        # Scaling policies
        asg.scale_on_cpu_utilization(
            "CPUScaling",
            target_utilization_percent=70,
            cooldown=Duration.minutes(5)
        )

        # ========== Outputs ==========
        
        CfnOutput(
            self, "VPCId",
            value=vpc.vpc_id,
            description="VPC ID"
        )

        CfnOutput(
            self, "ALBDNSName",
            value=alb.load_balancer_dns_name,
            description="Application Load Balancer DNS name"
        )

        CfnOutput(
            self, "ALBURL",
            value=f"http://{alb.load_balancer_dns_name}",
            description="Application URL"
        )

        CfnOutput(
            self, "DatabaseEndpoint",
            value=database.db_instance_endpoint_address,
            description="RDS database endpoint"
        )

        CfnOutput(
            self, "S3BucketName",
            value=avatars_bucket.bucket_name,
            description="S3 bucket for avatars"
        )

        CfnOutput(
            self, "DBSecretArn",
            value=db_credentials.secret_arn,
            description="Database credentials secret ARN"
        )
