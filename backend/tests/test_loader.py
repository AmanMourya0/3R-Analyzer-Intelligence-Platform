"""
Tests for incident loading and preprocessing.
"""

from app.constants import COMBINED_TEXT
from app.services.incident_loader import IncidentLoader
from app.services.preprocessing import Preprocessor


def test_loader_reads_csv_and_preprocessor_adds_combined_text(tmp_path):
    dataset = tmp_path / "incidents.csv"
    dataset.write_text(
        "\n".join(
            [
                "Incident Number,Short Description,Description,Category,Subcategory,"
                "Priority,State,Assignment Group,Configuration Item (Application),"
                "Business Service,Region,Created Date,Resolved Date,Resolution Notes,"
                "Problem Candidate",
                "INC001,Email Down,Mail unavailable,Software,Email,P2,Closed,"
                "Messaging,Exchange,Collaboration,NA,2026-01-01,2026-01-01,"
                "Fixed,False",
            ]
        ),
        encoding="utf-8"
    )

    dataframe = IncidentLoader(str(dataset)).load()
    cleaned = Preprocessor().clean(dataframe)

    assert len(cleaned) == 1
    assert COMBINED_TEXT in cleaned.columns
    assert "email down" in cleaned.loc[0, COMBINED_TEXT]
