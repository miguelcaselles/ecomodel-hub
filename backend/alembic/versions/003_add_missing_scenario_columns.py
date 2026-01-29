"""Add missing columns to scenarios table

Revision ID: 003
Revises: 002
Create Date: 2026-01-29 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to scenarios table
    op.add_column('scenarios', sa.Column('country_code', sa.String(2), nullable=True))
    op.add_column('scenarios', sa.Column('parameter_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('scenarios', sa.Column('is_base_case', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('scenarios', sa.Column('is_locked', sa.Boolean(), server_default='false', nullable=True))


def downgrade() -> None:
    op.drop_column('scenarios', 'is_locked')
    op.drop_column('scenarios', 'is_base_case')
    op.drop_column('scenarios', 'parameter_values')
    op.drop_column('scenarios', 'country_code')
