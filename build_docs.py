import os

DOCS_DIR = "docs"

docs = {
    "DOCUMENTATION_INDEX.md": """# 3R Analyzer Intelligence Documentation Index

Welcome to the 3R Analyzer Intelligence Master Documentation. This documentation reflects the current Phase 3 Production Baseline.

## Product
* [Product Overview](3R_ANALYZER_PRODUCT_OVERVIEW.md) - High-level introduction to 3R Analyzer Intelligence.
* [Dashboard](3R_ANALYZER_DASHBOARD.md) - Analytics and KPIs.
* [Incident Workspace](3R_ANALYZER_INCIDENT_WORKSPACE.md) - Interactive ticket investigation.

## Architecture
* [Technical Architecture](3R_ANALYZER_TECHNICAL_ARCHITECTURE.md) - Complete system architecture.
* [Database](3R_ANALYZER_DATABASE.md) - PostgreSQL schema, models, and migrations.

## Data & Ingestion
* [Data Ingestion](3R_ANALYZER_DATA_INGESTION.md) - CSV/Excel upload validation and persistence.
* [ServiceNow Data Model](3R_ANALYZER_SERVICENOW_DATA_MODEL.md) - Supported fields and schemas.

## 3R Intelligence
* [3R Intelligence](3R_ANALYZER_3R_INTELLIGENCE.md) - Logic behind Runner, Repeater, and Rare classifications.
* [Pipeline](3R_ANALYZER_PIPELINE.md) - The 11-stage background processing pipeline.

## Filtering
* [Filtering](3R_ANALYZER_FILTERING.md) - Advanced ServiceNow-style AST filtering.

## Jobs
* [Job Operations](3R_ANALYZER_JOB_OPERATIONS.md) - Background AI clustering lifecycle and UI.

## Reporting
* [Reporting & Exports](3R_ANALYZER_REPORTING_EXPORTS.md) - CSV and PDF export capabilities.

## API
* [API Guide](3R_ANALYZER_API_GUIDE.md) - Core FastAPI endpoints.

## Security & Reliability
* [Security](3R_ANALYZER_SECURITY.md) - Environment secrets and protection boundaries.
* [Reliability](3R_ANALYZER_RELIABILITY.md) - Transaction boundaries, failure handling, and rollback.
* [Observability](3R_ANALYZER_OBSERVABILITY.md) - Structured telemetry and logging.

## Development & Operations
* [Testing](3R_ANALYZER_TESTING.md) - Pytest suite and validation.
* [Configuration](3R_ANALYZER_CONFIGURATION.md) - Environment setup.
* [Development Guide](DEVELOPMENT_GUIDE.md) - Local setup instructions.
* [Production Deployment Guide](PRODUCTION_DEPLOYMENT_GUIDE.md) - Pre-requisites for Phase 4 deployment.
* [Operations Runbook](OPERATIONS_RUNBOOK.md) - Maintenance and troubleshooting.

*Deprecated Files (Merged):*
* `3R_Analyzer_Filter_Builder.md` -> 3R_ANALYZER_FILTERING.md
* `3R_Analyzer_Incident_Field_Registry.md` -> 3R_ANALYZER_SERVICENOW_DATA_MODEL.md
* `3R_Analyzer_Optimized_Pipeline_Architecture.md` -> 3R_ANALYZER_PIPELINE.md / OBSERVABILITY.md
* `3R_Analyzer_Table_Column_Selection.md` -> 3R_ANALYZER_INCIDENT_WORKSPACE.md
* `Production_Hardening_Report.md` -> 3R_ANALYZER_RELIABILITY.md
* `ServiceNow_Data_Ingestion.md` -> 3R_ANALYZER_DATA_INGESTION.md
""",

    "3R_ANALYZER_PRODUCT_OVERVIEW.md": """# Product Overview

## What is 3R Analyzer Intelligence?
3R Analyzer Intelligence is an analytical platform designed to ingest IT incident data (e.g., from ServiceNow), intelligently group similar incidents using semantic AI clustering, and classify those clusters into actionable categories: **Runner**, **Repeater**, or **Rare**. 

## Business Problem
IT Service Desks are often overwhelmed by recurring incidents. Traditional text matching is insufficient to detect conceptually similar problems. By leveraging Large Language Models (LLMs) and embeddings, 3R Analyzer identifies the true underlying recurring problems, allowing IT leadership to prioritize permanent fixes.

## Target Users
* **Service Desk Managers**: To view the dashboard and monitor volume.
* **Problem Managers**: To investigate specific clusters and formulate problem tickets.
* **IT Executives**: To review PDF summary reports.

## Main Workflow
1. **Ingestion**: User uploads a CSV/XLSX export from ServiceNow.
2. **Background Processing**: The system queues a Job, generating embeddings, clustering, and performing 3R classification.
3. **Analysis**: Once complete, users explore the results in the Dashboard and Incident Investigation Workspace.
4. **Action**: Users export results to create ServiceNow Problem records.
""",

    "3R_ANALYZER_3R_INTELLIGENCE.md": """# 3R Intelligence

The core analytical value of this platform is the categorization of incident clusters into three buckets:

* **Runner**: High-volume, high-velocity incidents that need immediate automation or systemic fixes. These typically have supporting problem signals.
* **Repeater**: Recurring issues that happen regularly but at a lower velocity or without systemic severity, needing gradual root-cause elimination.
* **Rare**: One-off incidents that do not form a pattern.

## Fundamental Invariant
`Total Incidents = Runner Incidents + Repeater Incidents + Rare Incidents`

## Classification Logic
The system implements the following rules (in order):
1. **Priority Repeater**: If a cluster consists entirely of High Priority (P1/P2) incidents, it is immediately a `Repeater`.
2. **High-Velocity Burst (Runner/Repeater)**: If a cluster has ≥3 incidents within a 7-day window:
   - If it has a supporting problem signal (Problem Candidate = True), it is a `Runner`.
   - Otherwise, it is a `Repeater`.
3. **Sustained High Activity**: If a cluster has ≥3 incidents spanning more than 7 days, it is a `Repeater`.
4. **Rare**: Any cluster that does not meet the above criteria is `Rare`.

## What is a Cluster?
Clusters are formed by taking the `Short description` + `Description` of incidents, passing them through `all-MiniLM-L6-v2` to get semantic embeddings, and clustering them using DBSCAN/Cosine Similarity algorithms.
""",

    "3R_ANALYZER_TECHNICAL_ARCHITECTURE.md": """# Technical Architecture

## Architecture Diagram
```mermaid
graph TD
    UI[React + Vite Frontend] -->|REST API| API[FastAPI Backend]
    API --> Services[Service Layer]
    Services --> JobQueue[APScheduler Background Jobs]
    Services --> DB[(PostgreSQL)]
    JobQueue --> Pipeline[AI Pipeline]
    Pipeline --> Models[all-MiniLM-L6-v2 Embeddings]
    Pipeline --> DB
```

## Layers
1. **Frontend**: React 18, Vite, Tailwind CSS. Implements the Dashboard, Workspace, and Job Operations.
2. **API Layer (FastAPI)**: Exposes endpoints for data ingestion, filtering, analytics, and job status.
3. **Service Layer**: Contains business logic (e.g., `ProcessService`, `JobService`, `ReportService`).
4. **Pipeline / Job Processing**: Handles the heavy lifting of parsing datasets, generating AI embeddings, and clustering.
5. **Database (PostgreSQL)**: Persists Incidents, Clusters, and Jobs. Managed via SQLAlchemy and Alembic.
""",

    "3R_ANALYZER_PIPELINE.md": """# AI Pipeline

The 3R Analyzer pipeline consists of 11 strictly ordered stages. 

## Stages
1. **LOADING_DATA**: Reads the uploaded CSV/XLSX into a pandas DataFrame.
2. **APPLYING_SCOPE**: Filters out incidents already processed (if delta processing is implemented).
3. **PREPROCESSING**: Cleans text, handles nulls, formats dates, and prepares the `combined_text` column.
4. **GENERATING_EMBEDDINGS**: Uses `all-MiniLM-L6-v2` to convert text into high-dimensional vectors. (Batch size optimized).
5. **STORING_EMBEDDINGS**: Temporarily holds vectors in memory for clustering.
6. **CLUSTERING**: Groups similar embeddings using optimized DBSCAN with cosine similarity.
7. **CLUSTER_ANALYSIS**: Aggregates metadata (top CI, top Assignment Group) per cluster.
8. **NAMING_CLUSTERS**: Uses KeyBERT to extract a readable 3-4 word summary phrase for the cluster.
9. **RECURRENCE_ANALYSIS**: Analyzes the time-series distribution of the cluster to find bursts or sustained activity.
10. **THREE_R_CLASSIFICATION**: Applies the Runner/Repeater/Rare logic to each cluster.
11. **PERSISTING_RESULTS**: Safely writes all records to PostgreSQL using transaction chunks.

## Performance Characteristics
Baseline for a 5,000 incident dataset: **~65 seconds**.
The pipeline is instrumented with `stage_timer` for structured observability.
""",

    "3R_ANALYZER_SERVICENOW_DATA_MODEL.md": """# ServiceNow Data Model

The platform is designed to ingest standard ServiceNow Incident exports.

## Supported Fields
| ServiceNow Field | Internal Model Name | Type | Nullable | Used in 3R/Clustering |
| :--- | :--- | :--- | :--- | :--- |
| Number | `incident_number` | String | No | No |
| Caller | `caller` | String | Yes | No |
| Short description | `short_description` | Text | Yes | **Yes** |
| Description | `description` | Text | Yes | **Yes** |
| Category | `category` | String | Yes | No |
| Subcategory | `subcategory` | String | Yes | No |
| Priority | `priority` | String | Yes | **Yes** |
| State | `state` | String | Yes | No |
| Assignment group | `assignment_group` | String | Yes | Yes (Metadata) |
| Assigned to | `assigned_to` | String | Yes | No |
| Resolved by | `resolved_by` | String | Yes | No |
| Configuration item | `configuration_item` | String | Yes | Yes (Metadata) |
| Offending CI | `offending_ci` | String | Yes | No |
| Offending CI Category | `offending_ci_category` | String | Yes | No |
| Business service | `business_service` | String | Yes | No |
| Region | `region` | String | Yes | No |
| KB Number | `kb_number` | String | Yes | No |
| IT Batch Job | `it_batch_job` | String | Yes | No |
| Reassignment count | `reassignment_count` | Integer | Yes | No |
| Created | `created_date` | DateTime | Yes | **Yes (Time Series)** |
| Resolved | `resolved_date` | DateTime | Yes | No |

## Dynamic Workspace
All the above fields are fully exposed in the Incident Investigation Workspace, allowing users to dynamically select them as columns and filter by them.
""",

    "3R_ANALYZER_DATA_INGESTION.md": """# Data Ingestion

## Upload Flow
1. **User Action**: The user selects a dataset and uploads it via the frontend.
2. **API Validation**: The `/api/upload` endpoint checks:
   - File extension must be `.csv`, `.xls`, or `.xlsx`.
   - File size must be > 0 bytes and ≤ 100MB.
3. **Storage**: The file is safely written to the `uploads/` directory with a unique UUID name to prevent collisions.
4. **Job Creation**: A `ProcessingJob` is created in the database with status `PENDING`.
5. **Background Kickoff**: The API returns the `job_id` and APScheduler asynchronously picks up the file.

## Failure Behavior
If the file is malformed, missing required ServiceNow columns (like `Number`), or empty, the job will fail gracefully during the `LOADING_DATA` or `PREPROCESSING` stage.
""",

    "3R_ANALYZER_JOB_OPERATIONS.md": """# Job Operations

## ProcessingJob Lifecycle
A `ProcessingJob` has the following statuses:
1. `PENDING`: Queued for execution.
2. `RUNNING`: Currently being processed by the AI Pipeline.
3. `COMPLETED`: Data is fully ingested and available in the UI.
4. `FAILED`: An error occurred during processing.

## Concurrency Protection
The platform enforces a strict limit: **Only one AI clustering job can run at a time**.
If a new job is initiated while another is `RUNNING` or `PENDING`, the new job immediately transitions to `FAILED` with an error message: `"Another AI clustering job is currently active."`

## Stale Jobs & Recovery
If the server crashes mid-processing, a job may be left stuck in `RUNNING`. 
When the server restarts, the application will detect stuck jobs and fail them, or administrators can view them in the Job History page. Currently, jobs that remain `RUNNING` for abnormal durations must be reviewed; however, database rollbacks ensure that half-processed data does not pollute the dashboard.
""",

    "3R_ANALYZER_FILTERING.md": """# Advanced Filter Builder

The platform features a ServiceNow-style Advanced Filter Builder allowing complex AST (Abstract Syntax Tree) query generation.

## Supported Logic
* Nested Groups: `AND` / `OR`
* Operators: `==`, `!=`, `>`, `<`, `>=`, `<=`, `in`, `not_in`, `contains`, `not_contains`, `starts_with`, `ends_with`, `between`, `is_empty`, `is_not_empty`.

## Abstract Syntax Tree (AST) Example
Filters are serialized as JSON and passed via query parameters to the backend:
```json
{
  "type": "group",
  "logic": "AND",
  "conditions": [
    {
      "type": "condition",
      "field": "priority",
      "operator": "in",
      "value": ["1 - Critical", "2 - High"]
    },
    {
      "type": "group",
      "logic": "OR",
      "conditions": [
        {
          "type": "condition",
          "field": "assignment_group",
          "operator": "==",
          "value": "Database Admins"
        }
      ]
    }
  ]
}
```

## Backend Validation
The backend `QueryBuilder` walks this AST, safely translates it to SQLAlchemy clauses, and enforces the `FIELD_REGISTRY` to prevent SQL injection or invalid column references.
""",

    "3R_ANALYZER_INCIDENT_WORKSPACE.md": """# Incident Investigation Workspace

The Workspace is the primary analytical table for viewing incident data.

## Features
* **Column Selection**: Users can toggle any ServiceNow field on or off. The column selection is a reusable component applied to both the Incident table and Job History table.
* **Filtering**: Fully integrated with the Advanced Filter Builder.
* **Server-side Pagination**: Supports large datasets safely.
* **Ticket Drawer**: Clicking a row opens a drawer showing full details, including its assigned 3R Category (Runner/Repeater/Rare) and the AI-generated Cluster Name.
""",

    "3R_ANALYZER_DASHBOARD.md": """# Dashboard & Analytics

The dashboard provides immediate executive visibility into the IT environment.

## KPI Cards
* **Total Incidents**
* **Runner Incidents**
* **Repeater Incidents**
* **Rare Incidents**

## Visualizations
* **Distribution Charts**: Displays the ratio of 3R categories.
* **Top Insights**: Highlights the most problematic Configuration Items (CIs) and Assignment Groups based on cluster data.

The dashboard respects the Advanced Filter Builder, meaning executives can filter by Date or Assignment Group and see the KPIs dynamically recalculate.
""",

    "3R_ANALYZER_REPORTING_EXPORTS.md": """# Reporting & Exports

## API Endpoints
All exports respect the current active AST filter from the UI.
* `GET /api/export/tickets/csv`: Dumps raw tickets.
* `GET /api/export/clusters/csv`: Dumps cluster summaries.
* `GET /api/export/summary/csv`: Dumps high-level 3R KPIs.
* `GET /api/export/executive-report/pdf`: Generates a fully formatted, leadership-ready PDF using `reportlab`.

## Implementation Details
The backend streams these exports with correct `Content-Disposition` attachment headers and `text/csv` or `application/pdf` media types.
""",

    "3R_ANALYZER_API_GUIDE.md": """# API Guide

The API is built on FastAPI and accessible at `/api`.

## Core Endpoints
* `POST /api/upload`: Upload a dataset. (Requires `multipart/form-data`).
* `GET /api/jobs`: List all processing jobs.
* `GET /api/tickets`: Paginated ticket listing. (Query params: `filter` (AST JSON), `sort`, `page`, `page_size`).
* `GET /api/clusters`: List all clusters.
* `GET /api/dashboard/metrics`: Core KPI metrics for the dashboard.

## Health & Readiness
* `GET /health`: Liveness probe (Returns `200 OK`).
* `GET /ready`: Readiness probe (Checks DB connection).
""",

    "3R_ANALYZER_CONFIGURATION.md": """# Configuration

Configuration is exclusively environment-driven via `pydantic-settings`.
No passwords or secrets are hardcoded in the source code.

## Environment Variables
* `DATABASE_URL`: Connection string for PostgreSQL (e.g., `postgresql://user:pass@localhost:5432/threer`).
* `CORS_ORIGINS`: Comma-separated list of allowed UI domains.
* `SIMILARITY_THRESHOLD`: Cosine similarity cutoff for clustering (Default: 0.85).
* `BATCH_SIZE`: AI processing batch size (Default: 500).

A `.env.example` file is provided in the repository.
""",

    "3R_ANALYZER_SECURITY.md": """# Security

## Current Controls
* **Secrets Management**: Completely extracted to environment variables.
* **Upload Validation**: 100MB limit, strictly enforced allowed extensions.
* **AST Validation**: The Filter Builder strictly validates fields against an internal `FIELD_REGISTRY` mapping to prevent injection attacks.
* **Resource Protection**: API endpoints cap `page_size` at 1000 and `limit` at 5000 to prevent DoS.
* **Concurrency Limits**: The backend protects the database and CPU by locking the AI pipeline to a single active job.

*Note: Authentication/Authorization (SSO/OAuth) is not yet implemented and is scheduled for Phase 4.*
""",

    "3R_ANALYZER_RELIABILITY.md": """# Reliability & Failure Handling

## Database Transaction Boundaries
Long-running AI jobs execute within safe database sessions. If a crash or exception occurs mid-pipeline, the `session.rollback()` is automatically invoked. This prevents partial data from breaking the dashboard invariant.

## Stuck Jobs
The system catches internal exceptions and correctly updates the `ProcessingJob` to `FAILED` while saving the error message.

## Troubleshooting
| Problem | Detection | Cause | Recovery |
| :--- | :--- | :--- | :--- |
| Another job is running | UI shows Error | Concurrency protection | Wait for the active job to finish. |
| Job fails on loading | Job History shows FAILED | Corrupt CSV/Missing Headers | Fix the CSV in Excel and re-upload. |
| Dashboard Offline | `/ready` returns 503 | DB is unreachable | Restart PostgreSQL. |
""",

    "3R_ANALYZER_OBSERVABILITY.md": """# Observability

## Structured Logging
The backend uses a standard `logging` setup. During background processing, the `PipelineProfiler` emits highly structured telemetry logs to standard out:
`job_id=123-abc stage=GENERATING_EMBEDDINGS status=COMPLETED duration_ms=15420 incident_count=5000`

## Health Probes
* **Liveness (`/health`)**: Ensures the FastAPI thread is responsive.
* **Readiness (`/ready`)**: Performs a `SELECT 1` on the PostgreSQL database to ensure the app is fully ready for traffic.
""",

    "3R_ANALYZER_DATABASE.md": """# Database

PostgreSQL is the primary datastore, managed via SQLAlchemy ORM and Alembic migrations.

## Major Tables
* `incidents`: Stores the individual ServiceNow tickets. Indexed heavily on `three_r_category`, `cluster_id`, `assignment_group`, and `configuration_item`.
* `clusters`: Stores the aggregated AI intelligence per semantic group.
* `processing_jobs`: Stores the history and status of uploaded datasets.

## Migrations
Migrations live in `backend/alembic/versions/`.
Run `alembic upgrade head` to apply schema changes.
""",

    "3R_ANALYZER_TESTING.md": """# Testing

The backend is fully tested using `pytest`.

## Baseline
* Current automated tests: **74 passing**.
* Suite includes:
  - Integration tests for data ingestion.
  - Concurrency testing for Job failures.
  - AST filter logic verification.
  - 3R classification logic edge cases.
  - PDF/CSV export generation.

*Note: The test suite runs against a patched in-memory SQLite database (`conftest.py`) to ensure speed and isolation.*
""",

    "DEVELOPMENT_GUIDE.md": """# Local Development Guide

## Prerequisites
* Python 3.11+
* Node.js 18+
* PostgreSQL 14+

## Backend Setup
```bash
cd backend
python -m venv venv
venv\\Scripts\\activate   # (Windows)
# source venv/bin/activate (Linux/Mac)
pip install -r requirements.txt
```

Set up your `.env` file referencing `.env.example`.

Run Migrations:
```bash
alembic upgrade head
```

Start Server:
```bash
uvicorn app.main:app --reload
```

## Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
""",

    "PRODUCTION_DEPLOYMENT_GUIDE.md": """# Production Deployment Guide (Phase 4 Prep)

This document outlines the infrastructure required for the eventual Phase 4 production rollout.

## Infrastructure Requirements
* **Database**: Managed PostgreSQL instance (e.g., AWS RDS, Azure Postgres).
* **Backend Compute**: 4+ vCPU, 8GB+ RAM required for the AI embedding models. Containerization (Docker) is recommended.
* **Frontend Hosting**: Static web host (e.g., Nginx, Vercel, AWS S3+CloudFront).

## Monitoring
Ensure `/health` and `/ready` endpoints are hooked into the load balancer or Kubernetes readiness probes.
""",

    "OPERATIONS_RUNBOOK.md": """# Operations Runbook

## Validating the Database
Connect to PostgreSQL and run:
```sql
SELECT three_r_category, count(*) FROM incidents GROUP BY three_r_category;
```

## Handling Stuck Jobs
If the server is forcefully killed, a job may remain in `RUNNING`.
Connect to PostgreSQL:
```sql
UPDATE processing_jobs SET status = 'FAILED', error_message = 'Manually failed by admin' WHERE status = 'RUNNING';
```

## Checking Logs
Standard application logs will display:
```
INFO: 3RAnalyzer: job_id=uuid stage=CLUSTERING status=COMPLETED duration_ms=4500
```
Use standard grep or Logstash to parse `job_id` traces.
"""
}

for filename, content in docs.items():
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

print(f"Created {len(docs)} documentation files in {DOCS_DIR}/")
