import os
import subprocess

from typer.testing import CliRunner

from cli.main import app
from cli.utils.config import AstrobaseConfig

runner = CliRunner()
astrobase_config = AstrobaseConfig()


def cleanup_init_container(container_name: str):
    subprocess.run(["docker", "kill", container_name], stdout=subprocess.DEVNULL)


def test_init():
    test_profile_name = os.getenv(AstrobaseConfig.ASTROBASE_PROFILE)
    runner.invoke(
        app,
        [
            "profile",
            "create",
            test_profile_name,
            "--gcp-creds",
            "test-gcp",
            "--aws-creds",
            "test-aws",
            "--aws-profile-name",
            "test-aws",
        ],
    )
    container_name = f"astrobase-{os.environ[AstrobaseConfig.ASTROBASE_PROFILE]}"
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Astrobase initialized and running at " in result.stdout
    cleanup_init_container(container_name)


def test_init_no_profile():
    del os.environ[astrobase_config.ASTROBASE_PROFILE]
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 1
    assert "No profile is set! set a profile with: export" in result.stdout
