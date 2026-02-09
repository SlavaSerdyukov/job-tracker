# Job Tracker API

REST API for tracking job applications.

The project allows users to:
- register and log in
- create job applications
- filter and search records
- use pagination
- view statistics
- authenticate via JWT
- run the project using Docker

---

## 🚀 Tech Stack

- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker
- JWT Authentication
- Pydantic v2

---

## 📦 Project Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-username/job-tracker.git
cd job-tracker
```

### 2. Environment Variables

Create `.env` file:

```env
POSTGRES_DB=jobtracker
POSTGRES_USER=jobtracker
POSTGRES_PASSWORD=jobtracker
POSTGRES_HOST=db
POSTGRES_PORT=5432

SECRET_KEY=supersecret
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 3. Run with Docker

```bash
docker compose up --build
```

API will be available at:

```
http://localhost:8000
```

Swagger UI:

```
http://localhost:8000/docs
```

---

## 🗄 Database Migrations

Run inside container:

```bash
docker compose exec api alembic upgrade head
```

---

## 🔐 Authentication

### Register

```http
POST /api/v1/auth/register
```

Request body:

```json
{
  "email": "user@example.com",
  "password": "pass12345"
}
```

---

### Login

```http
POST /api/v1/auth/login
```

Response:

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

Use token in headers:

```
Authorization: Bearer <token>
```

---

## 📄 Applications

### Create Application

```http
POST /api/v1/applications
```

---

### List Applications with Filters

```http
GET /api/v1/applications
```

Query parameters:

| Param | Description |
|-------|-------------|
| q | search query |
| status | application status |
| company | company name |
| sort | sorting field |
| page | page number |
| page_size | page size |

Example:

```http
GET /api/v1/applications?q=google&page=1&page_size=10&sort=-created_at
```

---

### Get Single Application

```http
GET /api/v1/applications/{id}
```

---

### Update Application

```http
PATCH /api/v1/applications/{id}
```

---

### Delete Application

```http
DELETE /api/v1/applications/{id}
```

---

## 📊 Statistics

```http
GET /api/v1/applications/stats
```

Example:

```http
GET /api/v1/applications/stats?q=google
```

Response:

```json
{
  "total": 12,
  "statuses": {
    "applied": 5,
    "interview": 4,
    "offer": 2,
    "rejected": 1
  }
}
```

---

## ⚡ Rate Limiting

Application creation limit:

```
30 requests per minute
```

---

## 🧪 Tests

```bash
pytest
```

---

## 📚 API Documentation

Swagger UI:

```
http://localhost:8000/docs
```

OpenAPI Schema:

```
http://localhost:8000/openapi.json
```

---

## 📌 Features

- JWT Authentication
- CRUD operations
- Search
- Pagination
- Sorting
- Statistics
- Rate limiting
- Docker support
- Alembic migrations
- Pytest coverage

---

## 👨‍💻 Author

Slava Serdyukov  
Backend Developer (Python / FastAPI)

GitHub: https://github.com/SlavaSerdyukov  
LinkedIn: https://linkedin.com/in/slava-serdyukov

