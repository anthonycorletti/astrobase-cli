from typing import List, Union

from pydantic import BaseModel


class Resource(BaseModel):
    name: str
    provider: str
    cluster_name: str
    cluster_location: str
    resource_location: str


class GKEResource(Resource):
    project_id: str


class EKSResource(Resource):
    pass


class AKSResource(Resource):
    resource_group_name: str


class ResourceList(BaseModel):
    resources: List[Union[GKEResource, EKSResource, AKSResource]] = []
