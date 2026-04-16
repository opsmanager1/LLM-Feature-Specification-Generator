<div align="center">

# Specification Generator API

Production-ready FastAPI backend for authentication, LLM-powered specification generation, health checks, and secure API middleware baseline.

<p align="center">
    <img alt="python" src="https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white"/>
    <img alt="fastapi" src="https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white"/>
    <img alt="sqlalchemy" src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white"/>
    <img alt="alembic" src="https://img.shields.io/badge/Alembic-migrations-222222"/>
    <img alt="tests" src="https://img.shields.io/badge/tests-pytest-0A9EDC"/>
    <img alt="docs" src="https://img.shields.io/badge/docs-Swagger%20%2B%20ReDoc-85EA2D"/>
</p>

</div>

## What This Project Includes

- JWT authentication based on fastapi-users
- User registration and user management endpoints
- Feature specification generation endpoints powered by Ollama
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
- PostgreSQL (via DATABASE_URL)
- Ollama (LLM provider)
- Pytest

## Project Structure

- app/main.py: FastAPI app bootstrap and router registration
- app/core/: settings, database wiring, startup/lifespan, bootstrap logic
- app/api/: health, readiness, OpenAPI customization
- app/middlewares/: security middleware composition and implementations
- app/modules/auth/: auth domain (models, schemas, dependencies, router)
- app/modules/feature_spec/: feature spec API, schemas, prompts, providers
- app/scripts/: utility scripts (admin and prompt/model bootstrap)
- alembic/: migration config and versions
- docker-compose.yml: containerized app run

## Setup Guide

### Prerequisites

- Python 3.10+
- PostgreSQL database
- Optional: Docker + Docker Compose (recommended for VPS)

### 1) Configure environment

Create .env in the project root and set required values.

Required minimum:

- DATABASE_URL
- SECRET_KEY

Recommended auth bootstrap values:

- AUTH_USERNAME
- AUTH_EMAIL
- AUTH_PASSWORD (or AUTH_PASSWORD_HASH)

LLM values:

- OLLAMA_BASE_URL
- OLLAMA_MODEL

For Docker Compose in this project use:

- OLLAMA_BASE_URL=http://ollama:11434

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
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
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
- On first deploy, startup may take longer while the configured `OLLAMA_MODEL` is downloaded.
- FastAPI container reaches Ollama via internal Docker network URL: http://ollama:11434

Verify Ollama API:

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "hello",
  "stream": false
}'
```

## API Docs

When server is running locally:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc (pinned ReDoc 2.x script)
- OpenAPI JSON: http://localhost:8000/openapi.json

For Docker Compose deployment, use port 8001 instead of 8000.

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
- GET /api/v1/feature-spec/history?limit=10

Request body example for generation:

```json
{
  "feature_idea": "payment for premium posts"
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

If LLM requests fail:

- Verify OLLAMA_BASE_URL
- Ensure Ollama is running and model is available
- For Docker deployment, ensure OLLAMA_BASE_URL is http://ollama:11434
