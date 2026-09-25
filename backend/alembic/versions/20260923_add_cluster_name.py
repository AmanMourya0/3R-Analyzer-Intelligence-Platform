"""add cluster_name to clusters table

Revision ID: 20260923_add_cluster_name
Revises: 20260828_processing_scope
Create Date: 2026-09-23

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260923_add_cluster_name'
down_revision = '20260828_processing_scope'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'clusters',
        sa.Column('cluster_name', sa.String(300), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('clusters', 'cluster_name')
