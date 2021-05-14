import base64
import os
import sys
from tempfile import NamedTemporaryFile

import google.auth
import google.auth.transport.requests
import requests
import typer
from sh import kubectl

from astrobase_cli.schemas.kubernetes import GKEKubernetesCredentials
from astrobase_cli.utils.config import AstrobaseConfig
from astrobase_cli.utils.formatter import json_out
from astrobase_cli.utils.http import query_str


class GKEClient:
    def __init__(self):
        astrobase_config = AstrobaseConfig()
        self.url = f"{astrobase_config.current_profile().server}/gke"

    def create(self, cluster: dict) -> None:
        res = requests.post(self.url, json=cluster)
        typer.echo(json_out(res.json()))

    def destroy(self, cluster: dict) -> None:
        params = {
            "location": cluster.get("location"),
            "project_id": cluster.get("project_id"),
        }
        cluster_url = f"{self.url}/{cluster.get('name')}?{query_str(params)}"
        res = requests.delete(cluster_url)
        typer.echo(json_out(res.json()))

    def get_gke_kubectl_credentials(
        self, cluster_name: str, cluster_location: str, project_id: str
    ) -> GKEKubernetesCredentials:
        response = requests.get(
            f"{self.url}/{cluster_name}"
            f"?project_id={project_id}&location={cluster_location}"
        )
        response_json = response.json()
        endpoint = response_json.get("endpoint")
        cluster_ca_certificate = response_json.get("masterAuth").get(
            "clusterCaCertificate"
        )
        creds, _ = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        with NamedTemporaryFile(delete=False) as ca_cert:
            ca_cert.write(base64.b64decode(cluster_ca_certificate))
        return GKEKubernetesCredentials(
            endpoint=endpoint, ca_path=ca_cert.name, token=creds.token
        )

    def apply_kubernetes_resources(
        self,
        kubernetes_resource_location: str,
        cluster_name: str,
        cluster_location: str,
        project_id: str,
        **kwargs,
    ) -> None:
        gke_kubectl_creds = self.get_gke_kubectl_credentials(
            cluster_name=cluster_name,
            cluster_location=cluster_location,
            project_id=project_id,
        )
        kubectl(
            "apply",
            "-f",
            f"{kubernetes_resource_location}",
            "--server",
            f"https://{gke_kubectl_creds.endpoint}",
            "--certificate-authority",
            f"{gke_kubectl_creds.ca_path}",
            "--token",
            f"{gke_kubectl_creds.token}",
            _out=sys.stdout,
        )
        os.remove(gke_kubectl_creds.ca_path)

    def destroy_kubernetes_resources(
        self,
        kubernetes_resource_location: str,
        cluster_name: str,
        cluster_location: str,
        project_id: str,
        **kwargs,
    ) -> None:
        gke_kubectl_creds = self.get_gke_kubectl_credentials(
            cluster_name=cluster_name,
            cluster_location=cluster_location,
            project_id=project_id,
        )
        kubectl(
            "delete",
            "-f",
            f"{kubernetes_resource_location}",
            "--server",
            f"https://{gke_kubectl_creds.endpoint}",
            "--certificate-authority",
            f"{gke_kubectl_creds.ca_path}",
            "--token",
            f"{gke_kubectl_creds.token}",
            _out=sys.stdout,
        )
        os.remove(gke_kubectl_creds.ca_path)
