"""
Domain model representing a semantic cluster.

This is a business/domain model and NOT a database model.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass(slots=True)
class ClusterSummary:
    """
    Represents one semantic cluster.
    """

    # Basic Information
    cluster_id: int

    incident_count: int

    # Cluster Metadata
    top_configuration_item: str

    top_assignment_group: str

    top_region: str

    top_priority: str

    # Distribution Information
    configuration_item_distribution: Dict[str, int]

    assignment_group_distribution: Dict[str, int]

    region_distribution: Dict[str, int]

    priority_distribution: Dict[str, int]

    # Date Information
    first_incident_date: str

    last_incident_date: str

    # Human-readable cluster name (populated by ClusterNamer after ClusterAnalyzer)
    cluster_name: str = ""

    # 3R Classification
    three_r_category: str = ""
    three_r_reason: str = ""
