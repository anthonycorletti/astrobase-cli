import json
import os

from typer.testing import CliRunner

from cli.utils.config import AstrobaseConfig

runner = CliRunner()


def test_empty_config_setting():
    orig_config = AstrobaseConfig.DEFAULT_ASTROBASE_CONFIG_FULLPATH
    config_path = "astrobase-test-config.json"
    AstrobaseConfig.DEFAULT_ASTROBASE_CONFIG_FULLPATH = config_path
    astrobase_config = AstrobaseConfig()
    assert astrobase_config.config == config_path
    with open(config_path) as test_config:
        data = json.load(test_config)
        assert data == {}
    AstrobaseConfig.DEFAULT_ASTROBASE_CONFIG_FULLPATH = orig_config
    os.remove(config_path)
