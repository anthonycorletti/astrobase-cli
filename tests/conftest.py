import os

import pytest
from typer.testing import CliRunner

from cli.utils.config import AstrobaseConfig

runner = CliRunner()


@pytest.fixture(scope="module", autouse=True)
def setup_astrobase_test_config():
    os.environ[AstrobaseConfig.ASTROBASE_PROFILE] = "test-profile"
    os.environ[AstrobaseConfig.ASTROBASE_CONFIG] = "test-config.json"
    yield
    # we try here because not every test will use a profile
    try:
        os.remove(os.environ[AstrobaseConfig.ASTROBASE_CONFIG])
    except FileNotFoundError:
        pass
