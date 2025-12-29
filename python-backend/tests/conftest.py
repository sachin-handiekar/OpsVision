# tests/conftest.py
"""
Pytest fixtures for EventStream Intelligence tests
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from app import app
from app.services.websocket_manager import ConnectionManager
from app.services.kafka_service import KafkaProducerService


@pytest.fixture
def test_client():
    """Synchronous test client for FastAPI"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Async test client for FastAPI"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_kafka_producer():
    """Mock Kafka producer to avoid real Kafka connections"""
    mock_producer = MagicMock(spec=KafkaProducerService)
    mock_producer.produce_event = MagicMock()
    return mock_producer


@pytest.fixture
def connection_manager():
    """Fresh ConnectionManager instance for testing"""
    return ConnectionManager()


@pytest.fixture
def mock_websocket():
    """Mock WebSocket for testing"""
    mock_ws = AsyncMock()
    mock_ws.accept = AsyncMock()
    mock_ws.send_json = AsyncMock()
    mock_ws.receive_text = AsyncMock(return_value="ping")
    return mock_ws


@pytest.fixture
def sample_event_data():
    """Sample event data for testing"""
    return {
        "source": "github",
        "event_type": "com.github.push",
        "severity": "info",
        "subject": "Test push event",
        "category": "cicd",
        "correlation_id": None,
        "data": {"test": True}
    }


@pytest.fixture
def sample_summary_data():
    """Sample summary data for AI insight testing"""
    return {
        "health_status": "healthy",
        "total_events": 100,
        "critical_count": 0,
        "error_count": 2,
        "error_rate_percent": 2.0
    }
