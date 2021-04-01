from enum import Enum, unique


@unique
class Command(str, Enum):
    aws = "aws"
    gcloud = "gcloud"
    kubectl = "kubectl"
