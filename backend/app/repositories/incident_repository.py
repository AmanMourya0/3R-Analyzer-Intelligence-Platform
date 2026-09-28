"""
Incident Repository

Responsible only for persisting Incident records.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from typing import List

import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.constants import (
    INCIDENT_NUMBER,
    SHORT_DESCRIPTION,
    DESCRIPTION,
    CATEGORY,
    SUBCATEGORY,
    PRIORITY,
    STATE,
    ASSIGNMENT_GROUP,
    CONFIGURATION_ITEM,
    BUSINESS_SERVICE,
    REGION,
    CREATED_DATE,
    RESOLVED_DATE,
    CLUSTER_ID,
    THREE_R_CATEGORY,
    SEMANTIC_MATCH_CLUSTER_ID
)
from app.database.incident_model import Incident
from app.repositories.repository_interface import RepositoryInterface
from app.utils.logger import logger


class IncidentRepository(RepositoryInterface):
    """
    Repository responsible for Incident persistence.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, dataframe: pd.DataFrame) -> None:
        """
        Persist processed incidents into PostgreSQL.

        Parameters
        ----------
        dataframe : pd.DataFrame
            Processed dataframe containing cluster assignments.
        """
        try:
            logger.info("Persisting %d incidents...", len(dataframe))

            incident_records: List[Incident] = []

            def _parse_dt(val):
                if val is None or pd.isna(val) or str(val).strip() == "":
                    return None
                try:
                    return pd.to_datetime(val).to_pydatetime()
                except Exception:
                    return None

            def _to_str(val):
                if val is None or pd.isna(val):
                    return None
                s = str(val).strip()
                return s if s else None

            for _, row in dataframe.iterrows():
                cid = row.get(CLUSTER_ID)
                cluster_id_val = None
                if cid is not None and not pd.isna(cid):
                    try:
                        cid_int = int(cid)
                        if cid_int != -1:
                            cluster_id_val = cid_int
                    except (ValueError, TypeError):
                        pass

                incident_records.append(
                    Incident(
                        incident_number=_to_str(row.get(INCIDENT_NUMBER)),
                        caller=_to_str(row.get("caller")),
                        short_description=_to_str(row.get(SHORT_DESCRIPTION)),
                        description=_to_str(row.get(DESCRIPTION)),
                        category=_to_str(row.get(CATEGORY)),
                        subcategory=_to_str(row.get(SUBCATEGORY)),
                        priority=_to_str(row.get(PRIORITY)),
                        state=_to_str(row.get(STATE)),
                        assignment_group=_to_str(row.get(ASSIGNMENT_GROUP)),
                        assigned_to=_to_str(row.get("assigned_to")),
                        resolved_by=_to_str(row.get("resolved_by")),
                        configuration_item=_to_str(row.get(CONFIGURATION_ITEM)),
                        offending_ci=_to_str(row.get("offending_ci")),
                        offending_ci_category=_to_str(row.get("offending_ci_category")),
                        business_service=_to_str(row.get(BUSINESS_SERVICE)),
                        region=_to_str(row.get(REGION)),
                        created_date=_parse_dt(row.get(CREATED_DATE)),
                        resolved_date=_parse_dt(row.get(RESOLVED_DATE)),
                        kb_number=_to_str(row.get("kb_number")),
                        it_batch_job=_to_str(row.get("it_batch_job")),
                        reassignment_count=int(row.get("reassignment_count")) if pd.notna(row.get("reassignment_count")) and str(row.get("reassignment_count")).strip() != "" else None,
                        cluster_id=cluster_id_val,
                        three_r_category=_to_str(row.get(THREE_R_CATEGORY)),
                        semantic_match_cluster_id=row.get(SEMANTIC_MATCH_CLUSTER_ID) if not pd.isna(row.get(SEMANTIC_MATCH_CLUSTER_ID)) else None
                    )
                )

            self.session.bulk_save_objects(incident_records)

            logger.info(
                "Successfully persisted %d incidents.",
                len(incident_records)
            )

        except Exception:
            logger.exception("Failed to persist incidents.")
            raise

    def get_total_incidents(self) -> int:
        """Return the total number of processed incidents."""

        try:

            return (
                self.session.query(func.count(Incident.id))
                .scalar()
                or 0
            )

        except Exception:

            logger.exception(
                "Unable to fetch total incidents."
            )

            raise


    def get_incidents_by_cluster(
        self,
        cluster_id: int
    ) -> int:
        """
        Return number of incidents for a cluster.
        """

        try:

            return (

                self.session.query(func.count(Incident.id))

                .filter(
                    Incident.cluster_id == cluster_id
                )

                .scalar()

                or 0

            )

        except Exception:

            logger.exception(
                "Unable to fetch incident count."
            )

            raise

    def get_average_cluster_size(self) -> float:
        """
        Return average number of incidents per non-noise cluster.
        """

        try:

            cluster_counts = (
                self.session.query(
                    Incident.cluster_id,
                    func.count(Incident.id).label("incident_count")
                )
                .filter(Incident.cluster_id.is_not(None))
                .group_by(Incident.cluster_id)
                .subquery()
            )

            value = (
                self.session.query(
                    func.avg(cluster_counts.c.incident_count)
                )
                .scalar()
            )

            return round(float(value), 2) if value else 0.0

        except Exception:

            logger.exception(
                "Unable to fetch average cluster size."
            )

            raise

    def delete_all(self) -> None:
        """
        Delete all processed incidents.
        """

        try:

            deleted = self.session.query(Incident).delete()

            logger.info(
            "Deleted %d incident records.",
            deleted
            )

        except Exception:

            logger.exception(
                "Unable to delete incidents."
            )

            raise
