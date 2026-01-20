# Claude.md - Development Notes

## Project Overview

This is a comprehensive task management and life organization application built as a Wunderlist-inspired productivity hub. The application helps users manage tasks, calendar events, and track weather for important locations.

## Architecture Decisions

### Backend Architecture

**FastAPI Framework**
- Chosen for its modern async support, automatic API documentation, and excellent performance
- Built-in data validation with Pydantic
- Easy to test and maintain

**Database Design**
- PostgreSQL for relational data with strong ACID guarantees
- Four main entities:
  - `tasks` - Individual to-do items with priorities and due dates
  - `lists` - Project/category groupings for tasks
  - `calendar_events` - Time-based events with locations
  - `locations` - Places for weather tracking

**API Structure**
- RESTful design following standard HTTP methods
- Consistent response formats
- Proper status codes (200, 201, 204, 404, etc.)
- Query parameters for filtering and pagination

### Frontend Architecture

**Frontend Repository**
- Frontend is hosted separately at: https://github.com/vaggab0nd/your-digital-hub
- Deployed and running on Lovable platform
- Connects to this backend API

**Vanilla JavaScript Approach**
- No framework overhead for faster initial load
- Direct DOM manipulation for simplicity
- Modern ES6+ features
- Async/await for API calls

**UI/UX Design**
- Card-based dashboard layout
- Modal dialogs for data entry
- Color-coded priorities for visual clarity
- Real-time updates after CRUD operations
- Empty states with helpful messages

### Integration Points

**Weather Service**
- OpenWeatherMap API integration
- Caches location data to minimize API calls
- Graceful error handling for API failures
- Support for current weather and forecasts

## Key Features Implementation

### Task Management
- Priority levels: low, medium, high, urgent
- Visual indicators with color-coded borders
- Checkbox for quick completion toggle
- Due date tracking
- List/project association

### Lists/Projects
- Customizable with colors and icons (emoji support)
- Acts as task categories
- Helps organize different life areas (work, personal, family)

### Calendar Events
- Start and end times
- Optional location field
- Sorted chronologically
- Future-focused view (only shows upcoming events)

### Weather Widgets
- Dashboard integration
- Multiple location tracking
- Temperature in Celsius
- Weather description
- Error handling for API failures

## File Structure

```
backend/app/
├── models/           # SQLAlchemy ORM models
├── routes/           # API endpoint handlers
├── schemas/          # Pydantic validation schemas
├── services/         # Business logic (weather API)
├── config.py         # Environment configuration
├── database.py       # DB connection and session management
└── main.py           # FastAPI application entry point
```

**Note:** Frontend is maintained in a separate repository at https://github.com/vaggab0nd/your-digital-hub and hosted on Lovable.

## Development Workflow

### Adding a New Feature

1. **Backend** (This Repository)
   - Create model in `backend/app/models/`
   - Add Pydantic schemas in `backend/app/schemas/`
   - Implement routes in `backend/app/routes/`
   - Register router in `main.py`

2. **Frontend** (Separate Repository)
   - Frontend changes are made in https://github.com/vaggab0nd/your-digital-hub
   - Deployed automatically via Lovable platform

### Database Migrations

Uses Alembic for schema versioning:
```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Deployment

### Docker Deployment
- Multi-stage Dockerfile for optimized images
- Docker Compose orchestrates backend and database
- Environment variables via `.env` file
- Volume mounts for data persistence

### Environment Configuration
Required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `OPENWEATHER_API_KEY` - Weather API key
- `DEBUG`, `HOST`, `PORT` - Server configuration

## Future Enhancements

### Phase 2 Roadmap
1. **Google Calendar Sync**
   - OAuth2 integration
   - Bidirectional sync
   - Conflict resolution

2. **Smart Features**
   - Task prioritization based on due dates
   - Weather alerts for travel days
   - Suggested task scheduling

3. **Mobile Support**
   - Responsive design improvements
   - PWA capabilities
   - Touch-optimized interactions

4. **Notifications**
   - Email reminders
   - Browser notifications
   - Webhook support

### Technical Debt
- Add comprehensive test suite (pytest for backend, Jest for frontend)
- Implement proper authentication/authorization
- Add request rate limiting
- Implement caching layer (Redis)
- Add logging and monitoring
- API versioning strategy

## API Design Patterns

### Consistent Response Format
```json
{
  "id": 1,
  "title": "Task name",
  "created_at": "2024-01-18T10:00:00Z",
  "updated_at": "2024-01-18T12:00:00Z"
}
```

### Error Handling
```json
{
  "detail": "Resource not found"
}
```

### Filtering and Pagination
- Query parameters for filters: `?is_completed=false`
- Pagination: `?skip=0&limit=100`
- Date ranges: `?start_date=2024-01-01`

## Performance Considerations

### Database
- Indexes on frequently queried fields (`id`, `created_at`, `is_completed`)
- Connection pooling via SQLAlchemy
- Lazy loading for relationships

### Frontend
- Minimal JavaScript bundle size
- CSS with modern features (Grid, Flexbox)
- Debounced API calls for search/filter
- Optimistic UI updates

### Caching Strategy
- Weather data cached at service layer
- Static assets served with cache headers
- Database query result caching (future)

## Security Considerations

### Current Implementation
- Input validation with Pydantic
- SQL injection protection via ORM
- CORS configuration
- Environment variable secrets

### Future Additions
- User authentication (JWT tokens)
- API rate limiting
- HTTPS enforcement
- CSP headers
- XSS protection
- CSRF tokens for forms

## Testing Strategy

### Backend Testing (Recommended)
```python
# pytest with fixtures
def test_create_task(client, db_session):
    response = client.post("/api/tasks/", json={
        "title": "Test task",
        "priority": "high"
    })
    assert response.status_code == 201
```

### Frontend Testing (Recommended)
- Jest for unit tests
- Cypress for E2E tests
- Testing user flows (create task, complete task, etc.)

## Maintenance

### Regular Tasks
- Update dependencies monthly
- Review and rotate API keys
- Database backups
- Monitor error logs
- Performance profiling

### Monitoring Metrics
- API response times
- Database query performance
- Error rates
- Active users
- Weather API usage

## Local Development Tips

1. **Database GUI**: Use pgAdmin or DBeaver to inspect database
2. **API Testing**: Use FastAPI's built-in `/docs` (Swagger UI)
3. **Hot Reload**: `uvicorn --reload` watches for file changes
4. **Docker Logs**: `docker-compose logs -f` to monitor in real-time

## Notes

- Built with focus on simplicity and maintainability
- Prioritizes user experience over technical complexity
- Architecture allows for easy feature additions
- Designed for single-user use (authentication coming in Phase 2)

---

**Built by**: Claude (Anthropic AI)
**Date**: January 2026
**Purpose**: Personal productivity and life organization
