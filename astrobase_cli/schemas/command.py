from enum import Enum, unique


@unique
class Command(str, Enum):
    aws = "aws"
    docker = "docker"
    gcloud = "gcloud"
    kubectl = "kubectl"