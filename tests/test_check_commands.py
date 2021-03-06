import os

from typer.testing import CliRunner

from astrobase_cli.main import app

runner = CliRunner()


def test_check_commands():
    result = runner.invoke(app, ["check", "commands"])
    assert result.exit_code == 0
    assert "kubectl found at: " in result.stdout


def test_check_commands_missing_commands():
    path = os.environ["PATH"]
    os.environ["PATH"] = ""
    result = runner.invoke(app, ["check", "commands"])
    assert result.exit_code == 0
    assert "kubectl not found in path!" in result.stdout
    os.environ["PATH"] = path
