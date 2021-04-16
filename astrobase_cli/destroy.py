import tempfile

from astrobase_cli.clients.aks import AKSClient
from astrobase_cli.clients.eks import EKSClient
from astrobase_cli.clients.gke import GKEClient
from astrobase_cli.schemas.cluster import Clusters
from astrobase_cli.schemas.resource import ResourceList
from astrobase_cli.utils.params import YamlParams


class Destroy:
    def __init__(self):
        self.clients = {"eks": EKSClient, "gke": GKEClient, "aks": AKSClient}

    def destroy_clusters(self, clusters: Clusters) -> None:
        for cluster in clusters.clusters:
            client = self.clients.get(cluster.get("provider"))()
            client.destroy(cluster)

    def destroy_resources(self, resources: ResourceList, params: YamlParams) -> None:
        for resource in resources.resources:
            temp_dir = tempfile.TemporaryDirectory()
            params.template_resource_files(  # pragma: no cover
                src_dir=resource.resource_location,
                dst_dir=temp_dir.name,
            )
            client = self.clients.get(resource.provider)()  # pragma: no cover
            client.destroy_kubernetes_resources(  # pragma: no cover
                kubernetes_resource_location=temp_dir.name, **resource.dict()
            )
            temp_dir.cleanup()
