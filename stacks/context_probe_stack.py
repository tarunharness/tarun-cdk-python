import json
import os

import aws_cdk as cdk
from constructs import Construct


def read_cdk_json_context(path: str = "cdk.json") -> dict:
    """The "context" block of cdk.json: where the plugin writes the merged context files."""
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f).get("context", {})


class ContextProbeStack(cdk.Stack):
    """Prints every CDK context value so context file merging can be verified from the logs.

    Testing only: values are printed in plain text, so do not use real secrets.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        file_context = read_cdk_json_context()
        print("=== cdk.json context (merged context files) ===")
        for key in sorted(file_context):
            print(f"{key} = {json.dumps(file_context[key])}")

        # try_get_context resolves the final value: --context flags > cdk.json > cdk.context.json.
        # Only keys present in cdk.json are probed; add names here for --context-only variables.
        print("=== Resolved by CDK (try_get_context) ===")
        for key in sorted(file_context):
            print(f"{key} = {json.dumps(self.node.try_get_context(key))}")

        stage = self.node.try_get_context("stage")
        instance_count = self.node.try_get_context("instanceCount")
        print(f"stage={stage!r} instanceCount={instance_count!r} ({type(instance_count).__name__})")

        # Arrays and objects arrive as list / dict. A value passed with --context is always a
        # string, so decode it if a context variable shadows a context file key.
        allowed_cidrs = self.node.try_get_context("allowedCidrs")
        if isinstance(allowed_cidrs, str):
            allowed_cidrs = json.loads(allowed_cidrs)
        vpc_config = self.node.try_get_context("vpcConfig")
        if isinstance(vpc_config, str):
            vpc_config = json.loads(vpc_config)
        tags = self.node.try_get_context("tags")
        if isinstance(tags, str):
            tags = json.loads(tags)

        print(f"allowedCidrs ({type(allowed_cidrs).__name__}):")
        for cidr in allowed_cidrs or []:
            print(f"  - {cidr}")

        print(f"vpcConfig ({type(vpc_config).__name__}):")
        for key, value in (vpc_config or {}).items():
            print(f"  {key} = {value!r}")

        max_azs = (vpc_config or {}).get("maxAzs", 2)
        nat_gateways = (vpc_config or {}).get("natGateways", 1)
        print(f"maxAzs={max_azs} natGateways={nat_gateways}")

        for key, value in (tags or {}).items():
            cdk.Tags.of(self).add(key, str(value))

        # Harmless output so `cdk synth` / `cdk diff` produce a template.
        cdk.CfnOutput(self, "ContextProbe", value="ok")
