# Security Implementation

This document describes the security measures implemented in the Wunderlists application.

## Overview

The Wunderlists application implements multiple layers of security to protect user data:

1. **User Authentication** - User accounts with password hashing
2. **Row Level Security (RLS)** - Database-level data isolation
3. **User Context Management** - Session-based user identification
4. **Data Ownership** - All data entities are owned by specific users

## Row Level Security (RLS)

### What is RLS?

Row Level Security is a PostgreSQL feature that allows you to control which rows users can access at the database level. Even if an attacker gains direct database access, RLS policies ensure they can only see their own data.

### Implementation

RLS has been enabled on all tables in the database:
- `users` - Users can only see their own user record
- `tasks` - Users can only access their own tasks
- `lists` - Users can only access their own lists
- `calendar_events` - Users can only access their own calendar events
- `locations` - Users can only access their own locations

### How It Works

1. **User Context**: When a user authenticates, their user ID is stored in a PostgreSQL session variable (`app.current_user_id`)

2. **RLS Policies**: Each table has an RLS policy that filters rows based on the current user ID:
   ```sql
   CREATE POLICY tasks_isolation_policy ON tasks
       FOR ALL
       USING (user_id = current_setting('app.current_user_id', true)::integer);
   ```

3. **Automatic Filtering**: All SQL queries are automatically filtered by PostgreSQL to only return rows belonging to the current user

### Superuser Access

Superusers (administrators) can bypass RLS policies to access all data. This is controlled by:
- The `is_superuser` flag in the users table
- A PostgreSQL function `is_superuser()` that checks this flag
- Additional RLS policies that grant access to superusers

## Database Schema Changes

### New Tables

- **users**: Stores user accounts with authentication information

### Modified Tables

All existing tables now have a `user_id` foreign key that references the `users` table:
- `tasks.user_id`
- `lists.user_id`
- `calendar_events.user_id`
- `locations.user_id`

### Indexes

Indexes have been added on `user_id` columns for performance optimization.

## Authentication Flow

### Current Implementation

The current implementation provides the database foundation for authentication:

1. User accounts can be created in the `users` table
2. Passwords are hashed using bcrypt
3. User context can be set in database sessions

### Future Implementation (Recommended)

For a complete authentication system, you should implement:

1. **API Endpoints**:
   - `POST /api/auth/register` - User registration
   - `POST /api/auth/login` - User login (returns JWT token)
   - `POST /api/auth/logout` - User logout
   - `GET /api/auth/me` - Get current user info

2. **JWT Tokens**:
   - Generate JWT tokens on login
   - Include user_id in token payload
   - Validate tokens on each request

3. **Middleware**:
   - Extract JWT token from request headers
   - Validate token and extract user_id
   - Set user context in database session using `set_user_context()`
   - Attach user info to request object

4. **Protected Routes**:
   - Require authentication for all data endpoints
   - Return 401 Unauthorized if no valid token

## Security Best Practices

### What's Implemented

✅ Password hashing with bcrypt
✅ Row Level Security on all tables
✅ User data isolation
✅ Indexed foreign keys
✅ Database-level access control

### What's Needed (Future)

⚠️ API authentication with JWT tokens
⚠️ Rate limiting on API endpoints
⚠️ HTTPS enforcement in production
⚠️ CSRF protection for forms
⚠️ Session management
⚠️ Password strength requirements
⚠️ Account lockout after failed login attempts
⚠️ Email verification for new accounts
⚠️ Password reset functionality

## Testing RLS

You can test RLS policies directly in PostgreSQL:

```sql
-- Create two test users
INSERT INTO users (email, username, hashed_password) VALUES
    ('user1@example.com', 'user1', 'hashed_password_1'),
    ('user2@example.com', 'user2', 'hashed_password_2');

-- Create tasks for each user
INSERT INTO tasks (title, user_id) VALUES
    ('User 1 Task', 1),
    ('User 2 Task', 2);

-- Set user context to user 1
SET app.current_user_id = 1;

-- This will only return user 1's tasks
SELECT * FROM tasks;

-- Set user context to user 2
SET app.current_user_id = 2;

-- This will only return user 2's tasks
SELECT * FROM tasks;

-- Clear user context
RESET app.current_user_id;

-- Without user context, RLS blocks all access (returns no rows)
SELECT * FROM tasks;
```

## Migration

The security implementation is provided as an Alembic migration located at:
`backend/alembic/versions/001_add_users_and_rls_policies.py`

### Running the Migration

```bash
# Run migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Important Notes

- The migration is designed to work with both new and existing databases
- If tables already exist, it adds the `user_id` column
- If tables don't exist yet, they'll be created by SQLAlchemy with RLS already enabled
- Existing data will have `NULL` user_id values - you'll need to assign ownership manually or create a data migration

## User Context Management

The `backend/app/auth.py` module provides utilities for managing user context:

```python
from backend.app.auth import set_user_context, clear_user_context

# Set user context for current request
set_user_context(db, user_id=1)

# Perform database operations (automatically filtered by RLS)
tasks = db.query(Task).all()  # Only returns tasks for user 1

# Clear user context when done
clear_user_context(db)
```

## Environment Variables

No new environment variables are required for the security implementation. However, for full authentication you may want to add:

```
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
```

## Compatibility

- PostgreSQL 12 or higher (for RLS support)
- SQLAlchemy 1.4+
- Python 3.8+

## Support

For questions or issues related to security implementation, please refer to:
- PostgreSQL RLS documentation: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- SQLAlchemy documentation: https://docs.sqlalchemy.org/
- FastAPI security documentation: https://fastapi.tiangolo.com/tutorial/security/

## Compliance

The security implementation provides:
- Data isolation between users (GDPR compliance)
- Database-level access control (SOC 2 compliance)
- Password hashing with industry-standard bcrypt
- Audit trail with `created_at` and `updated_at` timestamps

## License

This security implementation is part of the Wunderlists project.
