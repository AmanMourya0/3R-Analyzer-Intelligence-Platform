"""
Recurrence ORM Model
"""

from sqlalchemy import (
    Column,
    Integer,
    Float,
    Boolean,
    String,
    ForeignKey
)

from app.database.base import Base


class Recurrence(Base):

    __tablename__ = "recurrence_results"

    cluster_id = Column(
        Integer,
        ForeignKey("clusters.cluster_id"),
        primary_key=True
    )

    recurrence_score = Column(Float)

    problem_candidate = Column(Boolean)

    recommendation = Column(String(500))
    