import logging
import os
import time

import httpx

logger = logging.getLogger(__name__)


def _env_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc


def _is_model_available(client: httpx.Client, model: str) -> bool:
    response = client.get("/api/tags")
    response.raise_for_status()
    models = response.json().get("models", [])
    return any(item.get("name") == model for item in models if isinstance(item, dict))


def wait_for_ollama(client: httpx.Client, wait_seconds: int) -> None:
    deadline = time.monotonic() + wait_seconds
    while time.monotonic() < deadline:
        try:
            client.get("/api/tags").raise_for_status()
            logger.info("Ollama is ready")
            return
        except httpx.HTTPError:
            logger.info("Waiting for Ollama to become ready...")
            time.sleep(2)

    raise RuntimeError(f"Ollama did not become ready within {wait_seconds}s")


def ensure_model(client: httpx.Client, model: str, pull_timeout: int) -> None:
    if _is_model_available(client, model):
        logger.info("Ollama model '%s' already available", model)
        return

    logger.info("Pulling missing Ollama model '%s'", model)
    response = client.post(
        "/api/pull",
        json={"model": model, "stream": False},
        timeout=pull_timeout,
    )
    response.raise_for_status()

    if not _is_model_available(client, model):
        raise RuntimeError(f"Ollama model '{model}' is still unavailable after pull")

    logger.info("Ollama model '%s' is ready", model)


def ensure_ollama_model() -> None:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "mistral").strip()
    connect_timeout = _env_int("OLLAMA_CONNECT_TIMEOUT", 10)
    request_timeout = _env_int("OLLAMA_TIMEOUT", 120)
    startup_wait = _env_int("OLLAMA_STARTUP_WAIT_SECONDS", 120)

    if not model:
        raise RuntimeError("OLLAMA_MODEL must not be empty")

    logger.info("Checking Ollama availability at %s", base_url)

    timeout = httpx.Timeout(timeout=request_timeout, connect=connect_timeout)
    with httpx.Client(base_url=base_url, timeout=timeout) as client:
        wait_for_ollama(client, startup_wait)
        ensure_model(client, model, pull_timeout=max(request_timeout, 300))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[ollama-bootstrap] %(message)s")
    ensure_ollama_model()


if __name__ == "__main__":
    main()
