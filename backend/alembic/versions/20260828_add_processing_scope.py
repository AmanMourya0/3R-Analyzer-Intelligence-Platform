"""Add processing scope fields to processing jobs.

Revision ID: 20260828_processing_scope
Revises:
Create Date: 2026-08-28
"""

from alembic import op
import sqlalchemy as sa


revision = "20260828_processing_scope"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("processing_jobs", sa.Column("source_type", sa.String(length=30), nullable=False, server_default="upload"))
    op.add_column("processing_jobs", sa.Column("assignment_groups", sa.Text(), nullable=True))
    op.add_column("processing_jobs", sa.Column("start_date", sa.DateTime(), nullable=True))
    op.add_column("processing_jobs", sa.Column("end_date", sa.DateTime(), nullable=True))
    op.alter_column("processing_jobs", "source_type", server_default=None)


def downgrade() -> None:
    op.drop_column("processing_jobs", "end_date")
    op.drop_column("processing_jobs", "start_date")
    op.drop_column("processing_jobs", "assignment_groups")
    op.drop_column("processing_jobs", "source_type")
