import docker
import typer

from astrobase_cli.utils.config import AstrobaseConfig, AstrobaseDockerConfig

docker_client = docker.from_env()


class Initializer:
    def docker_run(self, astrobase_container_version: str) -> None:
        astrobase_config = AstrobaseConfig()
        typer.echo("Initializing Astrobase ... ")
        astrobase_docker_config = AstrobaseDockerConfig(
            container_version=astrobase_container_version,
            astrobase_config=astrobase_config,
        )
        typer.echo("Starting Astrobase server ... ")
        docker_client.containers.run(
            image=astrobase_docker_config.image,
            ports=astrobase_docker_config.ports,
            environment=astrobase_docker_config.environment,
            volumes=astrobase_docker_config.volumes,
            auto_remove=astrobase_docker_config.auto_remove,
            detach=astrobase_docker_config.detach,
            name=astrobase_docker_config.name,
        )
        typer.echo(
            "Astrobase initialized and running at "
            f"{astrobase_config.current_profile().server}"
        )
