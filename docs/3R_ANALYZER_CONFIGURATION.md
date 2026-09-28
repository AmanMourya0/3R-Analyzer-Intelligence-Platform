# Configuration

Configuration is exclusively environment-driven via `pydantic-settings`.
No passwords or secrets are hardcoded in the source code.

## Environment Variables
* `DATABASE_URL`: Connection string for PostgreSQL (e.g., `postgresql://user:pass@localhost:5432/threer`).
* `CORS_ORIGINS`: Comma-separated list of allowed UI domains.
* `SIMILARITY_THRESHOLD`: Cosine similarity cutoff for clustering (Default: 0.85).
* `BATCH_SIZE`: AI processing batch size (Default: 500).

A `.env.example` file is provided in the repository.
