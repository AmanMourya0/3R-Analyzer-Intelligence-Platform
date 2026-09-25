"""Read-only analytics endpoints over the current processed snapshot."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.cluster_model import Cluster
from app.database.database import SessionLocal
from app.database.incident_model import Incident

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@router.get("/clusters")
def clusters(session: Session = Depends(get_session)) -> list[dict]:
    rows = session.query(Cluster).order_by(Cluster.incident_count.desc()).all()
    return [{
        "cluster_id": item.cluster_id,
        "incident_count": item.incident_count,
        "configuration_item": item.top_configuration_item,
        "assignment_group": item.top_assignment_group,
        "region": item.top_region,
        "priority": item.top_priority,
    } for item in rows]


@router.get("/incidents")
def incidents(session: Session = Depends(get_session), limit: int = 500) -> list[dict]:
    rows = session.query(Incident).order_by(Incident.created_date.desc()).limit(min(limit, 1000)).all()
    return [{
        "incident_number": item.incident_number,
        "short_description": item.short_description,
        "priority": item.priority,
        "assignment_group": item.assignment_group,
        "configuration_item": item.configuration_item,
        "region": item.region,
        "created_date": item.created_date,
        "cluster_id": item.cluster_id,
    } for item in rows]


@router.get("/configuration-items")
def configuration_items(session: Session = Depends(get_session)) -> list[dict]:
    return _grouped_incidents(session, Incident.configuration_item, "configuration_item")


@router.get("/assignment-groups")
def assignment_groups(session: Session = Depends(get_session)) -> list[dict]:
    return _grouped_incidents(session, Incident.assignment_group, "assignment_group")


def _grouped_incidents(session: Session, column, key: str) -> list[dict]:
    from sqlalchemy import func
    rows = session.query(column, func.count(Incident.id)).group_by(column).order_by(func.count(Incident.id).desc()).all()
    return [{key: value or "Unassigned", "incident_count": count} for value, count in rows]
