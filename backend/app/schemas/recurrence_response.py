"""
Recurrence Response Schema
"""

from pydantic import BaseModel
from pydantic import ConfigDict


class RecurrenceResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    cluster_id: int

    recurrence_score: float

    problem_candidate: bool

    recommendation: str