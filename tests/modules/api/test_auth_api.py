import pytest
from fastapi.testclient import TestClient

from app.main import app


def _get_auth_me_dependency_callable():
    for route in app.routes:
        if getattr(route, "path", None) == "/api/v1/auth/users/me" and "GET" in getattr(route, "methods", set()):
            dependant = getattr(route, "dependant", None)
            if dependant and dependant.dependencies:
                return dependant.dependencies[0].call
    raise RuntimeError("Could not resolve /api/v1/auth/users/me dependency callable")


@pytest.mark.unit
def test_auth_me_requires_token(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/auth/users/me")

    assert response.status_code == 401


@pytest.mark.unit
def test_auth_me_returns_mocked_current_user(api_client: TestClient) -> None:
    async def override_current_user():
        return {
            "id": 1,
            "email": "test_admin@example.com",
            "is_active": True,
            "is_superuser": True,
            "is_verified": True,
            "username": "test_admin",
        }

    current_user_dependency = _get_auth_me_dependency_callable()
    app.dependency_overrides[current_user_dependency] = override_current_user
    try:
        response = api_client.get("/api/v1/auth/users/me")
    finally:
        app.dependency_overrides.pop(current_user_dependency, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "test_admin@example.com"
    assert payload["username"] == "test_admin"


@pytest.mark.unit
def test_register_validates_required_fields(api_client: TestClient) -> None:
    response = api_client.post("/api/v1/auth/register", json={"email": "user@example.com"})

    assert response.status_code == 422


@pytest.mark.unit
def test_login_validates_form_payload(api_client: TestClient) -> None:
    response = api_client.post("/api/v1/auth/jwt/login", data={})

    assert response.status_code == 422
