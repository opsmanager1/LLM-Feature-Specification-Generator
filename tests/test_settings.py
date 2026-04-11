from __future__ import annotations

import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


TEST_DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
TEST_DB_PORT = int(os.getenv("TEST_DB_PORT", "5432"))
TEST_DB_USER = os.getenv("TEST_DB_USER", os.getenv("POSTGRES_USER", "postgres"))
TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", os.getenv("POSTGRES_PASSWORD", "postgres"))
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "postgres")
TEST_DB_SSLMODE = os.getenv("TEST_DB_SSLMODE", "disable")


def _build_database_url() -> str:
    encoded_user = quote_plus(TEST_DB_USER)
    encoded_password = quote_plus(TEST_DB_PASSWORD)
    return (
        f"postgresql://{encoded_user}:{encoded_password}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
        f"?sslmode={TEST_DB_SSLMODE}"
    )


def _resolve_test_database_url() -> str:
    raw = os.getenv("TEST_DATABASE_URL", "").strip()
    if raw.startswith("postgresql://"):
        return raw
    if raw.startswith("postgres://"):
        return raw.replace("postgres://", "postgresql://", 1)
    return _build_database_url()

TEST_DATABASE_URL = _resolve_test_database_url()

TEST_DEFAULT_USERNAME = os.getenv("TEST_DEFAULT_USERNAME", "test_admin")
TEST_DEFAULT_EMAIL = os.getenv("TEST_DEFAULT_EMAIL", "test_admin@example.com")
TEST_DEFAULT_HASHED_PASSWORD = os.getenv(
    "TEST_DEFAULT_HASHED_PASSWORD",
    "$2b$12$kAeaA3C3m6K1SZ8b0jYV8uVf5V8M0ltv8R8xX9mE0A1U6hL9I0i3K",
)


def apply_test_environment() -> None:
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ.setdefault("SECRET_KEY", "test_secret_key")
    os.environ.setdefault("ENV", "test")


def pytest_configure(config) -> None:
    apply_test_environment()
