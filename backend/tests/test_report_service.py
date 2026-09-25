import pytest
import io
import csv
from datetime import datetime
from app.services.report_service import report_service
from app.database.incident_model import Incident
from app.database.cluster_model import Cluster
from app.database.recurrence_model import Recurrence

@pytest.fixture
def populated_db(db_session):
    # Add clusters
    c1 = Cluster(cluster_id=999, cluster_name="Test Cluster 1", three_r_category="RUNNER", incident_count=5)
    c2 = Cluster(cluster_id=1000, cluster_name="Test Cluster 2", three_r_category="REPEATER", incident_count=3)
    db_session.add(c1)
    db_session.add(c2)
    db_session.flush()

    # Add recurrences
    r1 = Recurrence(cluster_id=999, problem_candidate=True)
    r2 = Recurrence(cluster_id=1000, problem_candidate=False)
    db_session.add(r1)
    db_session.add(r2)

    # Add incidents
    for i in range(5):
        inc = Incident(
            incident_number=f"INC999{i}",
            short_description="Test",
            priority="P1",
            state="New",
            cluster_id=999,
            three_r_category="RUNNER",
            created_date=datetime.utcnow()
        )
        db_session.add(inc)

    for i in range(5, 8):
        inc = Incident(
            incident_number=f"INC1000{i}",
            short_description="Test 2",
            priority="P2",
            state="New",
            cluster_id=1000,
            three_r_category="REPEATER",
            created_date=datetime.utcnow()
        )
        db_session.add(inc)
    
    db_session.flush()

def test_export_tickets_csv(db_session, populated_db):
    csv_bytes = report_service.export_tickets_csv()
    content = csv_bytes.decode('utf-8-sig')
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    
    # Check metadata exists
    assert rows[0][0] == "# REPORT METADATA"
    assert rows[2][0] == "# Total Dataset Size"
    assert rows[3][0] == "# Records Exported"
    
    # Check headers
    headers = rows[7]
    assert headers[0] == "Incident Number"
    assert "Problem Candidate" in headers
    
    # Check data rows
    assert len(rows) >= 16

def test_export_tickets_csv_with_filter(db_session, populated_db):
    # RUNNER filter
    filter_json = '{"logic":"AND","conditions":[{"field":"three_r_category","operator":"eq","value":"RUNNER"}]}'
    csv_bytes = report_service.export_tickets_csv(filter_json=filter_json)
    content = csv_bytes.decode('utf-8-sig')
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    
    assert rows[3][1] == "5" # 5 runners exported

def test_export_clusters_csv(db_session, populated_db):
    csv_bytes = report_service.export_clusters_csv()
    content = csv_bytes.decode('utf-8-sig')
    assert "Cluster ID" in content
    assert "Recurrence Score" in content

def test_export_3r_summary_csv(db_session, populated_db):
    csv_bytes = report_service.export_3r_summary_csv()
    content = csv_bytes.decode('utf-8-sig')
    assert "Runner" in content
    assert "Repeater" in content
    assert "Rare" in content
    
def test_executive_report_pdf(db_session, populated_db):
    pdf_bytes = report_service.generate_executive_report_pdf()
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 1000

def test_executive_report_pdf_filtered(db_session, populated_db):
    filter_json = '{"logic":"AND","conditions":[{"field":"priority","operator":"eq","value":"P1"}]}'
    pdf_bytes = report_service.generate_executive_report_pdf(filter_json=filter_json)
    assert pdf_bytes.startswith(b"%PDF-")
