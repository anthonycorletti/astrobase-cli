import requests
import typer

from astrobase_cli.clients.kubernetes import Kubernetes
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

    def get_kubernetes_config(self):
        pass

    def apply_kubernetes_resources(
        self,
        kubernetes_resource_location: str,
        cluster_name: str,
        cluster_location: str,
        **kwargs,
    ) -> None:
        self.kubernetes.apply(  # pragma: no cover
            kubernetes_resource_location, cluster_name, cluster_location
        )

    def destroy_kubernetes_resources(
        self,
        kubernetes_resource_location: str,
        cluster_name: str,
        cluster_location: str,
        **kwargs,
    ) -> None:
        self.kubernetes.destroy(  # pragma: no cover
            kubernetes_resource_location, cluster_name, cluster_location
        )
