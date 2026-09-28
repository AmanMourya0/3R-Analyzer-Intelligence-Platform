"""add_servicenow_fields

Revision ID: 80a7d13b10c8
Revises: 20260924_add_three_r_reason
Create Date: 2026-09-28 18:47:37.338399

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80a7d13b10c8'
down_revision: Union[str, Sequence[str], None] = '20260924_add_three_r_reason'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('incidents', sa.Column('caller', sa.String(length=150), nullable=True))
    op.add_column('incidents', sa.Column('assigned_to', sa.String(length=150), nullable=True))
    op.add_column('incidents', sa.Column('resolved_by', sa.String(length=150), nullable=True))
    op.add_column('incidents', sa.Column('kb_number', sa.String(length=100), nullable=True))
    op.add_column('incidents', sa.Column('it_batch_job', sa.String(length=100), nullable=True))
    op.add_column('incidents', sa.Column('reassignment_count', sa.Integer(), nullable=True))
    op.add_column('incidents', sa.Column('offending_ci', sa.String(length=150), nullable=True))
    op.add_column('incidents', sa.Column('offending_ci_category', sa.String(length=150), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('incidents', 'offending_ci_category')
    op.drop_column('incidents', 'offending_ci')
    op.drop_column('incidents', 'reassignment_count')
    op.drop_column('incidents', 'it_batch_job')
    op.drop_column('incidents', 'kb_number')
    op.drop_column('incidents', 'resolved_by')
    op.drop_column('incidents', 'assigned_to')
    op.drop_column('incidents', 'caller')
