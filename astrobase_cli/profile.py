from typing import Optional

import typer

from astrobase_cli.utils.config import (
    ASTROBASE_HOST_PORT,
    AstrobaseConfig,
    AstrobaseProfile,
)
from astrobase_cli.utils.formatter import json_out

app = typer.Typer(help="""Manage Astrobase profiles.""")


@app.command()
def create(
    name: str,
    server: str = typer.Option(default=f"http://localhost:{ASTROBASE_HOST_PORT}"),
    gcp_creds: str = typer.Option(None),
    aws_creds: str = typer.Option(None),
    aws_profile_name: str = typer.Option(None),
):
    """
    Create a profile.
    """
    astrobase_config = AstrobaseConfig()
    new_profile = AstrobaseProfile(
        name=name,
        server=server,
        gcp_creds=gcp_creds,
        aws_creds=aws_creds,
        aws_profile_name=aws_profile_name,
    )
    astrobase_config.config[name] = new_profile.dict()
    astrobase_config.write_config(astrobase_config.config)
    typer.echo(f"Created profile {name}.")


@app.command("get")
def get(name: Optional[str] = None):
    """
    Get profiles; Specify --name to read a specific profile.
    """
    astrobase_config = AstrobaseConfig()
    if name is not None:
        if name in astrobase_config.config:
            typer.echo(json_out(astrobase_config.config[name]))
        else:
            typer.echo(f"profile {name} not found")
    else:
        typer.echo(json_out(astrobase_config.config))


@app.command()
def current():
    """
    Retrieve the current profile, set by the env var ASTROBASE_PROFILE.
    """
    astrobase_config = AstrobaseConfig()
    typer.echo(json_out(dict(astrobase_config.current_profile())))


@app.command()
def delete(name: Optional[str] = None):
    """
    Delete a profile :(
    """
    astrobase_config = AstrobaseConfig()
    typer.confirm(f"Are you sure you want to delete the {name} profile?")
    if name in astrobase_config.config:
        del astrobase_config.config[name]
        astrobase_config.write_config(astrobase_config.config)
        typer.echo(f"Deleted {name} profile.")
    else:
        typer.echo(f"Profile {name} not found.")
