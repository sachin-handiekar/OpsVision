# app/routes/websocket.py
"""
WebSocket endpoint for real-time updates
"""

import json
import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..services.websocket_manager import manager
from ..services.kafka_service import KafkaConsumerService
from ..services.ai_service import gemini_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await manager.connect(websocket)
    
    try:
        # Start background task to consume Gemini summaries
        consumer_task = asyncio.create_task(consume_gemini_summaries(websocket))
        
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        consumer_task.cancel()
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def consume_gemini_summaries(websocket: WebSocket):
    """Consume Gemini summaries from Kafka and send to WebSocket"""
    consumer = None
    try:
        # Read only latest messages (set read_from_beginning=True for historical)
        consumer = KafkaConsumerService(read_from_beginning=False)
        logger.info("Starting to consume from gemini_summary topic (latest only)")
        
        while True:
            msg = consumer.poll(timeout=1.0)
            
            if msg is None:
                await asyncio.sleep(1)
                continue
            
            if msg.error():
                logger.warning(f"Consumer error: {msg.error()}")
                continue
            
            try:
                # Use the consumer's deserialize method (handles Avro or JSON)
                summary = consumer.deserialize_message(msg)
                
                if summary is None:
                    logger.warning("Failed to deserialize message")
                    continue
                
                logger.info(f"Received summary: {summary}")
                
                # Convert datetime objects to ISO string for JSON serialization
                for key, value in summary.items():
                    if hasattr(value, 'isoformat'):
                        summary[key] = value.isoformat()
                
                # Generate AI insight (optional - don't fail if quota exceeded)
                if gemini_service.is_available:
                    try:
                        insight = await gemini_service.generate_insight(summary)
                        summary['ai_insight'] = insight
                    except Exception as ai_err:
                        logger.warning(f"AI insight skipped: {ai_err}")
                        summary['ai_insight'] = {"status": "skipped", "reason": "quota exceeded"}
                
                # Send to WebSocket (always send, even without AI)
                await websocket.send_json({
                    "type": "ai_alert",
                    "summary": summary
                })
                logger.info(f"Sent summary to WebSocket: {summary.get('health_status')}")
                
                # Add delay between processing to avoid API rate limits
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error processing summary: {e}")
    
    except Exception as e:
        logger.error(f"Consumer error: {e}")
    finally:
        if consumer:
            consumer.close()
