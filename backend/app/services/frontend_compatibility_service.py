"""
Frontend Compatibility Service

Translates production domain structures into the response shapes
expected by the Friend frontend. Coordinates existing production
repositories and services.

Responsibilities:
- Field name mapping (production -> frontend)
- Analytics aggregation for frontend pages
- Dashboard adapter
- Cluster adapter
- Ticket adapter
- CI adapter
- Group adapter
- Status adapter

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import SessionLocal
from app.database.incident_model import Incident
from app.database.cluster_model import Cluster
from app.database.recurrence_model import Recurrence
from app.database.processing_job_model import ProcessingJob
import json
import math
from app.schemas.filter_ast import FilterGroup, SortRule
from app.services.query_builder import build_filter_expression, apply_sorting, has_cluster_field, has_recurrence_field
from app.repositories.job_repository import JobRepository
from app.constants import JOB_STATUS_COMPLETED, JOB_STATUS_FAILED

logger = logging.getLogger(__name__)


class FrontendCompatibilityService:
    """
    Translates production data into frontend-compatible response shapes.
    Uses short-lived sessions per query to avoid stale data.
    """

    def _session(self) -> Session:
        return SessionLocal()

    # ==================================================================
    # DASHBOARD
    # ==================================================================

    def get_dashboard(self) -> Dict[str, Any]:
        """
        Return dashboard data in the shape expected by Dashboard.jsx.
        """
        session = self._session()
        try:
            total_incidents = (
                session.query(func.count(Incident.id)).scalar() or 0
            )
            total_clusters = (
                session.query(func.count(Cluster.cluster_id)).scalar() or 0
            )
            # noise = incidents with no cluster assignment
            noise_count = (
                session.query(func.count(Incident.id))
                .filter(Incident.cluster_id.is_(None))
                .scalar() or 0
            )
            # recurring = incidents that belong to a cluster (for compatibility)
            recurring_count = total_incidents - noise_count
            recurring_pct = (
                round((recurring_count / total_incidents) * 100, 1)
                if total_incidents > 0 else 0
            )

            # 3R Metrics
            runner_count = (
                session.query(func.count(Incident.id))
                .filter(Incident.three_r_category == "RUNNER")
                .scalar() or 0
            )
            repeater_count = (
                session.query(func.count(Incident.id))
                .filter(Incident.three_r_category == "REPEATER")
                .scalar() or 0
            )
            rare_count = (
                session.query(func.count(Incident.id))
                .filter(Incident.three_r_category == "RARE")
                .scalar() or 0
            )
            
            runner_pct = round((runner_count / total_incidents) * 100, 1) if total_incidents > 0 else 0
            repeater_pct = round((repeater_count / total_incidents) * 100, 1) if total_incidents > 0 else 0
            rare_pct = round((rare_count / total_incidents) * 100, 1) if total_incidents > 0 else 0

            # Top clusters ordered by incident count descending
            top_cluster_rows = (
                session.query(Cluster)
                .order_by(Cluster.incident_count.desc())
                .limit(10)
                .all()
            )

            top_clusters = []
            for c in top_cluster_rows:
                name = c.cluster_name or f"Cluster {c.cluster_id}"
                # Sample tickets for this cluster
                sample_incidents = (
                    session.query(Incident)
                    .filter(Incident.cluster_id == c.cluster_id)
                    .limit(5)
                    .all()
                )
                sample_tickets = [
                    {
                        "ticket_id": inc.incident_number,
                        "short_description": inc.short_description,
                        "priority": inc.priority,
                        "status": inc.state,
                        "ci_name": inc.configuration_item,
                        "assigned_group": inc.assignment_group,
                        "created_date": (
                            inc.created_date.strftime("%Y-%m-%d")
                            if inc.created_date else None
                        ),
                    }
                    for inc in sample_incidents
                ]
                top_clusters.append({
                    "cluster_id": c.cluster_id,
                    "cluster_name": name,
                    "ticket_count": c.incident_count,
                    "sample_tickets": sample_tickets,
                    "top_ci": c.top_configuration_item,
                    "top_group": c.top_assignment_group,
                    "three_r_category": c.three_r_category,
                })

            return {
                "total_tickets": total_incidents,
                "total_clusters": total_clusters,
                "recurring_issue_percentage": recurring_pct,  # keep for compatibility
                "noise_ticket_count": noise_count,            # keep for compatibility
                "runner_count": runner_count,
                "runner_percentage": runner_pct,
                "repeater_count": repeater_count,
                "repeater_percentage": repeater_pct,
                "rare_count": rare_count,
                "rare_percentage": rare_pct,
                "top_clusters": top_clusters,
            }
        finally:
            session.close()

    # ==================================================================
    # CLUSTERS
    # ==================================================================

    def get_clusters(self) -> Dict[str, Any]:
        """
        Return clusters with intelligence fields for Clusters.jsx.
        """
        session = self._session()
        try:
            cluster_rows = (
                session.query(Cluster)
                .order_by(Cluster.incident_count.desc())
                .all()
            )

            # Build recurrence lookup in one query
            recurrence_rows = session.query(Recurrence).all()
            recurrence_map = {r.cluster_id: r for r in recurrence_rows}

            # Build date aggregates in one query
            date_agg = (
                session.query(
                    Incident.cluster_id,
                    func.min(Incident.created_date).label("first_date"),
                    func.max(Incident.created_date).label("last_date"),
                )
                .filter(Incident.cluster_id.isnot(None))
                .group_by(Incident.cluster_id)
                .all()
            )
            date_map = {r[0]: (r[1], r[2]) for r in date_agg}

            clusters = []
            for c in cluster_rows:
                name = c.cluster_name or f"Cluster {c.cluster_id}"
                # Collect unique CIs for this cluster
                ci_rows = (
                    session.query(Incident.configuration_item)
                    .filter(
                        Incident.cluster_id == c.cluster_id,
                        Incident.configuration_item.isnot(None),
                        Incident.configuration_item != "",
                    )
                    .distinct()
                    .limit(20)
                    .all()
                )
                ci_names = [r[0] for r in ci_rows if r[0]]

                # Recurrence data
                rec = recurrence_map.get(c.cluster_id)
                recurrence_score = rec.recurrence_score if rec else None
                problem_candidate = rec.problem_candidate if rec else None

                # Date data
                dates = date_map.get(c.cluster_id)
                first_date = dates[0] if dates else None
                last_date = dates[1] if dates else None

                clusters.append({
                    "cluster_id": c.cluster_id,
                    "cluster_name": name,
                    "ticket_count": c.incident_count,
                    "ci_names": ci_names,
                    "top_ci": c.top_configuration_item,
                    "top_group": c.top_assignment_group,
                    "top_priority": c.top_priority,
                    "top_region": c.top_region,
                    "three_r_category": c.three_r_category,
                    "three_r_reason": c.three_r_reason,
                    "recurrence_score": round(recurrence_score, 1) if recurrence_score is not None else None,
                    "problem_candidate": problem_candidate,
                    "first_incident_date": first_date.strftime("%Y-%m-%d") if first_date else None,
                    "last_incident_date": last_date.strftime("%Y-%m-%d") if last_date else None,
                })
            return {"clusters": clusters}
        finally:
            session.close()

    # ==================================================================
    # CLUSTER DETAIL
    # ==================================================================

    def get_cluster_detail(self, cluster_id: int) -> Optional[Dict[str, Any]]:
        """
        Return full intelligence detail for a single cluster.
        """
        session = self._session()
        try:
            c = session.query(Cluster).filter(Cluster.cluster_id == cluster_id).one_or_none()
            if c is None:
                return None

            name = c.cluster_name or f"Cluster {c.cluster_id}"

            # Recurrence
            rec = session.query(Recurrence).filter(Recurrence.cluster_id == cluster_id).one_or_none()

            # Date + priority aggregation
            date_row = (
                session.query(
                    func.min(Incident.created_date).label("first_date"),
                    func.max(Incident.created_date).label("last_date"),
                )
                .filter(Incident.cluster_id == cluster_id)
                .one()
            )
            first_date = date_row[0]
            last_date = date_row[1]

            # Active span and velocity — same semantics as ThreeRClassifier
            active_span_days = 0
            velocity = None
            if first_date and last_date:
                active_span_days = (last_date - first_date).days
                if active_span_days > 0:
                    velocity = round(c.incident_count / active_span_days, 2)
                else:
                    velocity = float(c.incident_count)

            # Priority distribution
            prio_rows = (
                session.query(Incident.priority, func.count(Incident.id))
                .filter(Incident.cluster_id == cluster_id)
                .group_by(Incident.priority)
                .all()
            )
            priority_distribution = {p: cnt for p, cnt in prio_rows if p}

            # Sample tickets (limit 5)
            sample_incidents = (
                session.query(Incident)
                .filter(Incident.cluster_id == cluster_id)
                .limit(5)
                .all()
            )
            sample_tickets = [
                {
                    "ticket_id": inc.incident_number,
                    "short_description": inc.short_description,
                    "priority": inc.priority,
                    "status": inc.state,
                    "ci_name": inc.configuration_item,
                    "assigned_group": inc.assignment_group,
                    "three_r_category": inc.three_r_category,
                    "created_date": inc.created_date.strftime("%Y-%m-%d") if inc.created_date else None,
                }
                for inc in sample_incidents
            ]

            return {
                "cluster_id": c.cluster_id,
                "cluster_name": name,
                "three_r_category": c.three_r_category,
                "three_r_reason": c.three_r_reason,
                "incident_count": c.incident_count,
                "recurrence_score": round(rec.recurrence_score, 1) if rec and rec.recurrence_score is not None else None,
                "problem_candidate": rec.problem_candidate if rec else None,
                "top_configuration_item": c.top_configuration_item,
                "top_assignment_group": c.top_assignment_group,
                "top_priority": c.top_priority,
                "top_region": c.top_region,
                "first_incident_date": first_date.strftime("%Y-%m-%d") if first_date else None,
                "last_incident_date": last_date.strftime("%Y-%m-%d") if last_date else None,
                "active_span_days": active_span_days,
                "velocity": velocity,
                "priority_distribution": priority_distribution,
                "sample_tickets": sample_tickets,
            }
        finally:
            session.close()

    # ==================================================================
    # TICKETS
    # ==================================================================

    def get_tickets(
        self,
        cluster_id: Optional[int] = None,
        ci_name: Optional[str] = None,
        assigned_group: Optional[str] = None,
        three_r_category: Optional[str] = None,
        filter_json: Optional[str] = None,
        sort_json: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        limit: int = 1000,
    ) -> Dict[str, Any]:
        """
        Return filtered tickets in shape expected by Tickets/Clusters pages:
        { tickets: [...], total: int, page: int, page_size: int, total_pages: int }
        Supports legacy filters + AST structured filters.
        """
        session = self._session()
        try:
            q = session.query(Incident, Cluster, Recurrence)

            ast = None
            if filter_json:
                try:
                    parsed = json.loads(filter_json)
                    if parsed:
                        ast = FilterGroup(**parsed)
                except Exception as e:
                    logging.error(f"Failed to parse filter AST: {e}")
                    raise ValueError(f"Invalid filter AST: {e}")

            # Decide on joins based on AST fields
            needs_cluster = ast and has_cluster_field(ast)
            needs_recurrence = ast and has_recurrence_field(ast)

            # We ALWAYS outerjoin to fetch three_r_reason and problem_candidate for the ticket drawer
            q = q.outerjoin(Cluster, Incident.cluster_id == Cluster.cluster_id)
            q = q.outerjoin(Recurrence, Cluster.cluster_id == Recurrence.cluster_id)

            # Apply legacy filters
            if cluster_id is not None:
                if cluster_id == -1:
                    q = q.filter(Incident.cluster_id.is_(None))
                else:
                    q = q.filter(Incident.cluster_id == cluster_id)
            if ci_name:
                q = q.filter(Incident.configuration_item == ci_name)
            if assigned_group:
                q = q.filter(Incident.assignment_group == assigned_group)
            if three_r_category:
                q = q.filter(Incident.three_r_category == three_r_category)

            # Apply AST filter
            if ast:
                expr = build_filter_expression(ast)
                if expr is not None:
                    q = q.filter(expr)

            # Count total
            total = q.count()
            total_pages = math.ceil(total / page_size) if total > 0 else 1

            # Apply Sorting
            if sort_json:
                try:
                    parsed_sort = json.loads(sort_json)
                    if parsed_sort:
                        rules = [SortRule(**r) for r in parsed_sort]
                        q = apply_sorting(q, rules)
                except Exception as e:
                    logging.error(f"Failed to parse sort rules: {e}")
                    raise ValueError(f"Invalid sort definition: {e}")
            else:
                # Default fallback sort
                q = q.order_by(Incident.created_date.desc())

            # Pagination
            # if page is requested, use it; otherwise fallback to legacy limit
            if page and page_size:
                offset = (page - 1) * page_size
                q = q.offset(offset).limit(page_size)
            else:
                q = q.limit(limit)

            rows = q.all()

            tickets = []
            for inc, clus, rec in rows:
                cid = inc.cluster_id
                cluster_name = clus.cluster_name if clus and clus.cluster_name else (f"Cluster {cid}" if cid else "Noise / Unclustered")
                if cid is None:
                    cluster_name = "Noise / Unclustered"
                    
                tickets.append({
                    "ticket_id": inc.incident_number,
                    "incident_number": inc.incident_number,
                    "caller": inc.caller,
                    "short_description": inc.short_description,
                    "description": inc.description,
                    "category": inc.category,
                    "priority": inc.priority,
                    "state": inc.state,
                    "status": inc.state, # for legacy
                    "assignment_group": inc.assignment_group,
                    "assigned_group": inc.assignment_group, # for legacy
                    "assigned_to": inc.assigned_to,
                    "resolved_by": inc.resolved_by,
                    "kb_number": inc.kb_number,
                    "it_batch_job": inc.it_batch_job,
                    "reassignment_count": inc.reassignment_count,
                    "configuration_item": inc.configuration_item,
                    "ci_name": inc.configuration_item, # for legacy
                    "offending_ci": inc.offending_ci,
                    "offending_ci_category": inc.offending_ci_category,
                    "created_date": (
                        inc.created_date.strftime("%Y-%m-%d") if inc.created_date else None
                    ),
                    "resolved_date": (
                        inc.resolved_date.strftime("%Y-%m-%d") if inc.resolved_date else None
                    ),
                    "cluster_id": cid if cid is not None else -1,
                    "cluster_name": cluster_name,
                    "three_r_category": inc.three_r_category,
                    "semantic_match_cluster_id": inc.semantic_match_cluster_id,
                    "three_r_reason": clus.three_r_reason if clus else None,
                    "problem_candidate": rec.problem_candidate if rec else None,
                })

            return {
                "tickets": tickets,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        finally:
            session.close()

    # ==================================================================
    # CI LIST
    # ==================================================================

    def get_ci_list(self) -> Dict[str, Any]:
        """
        Return CI list in shape expected by CIAnalysis.jsx:
        { ci_list: [{ci_name, total_tickets, recurring_tickets, recurring_percentage, cluster_count}] }
        """
        session = self._session()
        try:
            # CIs from incidents table
            ci_rows = (
                session.query(
                    Incident.configuration_item,
                    func.count(Incident.id).label("total"),
                    func.count(Incident.cluster_id).label("recurring"),
                )
                .filter(
                    Incident.configuration_item.isnot(None),
                    Incident.configuration_item != "",
                )
                .group_by(Incident.configuration_item)
                .order_by(func.count(Incident.id).desc())
                .all()
            )

            ci_list = []
            for ci_name, total, recurring in ci_rows:
                # Count distinct clusters for this CI
                cluster_count = (
                    session.query(func.count(func.distinct(Incident.cluster_id)))
                    .filter(
                        Incident.configuration_item == ci_name,
                        Incident.cluster_id.isnot(None),
                    )
                    .scalar() or 0
                )
                pct = round((recurring / total) * 100, 1) if total > 0 else 0
                ci_list.append({
                    "ci_name": ci_name,
                    "total_tickets": total,
                    "recurring_tickets": recurring,
                    "recurring_percentage": pct,
                    "cluster_count": cluster_count,
                })
            return {"ci_list": ci_list}
        finally:
            session.close()

    # ==================================================================
    # CI CLUSTERS (drill-down)
    # ==================================================================

    def get_ci_clusters(self, ci_name: str) -> Dict[str, Any]:
        """
        Return detail for one CI in shape expected by CIAnalysis CIDetail:
        { ci_name, total_tickets, recurring_tickets, recurring_percentage, clusters }
        """
        session = self._session()
        try:
            total = (
                session.query(func.count(Incident.id))
                .filter(Incident.configuration_item == ci_name)
                .scalar() or 0
            )
            recurring = (
                session.query(func.count(Incident.id))
                .filter(
                    Incident.configuration_item == ci_name,
                    Incident.cluster_id.isnot(None),
                )
                .scalar() or 0
            )
            pct = round((recurring / total) * 100, 1) if total > 0 else 0

            # Clusters that have incidents for this CI
            cluster_rows = (
                session.query(
                    Cluster,
                    func.count(Incident.id).label("ci_ticket_count"),
                )
                .join(Incident, Incident.cluster_id == Cluster.cluster_id)
                .filter(Incident.configuration_item == ci_name)
                .group_by(Cluster.cluster_id)
                .order_by(func.count(Incident.id).desc())
                .all()
            )

            clusters = []
            for c, ci_count in cluster_rows:
                name = c.cluster_name or f"Cluster {c.cluster_id}"
                clusters.append({
                    "cluster_id": c.cluster_id,
                    "cluster_name": name,
                    "ticket_count": ci_count,
                    "tickets": [],  # lazy loaded by frontend on expand
                })

            # Noise tickets for this CI
            noise_count = total - recurring
            if noise_count > 0:
                clusters.append({
                    "cluster_id": -1,
                    "cluster_name": "Noise / Unclustered",
                    "ticket_count": noise_count,
                    "tickets": [],
                })

            return {
                "ci_name": ci_name,
                "total_tickets": total,
                "recurring_tickets": recurring,
                "recurring_percentage": pct,
                "clusters": clusters,
            }
        finally:
            session.close()

    # ==================================================================
    # GROUP LIST
    # ==================================================================

    def get_group_list(self) -> Dict[str, Any]:
        """
        Return group list in shape expected by AssignedGroup.jsx:
        { group_list: [{group_name, total_tickets, recurring_tickets, recurring_percentage, cluster_count}] }
        """
        session = self._session()
        try:
            rows = (
                session.query(
                    Incident.assignment_group,
                    func.count(Incident.id).label("total"),
                    func.count(Incident.cluster_id).label("recurring"),
                )
                .filter(
                    Incident.assignment_group.isnot(None),
                    Incident.assignment_group != "",
                )
                .group_by(Incident.assignment_group)
                .order_by(func.count(Incident.id).desc())
                .all()
            )

            group_list = []
            for group_name, total, recurring in rows:
                cluster_count = (
                    session.query(func.count(func.distinct(Incident.cluster_id)))
                    .filter(
                        Incident.assignment_group == group_name,
                        Incident.cluster_id.isnot(None),
                    )
                    .scalar() or 0
                )
                pct = round((recurring / total) * 100, 1) if total > 0 else 0
                group_list.append({
                    "group_name": group_name,
                    "total_tickets": total,
                    "recurring_tickets": recurring,
                    "recurring_percentage": pct,
                    "cluster_count": cluster_count,
                })
            return {"group_list": group_list}
        finally:
            session.close()

    # ==================================================================
    # GROUP CLUSTERS (drill-down)
    # ==================================================================

    def get_group_clusters(self, group_name: str) -> Dict[str, Any]:
        """
        Return detail for one group in shape expected by GroupDetail component.
        """
        session = self._session()
        try:
            total = (
                session.query(func.count(Incident.id))
                .filter(Incident.assignment_group == group_name)
                .scalar() or 0
            )
            recurring = (
                session.query(func.count(Incident.id))
                .filter(
                    Incident.assignment_group == group_name,
                    Incident.cluster_id.isnot(None),
                )
                .scalar() or 0
            )
            pct = round((recurring / total) * 100, 1) if total > 0 else 0

            cluster_rows = (
                session.query(
                    Cluster,
                    func.count(Incident.id).label("grp_count"),
                )
                .join(Incident, Incident.cluster_id == Cluster.cluster_id)
                .filter(Incident.assignment_group == group_name)
                .group_by(Cluster.cluster_id)
                .order_by(func.count(Incident.id).desc())
                .all()
            )

            clusters = []
            for c, grp_count in cluster_rows:
                name = c.cluster_name or f"Cluster {c.cluster_id}"
                clusters.append({
                    "cluster_id": c.cluster_id,
                    "cluster_name": name,
                    "ticket_count": grp_count,
                    "tickets": [],
                })

            noise_count = total - recurring
            if noise_count > 0:
                clusters.append({
                    "cluster_id": -1,
                    "cluster_name": "Noise / Unclustered",
                    "ticket_count": noise_count,
                    "tickets": [],
                })

            return {
                "group_name": group_name,
                "total_tickets": total,
                "recurring_tickets": recurring,
                "recurring_percentage": pct,
                "clusters": clusters,
            }
        finally:
            session.close()

    # ==================================================================
    # STATUS (polling)
    # ==================================================================

    def get_status(self) -> Dict[str, Any]:
        """
        Return latest job status in shape expected by App.jsx pollStatus():
        { status: "idle"|"processing"|"done"|"error", message, result }
        """
        session = self._session()
        try:
            latest_job = (
                session.query(ProcessingJob)
                .order_by(ProcessingJob.created_at.desc())
                .first()
            )

            if latest_job is None:
                return {"status": "idle", "message": "No processing jobs found.", "result": None}

            job_status = latest_job.status or ""
            progress_msg = latest_job.progress_message or ""

            if job_status == JOB_STATUS_COMPLETED:
                return {
                    "status": "done",
                    "message": progress_msg or "Processing completed.",
                    "stage": latest_job.progress_stage or "COMPLETED",
                    "percent": 100,
                    "job_id": str(latest_job.id),
                    "result": {
                        "total_tickets": latest_job.total_incidents or 0,
                        "total_clusters": latest_job.total_clusters or 0,
                    },
                }
            elif job_status == JOB_STATUS_FAILED:
                return {
                    "status": "error",
                    "message": latest_job.error_message or "Processing failed.",
                    "stage": latest_job.progress_stage or "FAILED",
                    "percent": latest_job.progress_percent or 0,
                    "job_id": str(latest_job.id),
                    "result": None,
                }
            elif job_status == "CANCELLED":
                return {
                    "status": "cancelled",
                    "message": "Processing cancelled by user.",
                    "stage": "CANCELLED",
                    "percent": latest_job.progress_percent or 0,
                    "job_id": str(latest_job.id),
                    "result": None,
                }
            elif job_status in ("PENDING", "RUNNING"):
                return {
                    "status": "processing",
                    "message": progress_msg or "Processing...",
                    "stage": latest_job.progress_stage or "PENDING",
                    "percent": latest_job.progress_percent or 0,
                    "job_id": str(latest_job.id),
                    "result": None,
                }
            else:
                return {
                    "status": "idle",
                    "message": "Ready.",
                    "stage": None,
                    "percent": 0,
                    "job_id": str(latest_job.id),
                    "result": None,
                }
        finally:
            session.close()

    # ==================================================================
    # HEALTH
    # ==================================================================

    def get_health(self) -> Dict[str, Any]:
        """Return health status for the frontend health check."""
        session = self._session()
        try:
            has_data = (
                session.query(func.count(Incident.id)).scalar() or 0
            ) > 0
            return {
                "status": "ok",
                "data_loaded": has_data,
            }
        except Exception:
            return {"status": "error", "data_loaded": False}
        finally:
            session.close()
