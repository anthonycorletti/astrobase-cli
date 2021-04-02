import json
import os
from typing import Optional

import typer
from pydantic import BaseModel

ASTROBASE_HOST_PORT = os.getenv("ASTROBASE_HOST_PORT", "8787")


class AstrobaseProfile(BaseModel):
    server: str = f"http://localhost:{ASTROBASE_HOST_PORT}"
    gcp_creds: Optional[str]
    aws_creds: Optional[str]
    aws_profile_name: Optional[str]


class AstrobaseConfig:
    ASTROBASE_PROFILE = "ASTROBASE_PROFILE"
    ASTROBASE_CONFIG = "ASTROBASE_CONFIG"
    DEFAULT_ASTROBASE_CONFIG_FULLPATH = f"{os.getenv('HOME')}/.astrobase/config.json"

    def __init__(self):
        self.config = os.getenv(
            self.ASTROBASE_CONFIG, self.DEFAULT_ASTROBASE_CONFIG_FULLPATH
        )

        try:
            self._setup_config_dir()
            self._setup_config_file()
        except FileExistsError:
            pass

        self.config_dict = self._load_config_file()
        self.profile_name = os.getenv(self.ASTROBASE_PROFILE)
        if not self.profile_name:
            typer.echo(
                "ASTROBASE_PROFILE not set! Set it with "
                "export ASTROBASE_PROFILE=<your-profile-name>"
            )
            raise typer.Exit(1)

        self.current_profile = AstrobaseProfile()

        if self.profile_name in self.config_dict:
            self.current_profile = AstrobaseProfile(
                **self.config_dict[self.profile_name]
            )

    def _setup_config_dir(self) -> None:
        dirname = os.path.dirname(self.config)
        if dirname:
            os.makedirs(dirname)

    def _setup_config_file(self) -> None:
        if not os.path.exists(self.config):
            with open(self.config, "w+") as f:
                f.write("{}")

    def _load_config_file(self) -> dict:
        with open(self.config) as f:
            return json.load(f)

    def write_config(self, data: dict) -> None:
        with open(self.config, "w+") as f:
            f.write(json.dumps(data))


class AstrobaseDockerConfig:
    CONTAINER_REGISTRY_DOMAIN = "gcr.io"
    DOCKER_GROUP = "astrobaseco"
    DOCKER_CONTAINER_NAME = "astrobase"
    AWS_PROFILE_ENV_KEY = "AWS_PROFILE"
    AWS_CREDS_CONTAINER = "/aws-credentials"
    AWS_SHARED_CREDS_FILE_ENV_KEY = "AWS_SHARED_CREDENTIALS_FILE"
    GOOGLE_CREDS_CONTAINER = "/google-credentials.json"
    GOOGLE_APPLICATION_CREDS_ENV_KEY = "GOOGLE_APPLICATION_CREDENTIALS"

    def __init__(
        self,
        container_version: str,
        astrobase_config: AstrobaseConfig,
        environment: dict = {},
        volumes: dict = {},
        auto_remove: bool = True,
        detach: bool = True,
        host_port: str = ASTROBASE_HOST_PORT,
        container_registry_domain: str = CONTAINER_REGISTRY_DOMAIN,
    ):
        self.container_registry_domain = container_registry_domain
        self.image = (
            f"{self.container_registry_domain}/{self.DOCKER_GROUP}/"
            f"{self.DOCKER_CONTAINER_NAME}:{container_version}"
        )
        self.ports = {f"{host_port}/tcp": str(host_port)}
        self.auto_remove = auto_remove
        self.detach = detach
        self.name = f"astrobase-{astrobase_config.profile_name}"
        self.astrobase_config = astrobase_config
        self.volumes = volumes
        self.environment = environment

        self._configure_aws()
        self._configure_gcp()

    def _configure_gcp(self) -> None:
        host_gcp_creds = self.astrobase_config.current_profile.gcp_creds
        if host_gcp_creds:
            self.environment[
                self.GOOGLE_APPLICATION_CREDS_ENV_KEY
            ] = self.GOOGLE_CREDS_CONTAINER
            self.volumes[host_gcp_creds] = {
                "bind": self.GOOGLE_CREDS_CONTAINER,
                "mode": "ro",
            }

    def _configure_aws(self) -> None:
        host_aws_creds = self.astrobase_config.current_profile.aws_creds
        if host_aws_creds:
            self.volumes[host_aws_creds] = {
                "bind": self.AWS_CREDS_CONTAINER,
                "mode": "ro",
            }
        aws_profile_name = self.astrobase_config.current_profile.aws_profile_name
        if aws_profile_name:
            self.environment[
                self.AWS_SHARED_CREDS_FILE_ENV_KEY
            ] = self.AWS_CREDS_CONTAINER
            self.environment[self.AWS_PROFILE_ENV_KEY] = aws_profile_name
