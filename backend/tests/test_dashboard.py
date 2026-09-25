from app.database.database import SessionLocal
from app.services.dashboard_service import DashboardService


def test_dashboard_service():

    session = SessionLocal()

    service = DashboardService(session)

    dashboard = service.get_dashboard()

    assert dashboard is not None

    assert dashboard.summary.total_incidents >= 0

    assert dashboard.summary.total_clusters >= 0

    session.close()