from typing import List, Optional

from pydantic import BaseModel


class Resource(BaseModel):
    name: str
    provider: str
    cluster_name: str
    cluster_location: str
    resource_location: str
    resource_group_name: Optional[str]


class ResourceList(BaseModel):
    resources: List[Resource] = []
