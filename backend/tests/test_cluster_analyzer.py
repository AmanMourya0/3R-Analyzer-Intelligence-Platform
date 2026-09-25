"""
Tests for cluster summary generation.
"""

import pandas as pd

from app.clustering.cluster_analyzer import ClusterAnalyzer
from app.constants import (
    ASSIGNMENT_GROUP,
    CATEGORY,
    CLUSTER_ID,
    CONFIGURATION_ITEM,
    CREATED_DATE,
    DESCRIPTION,
    PRIORITY,
    REGION,
    SHORT_DESCRIPTION,
    SUBCATEGORY,
)


def test_cluster_analyzer_ignores_noise_cluster():
    dataframe = pd.DataFrame(
        {
            SHORT_DESCRIPTION: ["email down", "email outage", "vpn slow"],
            DESCRIPTION: ["mail unavailable", "mail failure", "vpn latency"],
            CATEGORY: ["software", "software", "network"],
            SUBCATEGORY: ["email", "email", "vpn"],
            CONFIGURATION_ITEM: ["Exchange", "Exchange", "VPN"],
            ASSIGNMENT_GROUP: ["Messaging", "Messaging", "Network"],
            REGION: ["NA", "NA", "EU"],
            PRIORITY: ["P2", "P2", "P4"],
            CREATED_DATE: pd.to_datetime(
                ["2026-01-01", "2026-01-02", "2026-01-03"]
            ),
            CLUSTER_ID: [0, 0, -1],
        }
    )

    summaries = ClusterAnalyzer().analyze(dataframe)

    assert len(summaries) == 1
    assert summaries[0].cluster_id == 0
    assert summaries[0].incident_count == 2
    assert summaries[0].top_configuration_item == "Exchange"
