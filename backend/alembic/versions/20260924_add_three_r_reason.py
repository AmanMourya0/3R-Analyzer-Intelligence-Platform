"""Add three_r_reason column to clusters table

Revision ID: 20260924_add_three_r_reason
Revises: 20260923_add_cluster_name
Create Date: 2026-09-24
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260924_add_three_r_reason'
down_revision = '18faded1fb43'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('clusters', sa.Column('three_r_reason', sa.String(300), nullable=True))


def downgrade() -> None:
    op.drop_column('clusters', 'three_r_reason')
