"""
Cluster Response Schema
"""

from pydantic import BaseModel
from pydantic import ConfigDict


class ClusterResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    cluster_id: int

    incident_count: int

    top_configuration_item: str

    top_assignment_group: str

    top_region: str

    top_priority: str