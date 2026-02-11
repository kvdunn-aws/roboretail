#!/usr/bin/env python3
import aws_cdk as cdk
from roboretail_stack import RoboRetailStack

app = cdk.App()

RoboRetailStack(
    app,
    "RoboRetailStack",
    env=cdk.Environment(
        account="730335363819",
        region="us-west-2"
    ),
    description="RoboRetail - Deliberately vulnerable robot e-commerce platform"
)

app.synth()
