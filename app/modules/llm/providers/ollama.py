from typing import AsyncGenerator
import logging

import httpx

from app.core.settings import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self) -> None:
        self._base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self._model = settings.OLLAMA_MODEL
        self._timeout = settings.OLLAMA_TIMEOUT
        self._system_prompt = settings.OLLAMA_SYSTEM_PROMPT

    def _build_payload(self, user_prompt: str, stream: bool = False) -> dict:
        return {
            "model": self._model,
            "stream": stream,
            "messages": [
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

    async def generate(self, user_prompt: str) -> str:
        url = f"{self._base_url}/api/chat"
        payload = self._build_payload(user_prompt, stream=False)

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
            except httpx.TimeoutException as exc:
                logger.exception("Ollama request timed out")
                raise RuntimeError(
                    f"Ollama request timed out after {self._timeout}s"
                ) from exc
            except httpx.HTTPStatusError as exc:
                logger.exception("Ollama returned error response")
                raise RuntimeError(
                    f"Ollama returned HTTP {exc.response.status_code}: {exc.response.text}"
                ) from exc

        data = response.json()
        return data["message"]["content"]

    async def generate_stream(self, user_prompt: str) -> AsyncGenerator[str, None]:
        url = f"{self._base_url}/api/chat"
        payload = self._build_payload(user_prompt, stream=True)

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    import json as _json

                    chunk = _json.loads(line)
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        yield token
                    if chunk.get("done"):
                        break


ollama_client = OllamaClient()