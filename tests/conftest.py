import os

import pytest
from typer.testing import CliRunner

from astrobase_cli.utils.config import AstrobaseConfig

runner = CliRunner()
os.environ[AstrobaseConfig.ASTROBASE_PROFILE] = "test-profile"
os.environ[AstrobaseConfig.ASTROBASE_CONFIG_FILE] = "test-config.json"


@pytest.fixture(scope="module", autouse=True)
def setup_astrobase_test_config():
    # pre-test function
    # add setup on a modular basis if necessary
    yield
    # post-test function
    # we try here because not every test will use a profile
    try:
        os.remove(os.environ[AstrobaseConfig.ASTROBASE_CONFIG_FILE])
    except FileNotFoundError:
        pass
