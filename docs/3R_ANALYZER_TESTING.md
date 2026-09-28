# Testing

The backend is fully tested using `pytest`.

## Baseline
* Current automated tests: **74 passing**.
* Suite includes:
  - Integration tests for data ingestion.
  - Concurrency testing for Job failures.
  - AST filter logic verification.
  - 3R classification logic edge cases.
  - PDF/CSV export generation.

*Note: The test suite runs against a patched in-memory SQLite database (`conftest.py`) to ensure speed and isolation.*
