# Security

## Current Controls
* **Secrets Management**: Completely extracted to environment variables.
* **Upload Validation**: 100MB limit, strictly enforced allowed extensions.
* **AST Validation**: The Filter Builder strictly validates fields against an internal `FIELD_REGISTRY` mapping to prevent injection attacks.
* **Resource Protection**: API endpoints cap `page_size` at 1000 and `limit` at 5000 to prevent DoS.
* **Concurrency Limits**: The backend protects the database and CPU by locking the AI pipeline to a single active job.

*Note: Authentication/Authorization (SSO/OAuth) is not yet implemented and is scheduled for Phase 4.*
