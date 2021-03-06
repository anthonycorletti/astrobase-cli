import json
import os

import requests  # noqa
from typer.testing import CliRunner

from astrobase_cli.main import app
from astrobase_cli.utils.config import AstrobaseConfig

runner = CliRunner()
mock_server = "http://localhost:8787"


def test_apply_eks_cluster(requests_mock):
    profile_name = os.environ[AstrobaseConfig.ASTROBASE_PROFILE]
    runner.invoke(
        app,
        [
            "profile",
            "create",
            profile_name,
            "--gcp-creds",
            "test-gcp",
            "--aws-creds",
            "test-aws",
            "--aws-profile-name",
            "test-aws",
        ],
    )
    requests_mock.post(
        f"{mock_server}/eks",
        json={"message": "EKS create request submitted for test-eks-cluster"},
    )
    result = runner.invoke(
        app,
        [
            "apply",
            "-f",
            "tests/assets/test-eks-cluster.yaml",
            "-v",
            "CLUSTER_ROLE_ARN=aws:acm:iam::account_id:role/cluster_role "
            "NODE_ROLE_ARN=aws:acm:iam::account_id:role/node_role "
            "SUBNET_ID_0=subnet-0 "
            "SUBNET_ID_1=subnet-1 "
            "SECURITY_GROUP=sg-1234",
        ],
    )
    assert result.exit_code == 0
    assert "EKS create request submitted for test-eks-cluster" == json.loads(
        result.stdout
    ).get("message")


def test_destroy_eks_cluster(requests_mock):
    test_cluster_location = "us-east-1"
    requests_mock.delete(
        f"{mock_server}/eks/astrobase-test-eks?region={test_cluster_location}",
        json={
            "message": "EKS delete request submitted for astrobase-test-eks cluster"
            " and nodegroups: test-nodegroup-cpu"
        },
    )
    result = runner.invoke(
        app,
        [
            "destroy",
            "-f",
            "tests/assets/test-eks-cluster.yaml",
            "-v",
            "CLUSTER_ROLE_ARN=aws:acm:iam::account_id:role/cluster_role "
            "NODE_ROLE_ARN=aws:acm:iam::account_id:role/node_role "
            "SUBNET_ID_0=subnet-0 "
            "SUBNET_ID_1=subnet-1 "
            "SECURITY_GROUP=sg-1234",
        ],
    )
    assert result.exit_code == 0
    assert (
        "EKS delete request submitted for astrobase-test-eks cluster"
        " and nodegroups: test-nodegroup-cpu"
        == json.loads(result.stdout).get("message")
    )
