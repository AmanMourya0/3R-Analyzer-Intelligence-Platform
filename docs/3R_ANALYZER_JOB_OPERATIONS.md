# Job Operations

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
