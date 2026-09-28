# Operations Runbook

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
