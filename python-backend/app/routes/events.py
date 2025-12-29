# app/routes/events.py
"""
Event simulation and scenario endpoints
"""

import uuid
import json
import asyncio
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException

from ..config import EVENT_TEMPLATES, SCENARIOS
from ..models import EventSimulation
from ..services.websocket_manager import manager
from ..services.kafka_service import kafka_producer

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/api/templates")
async def get_templates():
    """Get available event templates"""
    return {
        "sources": list(EVENT_TEMPLATES.keys()),
        "templates": EVENT_TEMPLATES,
        "scenarios": SCENARIOS
    }


@router.post("/api/simulate")
async def simulate_event(event: EventSimulation):
    """Simulate a single event"""
    try:
        # Create CloudEvent
        cloud_event = {
            "specversion": "1.0",
            "id": str(uuid.uuid4()),
            "type": event.event_type,
            "source": f"https://{event.source}.com/demo",
            "time": datetime.utcnow().isoformat() + "Z",
            "subject": event.subject,
            "severity": event.severity,
            "category": event.category,
            "correlation_id": event.correlation_id,
            "data": event.data or {"simulated": True}
        }
        
        # Send to Kafka
        kafka_producer.produce_event(cloud_event)
        
        # Broadcast to WebSocket clients
        await manager.broadcast({
            "type": "event_sent",
            "event": cloud_event
        })
        
        logger.info(f"Simulated event: {event.event_type} from {event.source}")
        
        return {
            "status": "success",
            "event_id": cloud_event['id'],
            "message": "Event sent to Kafka topic: cloudevents-stream"
        }
    
    except Exception as e:
        logger.error(f"Error simulating event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/scenario/{scenario_name}")
async def run_scenario(scenario_name: str):
    """Run a predefined scenario"""
    if scenario_name not in SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_name}' not found")
    
    scenario = SCENARIOS[scenario_name]
    
    # Start scenario in background
    asyncio.create_task(execute_scenario(scenario_name, scenario))
    
    return {
        "status": "started",
        "scenario": scenario_name,
        "description": scenario["description"],
        "message": f"Scenario '{scenario['name']}' is running"
    }


async def execute_scenario(scenario_name: str, scenario: dict):
    """Execute scenario events"""
    try:
        await manager.broadcast({
            "type": "scenario_started",
            "scenario": scenario_name,
            "name": scenario["name"]
        })
        
        if "events" in scenario:
            # Predefined sequence of events
            for event in scenario["events"]:
                cloud_event = {
                    "specversion": "1.0",
                    "id": str(uuid.uuid4()),
                    "type": event["type"],
                    "source": f"https://{event['source']}.com/demo",
                    "time": datetime.utcnow().isoformat() + "Z",
                    "subject": event["subject"],
                    "severity": event["severity"],
                    "category": event.get("category", "other"),
                    "correlation_id": event.get("correlation_id"),
                    "data": {"simulated": True, "scenario": scenario_name}
                }
                
                kafka_producer.produce_event(cloud_event)
                
                await manager.broadcast({
                    "type": "event_sent",
                    "event": cloud_event
                })
                
                await asyncio.sleep(2)  # 2 seconds between events
        
        await manager.broadcast({
            "type": "scenario_completed",
            "scenario": scenario_name
        })
        
    except Exception as e:
        logger.error(f"Error executing scenario: {e}")
