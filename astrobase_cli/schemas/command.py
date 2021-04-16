from enum import Enum, unique


@unique
class Command(str, Enum):
    az = "az"
    aws = "aws"
    docker = "docker"
    gcloud = "gcloud"
    kubectl = "kubectl"
