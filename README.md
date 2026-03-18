# Job Tracker API + Dashboard

## Features
- Authentication (JWT)
- Applications CRUD
- Timeline (events)
- Notes
- Follow-ups
- Analytics (summary, funnel, recruiter, status duration)
- Frontend dashboard

## Tech Stack
Backend:
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic

Frontend:
- React
- Vite
- TypeScript
- React Query
- Recharts

## How to Run

### Backend
```bash
docker compose up --build
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API Docs
http://localhost:8000/docs

## Demo Flow
- Register
- Login
- Create application
- Change status
- Add note
- View analytics

## Project Highlights
- Event-driven timeline
- Status transition tracking
- Analytics pipeline
- Clean architecture
