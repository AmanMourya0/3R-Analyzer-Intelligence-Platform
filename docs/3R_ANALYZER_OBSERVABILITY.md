# Observability

## Structured Logging
The backend uses a standard `logging` setup. During background processing, the `PipelineProfiler` emits highly structured telemetry logs to standard out:
`job_id=123-abc stage=GENERATING_EMBEDDINGS status=COMPLETED duration_ms=15420 incident_count=5000`

## Health Probes
* **Liveness (`/health`)**: Ensures the FastAPI thread is responsive.
* **Readiness (`/ready`)**: Performs a `SELECT 1` on the PostgreSQL database to ensure the app is fully ready for traffic.
