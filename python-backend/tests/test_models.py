# tests/test_models.py
"""
Tests for Pydantic models
"""

import pytest
from pydantic import ValidationError

from app.models import EventSimulation, SimulationScenario, EventResponse, StatsResponse


class TestEventSimulation:
    """Tests for EventSimulation model"""
    
    def test_valid_event_simulation(self):
        """Test creating a valid EventSimulation"""
        event = EventSimulation(
            source="github",
            event_type="com.github.push",
            severity="info",
            subject="Test event",
            category="cicd"
        )
        assert event.source == "github"
        assert event.event_type == "com.github.push"
        assert event.severity == "info"
        assert event.subject == "Test event"
        assert event.category == "cicd"
        assert event.correlation_id is None
        assert event.data is None
    
    def test_event_simulation_with_optional_fields(self):
        """Test EventSimulation with all optional fields"""
        event = EventSimulation(
            source="datadog",
            event_type="com.datadog.alert",
            severity="critical",
            subject="High latency",
            category="alert",
            correlation_id="incident-123",
            data={"metric": "latency", "value": 500}
        )
        assert event.correlation_id == "incident-123"
        assert event.data == {"metric": "latency", "value": 500}
    
    def test_event_simulation_missing_required_field(self):
        """Test that missing required fields raise ValidationError"""
        with pytest.raises(ValidationError):
            EventSimulation(
                source="github",
                event_type="com.github.push",
                # missing severity, subject, category
            )


class TestSimulationScenario:
    """Tests for SimulationScenario model"""
    
    def test_valid_scenario(self):
        """Test creating a valid SimulationScenario"""
        scenario = SimulationScenario(
            scenario_name="incident"
        )
        assert scenario.scenario_name == "incident"
        assert scenario.duration_seconds == 60  # default
        assert scenario.events_per_minute == 30  # default
    
    def test_scenario_with_custom_values(self):
        """Test SimulationScenario with custom duration and rate"""
        scenario = SimulationScenario(
            scenario_name="traffic_spike",
            duration_seconds=120,
            events_per_minute=60
        )
        assert scenario.duration_seconds == 120
        assert scenario.events_per_minute == 60


class TestEventResponse:
    """Tests for EventResponse model"""
    
    def test_event_response(self):
        """Test creating an EventResponse"""
        response = EventResponse(
            status="success",
            event_id="abc-123",
            message="Event sent"
        )
        assert response.status == "success"
        assert response.event_id == "abc-123"


class TestStatsResponse:
    """Tests for StatsResponse model"""
    
    def test_stats_response(self):
        """Test creating a StatsResponse"""
        response = StatsResponse(
            websocket_connections=5,
            gemini_available=True,
            kafka_configured=True,
            timestamp="2024-01-01T00:00:00"
        )
        assert response.websocket_connections == 5
        assert response.gemini_available is True
