# app/services/ai_service.py
"""
Gemini AI service for generating insights
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from ..config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

# Attempt to import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None


class GeminiService:
    """Service for generating AI insights using Google Gemini"""
    
    def __init__(self):
        self._model = None
        self._configured = False
        
        if GEMINI_AVAILABLE and GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                # Use gemini-2.0-flash (gemini-1.5-pro is deprecated)
                self._model = genai.GenerativeModel('gemini-2.0-flash')
                self._configured = True
                logger.info("✓ Gemini configured (model: gemini-2.0-flash)")
            except Exception as e:
                logger.error(f"Failed to configure Gemini: {e}")
    
    @property
    def is_available(self) -> bool:
        """Check if Gemini is available and configured"""
        return GEMINI_AVAILABLE and self._configured and self._model is not None
    
    async def generate_insight(self, summary: dict) -> Dict[str, Any]:
        """Generate AI insight from a system health summary"""
        if not self.is_available:
            return {
                "status": "AI not available",
                "recommendation": "Enable Gemini API for AI insights"
            }
        
        try:
            prompt = f"""Analyze this system health summary and provide actionable insights:

**System Health Status:** {summary.get('health_status', 'unknown')}
**Time Window:** {summary.get('window_end', 'unknown')}

**Event Metrics:**
- Total Events: {summary.get('total_events', 0)}
- Critical Events: {summary.get('critical_count', 0)}
- Error Events: {summary.get('error_count', 0)}
- Warning Events: {summary.get('warning_count', 0)}
- Error Rate: {summary.get('error_rate_percent', 0):.2f}%
- Error Trend: {summary.get('error_trend', 'unknown')}

**Top Problem Source:** {summary.get('top_error_source', 'None identified')}
- Error Count from this source: {summary.get('top_error_count', 0)}

**Additional Context:**
- Total Sources Monitored: {summary.get('total_sources', 0)}
- Correlated Incidents: {summary.get('correlation_count', 0)}
- Anomalies Detected: {summary.get('anomaly_count', 0)}

Provide a brief assessment:
1. **Status**: One sentence summarizing the current state
2. **Root Cause**: Which system/service is the primary issue source
3. **Impact**: What's affected and severity level
4. **Recommendation**: One actionable step to resolve

Keep response under 150 words."""
            
            response = await asyncio.to_thread(
                self._model.generate_content, prompt
            )
            
            return {
                "status": "success",
                "insight": response.text,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


# Global instance
gemini_service = GeminiService()
