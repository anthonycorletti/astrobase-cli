import requests
import typer

from astrobase_cli.clients.kubernetes import Kubernetes
from astrobase_cli.utils.config import AstrobaseConfig
from astrobase_cli.utils.formatter import json_out
from astrobase_cli.utils.http import query_str


class AKSClient:
    def __init__(self):
        astrobase_config = AstrobaseConfig()
        self.url = f"{astrobase_config.current_profile().server}/aks"
        self.kubernetes = Kubernetes(via="az")

    def create(self, cluster: dict) -> None:
        res = requests.post(self.url, json=cluster)
        typer.echo(json_out(res.json()))

    def destroy(self, cluster: dict) -> None:
        cluster_name = cluster.get("name")
        params = {"resource_group_name": cluster.get("resource_group_name")}
        cluster_url = f"{self.url}/{cluster_name}?{query_str(params)}"
        res = requests.delete(cluster_url)
        typer.echo(json_out(res.json()))

    def get_kubernetes_config(self):
        pass

    def apply_kubernetes_resources(
        self,
        kubernetes_resource_location: str,
        cluster_name: str,
        cluster_location: str,
        resource_group_name: str,
        **kwargs,
    ) -> None:
        self.kubernetes.apply(  # pragma: no cover
            kubernetes_resource_location,
            cluster_name,
            cluster_location,
            resource_group_name,
        )

    def destroy_kubernetes_resources(
        self,
        kubernetes_resource_location: str,
        cluster_name: str,
        cluster_location: str,
        resource_group_name: str,
        **kwargs,
    ) -> None:
        self.kubernetes.destroy(  # pragma: no cover
            kubernetes_resource_location,
            cluster_name,
            cluster_location,
            resource_group_name,
        )
