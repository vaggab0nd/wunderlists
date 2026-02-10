# 📋 Wunderlists - Your Digital Life Hub

A modern task tracking and life organization application inspired by the beloved Wunderlist. Built for busy professionals juggling job hunting, family activities, calendar management, and daily tasks - all with weather information for your important locations.

## ✨ Features

### Phase 1 - MVP (Current)

- **Task Management** - Create, organize, and track tasks with priorities and due dates
- **Project Lists** - Organize tasks into customizable lists with colors and icons
- **Calendar Integration** - View and manage upcoming events in a clean timeline
- **Weather Widgets** - Real-time weather for locations that matter (work trips, family, home)
- **Clean Dashboard** - One-stop view of your digital life

### Phase 2 - Smart Features (Coming Soon)

- Calendar sync (Google Calendar API)
- Weather alerts for travel days
- Task prioritization suggestions
- Mobile-responsive views
- Task reminders and notifications

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Free OpenWeather API key ([Get one here](https://openweathermap.org/api))

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd wunderlists
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your OpenWeather API key:
   ```
   OPENWEATHER_API_KEY=your_api_key_here
   ```

3. **Start the application**
   ```bash
   ./run.sh
   ```
   Or manually with Docker Compose:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Backend API: `http://localhost:8000`
   - API documentation: `http://localhost:8000/docs`
   - Frontend: See Frontend Setup section below

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast Python web framework
- **PostgreSQL** - Robust relational database
- **SQLAlchemy** - Powerful ORM
- **Alembic** - Database migrations
- **Pydantic** - Data validation

### Frontend
- **React 18** - Modern UI framework
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **shadcn-ui** - Component library
- **Tailwind CSS** - Utility-first styling
- **React Query** - Server state management
- **React Router** - Client-side routing

### Infrastructure
- **Docker** - Containerized deployment
- **Docker Compose** - Easy multi-container orchestration
- **Monorepo** - Frontend and backend in single repository

## 📁 Project Structure

```
wunderlists/ (Monorepo)
├── backend/                # FastAPI Backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy database models
│   │   ├── routes/         # API endpoints
│   │   ├── schemas/        # Pydantic validation schemas
│   │   ├── services/       # Business logic (weather, etc.)
│   │   ├── database.py     # Database configuration
│   │   ├── config.py       # App configuration
│   │   └── main.py         # FastAPI application
│   └── alembic/            # Database migrations
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Route pages
│   │   ├── hooks/          # Custom hooks
│   │   └── App.tsx         # Root component
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml      # Docker orchestration
├── Dockerfile              # Container configuration
├── requirements.txt        # Python dependencies
├── CLAUDE.md               # Detailed development notes
└── README.md
```

## ☁️ AWS Deployment

This project includes comprehensive AWS deployment guides:

- **[AWS_QUICK_START.md](./AWS_QUICK_START.md)** - Deploy to AWS in 30 minutes
- **[AWS_DEPLOYMENT.md](./AWS_DEPLOYMENT.md)** - Complete deployment guide with security, monitoring, and best practices

**Architecture:**
- **Frontend**: AWS Amplify (auto-deploy from GitHub)
- **Backend**: AWS App Runner (auto-deploy from GitHub)
- **Database**: Amazon RDS PostgreSQL

**Estimated Costs:**
- Development: ~$40-65/month (includes free tier)
- Production: ~$150-265/month

## 🔧 Development

### Backend Development (without Docker)

1. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL**
   - Install PostgreSQL
   - Create database: `wunderlists_db`
   - Create user: `wunderlists_user`
   - Update `DATABASE_URL` in `.env`

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Run the backend server**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
   Backend runs on `http://localhost:8000`

### Frontend Development

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `frontend/.env` and set:
   ```
   VITE_RAILWAY_API_URL=http://localhost:8000/api
   ```

4. **Run the development server**
   ```bash
   npm run dev
   ```
   Frontend runs on `http://localhost:5173`

5. **Build for production**
   ```bash
   npm run build
   ```

### Running Both Simultaneously

For full-stack development, run both backend and frontend:
- Backend: Terminal 1 - `cd backend && uvicorn app.main:app --reload`
- Frontend: Terminal 2 - `cd frontend && npm run dev`

### API Endpoints

#### Tasks
- `GET /api/tasks/` - List all tasks
- `POST /api/tasks/` - Create a task
- `GET /api/tasks/{id}` - Get task details
- `PUT /api/tasks/{id}` - Update a task
- `DELETE /api/tasks/{id}` - Delete a task

#### Lists
- `GET /api/lists/` - List all lists/projects
- `POST /api/lists/` - Create a list
- `GET /api/lists/{id}` - Get list details
- `PUT /api/lists/{id}` - Update a list
- `DELETE /api/lists/{id}` - Delete a list

#### Calendar Events
- `GET /api/calendar/events` - List all events
- `POST /api/calendar/events` - Create an event
- `GET /api/calendar/events/{id}` - Get event details
- `PUT /api/calendar/events/{id}` - Update an event
- `DELETE /api/calendar/events/{id}` - Delete an event

#### Locations
- `GET /api/locations/` - List all locations
- `POST /api/locations/` - Add a location
- `GET /api/locations/{id}` - Get location details
- `PUT /api/locations/{id}` - Update a location
- `DELETE /api/locations/{id}` - Delete a location

#### Weather
- `GET /api/weather/dashboard` - Get weather for all dashboard locations
- `GET /api/weather/current/{location_id}` - Get current weather for a location
- `GET /api/weather/forecast/{location_id}` - Get forecast for a location

## 🎯 Use Cases

### Job Hunting
- Track job applications with due dates
- Set interview reminders
- Organize by company or role type
- Weather check for interview locations

### Family & Kids
- Track kids' activities and schedules
- School events calendar
- After-school activity planning
- Birthday reminders

### Travel & Locations
- Weather for upcoming work trips
- Family visit planning
- Holiday destination weather
- Multi-city weather comparison

### Daily Life
- Grocery shopping lists
- Home improvement projects
- Personal goals tracking
- Ad hoc task management

## 🌐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `OPENWEATHER_API_KEY` | OpenWeather API key | (required) |
| `DEBUG` | Enable debug mode | `True` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Inspired by the beloved Wunderlist (RIP)
- Built with love for personal productivity
- OpenWeather for weather data

## 🗺️ Roadmap

### Completed ✅
- [x] Dark mode
- [x] Task prioritization (AI-powered)
- [x] Weather alerts for travel
- [x] Habit tracking
- [x] Note-taking
- [x] Modern React frontend
- [x] Monorepo consolidation

### In Progress 🚧
- [ ] Google Calendar integration (partial)
- [ ] Mobile-responsive improvements

### Planned 📋
- [ ] Mobile app (React Native)
- [ ] Recurring tasks
- [ ] Task templates
- [ ] Collaboration features
- [ ] Email notifications
- [ ] Export to CSV/PDF
- [ ] Task time tracking
- [ ] PWA capabilities

## 📜 Project History

**February 2026** - Consolidated frontend and backend into monorepo
- Merged React frontend from separate repository (vaggab0nd/your-digital-hub)
- Legacy vanilla JS frontend archived in `frontend-legacy-vanilla-js/`
- Simplified development workflow

**January 2026** - Initial development
- FastAPI backend created
- Vanilla JS frontend built separately
- Deployed on Railway + Lovable

---

Built with ❤️ for staying organized in a busy life

**Inspired by Wunderlist** - In memory of a great productivity app (RIP, killed by Microsoft)
