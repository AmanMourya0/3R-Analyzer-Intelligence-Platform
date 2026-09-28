# Database

PostgreSQL is the primary datastore, managed via SQLAlchemy ORM and Alembic migrations.

## Major Tables
* `incidents`: Stores the individual ServiceNow tickets. Indexed heavily on `three_r_category`, `cluster_id`, `assignment_group`, and `configuration_item`.
* `clusters`: Stores the aggregated AI intelligence per semantic group.
* `processing_jobs`: Stores the history and status of uploaded datasets.

## Migrations
Migrations live in `backend/alembic/versions/`.
Run `alembic upgrade head` to apply schema changes.
