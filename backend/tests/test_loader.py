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
                "Number,Caller,Assignment Group,Created,Short description,Category,Priority,State,Assigned to,Resolved by,Resolved,KB Number,IT Batch Job,Description,Reassignment Count,Configuration item,Offending CI,Offending CI Category",
                "INC001,Alice,Messaging,2026-01-01,Email Down,Software,P2,Closed,Bob,Bob,2026-01-01,, ,Mail unavailable,0,Exchange,Exchange Server,Hardware",
            ]
        ),
        encoding="utf-8"
    )

    dataframe = IncidentLoader(str(dataset)).load()
    cleaned = Preprocessor().clean(dataframe)

    assert len(cleaned) == 1
    assert COMBINED_TEXT in cleaned.columns
    assert "email down" in cleaned.loc[0, COMBINED_TEXT]
