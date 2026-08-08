import asyncio
import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)

    async def _make_request(method: str, path: str, **kwargs):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            return await ac.request(method, path, **kwargs)

    return _make_request


def run_async(coro):
    return asyncio.run(coro)
