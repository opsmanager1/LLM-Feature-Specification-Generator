import pytest
import httpx

from app.modules.llm.providers.ollama import OllamaClient


class FakeResponse:
    def __init__(self, *, json_data=None, status_code: int = 200, text: str = ""):
        self._json_data = json_data or {}
        self.status_code = status_code
        self.text = text

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request("POST", "http://mock/api/chat")
            response = httpx.Response(self.status_code, request=request, text=self.text)
            raise httpx.HTTPStatusError("error", request=request, response=response)

    def json(self):
        return self._json_data


class FakeAsyncClient:
    def __init__(self, response: FakeResponse | None = None, error: Exception | None = None):
        self._response = response
        self._error = error
        self.last_url = None
        self.last_json = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, json):
        self.last_url = url
        self.last_json = json
        if self._error:
            raise self._error
        return self._response


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_returns_content(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = FakeAsyncClient(
        response=FakeResponse(json_data={"message": {"content": "Generated specification"}})
    )
    monkeypatch.setattr(
        "app.modules.llm.providers.ollama.httpx.AsyncClient",
        lambda *args, **kwargs: fake_client,
    )

    client = OllamaClient()
    result = await client.generate("Build API spec")

    assert result == "Generated specification"
    assert fake_client.last_url.endswith("/api/chat")
    assert fake_client.last_json["messages"][1]["content"] == "Build API spec"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_maps_timeout_to_runtime_error(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = FakeAsyncClient(error=httpx.TimeoutException("timeout"))
    monkeypatch.setattr(
        "app.modules.llm.providers.ollama.httpx.AsyncClient",
        lambda *args, **kwargs: fake_client,
    )

    client = OllamaClient()

    with pytest.raises(RuntimeError, match="timed out"):
        await client.generate("Build API spec")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_maps_http_status_error_to_runtime_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = FakeAsyncClient(response=FakeResponse(status_code=500, text="internal error"))
    monkeypatch.setattr(
        "app.modules.llm.providers.ollama.httpx.AsyncClient",
        lambda *args, **kwargs: fake_client,
    )

    client = OllamaClient()

    with pytest.raises(RuntimeError, match="Ollama returned HTTP 500"):
        await client.generate("Build API spec")
