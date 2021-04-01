import os

from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


def test_check_commands():
    result = runner.invoke(app, ["check", "commands"])
    assert result.exit_code == 0
    assert "aws found at: " in result.stdout
    assert "gcloud found at: " in result.stdout
    assert "kubectl found at: " in result.stdout


def test_check_commands_missing_commands():
    path = os.environ["PATH"]
    os.environ["PATH"] = ""
    result = runner.invoke(app, ["check", "commands"])
    assert result.exit_code == 0
    assert "aws not found in path!" in result.stdout
    assert "gcloud not found in path!" in result.stdout
    assert "kubectl not found in path!" in result.stdout
    os.environ["PATH"] = path
