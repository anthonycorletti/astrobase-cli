from typer.testing import CliRunner

from astrobase_cli import __version__ as cli_version
from astrobase_cli.main import app

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert cli_version in result.stdout
