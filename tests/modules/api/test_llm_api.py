from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_generate_returns_service_result(
    monkeypatch: pytest.MonkeyPatch, api_client: TestClient
) -> None:
    mocked_generate = AsyncMock(
        return_value={
            "raw_content": "# Spec",
            "content": "Spec",
            "sections": None,
            "data": None,
        }
    )
    monkeypatch.setattr("app.modules.llm.router.generate_completion", mocked_generate)

    response = api_client.post(
        "/api/v1/llm/generate",
        json={"prompt": "Generate auth spec", "response_format": "text"},
    )

    assert response.status_code == 200
    assert response.json()["content"] == "Spec"


@pytest.mark.unit
def test_generate_maps_value_error_to_502(
    monkeypatch: pytest.MonkeyPatch, api_client: TestClient
) -> None:
    monkeypatch.setattr(
        "app.modules.llm.router.generate_completion",
        AsyncMock(side_effect=ValueError("invalid provider response")),
    )

    response = api_client.post(
        "/api/v1/llm/generate",
        json={"prompt": "Generate auth spec", "response_format": "text"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "invalid provider response"


@pytest.mark.unit
def test_generate_maps_runtime_error_to_502(
    monkeypatch: pytest.MonkeyPatch, api_client: TestClient
) -> None:
    monkeypatch.setattr(
        "app.modules.llm.router.generate_completion",
        AsyncMock(side_effect=RuntimeError("provider timeout")),
    )

    response = api_client.post(
        "/api/v1/llm/generate",
        json={"prompt": "Generate auth spec", "response_format": "sections"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "provider timeout"


@pytest.mark.unit
def test_generate_validates_request_payload(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/v1/llm/generate",
        json={"prompt": "", "response_format": "text"},
    )

    assert response.status_code == 422
