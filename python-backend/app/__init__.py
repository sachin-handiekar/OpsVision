# app/__init__.py
"""
EventStream Intelligence - Demo Application Backend
FastAPI server for simulating events and displaying AI insights
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import events_router, health_router, websocket_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(title="EventStream Intelligence Demo")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(events_router)
app.include_router(websocket_router)

logger.info("EventStream Intelligence Demo initialized")
