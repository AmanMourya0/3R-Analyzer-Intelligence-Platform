# Job Operations

## ProcessingJob Types
- `PROCESSING`: Standard incident data processing pipeline.
- `AI_CLUSTER_NAMING`: Optional asynchronous AI cluster name enrichment.

## ProcessingJob Lifecycle
A `ProcessingJob` has the following statuses:
1. `PENDING`: Queued for execution.
2. `RUNNING`: Currently being processed by the background worker.
3. `COMPLETED`: Job successfully finished. **Progress is exclusively set to 100% only when the job is actually complete and all data is fully persisted.**
4. `FAILED`: An error occurred during processing.
5. `CANCELLED`: Job was manually cancelled by the user.

## Job Status API Contract
- `/api/status`: This endpoint is exclusively for retrieving the status of a `PROCESSING` job. It ignores `AI_CLUSTER_NAMING` jobs.
- `/api/clusters/enrichment-status`: This endpoint is exclusively for retrieving the status of an `AI_CLUSTER_NAMING` job.

## Progress Tracking
Progress tracking is strictly monotonic. A job's progress percentage will never regress. The final `COMPLETED` stage (100%) is only reached after persistence logic successfully completes database transactions.

## Cancellation
The Main Processing Screen's "Cancel Processing" action targets the `PROCESSING` job specifically and gracefully halts processing. `AI_CLUSTER_NAMING` jobs cannot be cancelled by this action and do not alter core 3R processing states.

## Concurrency Protection
The platform enforces strict limits:
- **Only one core processing job can run at a time**. If initiated while active, it will be rejected.
- **AI Enrichment requires a stable dataset**: AI cluster naming can only run if no core processing job is active, and only one enrichment job can run at a time.
- **Core State Immutability**: AI naming operates out-of-band and does not alter the core 3R processing state (e.g. classification, IDs, frequencies).

## Stale Jobs & Recovery
If the server crashes mid-processing, a job may be left stuck in `RUNNING`. 
When the server restarts, the application will detect stuck jobs and fail them, or administrators can view them in the Job History page. Currently, jobs that remain `RUNNING` for abnormal durations must be reviewed; however, database rollbacks ensure that half-processed data does not pollute the dashboard.
