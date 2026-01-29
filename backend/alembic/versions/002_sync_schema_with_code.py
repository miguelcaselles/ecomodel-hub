"""Sync DB schema with current SQLAlchemy models

Revision ID: 002
Revises: 001
Create Date: 2026-01-29 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === ECONOMIC_MODELS TABLE ===

    # Add partition_survival to modeltype enum
    op.execute("ALTER TYPE modeltype ADD VALUE IF NOT EXISTS 'partition_survival'")

    # Add missing columns
    op.add_column('economic_models', sa.Column('script_content', sa.Text(), nullable=True))
    op.add_column('economic_models', sa.Column('script_hash', sa.String(), nullable=True))
    op.add_column('economic_models', sa.Column('is_published', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('economic_models', sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    # Copy data from structure to config if structure exists
    op.execute("UPDATE economic_models SET config = structure WHERE structure IS NOT NULL AND config IS NULL")

    # === PARAMETERS TABLE ===
    # The parameters table schema has changed significantly.
    # Old: scenario-level parameters (scenario_id, value, category enum, etc.)
    # New: model-level parameter templates (model_id, display_name, data_type, etc.)

    # Create new enum types for parameters
    op.execute("CREATE TYPE datatype AS ENUM ('float', 'int', 'percentage', 'currency', 'boolean')")
    op.execute("CREATE TYPE inputtype AS ENUM ('slider', 'number', 'select', 'checkbox')")

    # Drop old parameters table and recreate with new schema
    op.drop_table('parameters')

    op.create_table(
        'parameters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('data_type', postgresql.ENUM('float', 'int', 'percentage', 'currency', 'boolean', name='datatype', create_type=False), nullable=False, server_default='float'),
        sa.Column('input_type', postgresql.ENUM('slider', 'number', 'select', 'checkbox', name='inputtype', create_type=False), nullable=False, server_default='number'),
        sa.Column('default_value', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('constraints', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('distribution', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_country_specific', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('is_editable_by_local', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=True),
        sa.Column('unit', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['model_id'], ['economic_models.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop new parameters table
    op.drop_table('parameters')

    # Recreate old parameters table
    op.create_table(
        'parameters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scenario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', postgresql.ENUM('clinical', 'cost', 'utility', 'probability', 'discount', 'other', name='parametercategory', create_type=False), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('distribution', sa.String(), nullable=True),
        sa.Column('lower_bound', sa.Float(), nullable=True),
        sa.Column('upper_bound', sa.Float(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Remove columns from economic_models
    op.drop_column('economic_models', 'config')
    op.drop_column('economic_models', 'is_published')
    op.drop_column('economic_models', 'script_hash')
    op.drop_column('economic_models', 'script_content')

    # Drop new enum types
    op.execute('DROP TYPE IF EXISTS inputtype')
    op.execute('DROP TYPE IF EXISTS datatype')
