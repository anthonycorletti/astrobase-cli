import requests
import typer

from astrobase_cli.clients.kubernetes import Kubernetes
from astrobase_cli.utils.config import AstrobaseConfig
from astrobase_cli.utils.formatter import json_out
from astrobase_cli.utils.http import query_str


class GKEClient:
    def __init__(self):
        astrobase_config = AstrobaseConfig()
        self.url = f"{astrobase_config.current_profile().server}/gke"
        self.kubernetes = Kubernetes(via="gcloud")

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

    def apply_kubernetes_resources(
        self,
        kubernetes_resource_location: str,
        cluster_name: str,
        cluster_location: str,
    ) -> None:
        self.kubernetes.apply(  # pragma: no cover
            kubernetes_resource_location, cluster_name, cluster_location
        )

    def destroy_kubernetes_resources(
        self,
        kubernetes_resource_location: str,
        cluster_name: str,
        cluster_location: str,
    ) -> None:
        self.kubernetes.destroy(  # pragma: no cover
            kubernetes_resource_location, cluster_name, cluster_location
        )
