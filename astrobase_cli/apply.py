import tempfile
from typing import Callable, Dict

from astrobase_cli.clients.aks import AKSClient
from astrobase_cli.clients.eks import EKSClient
from astrobase_cli.clients.gke import GKEClient
from astrobase_cli.schemas.cluster import Clusters
from astrobase_cli.schemas.resource import (
    AKSResource,
    EKSResource,
    GKEResource,
    ResourceList,
)
from astrobase_cli.utils.params import YamlParams


class Apply:
    def __init__(self) -> None:
        self.clients: Dict[str, Callable] = {
            "eks": lambda: EKSClient,
            "gke": lambda: GKEClient,
            "aks": lambda: AKSClient,
        }
        self.client_resources: Dict = {
            "eks": EKSResource,
            "gke": GKEResource,
            "aks": AKSResource,
        }

    def apply_clusters(self, clusters: Clusters) -> None:
        for cluster in clusters.clusters:
            provider = cluster.get("provider")
            if provider is None:
                raise ValueError(f"Missing provider for cluster {cluster.get('name')}")
            client = self.clients[provider]()
            client_instance = client()
            client_instance.create(cluster)

    def apply_resources(self, resources: ResourceList, params: YamlParams) -> None:
        for resource in resources.resources:
            temp_dir = tempfile.TemporaryDirectory()
            params.template_resource_files(
                src_dir=resource.resource_location,
                dst_dir=temp_dir.name,
            )
            resource.resource_location = temp_dir.name
            provider = self.clients.get(resource.provider)
            if provider is None:
                raise ValueError(
                    f"Missing resource provider ({resource.provider})"
                    f" for resource: {resource.name}"
                )
            if resource.provider not in self.client_resources.keys():
                raise ValueError(
                    f"Missing resource schema ({resource.provider})"
                    f" for resource: {resource.name}"
                )
            client = provider()
            client_instance = client()
            client_resource = self.client_resources[resource.provider](
                **resource.dict()
            )
            client_instance.apply_kubernetes_resources(client_resource)
            temp_dir.cleanup()
