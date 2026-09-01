# Job Tracker API + Dashboard

Full-stack job application tracker with a FastAPI backend and React dashboard.

## Features
- JWT authentication
- Applications CRUD
- Event-driven application timeline
- Notes and follow-ups
- Status transition tracking
- Analytics: summary, funnel, recruiter and status duration
- React dashboard with charts

## Tech Stack

**Backend:** FastAPI, SQLAlchemy, PostgreSQL, Alembic, Pydantic, pytest  
**Frontend:** React, Vite, TypeScript, TanStack Query, Recharts  
**Delivery:** Docker, GitHub Actions

## Local Development

Create the local environment file:

```bash
cp .env.example .env
```

Start PostgreSQL and the API:

```bash
docker compose up --build
```

In a second terminal, start the frontend development server:

```bash
cd frontend
npm install
npm run dev
```

API documentation is available at `http://localhost:8000/docs`.

## Production Docker Image

The production Dockerfile builds the React frontend and serves it from the FastAPI application, so the deployed app uses one public origin and does not require CORS configuration.

At container startup the app runs pending Alembic migrations and then starts Uvicorn on the platform-provided `PORT`.

Required production variables:

```text
SECRET_KEY=<strong-random-secret>
DATABASE_URL=postgresql://user:password@host:5432/database
```

`DATABASE_URL` from managed PostgreSQL providers is accepted directly. The application also keeps the `POSTGRES_*` variables for local Docker Compose.

### Railway

1. Create a Railway project from this GitHub repository.
2. Add a PostgreSQL database to the project.
3. Set `SECRET_KEY` to a strong random value.
4. Set `DATABASE_URL` to the PostgreSQL service connection variable/reference.
5. Deploy the repository. Railway detects the Dockerfile automatically.
6. Generate a public domain for the application service.
7. Set the health check path to `/health`.

Useful endpoints after deployment:

- `/` - React dashboard
- `/docs` - Swagger / OpenAPI documentation
- `/health` - health check
- `/api/v1/...` - REST API

## Demo Flow

For a short portfolio demo:

1. Register a user.
2. Log in.
3. Create a job application.
4. Change its status.
5. Add a note and inspect the timeline.
6. Open Analytics to show funnel and status metrics.

## Project Highlights
- Clean backend layering with API, services, schemas and models
- Event-driven timeline and status history
- Analytics pipeline on top of application data
- Same-origin production deployment for API + React
- Automated backend lint/tests and frontend build in CI
