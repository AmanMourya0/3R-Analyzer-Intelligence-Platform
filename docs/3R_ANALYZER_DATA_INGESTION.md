# Data Ingestion

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
