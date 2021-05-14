import base64
import sys
from tempfile import NamedTemporaryFile

import google.auth
import google.auth.transport.requests
from google.cloud import container_v1
from kubernetes import client as kubernetes_client
from sh import kubectl


def check_k8s_client():
    project_id = "astrobase-284118"
    zone = "us-central1-c"
    cluster_id = "astrobase-test-gke"
    print("Attempting to init k8s client from cluster response.")
    container_client = container_v1.ClusterManagerClient()
    response = container_client.get_cluster(
        cluster_id=cluster_id, zone=zone, project_id=project_id
    )
    credentials, project = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    creds, projects = google.auth.default()
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    configuration = kubernetes_client.Configuration()
    configuration.host = f"https://{response.endpoint}"
    with NamedTemporaryFile(delete=False) as ca_cert:
        ca_cert.write(base64.b64decode(response.master_auth.cluster_ca_certificate))
        kubectl(
            "get",
            "po",
            "-A",
            "--server",
            f"https://{response.endpoint}",
            "--certificate-authority",
            f"{ca_cert.name}",
            "--token",
            f"{creds.token}",
            _out=sys.stdout,
        )
    # configuration.ssl_ca_cert = ca_cert.name
    # configuration.api_key_prefix["authorization"] = "Bearer"
    # configuration.api_key["authorization"] = creds.token


check_k8s_client()
