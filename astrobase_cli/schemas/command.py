from enum import Enum, unique


@unique
class Command(str, Enum):
    docker = "docker"
    kubectl = "kubectl"
