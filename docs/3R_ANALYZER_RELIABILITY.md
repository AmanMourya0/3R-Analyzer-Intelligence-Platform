# Reliability & Failure Handling

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
