# app/models.py
"""
Pydantic models for EventStream Intelligence
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class EventSimulation(BaseModel):
    """Model for simulating an event"""
    source: str  # github, datadog, kubernetes, jenkins, pagerduty, custom
    event_type: str
    severity: str  # info, warning, error, critical
    subject: str
    category: str  # cicd, infrastructure, alert, incident
    correlation_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class SimulationScenario(BaseModel):
    """Model for running a simulation scenario"""
    scenario_name: str  # "normal_operations", "incident", "deployment", "spike"
    duration_seconds: int = 60
    events_per_minute: int = 30


class EventResponse(BaseModel):
    """Response model for event simulation"""
    status: str
    event_id: str
    message: str


class ScenarioResponse(BaseModel):
    """Response model for scenario execution"""
    status: str
    scenario: str
    description: str
    message: str


class StatsResponse(BaseModel):
    """Response model for stats endpoint"""
    websocket_connections: int
    gemini_available: bool
    kafka_configured: bool
    timestamp: str
