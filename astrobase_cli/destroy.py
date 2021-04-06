from astrobase_cli.clients.eks import EKSClient
from astrobase_cli.clients.gke import GKEClient
from astrobase_cli.schemas.cluster import Clusters
from astrobase_cli.schemas.resource import ResourceList


class Destroy:
    def __init__(self):
        self.clients = {"eks": EKSClient, "gke": GKEClient}

    def destroy_clusters(self, clusters: Clusters) -> None:
        for cluster in clusters.clusters:
            client = self.clients.get(cluster.get("provider"))()
            client.destroy(cluster)

    def destroy_resources(self, resources: ResourceList) -> None:
        for resource in resources.resources:
            client = self.clients.get(resource.provider)()  # pragma: no cover
            client.destroy_kubernetes_resources(  # pragma: no cover
                kubernetes_resource_location=resource.resource_location,
                cluster_name=resource.cluster_name,
                cluster_location=resource.cluster_location,
            )
