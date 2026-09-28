# API Guide

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
