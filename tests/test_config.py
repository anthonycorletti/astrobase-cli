import json
import os
import shutil

from typer.testing import CliRunner

from astrobase_cli.main import app
from astrobase_cli.utils.config import AstrobaseConfig, AstrobaseDockerConfig

runner = CliRunner()


def test_empty_config_setting():
    astrobase_config = AstrobaseConfig()
    with open(astrobase_config.config_file) as test_config:
        assert {} == json.load(test_config)


def test_new_config():
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
            "--azure-client-id",
            "test-azure",
            "--azure-client-secret",
            "test-azure",
            "--azure-subscription-id",
            "test-azure",
            "--azure-tenant-id",
            "test-azure",
        ],
    )
    astrobase_config = AstrobaseConfig()
    astrobase_docker_config = AstrobaseDockerConfig(
        container_version="latest",
        astrobase_config=astrobase_config,
    )
    assert astrobase_docker_config.name == "astrobase-test-profile"
    assert astrobase_config.current_profile().server == "http://localhost:8787"
    assert astrobase_config.current_profile().aws_creds == "test-aws"


def test_missing_profile():
    os.environ[AstrobaseConfig.ASTROBASE_PROFILE] = "not-here"
    result = runner.invoke(app, ["profile", "current"])
    assert result.exit_code == 1
    assert "ASTROBASE_PROFILE environment variable is not set" in result.stdout


def test_make_config_file_dirs():
    os.environ[AstrobaseConfig.ASTROBASE_CONFIG_FILE] = "de/path/to/config.json"
    AstrobaseConfig()
    with open(os.environ[AstrobaseConfig.ASTROBASE_CONFIG_FILE]) as f:
        assert {} == json.load(f)
    os.remove(os.environ[AstrobaseConfig.ASTROBASE_CONFIG_FILE])
    shutil.rmtree("de")
    os.environ[AstrobaseConfig.ASTROBASE_CONFIG_FILE] = "test-config.json"
