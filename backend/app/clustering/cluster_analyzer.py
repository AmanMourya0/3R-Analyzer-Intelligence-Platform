"""
Cluster Analysis Module

Analyzes semantic clusters and generates
business-friendly summaries.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from typing import List

import pandas as pd

from app.constants import (
    CLUSTER_ID,
    CONFIGURATION_ITEM,
    ASSIGNMENT_GROUP,
    REGION,
    PRIORITY,
    CREATED_DATE,
    NOISE_CLUSTER
)

from app.models.cluster_summary import ClusterSummary
from app.utils.logger import logger


class ClusterAnalyzer:
    """
    Analyze generated semantic clusters.
    """

    def analyze(
        self,
        dataframe: pd.DataFrame
    ) -> List[ClusterSummary]:
        """
        Generate summaries for each semantic cluster.

        Parameters
        ----------
        dataframe : pd.DataFrame

        Returns
        -------
        List[ClusterSummary]
        """

        logger.info("Analyzing semantic clusters...")

        summaries: List[ClusterSummary] = []

        # Ignore HDBSCAN noise
        clustered_df = dataframe[
            dataframe[CLUSTER_ID] != NOISE_CLUSTER
        ]

        for cluster_id, cluster in clustered_df.groupby(CLUSTER_ID):

            summary = ClusterSummary(

                cluster_id=int(cluster_id),

                incident_count=len(cluster),

                top_configuration_item=cluster[
                    CONFIGURATION_ITEM
                ].mode().iat[0],

                top_assignment_group=cluster[
                    ASSIGNMENT_GROUP
                ].mode().iat[0],

                top_region=cluster[
                    REGION
                ].mode().iat[0],

                top_priority=cluster[
                    PRIORITY
                ].mode().iat[0],

                configuration_item_distribution=cluster[
                    CONFIGURATION_ITEM
                ].value_counts().to_dict(),

                assignment_group_distribution=cluster[
                    ASSIGNMENT_GROUP
                ].value_counts().to_dict(),

                region_distribution=cluster[
                    REGION
                ].value_counts().to_dict(),

                priority_distribution=cluster[
                    PRIORITY
                ].value_counts().to_dict(),

                first_incident_date=str(
                    cluster[CREATED_DATE].min()
                ),

                last_incident_date=str(
                    cluster[CREATED_DATE].max()
                )

            )

            summaries.append(summary)

        logger.info(
            "Generated summaries for %d clusters.",
            len(summaries)
        )

        return summaries