<div align="center">

# Feature Specification Generator API

Production-ready FastAPI backend with async LLM generation via Celery + Redis, JWT auth, and Docker Compose orchestration.

<p align="center">
  <img alt="FastAPI" src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" width="220"/>
</p>

<p align="center">
    <img alt="python" src="https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white"/>
    <img alt="fastapi" src="https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white"/>
    <img alt="sqlalchemy" src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white"/>
    <img alt="alembic" src="https://img.shields.io/badge/Alembic-migrations-222222"/>
    <img alt="tests" src="https://img.shields.io/badge/tests-pytest-0A9EDC"/>
    <img alt="docs" src="https://img.shields.io/badge/docs-Swagger%20%2B%20ReDoc-85EA2D"/>
    <img alt="celery" src="https://img.shields.io/badge/Celery-task%20queue-37814A?logo=celery&logoColor=white"/>
    <img alt="redis" src="https://img.shields.io/badge/Redis-cache%20%2F%20broker-DC382D?logo=redis&logoColor=white"/>
    <img alt="ollama" src="https://img.shields.io/badge/Ollama-local%20LLM-black"/>
</p>

</div>

## What This Project Includes

- JWT authentication based on fastapi-users
- User registration and user management endpoints
- Async feature specification generation with Celery tasks
- Redis as Celery broker/result backend
- Ollama integration for LLM responses
- Readiness and health probes for runtime checks
- Alembic database migrations
- Security middleware baseline:
  - CORS
  - Trusted Host
  - Optional HTTPS redirect
  - Request ID propagation
  - Security headers (CSP, HSTS in production, etc.)
  - In-memory rate limiting for auth paths
  - Suspicious-request logging

## Tech Stack

- Python 3.10
- FastAPI
- SQLAlchemy 2.0
- Alembic
- fastapi-users
- Celery
- Redis
- PostgreSQL
- Ollama
- Pytest

## Architecture (Async Flow)

1. Client calls `POST /api/v1/feature-spec/generate`.
2. API stores a run row and enqueues Celery task to Redis.
3. API returns immediately with `task_id` and `processing` status.
4. Celery worker calls Ollama and persists success/error in DB.
5. Client polls `GET /api/v1/feature-spec/tasks/{task_id}` for result.

## Project Structure

- app/main.py: FastAPI app bootstrap and router registration
- app/core/: settings, database wiring, startup/lifespan, bootstrap logic
- app/api/: health, readiness, OpenAPI customization
- app/middlewares/: security middleware composition and implementations
- app/modules/auth/: auth domain (models, schemas, dependencies, router)
- app/modules/feature_spec/: API layer + application services for feature spec
- app/infrastructure/: Celery app, task workers, Ollama client
- app/scripts/: utility scripts (admin and prompt/model bootstrap)
- alembic/: migration config and versions
- docker-compose.yml: app + celery-worker + redis + ollama

## Setup Guide

### Prerequisites

- Python 3.10+
- PostgreSQL database
- Docker + Docker Compose (recommended)

### 1) Configure environment

Create .env in the project root and set required values.

Required minimum:

- DATABASE_URL
- SECRET_KEY
- CELERY_BROKER_URL
- CELERY_RESULT_BACKEND

Recommended auth bootstrap values:

- AUTH_USERNAME
- AUTH_EMAIL
- AUTH_PASSWORD (or AUTH_PASSWORD_HASH)

LLM values:

- OLLAMA_BASE_URL
- OLLAMA_MODEL
- OLLAMA_TIMEOUT

Compose ports (host -> container):

- FASTAPI_HOST_PORT=8005
- FASTAPI_CONTAINER_PORT=8001
- REDIS_HOST_PORT=6380
- REDIS_CONTAINER_PORT=6379

For Docker Compose in this project use:

- OLLAMA_BASE_URL=http://ollama:11434
- CELERY_BROKER_URL=redis://redis:6379/0
- CELERY_RESULT_BACKEND=redis://redis:6379/1

### 2A) Run locally

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

python -m alembic upgrade head
python -m app.scripts.bootstrap_admin
python -m app.scripts.bootstrap_prompt_template
# terminal 1: api
python -m uvicorn app.main:app --host 0.0.0.0 --port 8005

# terminal 2: worker
celery -A app.infrastructure.celery_app:celery_app worker --loglevel=INFO
```

### 2B) Run with Docker

```bash
docker compose up -d --build
```

Notes:

- Container entrypoint automatically runs:
  - migration + DB head check (`python -m app.scripts.migrate_and_check`)
  - admin bootstrap script (`python -m app.scripts.bootstrap_admin`)
  - prompt template bootstrap script (`python -m app.scripts.bootstrap_prompt_template`)
  - Ollama model bootstrap (`python -m app.scripts.ensure_ollama_model`)
  - uvicorn app startup
- Celery worker runs in a dedicated container (`celery-worker`).
- Redis runs only in Docker Compose and is used internally by service name `redis`.
- On first deploy, startup may take longer while the configured `OLLAMA_MODEL` is downloaded.
- FastAPI container reaches Ollama via internal Docker network URL: http://ollama:11434

Verify services:

```bash
docker compose ps
docker compose logs -f app
docker compose logs -f celery-worker
```

## API Docs

When server is running locally (custom port):

- Swagger UI: http://localhost:8005/docs
- ReDoc: http://localhost:8005/redoc (pinned ReDoc 2.x script)
- OpenAPI JSON: http://localhost:8005/openapi.json

For Docker Compose deployment (default host mapping):

- Swagger UI: http://localhost:8005/docs
- ReDoc: http://localhost:8005/redoc
- OpenAPI JSON: http://localhost:8005/openapi.json

## API Endpoints

Base API prefix: /api/v1

### Health

- GET /health
- GET /ready

### Auth (fastapi-users)

- POST /api/v1/auth/jwt/login
- POST /api/v1/auth/jwt/refresh
- POST /api/v1/auth/jwt/logout
- POST /api/v1/auth/register
- GET /api/v1/auth/users/me
- PATCH /api/v1/auth/users/me
- GET /api/v1/auth/users/{id}
- PATCH /api/v1/auth/users/{id}
- DELETE /api/v1/auth/users/{id}

Login note:

- Endpoint `/api/v1/auth/jwt/login` uses `application/x-www-form-urlencoded`.
- In form field `username`, pass only `AUTH_USERNAME`.
- Login response returns `access_token` in body and sets HttpOnly refresh cookie.
- Use `/api/v1/auth/jwt/refresh` to get a new access token and refresh cookie.
- `/api/v1/auth/jwt/logout` clears refresh cookie on client side.
- Swagger `Authorize` value must contain only raw JWT token (without `Bearer ` prefix).

### Feature Spec

- POST /api/v1/feature-spec/generate
- GET /api/v1/feature-spec/tasks/{task_id}
- GET /api/v1/feature-spec/history?limit=10

Generate request:

```json
{
  "feature_idea": "payment for premium posts"
}
```

Generate response:

```json
{
  "task_id": "3b44daff-1e83-4328-925f-62c22a9163d2",
  "status": "processing"
}
```

Task status response examples:

```json
{
  "task_id": "3b44daff-1e83-4328-925f-62c22a9163d2",
  "status": "PENDING"
}
```

```json
{
  "task_id": "3b44daff-1e83-4328-925f-62c22a9163d2",
  "status": "SUCCESS",
  "result": {
    "run_id": 10,
    "status": "success",
    "feature_idea": "payment for premium posts",
    "feature_summary": {
      "user_stories": [],
      "acceptance_criteria": [],
      "db_models_and_api_endpoints": {
        "db_models": [],
        "api_endpoints": []
      },
      "risk_assessment": []
    }
  }
}
```

## Quality Checks

Run linter:

```bash
python -m flake8 .
```

Run auth unit tests:

```bash
pytest tests/modules/auth -q
```

Run all tests:

```bash
pytest -q
```

## Security Notes

- Replace default SECRET_KEY in production.
- Use explicit ALLOWED_ORIGINS and SECURITY_TRUSTED_HOSTS in production.
- Enable SECURITY_ENABLE_HTTPS_REDIRECT behind proper TLS/reverse proxy setup.
- In-memory rate limiting is a baseline; for high-load use Redis-based limiting.

## Troubleshooting

If migrations fail:

```bash
python -m alembic upgrade head
```

If app cannot connect to DB:

- Verify DATABASE_URL
- Verify DB network access and sslmode if needed

If Celery tasks stay in `PENDING`:

- Check worker is healthy: `docker compose ps`
- Check worker logs: `docker compose logs -f celery-worker`
- Verify Redis URLs in `.env` point to `redis` service inside Docker network

If LLM requests fail or timeout:

- Verify OLLAMA_BASE_URL
- Ensure Ollama is running and model is available
- For Docker deployment, ensure OLLAMA_BASE_URL is http://ollama:11434
- Increase `OLLAMA_TIMEOUT` for long generations

If compose prints `variable is not set` for random token-like names:

- Your `.env` likely has `$` inside secret values
- Escape `$` as `$$` in `.env` values used by Docker Compose
