# 3R Analyzer Intelligence Documentation Index

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
