"""
Incident ORM Model
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)

from app.database.base import Base


class Incident(Base):

    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)

    incident_number = Column(String(50), unique=True, nullable=False)

    short_description = Column(Text)

    description = Column(Text)

    category = Column(String(100))

    subcategory = Column(String(100))

    priority = Column(String(10))

    state = Column(String(50))

    assignment_group = Column(String(150))

    configuration_item = Column(String(150))

    business_service = Column(String(150))

    region = Column(String(100))

    created_date = Column(DateTime)

    resolved_date = Column(DateTime)

    cluster_id = Column(
        Integer,
        ForeignKey("clusters.cluster_id"),
        nullable=True
    )

    three_r_category = Column(String(20), nullable=True, index=True)

    semantic_match_cluster_id = Column(Integer, nullable=True)