import requests
import typer

from cli.clients.kubernetes import Kubernetes
from cli.utils.config import AstrobaseConfig
from cli.utils.formatter import json_out

astrobase_config = AstrobaseConfig()


class EKSClient:
    def __init__(self):
        server = astrobase_config.current_profile.server
        self.url = f"{server}/eks"
        self.kubernetes = Kubernetes(via="aws")

    def create(self, cluster: dict) -> None:
        for nodegroup in cluster.get("nodegroups", []):
            nodegroup["clusterName"] = cluster.get("name")
            nodegroup["subnets"] = cluster.get("resourcesVpcConfig", {}).get(
                "subnetIds", []
            )
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
