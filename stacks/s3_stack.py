from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    CfnOutput, # Import CfnOutput
)
from constructs import Construct


class S3Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self,
            "sunny-cdk-test-bucket-03",
            bucket_name="sunny-cdk-test-bucket-03",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            # encryption=s3.BucketEncryption.S3_MANAGED,
        )

        # Output the bucket ARN
        CfnOutput(self, "S3BucketARN",
            value=bucket.bucket_arn,
            description="The ARN of the S3 bucket",
            export_name="MyS3BucketARN", # Name for cross-stack reference
        )
