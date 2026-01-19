"""Add users table and Row Level Security policies

Revision ID: 001
Revises:
Create Date: 2026-01-19

This migration:
1. Creates users table
2. Adds user_id to all existing tables
3. Enables Row Level Security (RLS) on all tables
4. Creates RLS policies to ensure data isolation
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Add user_id to tasks table (if it exists)
    # First check if tables exist, if not they'll be created by SQLAlchemy
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'tasks' in tables:
        # Check if user_id column already exists
        columns = [col['name'] for col in inspector.get_columns('tasks')]
        if 'user_id' not in columns:
            op.add_column('tasks', sa.Column('user_id', sa.Integer(), nullable=True))
            op.create_index(op.f('ix_tasks_user_id'), 'tasks', ['user_id'], unique=False)
            op.create_foreign_key('fk_tasks_user_id', 'tasks', 'users', ['user_id'], ['id'])

    if 'lists' in tables:
        columns = [col['name'] for col in inspector.get_columns('lists')]
        if 'user_id' not in columns:
            op.add_column('lists', sa.Column('user_id', sa.Integer(), nullable=True))
            op.create_index(op.f('ix_lists_user_id'), 'lists', ['user_id'], unique=False)
            op.create_foreign_key('fk_lists_user_id', 'lists', 'users', ['user_id'], ['id'])

    if 'calendar_events' in tables:
        columns = [col['name'] for col in inspector.get_columns('calendar_events')]
        if 'user_id' not in columns:
            op.add_column('calendar_events', sa.Column('user_id', sa.Integer(), nullable=True))
            op.create_index(op.f('ix_calendar_events_user_id'), 'calendar_events', ['user_id'], unique=False)
            op.create_foreign_key('fk_calendar_events_user_id', 'calendar_events', 'users', ['user_id'], ['id'])

    if 'locations' in tables:
        columns = [col['name'] for col in inspector.get_columns('locations')]
        if 'user_id' not in columns:
            op.add_column('locations', sa.Column('user_id', sa.Integer(), nullable=True))
            op.create_index(op.f('ix_locations_user_id'), 'locations', ['user_id'], unique=False)
            op.create_foreign_key('fk_locations_user_id', 'locations', 'users', ['user_id'], ['id'])

    # Enable Row Level Security on all tables
    # RLS ensures that users can only access their own data at the database level
    op.execute("""
        -- Enable RLS on users table
        ALTER TABLE users ENABLE ROW LEVEL SECURITY;

        -- Users can only see their own user record
        CREATE POLICY users_isolation_policy ON users
            FOR ALL
            USING (id = current_setting('app.current_user_id', true)::integer);
    """)

    # Only enable RLS on tables that exist
    if 'tasks' in tables:
        op.execute("""
            ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

            -- Tasks RLS policy: users can only access their own tasks
            CREATE POLICY tasks_isolation_policy ON tasks
                FOR ALL
                USING (user_id = current_setting('app.current_user_id', true)::integer);
        """)

    if 'lists' in tables:
        op.execute("""
            ALTER TABLE lists ENABLE ROW LEVEL SECURITY;

            -- Lists RLS policy: users can only access their own lists
            CREATE POLICY lists_isolation_policy ON lists
                FOR ALL
                USING (user_id = current_setting('app.current_user_id', true)::integer);
        """)

    if 'calendar_events' in tables:
        op.execute("""
            ALTER TABLE calendar_events ENABLE ROW LEVEL SECURITY;

            -- Calendar events RLS policy: users can only access their own events
            CREATE POLICY calendar_events_isolation_policy ON calendar_events
                FOR ALL
                USING (user_id = current_setting('app.current_user_id', true)::integer);
        """)

    if 'locations' in tables:
        op.execute("""
            ALTER TABLE locations ENABLE ROW LEVEL SECURITY;

            -- Locations RLS policy: users can only access their own locations
            CREATE POLICY locations_isolation_policy ON locations
                FOR ALL
                USING (user_id = current_setting('app.current_user_id', true)::integer);
        """)

    # Create a function to bypass RLS for superusers
    op.execute("""
        -- Function to check if current user is superuser
        CREATE OR REPLACE FUNCTION is_superuser() RETURNS BOOLEAN AS $$
        DECLARE
            user_id INTEGER;
            is_super BOOLEAN;
        BEGIN
            user_id := current_setting('app.current_user_id', true)::integer;
            IF user_id IS NULL THEN
                RETURN false;
            END IF;

            SELECT is_superuser INTO is_super FROM users WHERE id = user_id;
            RETURN COALESCE(is_super, false);
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)

    # Add bypass policies for superusers on all tables
    if 'tasks' in tables:
        op.execute("""
            CREATE POLICY tasks_superuser_policy ON tasks
                FOR ALL
                TO PUBLIC
                USING (is_superuser());
        """)

    if 'lists' in tables:
        op.execute("""
            CREATE POLICY lists_superuser_policy ON lists
                FOR ALL
                TO PUBLIC
                USING (is_superuser());
        """)

    if 'calendar_events' in tables:
        op.execute("""
            CREATE POLICY calendar_events_superuser_policy ON calendar_events
                FOR ALL
                TO PUBLIC
                USING (is_superuser());
        """)

    if 'locations' in tables:
        op.execute("""
            CREATE POLICY locations_superuser_policy ON locations
                FOR ALL
                TO PUBLIC
                USING (is_superuser());
        """)


def downgrade() -> None:
    # Drop RLS policies and disable RLS
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    # Drop function
    op.execute("DROP FUNCTION IF EXISTS is_superuser();")

    # Drop RLS policies and disable RLS on each table
    if 'tasks' in tables:
        op.execute("DROP POLICY IF EXISTS tasks_isolation_policy ON tasks;")
        op.execute("DROP POLICY IF EXISTS tasks_superuser_policy ON tasks;")
        op.execute("ALTER TABLE tasks DISABLE ROW LEVEL SECURITY;")
        op.drop_constraint('fk_tasks_user_id', 'tasks', type_='foreignkey')
        op.drop_index(op.f('ix_tasks_user_id'), table_name='tasks')
        op.drop_column('tasks', 'user_id')

    if 'lists' in tables:
        op.execute("DROP POLICY IF EXISTS lists_isolation_policy ON lists;")
        op.execute("DROP POLICY IF EXISTS lists_superuser_policy ON lists;")
        op.execute("ALTER TABLE lists DISABLE ROW LEVEL SECURITY;")
        op.drop_constraint('fk_lists_user_id', 'lists', type_='foreignkey')
        op.drop_index(op.f('ix_lists_user_id'), table_name='lists')
        op.drop_column('lists', 'user_id')

    if 'calendar_events' in tables:
        op.execute("DROP POLICY IF EXISTS calendar_events_isolation_policy ON calendar_events;")
        op.execute("DROP POLICY IF EXISTS calendar_events_superuser_policy ON calendar_events;")
        op.execute("ALTER TABLE calendar_events DISABLE ROW LEVEL SECURITY;")
        op.drop_constraint('fk_calendar_events_user_id', 'calendar_events', type_='foreignkey')
        op.drop_index(op.f('ix_calendar_events_user_id'), table_name='calendar_events')
        op.drop_column('calendar_events', 'user_id')

    if 'locations' in tables:
        op.execute("DROP POLICY IF EXISTS locations_isolation_policy ON locations;")
        op.execute("DROP POLICY IF EXISTS locations_superuser_policy ON locations;")
        op.execute("ALTER TABLE locations DISABLE ROW LEVEL SECURITY;")
        op.drop_constraint('fk_locations_user_id', 'locations', type_='foreignkey')
        op.drop_index(op.f('ix_locations_user_id'), table_name='locations')
        op.drop_column('locations', 'user_id')

    # Drop users RLS
    op.execute("DROP POLICY IF EXISTS users_isolation_policy ON users;")
    op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY;")

    # Drop users table
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
