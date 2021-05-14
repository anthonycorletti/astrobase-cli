import base64
import os
import sys
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile

import requests
import typer
from awscli.customizations.eks.get_token import (
    TOKEN_EXPIRATION_MINS,
    STSClientFactory,
    TokenGenerator,
)
from botocore import session
from sh import kubectl

from astrobase_cli.clients.kubernetes import Kubernetes
from astrobase_cli.schemas.kubernetes import EKSKubernetesCredentials
from astrobase_cli.utils.config import AstrobaseConfig
from astrobase_cli.utils.formatter import json_out


class EKSClient:
    def __init__(self):
        astrobase_config = AstrobaseConfig()
        self.url = f"{astrobase_config.current_profile().server}/eks"
        self.kubernetes = Kubernetes(via="aws")

    def create(self, cluster: dict) -> None:
        res = requests.post(self.url, json=cluster)
        typer.echo(json_out(res.json()))

    def destroy(self, cluster: dict) -> None:
        cluster_name = cluster.get("name")
        cluster_region = cluster.get("region")
        cluster_url = f"{self.url}/{cluster_name}?region={cluster_region}"
        nodegroups = cluster.get("nodegroups", [])
        nodegroup_names = [ng.get("nodegroupName") for ng in nodegroups]
        res = requests.delete(cluster_url, json=nodegroup_names)
        typer.echo(json_out(res.json()))

    def get_eks_token_expiration_timestr(self) -> str:
        token_expiration = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINS)
        return token_expiration.strftime("%Y-%m-%dT%H:%M:%SZ")

    def get_eks_kubectl_credentials(
        self, cluster_name: str, cluster_location: str, role_arn: str = None
    ) -> EKSKubernetesCredentials:
        response = requests.get(
            f"{self.url}/{cluster_name}" f"?region={cluster_location}"
        )
        cluster_response_json = response.json().get("cluster")
        endpoint = cluster_response_json.get("endpoint")
        cluster_ca_certificate = cluster_response_json.get("certificateAuthority").get(
            "data"
        )
        botosession = session.get_session()
        sts_client_factory = STSClientFactory(botosession)
        sts_client = sts_client_factory.get_sts_client(role_arn=role_arn)
        token = TokenGenerator(sts_client).get_token(cluster_name)
        with NamedTemporaryFile(delete=False) as ca_cert:
            ca_cert.write(base64.b64decode(cluster_ca_certificate))
        return EKSKubernetesCredentials(
            endpoint=endpoint, ca_path=ca_cert.name, token=token
        )

    def apply_kubernetes_resources(
        self,
        kubernetes_resource_location: str,
        cluster_name: str,
        cluster_location: str,
        **kwargs,
    ) -> None:
        eks_kubectl_creds = self.get_eks_kubectl_credentials(
            cluster_name=cluster_name,
            cluster_location=cluster_location,
        )
        kubectl(
            "apply",
            "-f",
            f"{kubernetes_resource_location}",
            "--server",
            f"{eks_kubectl_creds.endpoint}",
            "--certificate-authority",
            f"{eks_kubectl_creds.ca_path}",
            "--token",
            f"{eks_kubectl_creds.token}",
            _out=sys.stdout,
        )
        os.remove(eks_kubectl_creds.ca_path)

    def destroy_kubernetes_resources(
        self,
        kubernetes_resource_location: str,
        cluster_name: str,
        cluster_location: str,
        **kwargs,
    ) -> None:
        eks_kubectl_creds = self.get_eks_kubectl_credentials(
            cluster_name=cluster_name,
            cluster_location=cluster_location,
        )
        kubectl(
            "delete",
            "-f",
            f"{kubernetes_resource_location}",
            "--server",
            f"{eks_kubectl_creds.endpoint}",
            "--certificate-authority",
            f"{eks_kubectl_creds.ca_path}",
            "--token",
            f"{eks_kubectl_creds.token}",
            _out=sys.stdout,
        )
        os.remove(eks_kubectl_creds.ca_path)
