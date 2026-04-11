from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def api_client() -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client
