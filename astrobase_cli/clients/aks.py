import base64
import os
import sys
from tempfile import NamedTemporaryFile

import requests
import typer
import yaml
from azure.identity import ClientSecretCredential
from azure.mgmt.containerservice import ContainerServiceClient
from sh import kubectl

from astrobase_cli.schemas.kubernetes import AKSKubernetesCredentials
from astrobase_cli.utils.config import AstrobaseConfig
from astrobase_cli.utils.formatter import json_out
from astrobase_cli.utils.http import query_str


class AKSClient:
    def __init__(self) -> None:
        astrobase_config = AstrobaseConfig()
        self.url = f"{astrobase_config.current_profile().server}/aks"

    def create(self, cluster: dict) -> None:
        res = requests.post(self.url, json=cluster)
        typer.echo(json_out(res.json()))

    def destroy(self, cluster: dict) -> None:
        cluster_name = cluster.get("name")
        params = {"resource_group_name": cluster.get("resource_group_name")}
        cluster_url = f"{self.url}/{cluster_name}?{query_str(params)}"
        res = requests.delete(cluster_url)
        typer.echo(json_out(res.json()))

    def get_aks_kubectl_credentials(
        self, cluster_name: str, resource_group_name: str
    ) -> AKSKubernetesCredentials:
        response = requests.get(
            f"{self.url}/{cluster_name}" f"?resource_group_name={resource_group_name}"
        )
        cluster_response_json = response.json()
        endpoint = cluster_response_json.get("fqdn")
        credential = ClientSecretCredential(
            tenant_id=os.getenv("AZURE_TENANT_ID", ""),
            client_id=os.getenv("AZURE_CLIENT_ID", ""),
            client_secret=os.getenv("AZURE_CLIENT_SECRET", ""),
        )
        container_client = ContainerServiceClient(
            credential=credential,
            subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID", ""),
        )
        cluster_user_credentials = (
            container_client.managed_clusters.list_cluster_admin_credentials(
                resource_name=cluster_name, resource_group_name=resource_group_name
            )
        )
        kubeconfig = cluster_user_credentials.kubeconfigs[0]
        cluster_ca_certificate = (
            yaml.safe_load(kubeconfig.value.decode("utf8"))
            .get("clusters")[0]
            .get("cluster")
            .get("certificate-authority-data")
        )
        token = (
            yaml.safe_load(kubeconfig.value.decode("utf8"))
            .get("users")[0]
            .get("user")
            .get("token")
        )
        with NamedTemporaryFile(delete=False) as ca_cert:
            ca_cert.write(base64.b64decode(cluster_ca_certificate))
        return AKSKubernetesCredentials(
            endpoint=endpoint, ca_path=ca_cert.name, token=token
        )

    def apply_kubernetes_resources(
        self,
        kubernetes_resource_location: str,
        cluster_name: str,
        resource_group_name: str,
    ) -> None:
        aks_kubectl_creds = self.get_aks_kubectl_credentials(
            cluster_name=cluster_name,
            resource_group_name=resource_group_name,
        )
        kubectl(
            "apply",
            "-f",
            f"{kubernetes_resource_location}",
            "--server",
            f"https://{aks_kubectl_creds.endpoint}",
            "--certificate-authority",
            f"{aks_kubectl_creds.ca_path}",
            "--token",
            f"{aks_kubectl_creds.token}",
            _out=sys.stdout,
        )
        os.remove(aks_kubectl_creds.ca_path)

    def destroy_kubernetes_resources(
        self,
        kubernetes_resource_location: str,
        cluster_name: str,
        cluster_location: str,
        resource_group_name: str,
    ) -> None:
        aks_kubectl_creds = self.get_aks_kubectl_credentials(
            cluster_name=cluster_name,
            resource_group_name=resource_group_name,
        )
        kubectl(
            "delete",
            "-f",
            f"{kubernetes_resource_location}",
            "--server",
            f"https://{aks_kubectl_creds.endpoint}",
            "--certificate-authority",
            f"{aks_kubectl_creds.ca_path}",
            "--token",
            f"{aks_kubectl_creds.token}",
            _out=sys.stdout,
        )
        os.remove(aks_kubectl_creds.ca_path)
