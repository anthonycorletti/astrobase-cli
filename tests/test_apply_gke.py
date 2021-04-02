import json

import requests  # noqa
from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()
mock_server = "http://localhost:8787"


def test_apply_gke_cluster(requests_mock):
    requests_mock.post(
        f"{mock_server}/gke",
        json={
            "name": "operation-unixts-id",
            "zone": "us-central1",
            "operationType": "CREATE_CLUSTER",
            "status": "RUNNING",
            "selfLink": (
                "https://container.googleapis.com/v1beta1/projects/"
                "project_id/locations/us-central1/operations/operation-unixts-id"
            ),
            "targetLink": (
                "https://container.googleapis.com/v1beta1/projects/"
                "project_id/locations/us-central1/clusters/test-gke"
            ),
            "startTime": "2021-04-02T05:33:57.442600205Z",
        },
    )
    result = runner.invoke(
        app,
        [
            "apply",
            "-f",
            "tests/assets/test-gke-cluster.yaml",
            "-v",
            "PROJECT_ID=test-project-id",
        ],
    )
    assert result.exit_code == 0
    assert "CREATE_CLUSTER" == json.loads(result.stdout).get("operationType")


def test_apply_gke_cluster_no_params(requests_mock):
    requests_mock.post(
        f"{mock_server}/gke",
        json={
            "name": "operation-unixts-id",
            "zone": "us-central1",
            "operationType": "CREATE_CLUSTER",
            "status": "RUNNING",
            "selfLink": (
                "https://container.googleapis.com/v1beta1/projects/"
                "project_id/locations/us-central1/operations/operation-unixts-id"
            ),
            "targetLink": (
                "https://container.googleapis.com/v1beta1/projects/"
                "project_id/locations/us-central1/clusters/test-gke"
            ),
            "startTime": "2021-04-02T05:33:57.442600205Z",
        },
    )
    result = runner.invoke(
        app,
        [
            "apply",
            "-f",
            "tests/assets/test-gke-cluster.yaml",
        ],
    )
    assert result.exit_code == 0
    assert "CREATE_CLUSTER" == json.loads(result.stdout).get("operationType")


def test_destroy_gke_cluster(requests_mock):
    test_cluster_location = "us-central1"
    test_cluster_project_id = "test-project-id"
    requests_mock.delete(
        (
            f"{mock_server}/gke/test-gke?location="
            f"{test_cluster_location}&project_id={test_cluster_project_id}"
        ),
        json={
            "name": "operation-unixts-id",
            "zone": "us-central1",
            "operationType": "DELETE_CLUSTER",
            "status": "RUNNING",
            "selfLink": (
                "https://container.googleapis.com/v1beta1/projects/"
                "project_id/locations/us-central1/operations/operation-unixts-id"
            ),
            "targetLink": (
                "https://container.googleapis.com/v1beta1/projects/"
                "project_id/locations/us-central1/clusters/test-gke"
            ),
            "startTime": "2021-04-02T05:42:42.481263761Z",
        },
    )
    result = runner.invoke(
        app,
        [
            "destroy",
            "-f",
            "tests/assets/test-gke-cluster.yaml",
            "-v",
            "PROJECT_ID=test-project-id",
        ],
    )
    assert result.exit_code == 0
    assert "DELETE_CLUSTER" == json.loads(result.stdout).get("operationType")


def test_apply_resources_gke_cluster(requests_mock):
    pass
