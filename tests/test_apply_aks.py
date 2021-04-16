import json  # noqa
import os

import requests  # noqa
from typer.testing import CliRunner

from astrobase_cli.main import app
from astrobase_cli.utils.config import AstrobaseConfig

runner = CliRunner()
mock_server = "http://localhost:8787"


def test_apply_aks_cluster(requests_mock):
    runner.invoke(
        app,
        [
            "profile",
            "create",
            os.environ[AstrobaseConfig.ASTROBASE_PROFILE],
            "--azure-client-id",
            "test-client-id",
            "--azure-client-secret",
            "test-client-secret",
            "--azure-subscription-id",
            "test-sub-id",
            "--azure-tenant-id",
            "test-tenant-id",
        ],
    )
    requests_mock.post(
        f"{mock_server}/aks",
        json={
            "result": "AKS create request submitted for astrobase-test-aks",
            "status": 200,
        },
    )
    result = runner.invoke(
        app,
        [
            "apply",
            "-f",
            "tests/assets/test-aks-cluster.yaml",
            "-v",
            "RESOURCE_GROUP_NAME=testresourcegroup",
        ],
    )
    assert result.exit_code == 0
    # assert "CREATE_CLUSTER" == json.loads(result.stdout).get("operationType")


def test_destroy_aks_cluster(requests_mock):
    resource_group_name = "testresourcegroup"
    requests_mock.delete(
        (
            f"{mock_server}/aks/astrobase-test-aks?resource_group_name="
            f"{resource_group_name}"
        ),
        json={
            "result": "AKS delete request submitted for astrobase-test-aks",
            "status": 200,
        },
    )
    result = runner.invoke(
        app,
        [
            "destroy",
            "-f",
            "tests/assets/test-aks-cluster.yaml",
            "-v",
            "RESOURCE_GROUP_NAME=testresourcegroup",
        ],
    )
    assert result.exit_code == 0
    # assert "DELETE_CLUSTER" == json.loads(result.stdout).get("operationType")
