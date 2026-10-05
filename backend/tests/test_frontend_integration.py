"""
Frontend Compatibility Integration Tests

Uses SQLite in-memory DB. No PostgreSQL required.
All DB tests share one engine (tables created once at module scope).

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


# ==============================================================
# One shared in-memory SQLite engine for this test module.
# Tables are created ONCE when the module is imported.
# ==============================================================

from app.database.base import Base
from app.database.cluster_model import Cluster
from app.database.incident_model import Incident
from app.database.recurrence_model import Recurrence
from app.database.processing_job_model import ProcessingJob

_ENGINE = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})


@event.listens_for(_ENGINE, "connect")
def _fk(dbapi_conn, _):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA foreign_keys=ON")
    cur.close()


Base.metadata.create_all(_ENGINE)
_SESSION_FACTORY = sessionmaker(autocommit=False, autoflush=False, bind=_ENGINE)


# ==============================================================
# Fixtures
# ==============================================================

@pytest.fixture(autouse=True)
def patch_session_local(monkeypatch):
    """Patch SessionLocal so all service/repository calls use SQLite."""
    from app.database import database as db_module
    from app.services.frontend_compatibility_service import FrontendCompatibilityService
    monkeypatch.setattr(db_module, "SessionLocal", _SESSION_FACTORY)
    
    # Also patch the service's _session method to return a clean session from the factory
    # to avoid issues where it cached the unpatched SessionLocal
    monkeypatch.setattr(FrontendCompatibilityService, "_session", lambda self: _SESSION_FACTORY())
    
    yield


@pytest.fixture
def db():
    """Clean SQLite session per test."""
    session = _SESSION_FACTORY()
    # Clean all tables
    session.query(Recurrence).delete()
    session.query(Incident).delete()
    session.query(Cluster).delete()
    session.query(ProcessingJob).delete()
    session.commit()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def seeded_db(db):
    """Session with clusters, incidents and recurrence seeded."""
    c1 = Cluster(cluster_id=0, cluster_name="VPN Authentication Issues",
                 incident_count=3, top_configuration_item="SAP",
                 top_assignment_group="Network Team", top_region="EMEA", top_priority="P2")
    c2 = Cluster(cluster_id=1, cluster_name="Outlook Crash Issues",
                 incident_count=2, top_configuration_item="Outlook",
                 top_assignment_group="Desktop Team", top_region="APAC", top_priority="P3")
    db.add_all([c1, c2])
    db.flush()

    for i in range(3):
        db.add(Incident(
            incident_number=f"INC{i:06d}", short_description=f"VPN issue {i}",
            description=f"VPN desc {i}", category="Network", subcategory="VPN",
            priority="P2", state="Resolved", assignment_group="Network Team",
            configuration_item="SAP", business_service="IT", region="EMEA",
            created_date=datetime(2026, 1, i+1), resolved_date=datetime(2026, 1, i+2),
            cluster_id=0, three_r_category="RUNNER"
        ))
    for i in range(2):
        db.add(Incident(
            incident_number=f"INC{i+100:06d}", short_description=f"Outlook crash {i}",
            description=f"Outlook crash {i}", category="Application", subcategory="Email",
            priority="P3", state="Resolved", assignment_group="Desktop Team",
            configuration_item="Outlook", business_service="Email", region="APAC",
            created_date=datetime(2026, 2, i+1), resolved_date=None, cluster_id=1,
            three_r_category="REPEATER"
        ))
    db.add(Incident(
        incident_number="INC999999", short_description="Noise",
        description="Unrelated", category="Other", subcategory="",
        priority="P4", state="Open", assignment_group="General IT",
        configuration_item="", business_service="", region="NA",
        created_date=datetime(2026, 3, 1), resolved_date=None, cluster_id=None,
        three_r_category=None
    ))
    db.add(Recurrence(cluster_id=0, recurrence_score=75.0, problem_candidate=True))
    db.add(Recurrence(cluster_id=1, recurrence_score=40.0, problem_candidate=False))
    
    # Update cluster 0 to simulate Phase 2 fields
    c1.three_r_category = "RUNNER"
    c1.three_r_reason = "High volume and velocity."
        
    db.commit()
    yield db


# ==============================================================
# FrontendCompatibilityService tests
# ==============================================================

class TestFrontendCompatibilityService:

    def test_get_health_no_data(self, db):
        from app.services.frontend_compatibility_service import FrontendCompatibilityService
        result = FrontendCompatibilityService().get_health()
        assert result["status"] in ("ok", "error")
        assert "data_loaded" in result

    def test_get_health_with_data(self, seeded_db):
        from app.services.frontend_compatibility_service import FrontendCompatibilityService
        result = FrontendCompatibilityService().get_health()
        assert result["status"] == "ok"
        assert result["data_loaded"] is True

    def test_get_dashboard(self, seeded_db):
        from app.services.frontend_compatibility_service import FrontendCompatibilityService
        result = FrontendCompatibilityService().get_dashboard()
        assert result["total_tickets"] == 6
        assert result["total_clusters"] == 2
        assert result["noise_ticket_count"] == 1
        assert isinstance(result["recurring_issue_percentage"], float)
        assert len(result["top_clusters"]) > 0
        for c in result["top_clusters"]:
            assert "cluster_name" in c
            assert "ticket_count" in c

    def test_get_clusters(self, seeded_db):
        from app.services.frontend_compatibility_service import FrontendCompatibilityService
        result = FrontendCompatibilityService().get_clusters()
        assert "clusters" in result
        assert len(result["clusters"]) == 2
        for c in result["clusters"]:
            assert "cluster_id" in c
            assert "cluster_name" in c
            assert "ci_names" in c

    def test_get_tickets_no_filter(self, seeded_db):
        from app.services.frontend_compatibility_service import FrontendCompatibilityService
        result = FrontendCompatibilityService().get_tickets()
        assert result["total"] == 6
        assert len(result["tickets"]) == 6

    def test_get_tickets_cluster_filter(self, seeded_db):
        from app.services.frontend_compatibility_service import FrontendCompatibilityService
        result = FrontendCompatibilityService().get_tickets(cluster_id=0)
        assert result["total"] == 3
        for t in result["tickets"]:
            assert "ticket_id" in t
            assert "cluster_name" in t

    def test_get_tickets_noise(self, seeded_db):
        from app.services.frontend_compatibility_service import FrontendCompatibilityService
        result = FrontendCompatibilityService().get_tickets(cluster_id=-1)
        assert result["total"] == 1

    def test_get_tickets_category_filter(self, seeded_db):
        from app.services.frontend_compatibility_service import FrontendCompatibilityService
        result = FrontendCompatibilityService().get_tickets(three_r_category="RUNNER")
        assert result["total"] == 3
        for t in result["tickets"]:
            assert t["three_r_category"] == "RUNNER"

    def test_get_tickets_combined_filter(self, seeded_db):
        from app.services.frontend_compatibility_service import FrontendCompatibilityService
        result = FrontendCompatibilityService().get_tickets(cluster_id=0, three_r_category="RUNNER")
        assert result["total"] == 3
        
    def test_get_cluster_detail(self, seeded_db):
        from app.services.frontend_compatibility_service import FrontendCompatibilityService
        result = FrontendCompatibilityService().get_cluster_detail(0)
        assert result is not None
        assert result["cluster_id"] == 0
        assert result["three_r_category"] == "RUNNER"
        assert result["three_r_reason"] == "High volume and velocity."
        assert result["recurrence_score"] == 75.0
        assert result["problem_candidate"] is True
        assert "first_incident_date" in result
        assert "last_incident_date" in result
        assert "active_span_days" in result
        assert "velocity" in result
        assert "sample_tickets" in result
        assert len(result["sample_tickets"]) <= 5
        
    def test_get_cluster_detail_not_found(self, seeded_db):
        from app.services.frontend_compatibility_service import FrontendCompatibilityService
        result = FrontendCompatibilityService().get_cluster_detail(999)
        assert result is None

    def test_get_ci_list(self, seeded_db):
        from app.services.frontend_compatibility_service import FrontendCompatibilityService
        result = FrontendCompatibilityService().get_ci_list()
        assert "ci_list" in result
        for item in result["ci_list"]:
            assert "ci_name" in item
            assert "total_tickets" in item
            assert "recurring_percentage" in item

    def test_get_ci_clusters(self, seeded_db):
        from app.services.frontend_compatibility_service import FrontendCompatibilityService
        result = FrontendCompatibilityService().get_ci_clusters("SAP")
        assert result["ci_name"] == "SAP"
        assert result["total_tickets"] == 3
        assert "clusters" in result

    def test_get_group_list(self, seeded_db):
        from app.services.frontend_compatibility_service import FrontendCompatibilityService
        result = FrontendCompatibilityService().get_group_list()
        assert "group_list" in result
        for item in result["group_list"]:
            assert "group_name" in item
            assert "total_tickets" in item

    def test_get_group_clusters(self, seeded_db):
        from app.services.frontend_compatibility_service import FrontendCompatibilityService
        result = FrontendCompatibilityService().get_group_clusters("Network Team")
        assert result["group_name"] == "Network Team"
        assert result["total_tickets"] == 3
        assert "clusters" in result

    def test_get_status_idle(self, db):
        from app.services.frontend_compatibility_service import FrontendCompatibilityService
        result = FrontendCompatibilityService().get_status()
        assert result["status"] == "idle"


# ==============================================================
# ClusterNamer tests (no DB)
# ==============================================================

class TestClusterNamer:



    def test_format_cluster_name_acronym(self):
        from app.clustering.cluster_namer import _format_cluster_name
        result = _format_cluster_name("vpn authentication")
        assert "VPN" in result
        assert "Issues" in result

    def test_frequency_fallback(self):
        from app.clustering.cluster_namer import _frequency_name
        result = _frequency_name(["network timeout vpn error", "timeout connection failed"])
        assert isinstance(result, str)
        assert "Issues" in result

    def test_name_clusters_sets_cluster_name(self):
        from app.clustering.cluster_namer import ClusterNamer
        from app.models.cluster_summary import ClusterSummary

        summary = ClusterSummary(
            cluster_id=0, incident_count=2,
            top_configuration_item="SAP", top_assignment_group="Net",
            top_region="EMEA", top_priority="P2",
            configuration_item_distribution={"SAP": 2},
            assignment_group_distribution={"Net": 2},
            region_distribution={"EMEA": 2},
            priority_distribution={"P2": 2},
            first_incident_date="2026-01-01",
            last_incident_date="2026-01-31",
        )
        namer = ClusterNamer()
        result = namer.name_clusters(
            [summary], ["vpn connection failed", "vpn auth error"], [0, 0]
        )
        assert result[0].cluster_name != ""
        assert "Issues" in result[0].cluster_name


# ==============================================================
# ClusterRepository with cluster_name
# ==============================================================

class TestClusterRepositoryClusterName:

    def test_save_with_cluster_name(self, db):
        from app.models.cluster_summary import ClusterSummary
        from app.repositories.cluster_repository import ClusterRepository

        summary = ClusterSummary(
            cluster_id=99, cluster_name="VPN Authentication Issues",
            incident_count=5, top_configuration_item="SAP",
            top_assignment_group="Network", top_region="EMEA", top_priority="P2",
            configuration_item_distribution={"SAP": 5},
            assignment_group_distribution={"Network": 5},
            region_distribution={"EMEA": 5},
            priority_distribution={"P2": 5},
            first_incident_date="2026-01-01", last_incident_date="2026-01-31",
        )
        repo = ClusterRepository(db)
        repo.save([summary])
        db.commit()

        saved = db.query(Cluster).filter_by(cluster_id=99).one()
        assert saved.cluster_name == "VPN Authentication Issues"

    def test_save_without_name_defaults_empty(self, db):
        from app.models.cluster_summary import ClusterSummary
        from app.repositories.cluster_repository import ClusterRepository

        summary = ClusterSummary(
            cluster_id=98, incident_count=2,
            top_configuration_item="Test", top_assignment_group="TestGrp",
            top_region="NA", top_priority="P3",
            configuration_item_distribution={"Test": 2},
            assignment_group_distribution={"TestGrp": 2},
            region_distribution={"NA": 2},
            priority_distribution={"P3": 2},
            first_incident_date="2026-01-01", last_incident_date="2026-01-31",
        )
        repo = ClusterRepository(db)
        repo.save([summary])
        db.commit()

        saved = db.query(Cluster).filter_by(cluster_id=98).one()
        assert saved.cluster_name in ("", None)

    def test_save_with_three_r_reason(self, db):
        from app.models.cluster_summary import ClusterSummary
        from app.repositories.cluster_repository import ClusterRepository

        summary = ClusterSummary(
            cluster_id=97, cluster_name="Test Reason",
            incident_count=1, top_configuration_item="Test",
            top_assignment_group="TestGrp", top_region="NA", top_priority="P3",
            configuration_item_distribution={}, assignment_group_distribution={},
            region_distribution={}, priority_distribution={},
            first_incident_date="2026-01-01", last_incident_date="2026-01-31",
        )
        summary.three_r_category = "RUNNER"
        summary.three_r_reason = "Test rule triggered"
        
        repo = ClusterRepository(db)
        repo.save([summary])
        db.commit()

        saved = db.query(Cluster).filter_by(cluster_id=97).one()
        assert saved.three_r_category == "RUNNER"
        assert saved.three_r_reason == "Test rule triggered"
