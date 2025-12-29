# app/routes/health.py
"""
Health and status endpoints
"""

import logging
from datetime import datetime
from fastapi import APIRouter
from typing import List

from ..config import KAFKA_CONFIG, GEMINI_SUMMARY_TOPIC
from ..services.websocket_manager import manager
from ..services.ai_service import gemini_service
from ..services.kafka_service import KafkaConsumerService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "EventStream Intelligence Demo",
        "status": "running",
        "endpoints": {
            "simulate": "/api/simulate",
            "scenario": "/api/scenario/{name}",
            "templates": "/api/templates",
            "summaries": "/api/summaries",
            "websocket": "/ws"
        }
    }


@router.get("/api/stats")
async def get_stats():
    """Get current statistics"""
    return {
        "websocket_connections": manager.connection_count,
        "gemini_available": gemini_service.is_available,
        "kafka_configured": bool(KAFKA_CONFIG.get('bootstrap.servers')),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/api/summaries")
async def get_summaries(limit: int = 5):
    """Fetch latest Gemini summaries from Kafka topic.
    
    Args:
        limit: Maximum number of summaries to return (default 5)
    """
    summaries: List[dict] = []
    
    try:
        # Create consumer that reads from beginning
        consumer = KafkaConsumerService(
            group_id='api-summary-reader',
            read_from_beginning=True
        )
        
        logger.info(f"Fetching up to {limit} summaries from {GEMINI_SUMMARY_TOPIC}")
        
        # Poll for messages (with timeout)
        poll_count = 0
        max_polls = 20  # Max ~20 seconds of polling
        
        while len(summaries) < limit and poll_count < max_polls:
            msg = consumer.poll(timeout=1.0)
            poll_count += 1
            
            if msg is None:
                # If we have some messages and no more coming, break
                if summaries and poll_count > 5:
                    break
                continue
            
            if msg.error():
                logger.warning(f"Consumer error: {msg.error()}")
                continue
            
            # Deserialize message
            record = consumer.deserialize_message(msg)
            if record:
                record['_offset'] = msg.offset()
                record['_partition'] = msg.partition()
                summaries.append(record)
                logger.info(f"Got summary {len(summaries)}: offset {msg.offset()}")
        
        consumer.close()
        
        return {
            "topic": GEMINI_SUMMARY_TOPIC,
            "count": len(summaries),
            "summaries": summaries
        }
    
    except Exception as e:
        logger.error(f"Error fetching summaries: {e}")
        return {
            "topic": GEMINI_SUMMARY_TOPIC,
            "count": 0,
            "error": str(e),
            "summaries": []
        }
