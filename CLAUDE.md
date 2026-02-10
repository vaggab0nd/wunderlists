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

**Monorepo Structure**
- Frontend and backend now consolidated in a single repository
- Modern React application located in `frontend/` directory
- Legacy vanilla JS frontend preserved in `frontend-legacy-vanilla-js/`
- Original separate repo: https://github.com/vaggab0nd/your-digital-hub (archived)

**React + TypeScript Stack**
- **React 18.3.1**: Modern UI framework with hooks
- **TypeScript 5.8.3**: Type-safe development
- **Vite 5.4.19**: Fast build tool and dev server
- **shadcn-ui**: Component library built on Radix UI
- **Tailwind CSS 3.4.17**: Utility-first styling
- **React Query**: Server state management
- **React Router**: Client-side routing

**Advanced Features**
- AI-powered task prioritization
- Weather alerts for travel locations (Open-Meteo API)
- Smart task filtering (overdue, due today, prioritized)
- Dark mode support with next-themes
- Habit tracking with streak monitoring
- Note-taking functionality
- Backend health monitoring
- Responsive mobile-first design
- Testing suite with Vitest

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
wunderlists/
├── backend/                      # FastAPI Backend
│   └── app/
│       ├── models/               # SQLAlchemy ORM models
│       ├── routes/               # API endpoint handlers
│       ├── schemas/              # Pydantic validation schemas
│       ├── services/             # Business logic (weather API)
│       ├── config.py             # Environment configuration
│       ├── database.py           # DB connection and session management
│       └── main.py               # FastAPI application entry point
│
├── frontend/                     # React Frontend (Lovable/Modern)
│   ├── src/
│   │   ├── components/           # React components
│   │   │   ├── dashboard/        # Dashboard-specific components
│   │   │   └── ui/               # shadcn-ui components
│   │   ├── pages/                # Route pages
│   │   ├── hooks/                # Custom React hooks (useRailwayData.ts)
│   │   ├── lib/                  # Utility functions
│   │   ├── test/                 # Test utilities
│   │   ├── App.tsx               # Root component
│   │   └── main.tsx              # Entry point
│   ├── public/                   # Static assets
│   ├── package.json              # Frontend dependencies
│   ├── vite.config.ts            # Vite configuration
│   ├── tailwind.config.ts        # Tailwind configuration
│   └── CLAUDE.MD                 # Frontend documentation
│
├── frontend-legacy-vanilla-js/   # Archived vanilla JS frontend
│   ├── templates/
│   └── static/
│
├── docker-compose.yml            # Docker orchestration
├── Dockerfile                    # Backend Docker image
├── requirements.txt              # Python dependencies
├── alembic.ini                   # Database migrations config
├── CLAUDE.md                     # This file
└── README.md                     # Project README
```

## Development Workflow

### Adding a New Feature

1. **Backend Development**
   - Create model in `backend/app/models/`
   - Add Pydantic schemas in `backend/app/schemas/`
   - Implement routes in `backend/app/routes/`
   - Register router in `main.py`
   - Test with FastAPI's `/docs` endpoint

2. **Frontend Development**
   - Add/modify components in `frontend/src/components/`
   - Create pages in `frontend/src/pages/`
   - Update API hooks in `frontend/src/hooks/useRailwayData.ts`
   - Add TypeScript interfaces for new API responses
   - Test with `npm run test` in frontend directory

3. **Full-Stack Integration**
   - Backend runs on port 8000 (default)
   - Frontend dev server runs on port 5173 (Vite default)
   - Configure `VITE_RAILWAY_API_URL` in `frontend/.env`
   - Both can run simultaneously for local development

### Database Migrations

Uses Alembic for schema versioning:
```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Local Development Setup

### Prerequisites
- Python 3.11+ for backend
- Node.js 18+ (recommend using nvm) for frontend
- PostgreSQL database
- Docker & Docker Compose (optional)

### Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your DATABASE_URL and API keys

# Run migrations
alembic upgrade head

# Start backend server
cd backend && uvicorn app.main:app --reload
# Backend runs on http://localhost:8000
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with VITE_RAILWAY_API_URL=http://localhost:8000/api

# Start dev server
npm run dev
# Frontend runs on http://localhost:5173
```

### Running with Docker
```bash
# From project root
docker-compose up --build
# Backend: http://localhost:8000
# Database: PostgreSQL on port 5432
```

## Deployment

### Docker Deployment
- Multi-stage Dockerfile for optimized backend images
- Docker Compose orchestrates backend and database
- Frontend built separately and deployed to Lovable or static hosting
- Environment variables via `.env` file
- Volume mounts for data persistence

### Environment Configuration

**Backend** (`.env` in root):
- `DATABASE_URL` - PostgreSQL connection string
- `OPENWEATHER_API_KEY` - Weather API key (if using legacy endpoints)
- `DEBUG`, `HOST`, `PORT` - Server configuration

**Frontend** (`frontend/.env`):
- `VITE_RAILWAY_API_URL` - Backend API URL (e.g., https://your-api.railway.app/api)

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

### Repository History

**February 2026 - Monorepo Consolidation**
- Merged frontend from separate repository (vaggab0nd/your-digital-hub)
- Consolidated into single monorepo structure
- Legacy vanilla JS frontend preserved in `frontend-legacy-vanilla-js/`
- Modern React frontend now in `frontend/` directory
- Simplified development workflow with co-located frontend and backend

**Original Architecture**
- Backend: https://github.com/vaggab0nd/wunderlists
- Frontend: https://github.com/vaggab0nd/your-digital-hub (now consolidated)
- Frontend was originally built and deployed on Lovable platform

---

**Built by**: Claude (Anthropic AI)
**Date**: January 2026 (Initial), February 2026 (Monorepo Consolidation)
**Purpose**: Personal productivity and life organization
**Inspiration**: Wunderlist (RIP - killed by Microsoft)
