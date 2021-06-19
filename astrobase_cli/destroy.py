import tempfile
from typing import Callable, Dict

from astrobase_cli.clients.aks import AKSClient
from astrobase_cli.clients.eks import EKSClient
from astrobase_cli.clients.gke import GKEClient
from astrobase_cli.schemas.cluster import Clusters
from astrobase_cli.schemas.resource import ResourceList
from astrobase_cli.utils.params import YamlParams


class Destroy:
    def __init__(self) -> None:
        self.clients: Dict[str, Callable] = {
            "eks": lambda: EKSClient,
            "gke": lambda: GKEClient,
            "aks": lambda: AKSClient,
        }

    def destroy_clusters(self, clusters: Clusters) -> None:
        for cluster in clusters.clusters:
            provider = cluster.get("provider")
            if provider is None:
                raise ValueError(f"Missing provider for cluster {cluster.get('name')}")
            client = self.clients[provider]()
            client_instance = client()
            client_instance.destroy(cluster)

    def destroy_resources(self, resources: ResourceList, params: YamlParams) -> None:
        for resource in resources.resources:
            temp_dir = tempfile.TemporaryDirectory()
            params.template_resource_files(  # pragma: no cover
                src_dir=resource.resource_location,
                dst_dir=temp_dir.name,
            )
            provider = self.clients.get(resource.provider)
            if provider is None:
                raise ValueError(
                    f"Missing resource provider for resource: {resource.name}"
                )
            client = provider()
            client_instance = client()
            client_instance.destroy_kubernetes_resources(  # pragma: no cover
                kubernetes_resource_location=temp_dir.name, **resource.dict()
            )
            temp_dir.cleanup()
