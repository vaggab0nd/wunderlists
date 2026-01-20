"""Add is_travel_day field to tasks table

Revision ID: 002
Revises: 001
Create Date: 2026-01-20

This migration adds the is_travel_day boolean field to tasks table
for tracking tasks that involve travel and need weather monitoring.
"""
from alembic import op
import sqlalchemy as sa
import logging

logger = logging.getLogger('alembic.migration')

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    logger.info("Starting migration 002: Add is_travel_day to tasks")

    # Get database connection and inspector
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Check if tasks table exists
    if 'tasks' in inspector.get_table_names():
        # Check if column already exists
        columns = [col['name'] for col in inspector.get_columns('tasks')]

        if 'is_travel_day' not in columns:
            logger.info("Adding is_travel_day column to tasks table...")
            op.add_column('tasks', sa.Column('is_travel_day', sa.Boolean(), nullable=False, server_default='false'))
            logger.info("✓ Added is_travel_day column")
        else:
            logger.info("✓ is_travel_day column already exists, skipping")
    else:
        logger.warning("Tasks table doesn't exist yet, skipping")

    logger.info("Migration 002 completed successfully")


def downgrade() -> None:
    logger.info("Starting downgrade for migration 002")

    # Get database connection and inspector
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Check if tasks table exists
    if 'tasks' in inspector.get_table_names():
        # Check if column exists
        columns = [col['name'] for col in inspector.get_columns('tasks')]

        if 'is_travel_day' in columns:
            logger.info("Removing is_travel_day column from tasks table...")
            op.drop_column('tasks', 'is_travel_day')
            logger.info("✓ Removed is_travel_day column")
        else:
            logger.info("✓ is_travel_day column doesn't exist, skipping")

    logger.info("Downgrade 002 completed successfully")
