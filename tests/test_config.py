import json
import os

from typer.testing import CliRunner

from cli.main import app
from cli.utils.config import AstrobaseConfig, AstrobaseDockerConfig

runner = CliRunner()


def test_empty_config_setting():
    astrobase_config = AstrobaseConfig()
    assert astrobase_config.config == "test-config.json"
    with open("test-config.json") as test_config:
        data = json.load(test_config)
        assert data == {}


def test_config():
    runner.invoke(
        app,
        [
            "profile",
            "create",
            os.environ[AstrobaseConfig.ASTROBASE_PROFILE],
            "--gcp-creds",
            "test-gcp",
            "--aws-creds",
            "test-aws",
            "--aws-profile-name",
            "test-aws",
        ],
    )
    astrobase_config = AstrobaseConfig()
    astrobase_docker_config = AstrobaseDockerConfig(
        container_version="latest",
        astrobase_config=astrobase_config,
    )
    assert astrobase_docker_config.name == "astrobase-test-profile"
    assert astrobase_config.current_profile.server == "http://localhost:8787"
