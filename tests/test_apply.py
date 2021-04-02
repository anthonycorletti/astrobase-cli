import requests  # noqa
from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()
mock_server = "http://localhost:8787"


def test_apply_gke_cluster(requests_mock):
    requests_mock.post(f"{mock_server}/gke", json={"hello": "world"})
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
    # TODO actually get the response and check it yo


def test_apply_resources():
    pass
