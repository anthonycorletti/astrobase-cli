import os
from typing import Optional

import typer

from cli.utils.config import ASTROBASE_HOST_PORT, AstrobaseConfig, AstrobaseProfile
from cli.utils.formatter import json_out

app = typer.Typer(help="""Manage Astrobase profiles.""")


@app.command()
def create(
    name: str,
    server: str = typer.Option(default=f"http://localhost:{ASTROBASE_HOST_PORT}"),
    gcp_creds: str = typer.Option(None),
    aws_creds: str = typer.Option(None),
    aws_profile_name: str = typer.Option(None),
):
    astrobase_config = AstrobaseConfig()
    new_profile = AstrobaseProfile(
        server=server,
        gcp_creds=gcp_creds,
        aws_creds=aws_creds,
        aws_profile_name=aws_profile_name,
    )
    astrobase_config.config_dict[name] = new_profile.dict()
    astrobase_config.write_config(astrobase_config.config_dict)
    typer.echo(f"Created profile {name}.")


@app.command("get")
def get(name: Optional[str] = None):
    astrobase_config = AstrobaseConfig()
    if name is not None:
        if name in astrobase_config.config_dict:
            typer.echo(json_out(astrobase_config.config_dict[name]))
        else:
            typer.echo(f"profile {name} not found")
    else:
        typer.echo(json_out(astrobase_config.config_dict))


@app.command()
def current():
    astrobase_config = AstrobaseConfig()
    profile_name = os.getenv(astrobase_config.ASTROBASE_PROFILE)
    profile_data = astrobase_config.current_profile.dict()
    typer.echo(json_out({profile_name: profile_data}))


@app.command()
def delete(name: Optional[str] = None):
    astrobase_config = AstrobaseConfig()
    typer.confirm(f"Are you sure you want to delete the {name} profile?")
    if name in astrobase_config.config_dict:
        del astrobase_config.config_dict[name]
        astrobase_config.write_config(astrobase_config.config_dict)
        typer.echo(f"Deleted {name} profile.")
    else:
        typer.echo(f"Profile {name} not found.")
