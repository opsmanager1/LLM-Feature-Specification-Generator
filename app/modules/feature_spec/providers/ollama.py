import asyncio
import json
import logging
from typing import Any, AsyncGenerator

import httpx

from app.core.settings import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self) -> None:
        self._base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self._model = settings.OLLAMA_MODEL
        self._timeout = settings.OLLAMA_TIMEOUT
        self._connect_timeout = settings.OLLAMA_CONNECT_TIMEOUT
        self._max_retries = settings.OLLAMA_MAX_RETRIES
        self._retry_backoff_seconds = settings.OLLAMA_RETRY_BACKOFF_SECONDS
        self._system_prompt = settings.OLLAMA_SYSTEM_PROMPT

    def _build_payload(self, user_prompt: str, stream: bool = False) -> dict:
        messages = []
        if self._system_prompt.strip():
            messages.append({"role": "system", "content": self._system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        return {"model": self._model, "stream": stream, "messages": messages}

    def _http_timeout(self) -> httpx.Timeout:
        return httpx.Timeout(float(self._timeout), connect=float(self._connect_timeout))

    def _should_retry_status(self, status_code: int) -> bool:
        return 500 <= status_code <= 599

    async def _backoff(self, attempt: int) -> None:
        await asyncio.sleep(self._retry_backoff_seconds * (attempt + 1))

    async def generate(self, user_prompt: str) -> str:
        url = f"{self._base_url}/api/chat"
        payload = self._build_payload(user_prompt, stream=False)

        async with httpx.AsyncClient(timeout=self._http_timeout()) as client:
            for attempt in range(self._max_retries + 1):
                try:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    message = data.get("message", {})
                    content = message.get("content", "")
                    return content if isinstance(content, str) else str(content)
                except httpx.TimeoutException as exc:
                    if attempt < self._max_retries:
                        await self._backoff(attempt)
                        continue
                    raise RuntimeError(
                        f"Ollama request timed out after {self._timeout}s"
                    ) from exc
                except httpx.HTTPStatusError as exc:
                    status_code = exc.response.status_code
                    if (
                        self._should_retry_status(status_code)
                        and attempt < self._max_retries
                    ):
                        await self._backoff(attempt)
                        continue
                    raise RuntimeError(
                        f"Ollama returned HTTP {status_code}: {exc.response.text}"
                    ) from exc
                except httpx.RequestError as exc:
                    if attempt < self._max_retries:
                        await self._backoff(attempt)
                        continue
                    raise RuntimeError("Ollama request failed") from exc

        raise RuntimeError("Ollama request failed after retries")

    async def generate_stream(self, user_prompt: str) -> AsyncGenerator[str, None]:
        url = f"{self._base_url}/api/chat"
        payload = self._build_payload(user_prompt, stream=True)

        yielded_any = False
        async with httpx.AsyncClient(timeout=self._http_timeout()) as client:
            for attempt in range(self._max_retries + 1):
                try:
                    async with client.stream("POST", url, json=payload) as response:
                        response.raise_for_status()
                        async for line in response.aiter_lines():
                            if not line:
                                continue
                            try:
                                chunk: Any = json.loads(line)
                            except Exception:
                                logger.warning("Skipping invalid Ollama stream chunk")
                                continue
                            token = chunk.get("message", {}).get("content", "")
                            if token:
                                yielded_any = True
                                yield token
                            if chunk.get("done"):
                                return
                        return
                except httpx.TimeoutException as exc:
                    if not yielded_any and attempt < self._max_retries:
                        await self._backoff(attempt)
                        continue
                    raise RuntimeError(
                        f"Ollama stream timed out after {self._timeout}s"
                    ) from exc
                except httpx.HTTPStatusError as exc:
                    status_code = exc.response.status_code
                    if (
                        not yielded_any
                        and self._should_retry_status(status_code)
                        and attempt < self._max_retries
                    ):
                        await self._backoff(attempt)
                        continue
                    raise RuntimeError(
                        f"Ollama stream returned HTTP {status_code}: {exc.response.text}"
                    ) from exc
                except httpx.RequestError as exc:
                    if not yielded_any and attempt < self._max_retries:
                        await self._backoff(attempt)
                        continue
                    raise RuntimeError("Ollama stream request failed") from exc

        raise RuntimeError("Ollama stream failed after retries")


ollama_client = OllamaClient()
