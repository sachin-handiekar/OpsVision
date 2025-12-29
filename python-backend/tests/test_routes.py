# tests/test_routes.py
"""
Tests for API routes
"""

import pytest
from unittest.mock import patch, MagicMock


class TestHealthRoutes:
    """Tests for health and status endpoints"""
    
    def test_root_endpoint(self, test_client):
        """Test GET / returns service information"""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        
        assert data["service"] == "EventStream Intelligence Demo"
        assert data["status"] == "running"
        assert "endpoints" in data
        assert data["endpoints"]["simulate"] == "/api/simulate"
        assert data["endpoints"]["scenario"] == "/api/scenario/{name}"
        assert data["endpoints"]["templates"] == "/api/templates"
        assert data["endpoints"]["websocket"] == "/ws"
    
    def test_stats_endpoint(self, test_client):
        """Test GET /api/stats returns statistics"""
        response = test_client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "websocket_connections" in data
        assert "gemini_available" in data
        assert "kafka_configured" in data
        assert "timestamp" in data
        assert isinstance(data["websocket_connections"], int)


class TestEventRoutes:
    """Tests for event simulation endpoints"""
    
    def test_get_templates(self, test_client):
        """Test GET /api/templates returns event templates"""
        response = test_client.get("/api/templates")
        assert response.status_code == 200
        data = response.json()
        
        assert "sources" in data
        assert "templates" in data
        assert "scenarios" in data
        
        # Check all expected sources are present
        expected_sources = ["github", "datadog", "kubernetes", "jenkins", "pagerduty"]
        for source in expected_sources:
            assert source in data["sources"]
            assert source in data["templates"]
        
        # Check scenarios
        expected_scenarios = ["normal_operations", "deployment", "incident", "traffic_spike"]
        for scenario in expected_scenarios:
            assert scenario in data["scenarios"]
    
    @patch('app.routes.events.kafka_producer')
    def test_simulate_event_success(self, mock_kafka, test_client, sample_event_data):
        """Test POST /api/simulate creates an event"""
        mock_kafka.produce_event = MagicMock()
        
        response = test_client.post("/api/simulate", json=sample_event_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "event_id" in data
        assert "message" in data
    
    def test_simulate_event_invalid_data(self, test_client):
        """Test POST /api/simulate with invalid data returns 422"""
        invalid_data = {
            "source": "github",
            # missing required fields
        }
        response = test_client.post("/api/simulate", json=invalid_data)
        assert response.status_code == 422
    
    @patch('app.routes.events.kafka_producer')
    def test_run_scenario_success(self, mock_kafka, test_client):
        """Test POST /api/scenario/{name} starts a scenario"""
        mock_kafka.produce_event = MagicMock()
        
        response = test_client.post("/api/scenario/incident")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "started"
        assert data["scenario"] == "incident"
        assert "description" in data
        assert "message" in data
    
    def test_run_scenario_not_found(self, test_client):
        """Test POST /api/scenario/{name} with invalid scenario returns 404"""
        response = test_client.post("/api/scenario/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
