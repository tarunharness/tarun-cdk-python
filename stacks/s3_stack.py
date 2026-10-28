from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    CfnOutput, # Import CfnOutput
)
from constructs import Construct

# Number of lifecycle rules added to the bucket purely to grow the synthesized template.
# With the default (336), cdk.out/S3Stack.template.json is 60,046 bytes (~60KB), i.e. above
# CloudFormation's 51,200-byte inline TemplateBody limit, so a change set diff has to go through
# S3. Each rule adds ~145 bytes on top of the 11,265-byte template of the unpadded stack.
# Override with `-c templatePaddingRules=<n>` (or a CDK context variable on the workspace):
# 0 gives the original small template, larger values grow it (CloudFormation allows at most
# 1000 lifecycle rules per bucket; the template must stay under 1MB).
DEFAULT_TEMPLATE_PADDING_RULES = 336


class S3Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        padding_rule_count = self._padding_rule_count()

        bucket = s3.Bucket(
            self,
            "sunny-cdk-test-bucket-03",
            bucket_name="sunny-cdk-test-bucket-03",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            # encryption=s3.BucketEncryption.S3_MANAGED,
            lifecycle_rules=self._padding_lifecycle_rules(padding_rule_count) or None,
        )

        # Output the bucket ARN
        CfnOutput(self, "S3BucketARN",
            value=bucket.bucket_arn,
            description="The ARN of the S3 bucket",
            export_name="MyS3BucketARN", # Name for cross-stack reference
        )

    def _padding_rule_count(self) -> int:
        # Context values passed on the command line (-c) arrive as strings.
        configured = self.node.try_get_context("templatePaddingRules")
        if configured is None:
            return DEFAULT_TEMPLATE_PADDING_RULES
        return int(configured)

    @staticmethod
    def _padding_lifecycle_rules(count: int) -> list:
        # Distinct ids and prefixes so S3 accepts every rule; they only expire objects under
        # archive/<n>/, which nothing writes to, so they have no effect on real data.
        return [
            s3.LifecycleRule(
                id=f"expire-archive-{index:04d}",
                prefix=f"archive/{index:04d}/",
                expiration=Duration.days(30),
            )
            for index in range(count)
        ]
