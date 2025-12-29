# app/routes/__init__.py
"""
Routes package for EventStream Intelligence
"""

from .events import router as events_router
from .health import router as health_router
from .websocket import router as websocket_router

__all__ = ['events_router', 'health_router', 'websocket_router']
