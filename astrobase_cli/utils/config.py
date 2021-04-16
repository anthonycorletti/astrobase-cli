import json
import os
from typing import Optional

import typer
from pydantic import BaseModel

ASTROBASE_HOST_PORT = os.getenv("ASTROBASE_HOST_PORT", "8787")


class AstrobaseProfile(BaseModel):
    name: str
    server: str = f"http://localhost:{ASTROBASE_HOST_PORT}"
    gcp_creds: Optional[str]
    aws_creds: Optional[str]
    aws_profile_name: Optional[str]
    azure_client_id: Optional[str]
    azure_client_secret: Optional[str]
    azure_subscription_id: Optional[str]
    azure_tenant_id: Optional[str]


class AstrobaseConfig:
    ASTROBASE_PROFILE = "ASTROBASE_PROFILE"
    ASTROBASE_CONFIG_FILE = "ASTROBASE_CONFIG"
    DEFAULT_ASTROBASE_CONFIG_FILE = f"{os.getenv('HOME')}/.astrobase/config.json"

    def __init__(self):
        self.config_file = os.getenv(
            self.ASTROBASE_CONFIG_FILE,
            self.DEFAULT_ASTROBASE_CONFIG_FILE,
        )
        self._setup_config_dir()
        self._setup_config_file()
        self.config = self._load_config_file()

    def _setup_config_dir(self) -> None:
        if not os.path.exists(self.config_file):
            dirname = os.path.dirname(self.config_file)
            if dirname:
                os.makedirs(dirname)

    def _setup_config_file(self) -> None:
        if not os.path.exists(self.config_file):
            with open(self.config_file, "w+") as f:
                f.write("{}")

    def _load_config_file(self) -> dict:
        with open(self.config_file) as f:
            return json.load(f)

    def write_config(self, data: dict) -> None:
        with open(self.config_file, "w+") as f:
            f.write(json.dumps(data))

    def current_profile(self) -> AstrobaseProfile:
        profile_name = os.getenv(self.ASTROBASE_PROFILE)
        if not profile_name or profile_name not in self.config:
            typer.echo(
                "ASTROBASE_PROFILE environment variable is not set properly.\n"
                "Please set it with `export ASTROBASE_PROFILE=<your-profile-name>`\n"
                "View profile names with `astrobase profile get | jq 'keys'`"
            )
            raise typer.Exit(1)
        return AstrobaseProfile(**self.config.get(profile_name))


class AstrobaseDockerConfig:
    CONTAINER_REGISTRY_DOMAIN = "gcr.io"
    DOCKER_GROUP = "astrobaseco"
    DOCKER_CONTAINER_NAME = "astrobase"
    AWS_PROFILE_ENV_KEY = "AWS_PROFILE"
    AWS_CREDS_CONTAINER = "/aws-credentials"
    AWS_SHARED_CREDS_FILE_ENV_KEY = "AWS_SHARED_CREDENTIALS_FILE"
    GOOGLE_CREDS_CONTAINER = "/google-credentials.json"
    GOOGLE_APPLICATION_CREDS_ENV_KEY = "GOOGLE_APPLICATION_CREDENTIALS"
    AZURE_CLIENT_ID_ENV_KEY = "AZURE_CLIENT_ID"
    AZURE_CLIENT_SECRET_ENV_KEY = "AZURE_CLIENT_SECRET"
    AZURE_SUBSCRIPTION_ID_ENV_KEY = "AZURE_SUBSCRIPTION_ID"
    AZURE_TENANT_ID_ENV_KEY = "AZURE_TENANT_ID"

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
        self.name = f"astrobase-{astrobase_config.current_profile().name}"
        self.astrobase_config = astrobase_config
        self.volumes = volumes
        self.environment = environment

        self._configure_aws()
        self._configure_gcp()
        self._configure_azure()

    def _configure_gcp(self) -> None:
        host_gcp_creds = self.astrobase_config.current_profile().gcp_creds
        if host_gcp_creds:
            self.environment[
                self.GOOGLE_APPLICATION_CREDS_ENV_KEY
            ] = self.GOOGLE_CREDS_CONTAINER
            self.volumes[host_gcp_creds] = {
                "bind": self.GOOGLE_CREDS_CONTAINER,
                "mode": "ro",
            }

    def _configure_aws(self) -> None:
        host_aws_creds = self.astrobase_config.current_profile().aws_creds
        if host_aws_creds:
            self.volumes[host_aws_creds] = {
                "bind": self.AWS_CREDS_CONTAINER,
                "mode": "ro",
            }
        aws_profile_name = self.astrobase_config.current_profile().aws_profile_name
        if aws_profile_name:
            self.environment[
                self.AWS_SHARED_CREDS_FILE_ENV_KEY
            ] = self.AWS_CREDS_CONTAINER
            self.environment[self.AWS_PROFILE_ENV_KEY] = aws_profile_name

    def _configure_azure(self) -> None:
        azure_client_id = self.astrobase_config.current_profile().azure_client_id
        if azure_client_id:
            self.environment[self.AZURE_CLIENT_ID_ENV_KEY] = azure_client_id
        azure_client_secret = (
            self.astrobase_config.current_profile().azure_client_secret
        )
        if azure_client_secret:
            self.environment[self.AZURE_CLIENT_SECRET_ENV_KEY] = azure_client_secret
        azure_subscription_id = (
            self.astrobase_config.current_profile().azure_subscription_id
        )
        if azure_subscription_id:
            self.environment[self.AZURE_SUBSCRIPTION_ID_ENV_KEY] = azure_subscription_id
        azure_tenant_id = self.astrobase_config.current_profile().azure_tenant_id
        if azure_tenant_id:
            self.environment[self.AZURE_TENANT_ID_ENV_KEY] = azure_tenant_id
