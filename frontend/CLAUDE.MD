# Your Digital Hub - CLAUDE.MD

## Project Overview

**Your Digital Hub** (working name: "Wunderlists") is a comprehensive productivity application that combines task management, note-taking, and habit tracking in a unified interface. Built with modern web technologies, it provides a clean, responsive experience for managing your digital life.

**IMPORTANT**: This repository contains the **FRONTEND ONLY**. The backend API is a separate project.

## Architecture

This is a **frontend-only** React application that connects to a separate backend API:

- **Frontend** (this repo): `https://github.com/vaggab0nd/your-digital-hub`
- **Backend** (separate repo): `https://github.com/vaggab0nd/wunderlists`
- **Hosting**: Backend deployed on Railway
- **Connection**: RESTful API via fetch calls

### API Communication
- Custom hook `useRailwayData.ts` handles all backend communication
- Backend health monitoring via `BackendStatus.tsx` component
- API URL configured via `VITE_RAILWAY_API_URL` environment variable
- Default API: `https://passionate-perception-production.up.railway.app/api`

## Tech Stack

### Core Technologies
- **React 18.3.1**: UI framework with hooks and modern patterns
- **TypeScript 5.8.3**: Type-safe development
- **Vite 5.4.19**: Fast build tool and dev server
- **React Router DOM 6.30.1**: Client-side routing

### UI & Styling
- **shadcn-ui**: Component library built on Radix UI primitives
- **Tailwind CSS 3.4.17**: Utility-first CSS framework
- **Lucide React**: Icon library
- **next-themes**: Dark/light mode support

### State Management & Data Fetching
- **@tanstack/react-query 5.83.0**: Server state management and caching
- **react-hook-form 7.61.1**: Form handling
- **Zod 3.25.76**: Schema validation

### Backend Integration
- **Native Fetch API**: HTTP requests to Railway backend
- **Custom React Query hooks**: Type-safe API interactions
- **No Supabase**: Supabase dependencies are from Lovable template but NOT actively used

### Testing
- **Vitest 3.2.4**: Unit testing framework
- **@testing-library/react 16.0.0**: Component testing utilities
- **jsdom 20.0.3**: DOM implementation for testing

## Project Structure

```
your-digital-hub/
├── src/
│   ├── components/          # React components
│   │   ├── dashboard/       # Dashboard-specific components
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── TaskList.tsx
│   │   │   ├── PrioritizedTasks.tsx    # AI-prioritized tasks view
│   │   │   ├── OverdueTasks.tsx        # Overdue tasks with alerts
│   │   │   ├── TodayTasks.tsx          # Today's tasks with progress
│   │   │   ├── QuickTaskView.tsx       # Dashboard quick overview
│   │   │   ├── TaskSuggestions.tsx     # AI task recommendations
│   │   │   ├── WeatherAlerts.tsx       # Weather monitoring widget
│   │   │   └── BackendStatus.tsx       # Backend health monitoring
│   │   ├── ui/              # shadcn-ui components
│   │   ├── ErrorBoundary.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── NavLink.tsx
│   ├── pages/               # Route pages
│   │   ├── Index.tsx        # Dashboard home (with QuickTaskView)
│   │   ├── Tasks.tsx        # Task management (with tabs)
│   │   ├── Notes.tsx        # Note-taking
│   │   ├── Habits.tsx       # Habit tracking
│   │   ├── Calendar.tsx     # Calendar view
│   │   ├── Users.tsx        # User management
│   │   ├── Settings.tsx     # App settings
│   │   ├── ListPage.tsx     # Custom list view
│   │   └── NotFound.tsx     # 404 page
│   ├── hooks/               # Custom React hooks
│   │   ├── useRailwayData.ts      # Main backend API hook
│   │   ├── useRailwayData.test.tsx
│   │   ├── use-mobile.tsx
│   │   └── use-toast.ts
│   ├── integrations/        # Third-party integrations (legacy)
│   │   └── supabase/        # Unused - from Lovable template
│   ├── lib/                 # Utility functions
│   │   └── utils.ts
│   ├── test/                # Test utilities and fixtures
│   ├── App.tsx              # Root app component
│   ├── main.tsx             # App entry point
│   └── index.css            # Global styles
├── backend-implementation/  # Backend code for wunderlists repo
│   ├── weather_service.py          # Open-Meteo API integration
│   ├── weather_routes_fastapi.py   # FastAPI endpoints
│   ├── weather_routes_flask.py     # Flask endpoints
│   ├── requirements.txt            # Python dependencies
│   └── README.md                   # Integration guide
├── public/                  # Static assets
└── [config files]           # Various config files
```

## Key Features

### 1. Smart Task Management
- **Multiple Views with Tabs**: All Tasks, Due Today, Overdue, Prioritized
- **Smart Filtering**: Backend-powered intelligent task prioritization
- **QuickTaskView Dashboard Widget**: At-a-glance view of overdue and today's tasks
- Custom lists with dynamic routing (`/list/:listId`)
- Task organization with priority badges and visual indicators
- Progress tracking for daily completion
- CRUD operations via Railway API

**New Task Endpoints:**
- `/api/tasks/prioritized` - AI-sorted tasks by priority
- `/api/tasks/overdue` - Tasks past their due date
- `/api/tasks/due-today` - Tasks due today

**Task Components:**
- `PrioritizedTasks.tsx` - Shows AI-prioritized tasks with star indicators
- `OverdueTasks.tsx` - Urgent tasks with red alert styling
- `TodayTasks.tsx` - Daily focus with progress bar
- `QuickTaskView.tsx` - Dashboard sidebar widget
- `TaskSuggestions.tsx` - AI-powered task recommendations

### 2. Weather Alerts
- **Real-time weather monitoring** for travel days
- **Hardcoded locations**: Dublin, Ireland & Île de Ré, France
- **Open-Meteo API integration** (no API key required)
- Warning/info alert classification
- Temperature display in Celsius
- Manual refresh capability

**Weather Endpoints:**
- `/api/weather/alerts` - Get current weather alerts
- `/api/weather/refresh` - Manually refresh weather data

**Backend Implementation Files:**
- `backend-implementation/weather_service.py` - Open-Meteo integration
- `backend-implementation/weather_routes_fastapi.py` - FastAPI routes
- `backend-implementation/weather_routes_flask.py` - Flask routes
- Complete implementation guide in `backend-implementation/README.md`

### 3. Notes
- Note-taking functionality with rich content
- Color-coded organization
- Integrated with main dashboard
- Full CRUD operations

### 4. Habits
- Habit tracking system with streak monitoring
- Daily completion tracking
- Week progress visualization
- Toggle habit completion with special API endpoint

### 5. Backend Status Monitoring
- Real-time backend health check (BackendStatus.tsx)
- Visual indicator (connected/offline/checking)
- Auto-refresh every 30 seconds
- Manual refresh on click

### 6. Responsive Design
- Mobile-first approach
- Sidebar navigation (collapsible on mobile)
- Responsive breakpoints using Tailwind
- Optimized layouts for dashboard widgets

## Architecture Patterns

### Code Splitting
The app uses React lazy loading for all route components to optimize initial load time:
```typescript
const Index = lazy(() => import("./pages/Index"));
const Tasks = lazy(() => import("./pages/Tasks"));
// etc.
```

### Error Handling
- Custom `ErrorBoundary` component wraps the entire app
- Catches and handles React errors gracefully

### Loading States
- `LoadingSpinner` component for Suspense fallback
- Consistent loading experience across routes

### Routing Structure
```
/ → Index (Dashboard with QuickTaskView, WeatherAlerts, TaskSuggestions)
/assigned → Tasks (Assigned view)
/starred → Tasks (Starred view)
/today → Tasks (Today view)
/tasks → Tasks (Tabbed view: All/Today/Overdue/Prioritized)
/list/:listId → ListPage (Custom list)
/notes → Notes
/habits → Habits
/calendar → Calendar
/users → Users
/settings → Settings
/* → NotFound (404)
```

### Tasks Page Tab Navigation
The `/tasks` route now features a tabbed interface:
- **All Tasks**: Complete list with client-side grouping
- **Due Today**: Backend-filtered tasks due today with progress bar
- **Overdue**: Urgent tasks with red alert styling
- **Prioritized**: AI-sorted tasks by priority with star indicators

Each tab fetches from dedicated backend endpoints for optimal performance.

## Development Commands

```bash
npm run dev              # Start development server
npm run build            # Production build
npm run build:dev        # Development build
npm run preview          # Preview production build
npm run lint             # Run ESLint
npm run test             # Run tests once
npm run test:watch       # Run tests in watch mode
npm run test:coverage    # Generate test coverage report
```

## Environment Setup

### Prerequisites
- Node.js (recommended: use nvm)
- npm or bun package manager
- Backend API running (see https://github.com/vaggab0nd/wunderlists)

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Railway API Configuration (REQUIRED)
VITE_RAILWAY_API_URL="https://your-api-url.up.railway.app/api"

# Legacy Supabase config (NOT USED - from Lovable template)
# VITE_SUPABASE_PROJECT_ID="..."
# VITE_SUPABASE_PUBLISHABLE_KEY="..."
# VITE_SUPABASE_URL="..."
```

The app will use a default Railway API URL if not specified, but it's recommended to set your own.

## Component Library (shadcn-ui)

The project uses shadcn-ui components, which are:
- Located in `src/components/ui/`
- Built on Radix UI primitives
- Fully customizable and owned by the project
- Styled with Tailwind CSS

Common components available:
- Button, Card, Dialog, Sheet, Toast
- Form elements: Input, Textarea, Checkbox, Switch, Select
- Navigation: Tabs, Menubar, Navigation Menu
- Data display: Avatar, Progress, Calendar, Accordion
- And many more...

## State Management Approach

### Server State
- Managed by TanStack Query (React Query)
- Automatic caching, background updates, and refetching
- Integrates with Supabase for real-time data

### Client State
- React hooks (useState, useReducer)
- Context API where needed
- Form state managed by react-hook-form

## Styling Guidelines

### Tailwind Configuration
- Custom theme configuration in `tailwind.config.ts`
- Typography plugin enabled
- Animations via tailwindcss-animate
- Theme variables defined in CSS custom properties

### Dark Mode
- Implemented using next-themes
- Supports system preference detection
- Persistent theme selection

## Testing Strategy

### Unit Tests
- Vitest as test runner
- Testing Library for component tests
- jsdom for DOM simulation

### Test Location
- Tests can be co-located with components
- Dedicated `src/test/` directory for test utilities

### Coverage
- Run `npm run test:coverage` to generate coverage reports
- Coverage powered by @vitest/coverage-v8

## Best Practices for Development

### TypeScript
- Strict mode enabled
- Use proper typing for props and state
- Avoid `any` type unless absolutely necessary

### Components
- Prefer functional components with hooks
- Keep components small and focused
- Use composition over inheritance
- Extract reusable logic into custom hooks

### Styling
- Use Tailwind utility classes
- Follow mobile-first responsive design
- Use CSS custom properties for theming
- Maintain consistent spacing and sizing

### Performance
- Lazy load routes and heavy components
- Use React.memo() for expensive renders
- Optimize images and assets
- Monitor bundle size

### Code Organization
- One component per file
- Group related components in directories
- Keep utility functions in `lib/`
- Use absolute imports with `@/` prefix

## Backend Integration

### Railway API Connection

This frontend connects to a separate Node.js/Express backend hosted on Railway. All backend code is in a separate repository: `https://github.com/vaggab0nd/wunderlists`

### API Hook (`useRailwayData.ts`)

The main hook provides typed interfaces and React Query hooks for all resources:

**Data Types:**
- `Task`: Tasks with title, completed status, due date, priority, category
- `Habit`: Habits with name, icon, streak, completion tracking
- `Note`: Notes with title, content, color coding

**Available Hooks:**

Tasks:
- `useTasks()`: Fetch all tasks
- `useCreateTask()`: Create new task
- `useUpdateTask()`: Update existing task
- `useDeleteTask()`: Delete task
- `usePrioritizedTasks()`: Fetch AI-prioritized tasks (NEW)
- `useOverdueTasks()`: Fetch overdue tasks (NEW)
- `useDueTodayTasks()`: Fetch tasks due today (NEW)
- `useTaskSuggestions()`: Fetch AI task suggestions
- `useGenerateTaskSuggestions()`: Generate new task suggestions

Habits:
- `useHabits()`: Fetch all habits
- `useCreateHabit()`: Create new habit
- `useUpdateHabit()`: Update existing habit
- `useToggleHabit()`: Toggle habit completion (special endpoint)
- `useDeleteHabit()`: Delete habit

Notes:
- `useNotes()`: Fetch all notes
- `useCreateNote()`: Create new note
- `useUpdateNote()`: Update existing note
- `useDeleteNote()`: Delete note

Users:
- `useUsers()`: Fetch all users
- `useCreateUser()`: Create new user
- `useUpdateUser()`: Update existing user
- `useDeleteUser()`: Delete user

Calendar:
- `useCalendarEvents()`: Fetch calendar events
- `useSyncGoogleCalendar()`: Sync with Google Calendar
- `useConnectGoogleCalendar()`: Connect Google Calendar

Weather:
- `useWeatherAlerts()`: Fetch weather alerts for travel locations (NEW)
- `useRefreshWeatherAlerts()`: Manually refresh weather data (NEW)

### API Configuration

```typescript
// Environment variable (recommended)
VITE_RAILWAY_API_URL="https://your-api.up.railway.app/api"

// Default fallback in code
const RAILWAY_API_URL = import.meta.env.VITE_RAILWAY_API_URL ||
  "https://passionate-perception-production.up.railway.app/api";
```

### Common Patterns

**Fetching Data:**
```typescript
const { data: tasks, isLoading, error } = useTasks();
```

**Creating Resources:**
```typescript
const createTask = useCreateTask();
createTask.mutate({ title: "New task", completed: false });
```

**Updating Resources:**
```typescript
const updateTask = useUpdateTask();
updateTask.mutate({ id: "123", title: "Updated title" });
```

**Cache Invalidation:**
- All mutations automatically invalidate relevant queries
- React Query refetches data to keep UI in sync
- 30-second stale time for optimal performance

### Error Handling

- Network errors caught and thrown with descriptive messages
- React Query retry logic (1 retry by default)
- HTTP status codes checked before parsing response

## Weather Alerts Implementation

### Overview
The weather alerts feature monitors weather conditions for hardcoded travel locations (Dublin, Ireland and Île de Ré, France) using the free Open-Meteo API.

### Frontend Components
- **WeatherAlerts.tsx**: Main dashboard widget displaying current weather
- **useWeatherAlerts()**: React Query hook fetching from `/api/weather/alerts`
- **useRefreshWeatherAlerts()**: Mutation for manual refresh

### Backend Implementation
This repository includes complete backend implementation code in `backend-implementation/`:

**Files Provided:**
1. `weather_service.py` - Core service using Open-Meteo API
   - Fetches weather for Dublin (53.3498°N, 6.2603°W)
   - Fetches weather for Île de Ré (46.2°N, 1.4°W)
   - Maps WMO weather codes to human-readable conditions
   - Classifies alerts as "warning" or "info"

2. `weather_routes_fastapi.py` - FastAPI endpoint implementation
   - `GET /api/weather/alerts` - Returns weather alerts
   - `POST /api/weather/refresh` - Triggers refresh

3. `weather_routes_flask.py` - Flask endpoint implementation (alternative)
   - Same endpoints as FastAPI version
   - Includes async helper for Flask

4. `requirements.txt` - Python dependencies (httpx)

5. `README.md` - Complete integration guide

**Integration Steps:**
1. Copy files to wunderlists backend repository
2. Install dependencies: `pip install httpx`
3. Register routes in main application
4. Deploy to Railway
5. Frontend automatically connects to new endpoints

**API Response Format:**
```typescript
{
  id: string;
  task_id: string;
  location: string;           // "Dublin, Ireland"
  date: string;               // ISO date
  weather_condition: string;  // "Partly cloudy", "Heavy rain", etc.
  temperature: number;        // Celsius
  alert_type: "warning" | "info";
  message: string;           // Human-readable alert
  created_at: string;
}
```

**Weather Classification:**
- Clear/cloudy conditions: "info"
- Rain/snow/fog/thunderstorms: "warning"
- Temperature always in Celsius
- No API key required (Open-Meteo is free)

## Git Workflow

This project follows a feature branch workflow:
- Main branch: Production-ready code
- Feature branches: Named `claude/*` for development
- Always commit with clear, descriptive messages
- Push to feature branches before creating PRs

## Known Issues & Considerations

### Frontend-Backend Separation
- This is a frontend-only repository
- Requires the backend API to be running (https://github.com/vaggab0nd/wunderlists)
- Backend must be deployed and accessible for full functionality

### Environment Configuration
- Project ID in README.md needs to be replaced with actual Lovable project ID
- `VITE_RAILWAY_API_URL` should be configured for your deployment
- Never commit `.env` files to repository

### Supabase Dependencies
- Supabase packages are present in package.json (from Lovable template)
- These dependencies are NOT actively used
- Can be safely removed if desired, but won't affect functionality

## Resources

### Project Repositories
- **Backend API**: [github.com/vaggab0nd/wunderlists](https://github.com/vaggab0nd/wunderlists)
- **Frontend**: [github.com/vaggab0nd/your-digital-hub](https://github.com/vaggab0nd/your-digital-hub) (this repo)

### Documentation
- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [shadcn-ui Components](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [TanStack Query](https://tanstack.com/query/latest)
- [Railway Documentation](https://docs.railway.app/)
- [Lovable Platform](https://lovable.dev/)

## Contributing

When making changes to this project:

### Frontend Changes (this repo)
1. Understand the existing patterns and follow them
2. Write tests for new features
3. Ensure TypeScript types are properly defined
4. Test responsive behavior on mobile and desktop
5. Run linting and tests before committing
6. Update this CLAUDE.MD if you add significant features or patterns

### Backend Changes
- Backend API changes should be made in the separate repository: https://github.com/vaggab0nd/wunderlists
- Coordinate frontend/backend changes for new features
- Update TypeScript interfaces in `useRailwayData.ts` if API contracts change

### Full-Stack Features
1. Plan API changes in backend repo first
2. Update and deploy backend
3. Update frontend TypeScript types and hooks
4. Test integration between frontend and backend
5. Deploy frontend changes

## Contact & Support

For issues or questions about this project:
- **Frontend issues**: Check GitHub issues in this repository
- **Backend issues**: Check GitHub issues in [wunderlists repository](https://github.com/vaggab0nd/wunderlists)
- **Deployment questions**: Consult the Lovable platform documentation
- **API questions**: Refer to Railway documentation
