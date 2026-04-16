import httpx

from app.core.settings import settings


class OllamaSyncClient:
    def __init__(self) -> None:
        self._base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self._model = settings.OLLAMA_MODEL
        self._timeout = httpx.Timeout(
            float(settings.OLLAMA_TIMEOUT),
            connect=float(settings.OLLAMA_CONNECT_TIMEOUT),
        )
        self._system_prompt = settings.OLLAMA_SYSTEM_PROMPT

    def _build_payload(self, user_prompt: str) -> dict:
        messages = []
        if self._system_prompt.strip():
            messages.append({"role": "system", "content": self._system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        return {
            "model": self._model,
            "stream": False,
            "format": "json",
            "messages": messages,
        }

    def generate(self, user_prompt: str) -> str:
        url = f"{self._base_url}/api/chat"
        payload = self._build_payload(user_prompt)
        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(url, json=payload, timeout=self._timeout)
            response.raise_for_status()
            data = response.json()
            content = data.get("message", {}).get("content", "")
            return content if isinstance(content, str) else str(content)


ollama_sync_client = OllamaSyncClient()
