import shutil

import typer

from astrobase_cli.schemas.command import Command

app = typer.Typer(help="Run preflight and status checks.")


@app.command()
def commands():
    """
    Check that the cli can access certain commands in your PATH.
    """
    message = ""
    for command in list(Command):
        command_location = shutil.which(command.value)
        if command_location is None:
            command_message = f"{command.value} not found in path!"
        else:
            command_message = command_location
        message += f"{command.value} found at: {command_message}\n"
    typer.echo(message.strip())
