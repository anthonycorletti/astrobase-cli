from pydantic import BaseModel


class GKEKubernetesCredentials(BaseModel):
    endpoint: str
    ca_path: str
    token: str
