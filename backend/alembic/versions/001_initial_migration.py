"""Initial migration with all tables

Revision ID: 001
Revises:
Create Date: 2026-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE userrole AS ENUM ('global_admin', 'local_user', 'viewer')")
    op.execute("CREATE TYPE modeltype AS ENUM ('decision_tree', 'markov', 'microsimulation', 'budget_impact', 'cohort')")
    op.execute("CREATE TYPE parametercategory AS ENUM ('clinical', 'cost', 'utility', 'probability', 'discount', 'other')")
    op.execute("CREATE TYPE simulationstatus AS ENUM ('pending', 'running', 'completed', 'failed')")

    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('country', sa.String(length=2), nullable=False),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('role', postgresql.ENUM('global_admin', 'local_user', 'viewer', name='userrole', create_type=False), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create economic_models table
    op.create_table(
        'economic_models',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('model_type', postgresql.ENUM('decision_tree', 'markov', 'microsimulation', 'budget_impact', 'cohort', name='modeltype', create_type=False), nullable=False),
        sa.Column('version', sa.String(), nullable=True),
        sa.Column('structure', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create scenarios table
    op.create_table(
        'scenarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('model_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['model_id'], ['economic_models.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create parameters table
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
        sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create simulations table
    op.create_table(
        'simulations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scenario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'running', 'completed', 'failed', name='simulationstatus', create_type=False), nullable=False),
        sa.Column('results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('simulations')
    op.drop_table('parameters')
    op.drop_table('scenarios')
    op.drop_table('economic_models')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('organizations')

    # Drop enum types
    op.execute('DROP TYPE simulationstatus')
    op.execute('DROP TYPE parametercategory')
    op.execute('DROP TYPE modeltype')
    op.execute('DROP TYPE userrole')
