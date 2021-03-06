import typer
import yaml

from astrobase_cli import __version__ as version
from astrobase_cli import apply, check, destroy, init, profile
from astrobase_cli.schemas.cluster import Clusters
from astrobase_cli.schemas.resource import ResourceList
from astrobase_cli.utils.params import YamlParams

name = f"🚀 Astrobase CLI {version} 🧑‍🚀"

app = typer.Typer(name=name)
app.add_typer(profile.app, name="profile")
app.add_typer(check.app, name="check")


@app.callback()
def main_callback() -> None:
    pass


main_callback.__doc__ = name


@app.command("version")
def _version() -> None:
    """
    Print the Astrobase CLI version.
    """
    typer.echo(name)


@app.command("init")
def _init(astrobase_container_version: str = "latest") -> None:
    """
    Initialize Astrobase.
    """
    initializer = init.Initializer()
    initializer.docker_run(astrobase_container_version)


@app.command("apply")
def _apply(
    astrobase_yaml_path: str = typer.Option(..., "-f"),
    yaml_params: str = typer.Option(
        None,
        "-v",
        help="Parameters to pass into your yaml. "
        "Format: key=value<space>key2=value2<space>key3=value3<space>...",
    ),
) -> None:
    """
    Apply clusters and resources.
    """
    astrobase_apply = apply.Apply()
    params = YamlParams(params=yaml_params)

    with open(astrobase_yaml_path, "r") as f:
        data = yaml.safe_load(f)
        data = params.update_data_with_values(data)
        clusters = Clusters(**data)
        resources = ResourceList(**data)
        astrobase_apply.apply_clusters(clusters)
        astrobase_apply.apply_resources(resources, params)


@app.command("destroy")
def _destroy(
    astrobase_yaml_path: str = typer.Option(..., "-f"),
    yaml_params: str = typer.Option(
        None,
        "-v",
        help="Parameters to pass into your yaml."
        "Format: key=value<space>key2=value2<space>key3=value3<space>...",
    ),
) -> None:
    """
    Destroy clusters and resources.
    """
    astrobase_destroy = destroy.Destroy()
    params = YamlParams(params=yaml_params)

    with open(astrobase_yaml_path, "r") as f:
        data = yaml.safe_load(f)
        data = params.update_data_with_values(data)
        clusters = Clusters(**data)
        resources = ResourceList(**data)
        astrobase_destroy.destroy_clusters(clusters)
        astrobase_destroy.destroy_resources(resources, params)
