import os

import pytest

from cli.utils.config import AstrobaseConfig

test_profile_name = "test-profile"


@pytest.fixture(scope="module", autouse=True)
def setup_astrobase_test_config():
    os.environ[AstrobaseConfig.ASTROBASE_PROFILE] = test_profile_name
    yield
