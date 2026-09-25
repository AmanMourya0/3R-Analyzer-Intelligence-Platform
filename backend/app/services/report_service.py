import csv
import io
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import database
from app.database.incident_model import Incident
from app.database.cluster_model import Cluster
from app.database.recurrence_model import Recurrence
from app.schemas.filter_ast import FilterGroup, SortRule
from app.services.query_builder import build_filter_expression, apply_sorting, has_cluster_field, has_recurrence_field

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.units import inch

class ReportService:
    def _session(self) -> Session:
        return database.SessionLocal()

    def _build_base_filtered_query(
        self,
        session: Session,
        ast_json: Optional[str] = None,
        sort_json: Optional[str] = None,
        cluster_id: Optional[int] = None,
        three_r_category: Optional[str] = None
    ):
        """Builds the base Incident query respecting all AST filters and sorting, but WITHOUT pagination."""
        q = session.query(Incident, Cluster, Recurrence)

        ast = None
        if ast_json:
            try:
                parsed = json.loads(ast_json)
                if parsed:
                    ast = FilterGroup(**parsed)
            except Exception as e:
                logging.error(f"Failed to parse filter AST in report: {e}")

        # Always outerjoin to fetch three_r_reason and problem_candidate reliably
        q = q.outerjoin(Cluster, Incident.cluster_id == Cluster.cluster_id)
        q = q.outerjoin(Recurrence, Cluster.cluster_id == Recurrence.cluster_id)

        # Legacy Filters
        if cluster_id is not None:
            if cluster_id == -1:
                q = q.filter(Incident.cluster_id.is_(None))
            else:
                q = q.filter(Incident.cluster_id == cluster_id)
        if three_r_category:
            q = q.filter(Incident.three_r_category == three_r_category)

        # AST Filter
        if ast:
            expr = build_filter_expression(ast)
            if expr is not None:
                q = q.filter(expr)

        # Count total matches BEFORE sorting to save time
        total = q.count()

        # Apply Sorting
        if sort_json:
            try:
                parsed_sort = json.loads(sort_json)
                if parsed_sort:
                    rules = [SortRule(**r) for r in parsed_sort]
                    q = apply_sorting(q, rules)
            except Exception as e:
                logging.error(f"Failed to parse sort rules in report: {e}")
        else:
            q = q.order_by(Incident.created_date.desc())

        return q, total, ast

    def export_tickets_csv(self, filter_json: Optional[str] = None, sort_json: Optional[str] = None) -> bytes:
        """Exports all tickets matching the AST filter to CSV format, ignoring pagination."""
        session = self._session()
        try:
            q, total_filtered, ast = self._build_base_filtered_query(session, ast_json=filter_json, sort_json=sort_json)
            total_dataset = session.query(Incident).count()
            rows = q.all()

            output = io.StringIO()
            writer = csv.writer(output)
            
            # Metadata Header
            writer.writerow(["# REPORT METADATA"])
            writer.writerow(["# Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow(["# Total Dataset Size", total_dataset])
            writer.writerow(["# Records Exported", total_filtered])
            
            active_filters = filter_json if filter_json and filter_json != "null" else "None"
            writer.writerow(["# Active Filters", active_filters])
            
            active_sorts = sort_json if sort_json and sort_json != "null" else "Default (Created Date DESC)"
            writer.writerow(["# Sort Configuration", active_sorts])
            writer.writerow([])
            
            # Header
            writer.writerow([
                "Incident Number", "Short Description", "Description", "3R Category", 
                "3R Reason", "Cluster ID", "Cluster Name", "Priority", "State", 
                "Category", "Subcategory", "Assignment Group", "Configuration Item", 
                "Business Service", "Region", "Created Date", "Resolved Date", 
                "Problem Candidate", "Semantic Match Cluster ID"
            ])

            for inc, clus, rec in rows:
                cid = inc.cluster_id
                cluster_name = clus.cluster_name if clus and clus.cluster_name else (f"Cluster {cid}" if cid else "Noise / Unclustered")
                if cid is None:
                    cluster_name = "Noise / Unclustered"
                    
                writer.writerow([
                    inc.incident_number,
                    inc.short_description,
                    inc.description,
                    inc.three_r_category or "UNCLASSIFIED",
                    clus.three_r_reason if clus else "",
                    cid if cid is not None else -1,
                    cluster_name,
                    inc.priority,
                    inc.state,
                    inc.category,
                    inc.subcategory,
                    inc.assignment_group,
                    inc.configuration_item,
                    inc.business_service,
                    inc.region,
                    inc.created_date.strftime("%Y-%m-%d %H:%M:%S") if inc.created_date else "",
                    inc.resolved_date.strftime("%Y-%m-%d %H:%M:%S") if inc.resolved_date else "",
                    "Yes" if (rec and rec.problem_candidate) else "No",
                    inc.semantic_match_cluster_id or ""
                ])

            # Prepend UTF-8 BOM
            return "\ufeff".encode('utf8') + output.getvalue().encode('utf8')
        finally:
            session.close()

    def export_clusters_csv(self) -> bytes:
        """Exports cluster analytics to CSV."""
        session = self._session()
        try:
            clusters = session.query(Cluster, Recurrence).outerjoin(Recurrence, Cluster.cluster_id == Recurrence.cluster_id).all()
            total_clusters = len(clusters)
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Metadata
            writer.writerow(["# REPORT METADATA"])
            writer.writerow(["# Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow(["# Total Clusters Exported", total_clusters])
            writer.writerow([])
            
            writer.writerow([
                "Cluster ID", "Cluster Name", "3R Category", "3R Reason", 
                "Incident Count", "Recurrence Score", "Problem Candidate", 
                "Top CI", "Top Group", "Recommendation"
            ])

            for clus, rec in clusters:
                writer.writerow([
                    clus.cluster_id,
                    clus.cluster_name or f"Cluster {clus.cluster_id}",
                    clus.three_r_category or "UNCLASSIFIED",
                    clus.three_r_reason or "",
                    clus.incident_count or 0,
                    f"{rec.recurrence_score:.4f}" if rec and rec.recurrence_score is not None else "",
                    "Yes" if (rec and rec.problem_candidate) else "No",
                    clus.top_configuration_item or "-",
                    clus.top_assignment_group or "-",
                    rec.recommendation if rec and rec.recommendation else ""
                ])

            return "\ufeff".encode('utf8') + output.getvalue().encode('utf8')
        finally:
            session.close()

    def export_3r_summary_csv(self) -> bytes:
        """Exports a high-level 3R distribution summary."""
        session = self._session()
        try:
            # We explicitly calculate from persisted `three_r_category` ONLY
            runner_count = session.query(Incident).filter(Incident.three_r_category == "RUNNER").count()
            repeater_count = session.query(Incident).filter(Incident.three_r_category == "REPEATER").count()
            rare_count = session.query(Incident).filter(Incident.three_r_category == "RARE").count()
            total_count = session.query(Incident).count()
            
            # Invariant check
            if runner_count + repeater_count + rare_count != total_count and total_count > 0:
                logging.error(f"INVARIANT FAILED: {runner_count} + {repeater_count} + {rare_count} != {total_count}")

            output = io.StringIO()
            writer = csv.writer(output)
            
            writer.writerow(["# REPORT METADATA"])
            writer.writerow(["# Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow(["# Analysis Scope", "Full Dataset"])
            writer.writerow([])
            
            writer.writerow(["Metric", "Value", "Percentage"])
            writer.writerow(["Total Incidents", total_count, "100.00%"])
            writer.writerow(["Runner", runner_count, f"{(runner_count/total_count*100):.2f}%" if total_count else "0%"])
            writer.writerow(["Repeater", repeater_count, f"{(repeater_count/total_count*100):.2f}%" if total_count else "0%"])
            writer.writerow(["Rare", rare_count, f"{(rare_count/total_count*100):.2f}%" if total_count else "0%"])
            
            return "\ufeff".encode('utf8') + output.getvalue().encode('utf8')
        finally:
            session.close()

    def generate_executive_report_pdf(self, filter_json: Optional[str] = None, sort_json: Optional[str] = None) -> bytes:
        """Generates a dynamic 3-5 page Executive Report using ReportLab."""
        session = self._session()
        try:
            q, total_filtered, ast = self._build_base_filtered_query(session, ast_json=filter_json, sort_json=sort_json)
            
            # Calculate metrics from the filtered set
            runner_count = q.filter(Incident.three_r_category == "RUNNER").count()
            repeater_count = q.filter(Incident.three_r_category == "REPEATER").count()
            rare_count = q.filter(Incident.three_r_category == "RARE").count()

            # Ensure invariant on filtered set (ignoring unclassified)
            classified_total = runner_count + repeater_count + rare_count
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
            Story = []
            styles = getSampleStyleSheet()
            
            # Custom Styles
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=24, spaceAfter=20, textColor=colors.HexColor('#0b0f1c'))
            h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=16, spaceBefore=15, spaceAfter=10, textColor=colors.HexColor('#0f62fe'))
            normal_style = styles['Normal']
            
            # --- PAGE 1: EXECUTIVE SUMMARY ---
            Story.append(Paragraph("3R Incident Intelligence Report", title_style))
            
            generation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            Story.append(Paragraph(f"Generated: {generation_date}", normal_style))
            
            scope_text = "All processed incidents." if not ast else "Filtered dataset matching specific criteria."
            Story.append(Paragraph(f"<b>Analysis Scope:</b> {scope_text}", normal_style))
            
            if ast:
                filter_desc = json.dumps(json.loads(filter_json), indent=2) if filter_json else "None"
                # Safe paragraph string replacing newlines
                Story.append(Paragraph(f"<b>Active Filters:</b> {filter_desc.replace(chr(10), '<br/>')}", normal_style))
                
            Story.append(Spacer(1, 0.2*inch))
            
            Story.append(Paragraph("Executive Summary", h2_style))
            Story.append(Paragraph(f"Total Incidents (in scope): <b>{total_filtered}</b>", normal_style))
            
            data = [
                ['Category', 'Count', 'Percentage'],
                ['Runner', str(runner_count), f"{(runner_count/total_filtered*100):.1f}%" if total_filtered else "0%"],
                ['Repeater', str(repeater_count), f"{(repeater_count/total_filtered*100):.1f}%" if total_filtered else "0%"],
                ['Rare', str(rare_count), f"{(rare_count/total_filtered*100):.1f}%" if total_filtered else "0%"]
            ]
            t = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f62fe')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f4f4f4')),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            Story.append(t)
            
            Story.append(Spacer(1, 0.3*inch))
            
            Story.append(Paragraph("Coverage Validation", h2_style))
            invariant_status = "PASSED" if classified_total == total_filtered else "PARTIAL (Unclassified entries exist)"
            Story.append(Paragraph(f"Runner + Repeater + Rare = {classified_total} (Total: {total_filtered}) - Status: {invariant_status}", normal_style))
            
            Story.append(PageBreak())
            
            # --- PAGE 2: TRENDS & DISTRIBUTIONS ---
            Story.append(Paragraph("Priority & Impact Distribution", h2_style))
            
            # Aggregate priorities
            priorities = session.query(Incident.priority, func.count(Incident.incident_number)).filter(Incident.incident_number.in_(q.with_entities(Incident.incident_number))).group_by(Incident.priority).all()
            
            pri_data = [['Priority', 'Count']]
            for p, c in sorted(priorities, key=lambda x: x[1], reverse=True):
                pri_data.append([p or "None", str(c)])
                
            pt = Table(pri_data, colWidths=[2*inch, 1.5*inch])
            pt.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3d4f70')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            Story.append(pt)
            
            Story.append(Spacer(1, 0.3*inch))
            
            Story.append(Paragraph("Top Affected Configuration Items", h2_style))
            cis = session.query(Incident.configuration_item, func.count(Incident.incident_number)).filter(Incident.incident_number.in_(q.with_entities(Incident.incident_number))).group_by(Incident.configuration_item).order_by(desc(func.count(Incident.incident_number))).limit(10).all()
            
            ci_data = [['CI / Application', 'Tickets']]
            for ci, c in cis:
                ci_data.append([ci or "None", str(c)])
                
            cit = Table(ci_data, colWidths=[3.5*inch, 1*inch])
            cit.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3d4f70')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            Story.append(cit)
            
            Story.append(PageBreak())
            
            # --- PAGE 3: PATTERN DETAILS ---
            Story.append(Paragraph("Top Recurring Patterns", h2_style))
            
            # Aggregate clusters within this filtered set
            top_clusters = session.query(Cluster.cluster_name, Cluster.three_r_category, func.count(Incident.incident_number)).join(Incident, Cluster.cluster_id == Incident.cluster_id).filter(Incident.incident_number.in_(q.with_entities(Incident.incident_number))).group_by(Cluster.cluster_name, Cluster.three_r_category).order_by(desc(func.count(Incident.incident_number))).limit(15).all()
            
            clus_data = [['Pattern Name', 'Category', 'Volume']]
            for name, cat, c in top_clusters:
                clus_data.append([name or "Noise", cat or "-", str(c)])
                
            ct = Table(clus_data, colWidths=[3.5*inch, 1*inch, 1*inch])
            ct.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3d4f70')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('FONTSIZE', (0,1), (-1,-1), 9)
            ]))
            Story.append(ct)
            
            Story.append(Spacer(1, 0.3*inch))
            
            Story.append(Paragraph("Factual Observations", h2_style))
            Story.append(Paragraph(f"• The highest-volume pattern in this scope is '{top_clusters[0][0] if top_clusters else 'None'}' with {top_clusters[0][2] if top_clusters else 0} occurrences.", normal_style))
            Story.append(Paragraph(f"• {runner_count} incidents have been classified as RUNNERS, representing active, ongoing pain points.", normal_style))
            
            doc.build(Story)
            return buffer.getvalue()
        finally:
            session.close()

report_service = ReportService()
