#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.s3_stack import S3Stack
from stacks.sqs_stack import SQSStack
from stacks.context_probe_stack import ContextProbeStack
# from stacks.ec2_stack import EC2Stack

app = cdk.App()
S3Stack(app, "S3Stack")
SQSStack(app, "SQSStack")
ContextProbeStack(app, "ContextProbeStack")
# EC2Stack(app, "EC2Stack")

app.synth()
