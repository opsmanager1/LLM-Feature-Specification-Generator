from datetime import datetime, timedelta, timezone

import pytest
from freezegun import freeze_time
from fastapi.testclient import TestClient

from app.main import app
from app.modules.auth.jwt_router import get_auth_session_service
from app.modules.auth.service import AuthTokens


def _get_auth_me_dependency_callable():
    for route in app.routes:
        if getattr(route, "path", None) == "/api/v1/auth/users/me" and "GET" in getattr(
            route, "methods", set()
        ):
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
    response = api_client.post(
        "/api/v1/auth/register", json={"email": "user@example.com"}
    )

    assert response.status_code == 422


@pytest.mark.unit
def test_login_validates_form_payload(api_client: TestClient) -> None:
    response = api_client.post("/api/v1/auth/jwt/login", data={})

    assert response.status_code == 422


@pytest.mark.unit
def test_login_returns_tokens_and_sets_refresh_cookie(api_client: TestClient) -> None:
    class FakeAuthSessionService:
        async def login(self, credentials):
            return AuthTokens(access_token="access-token", refresh_token="refresh-token")

    app.dependency_overrides[get_auth_session_service] = lambda: FakeAuthSessionService()
    try:
        response = api_client.post(
            "/api/v1/auth/jwt/login",
            data={"username": "admin", "password": "!QAZ1qaz"},
        )
    finally:
        app.dependency_overrides.pop(get_auth_session_service, None)

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"] == "access-token"
    assert "refresh_token=" in response.headers.get("set-cookie", "")


@pytest.mark.unit
def test_refresh_requires_refresh_cookie(api_client: TestClient) -> None:
    response = api_client.post("/api/v1/auth/jwt/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"


@pytest.mark.unit
def test_refresh_returns_new_access_token(api_client: TestClient) -> None:
    class FakeAuthSessionService:
        async def refresh(self, refresh_token):
            if refresh_token != "valid-refresh-token":
                return None
            return AuthTokens(
                access_token="new-access-token",
                refresh_token="new-refresh-token",
            )

    app.dependency_overrides[get_auth_session_service] = lambda: FakeAuthSessionService()
    try:
        response = api_client.post(
            "/api/v1/auth/jwt/refresh",
            cookies={"refresh_token": "valid-refresh-token"},
        )
    finally:
        app.dependency_overrides.pop(get_auth_session_service, None)

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"] == "new-access-token"
    assert "refresh_token=" in response.headers.get("set-cookie", "")


@pytest.mark.unit
def test_logout_clears_refresh_cookie(api_client: TestClient) -> None:
    class FakeAuthSessionService:
        async def logout(self, refresh_token):
            return None

    app.dependency_overrides[get_auth_session_service] = lambda: FakeAuthSessionService()
    try:
        response = api_client.post(
            "/api/v1/auth/jwt/logout",
            cookies={"refresh_token": "any-token"},
        )
    finally:
        app.dependency_overrides.pop(get_auth_session_service, None)

    assert response.status_code == 204
    set_cookie = response.headers.get("set-cookie", "")
    assert "refresh_token=" in set_cookie
    assert "Max-Age=0" in set_cookie or "expires=" in set_cookie.lower()


@pytest.mark.unit
def test_refresh_returns_401_when_mocked_token_expired_by_time(
    api_client: TestClient,
) -> None:
    class TimeAwareFakeAuthSessionService:
        def __init__(self) -> None:
            self._expires_at: datetime | None = None

        async def login(self, credentials):
            self._expires_at = datetime.now(timezone.utc) + timedelta(seconds=60)
            return AuthTokens(
                access_token="access-token",
                refresh_token="refresh-token",
            )

        async def refresh(self, refresh_token):
            if self._expires_at is None:
                return None

            if datetime.now(timezone.utc) >= self._expires_at:
                return None

            return AuthTokens(
                access_token="new-access-token",
                refresh_token="refresh-token",
            )

        async def logout(self, refresh_token):
            return None

    fake_service = TimeAwareFakeAuthSessionService()
    app.dependency_overrides[get_auth_session_service] = lambda: fake_service
    try:
        with freeze_time("2026-04-11 19:00:00"):
            login_response = api_client.post(
                "/api/v1/auth/jwt/login",
                data={"username": "admin", "password": "!QAZ1qaz"},
            )

        assert login_response.status_code == 200

        with freeze_time("2026-04-11 19:01:01"):
            refresh_response = api_client.post(
                "/api/v1/auth/jwt/refresh",
                cookies={"refresh_token": "refresh-token"},
            )
    finally:
        app.dependency_overrides.pop(get_auth_session_service, None)

    assert refresh_response.status_code == 401
    assert refresh_response.json()["detail"] == "Unauthorized"
