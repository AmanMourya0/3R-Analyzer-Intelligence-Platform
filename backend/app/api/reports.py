"""Download the current processed analytical snapshot as CSV."""

import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.incident_model import Incident

router = APIRouter(prefix="/reports", tags=["Reports"])


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@router.get("/current")
def download_current_report(session: Session = Depends(get_session)) -> StreamingResponse:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Incident Number", "Short Description", "Priority", "Assignment Group", "Configuration Item", "Region", "Created Date", "Cluster ID"])
    for incident in session.query(Incident).order_by(Incident.created_date.desc()).all():
        writer.writerow([incident.incident_number, incident.short_description, incident.priority, incident.assignment_group, incident.configuration_item, incident.region, incident.created_date, incident.cluster_id])
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=3r-analyzer-report.csv"})
