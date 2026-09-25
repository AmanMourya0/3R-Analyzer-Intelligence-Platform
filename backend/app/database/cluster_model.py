"""
Cluster ORM Model
"""

from sqlalchemy import (
    Column,
    Integer,
    String
)

from app.database.base import Base


class Cluster(Base):

    __tablename__ = "clusters"

    cluster_id = Column(
        Integer,
        primary_key=True
    )

    cluster_name = Column(String(300), nullable=True)

    incident_count = Column(Integer)

    top_configuration_item = Column(String(200))

    top_assignment_group = Column(String(200))

    top_region = Column(String(100))

    top_priority = Column(String(20))

    three_r_category = Column(String(20), nullable=True)

    three_r_reason = Column(String(300), nullable=True)
