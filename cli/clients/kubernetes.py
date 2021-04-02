import sys
from contextlib import contextmanager
from typing import Iterator

import typer
from kubernetes import client, config
from sh import aws, gcloud, kubectl


class Kubernetes:
    def __init__(self, via: str):
        self.via = via

    @contextmanager
    def kube_api_client(self) -> Iterator[None]:
        config.load_kube_config()
        yield client.ApiClient()

    def get_kubeconfig_via_gcloud(
        self, cluster_name: str, cluster_location: str
    ) -> None:
        gcloud(
            "container",
            "clusters",
            "get-credentials",
            cluster_name,
            "--region",
            cluster_location,
        )

    def get_kubeconfig_via_aws(self, cluster_name: str, cluster_location: str) -> None:
        aws(
            "eks",
            "update-kubeconfig",
            "--name",
            cluster_name,
            "--region",
            cluster_location,
        )

    def get_kubeconfig(self, cluster_name: str, cluster_location: str) -> None:
        if self.via == "gcloud":
            self.get_kubeconfig_via_gcloud(cluster_name, cluster_location)
        elif self.via == "aws":
            self.get_kubeconfig_via_aws(cluster_name, cluster_location)
        else:
            typer.echo(f"Encountered unsupported command, {self.via}.")
            raise typer.Exit(1)

    def apply(
        self,
        kubernetes_resource_location: str,
        cluster_name: str,
        cluster_location: str,
    ) -> None:
        self.get_kubeconfig(cluster_name, cluster_location)
        typer.echo(f"applying resources to {cluster_name}@{cluster_location}")
        with self.kube_api_client() as kube_api_client:
            if not kube_api_client:
                typer.echo("no kubernetes api client provisioned")
                raise typer.Exit(1)
            kubectl("apply", "-f", f"{kubernetes_resource_location}", _out=sys.stdout)

    def destroy(
        self,
        kubernetes_resource_location: str,
        cluster_name: str,
        cluster_location: str,
    ) -> None:
        self.get_kubeconfig(cluster_name, cluster_location)
        typer.echo(f"destroying resources in {cluster_name}@{cluster_location}")
        with self.kube_api_client() as kube_api_client:
            if not kube_api_client:
                typer.echo("no kubernetes api client provisioned")
                raise typer.Exit(1)
            kubectl("delete", "-f", f"{kubernetes_resource_location}", _out=sys.stdout)
