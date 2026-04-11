from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_health_returns_service_metadata(api_client: TestClient) -> None:
    response = api_client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "service" in payload
    assert "version" in payload
    assert "env" in payload


@pytest.mark.unit
def test_ready_returns_ready_when_db_check_passes(
    monkeypatch: pytest.MonkeyPatch, api_client: TestClient
) -> None:
    monkeypatch.setattr("app.api.health.check_database_ready", Mock(return_value=None))

    response = api_client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


@pytest.mark.unit
def test_ready_returns_503_when_db_check_fails(
    monkeypatch: pytest.MonkeyPatch, api_client: TestClient
) -> None:
    monkeypatch.setattr(
        "app.api.health.check_database_ready", Mock(side_effect=RuntimeError("db down"))
    )

    response = api_client.get("/ready")

    assert response.status_code == 503
    assert response.json()["detail"] == "Database is not ready"
