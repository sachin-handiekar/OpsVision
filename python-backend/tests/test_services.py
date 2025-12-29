# tests/test_services.py
"""
Tests for service layer
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestConnectionManager:
    """Tests for WebSocket ConnectionManager"""
    
    @pytest.mark.asyncio
    async def test_connect(self, connection_manager, mock_websocket):
        """Test connecting a WebSocket"""
        await connection_manager.connect(mock_websocket)
        
        mock_websocket.accept.assert_called_once()
        assert mock_websocket in connection_manager.active_connections
        assert connection_manager.connection_count == 1
    
    @pytest.mark.asyncio
    async def test_disconnect(self, connection_manager, mock_websocket):
        """Test disconnecting a WebSocket"""
        await connection_manager.connect(mock_websocket)
        connection_manager.disconnect(mock_websocket)
        
        assert mock_websocket not in connection_manager.active_connections
        assert connection_manager.connection_count == 0
    
    @pytest.mark.asyncio
    async def test_disconnect_not_connected(self, connection_manager, mock_websocket):
        """Test disconnect on non-connected socket doesn't raise"""
        # Should not raise an exception
        connection_manager.disconnect(mock_websocket)
        assert connection_manager.connection_count == 0
    
    @pytest.mark.asyncio
    async def test_broadcast_single_client(self, connection_manager, mock_websocket):
        """Test broadcasting to a single client"""
        await connection_manager.connect(mock_websocket)
        
        message = {"type": "test", "data": "hello"}
        await connection_manager.broadcast(message)
        
        mock_websocket.send_json.assert_called_once_with(message)
    
    @pytest.mark.asyncio
    async def test_broadcast_multiple_clients(self, connection_manager):
        """Test broadcasting to multiple clients"""
        mock_ws1 = AsyncMock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()
        
        mock_ws2 = AsyncMock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()
        
        await connection_manager.connect(mock_ws1)
        await connection_manager.connect(mock_ws2)
        
        message = {"type": "broadcast", "data": "hello all"}
        await connection_manager.broadcast(message)
        
        mock_ws1.send_json.assert_called_once_with(message)
        mock_ws2.send_json.assert_called_once_with(message)
    
    @pytest.mark.asyncio
    async def test_broadcast_removes_failed_connections(self, connection_manager, mock_websocket):
        """Test that failed connections are removed during broadcast"""
        await connection_manager.connect(mock_websocket)
        mock_websocket.send_json.side_effect = Exception("Connection closed")
        
        message = {"type": "test"}
        await connection_manager.broadcast(message)
        
        # Connection should be removed after failure
        assert connection_manager.connection_count == 0


class TestGeminiService:
    """Tests for Gemini AI service"""
    
    @pytest.mark.asyncio
    async def test_generate_insight_not_available(self, sample_summary_data):
        """Test insight generation when Gemini is not available"""
        with patch('app.services.ai_service.GEMINI_AVAILABLE', False):
            from app.services.ai_service import GeminiService
            service = GeminiService()
            
            result = await service.generate_insight(sample_summary_data)
            
            assert result["status"] == "AI not available"
            assert "recommendation" in result
    
    @pytest.mark.asyncio
    async def test_generate_insight_success(self, sample_summary_data):
        """Test successful insight generation with mocked Gemini"""
        with patch('app.services.ai_service.GEMINI_AVAILABLE', True):
            with patch('app.services.ai_service.GEMINI_API_KEY', 'test-key'):
                with patch('app.services.ai_service.genai') as mock_genai:
                    from app.services.ai_service import GeminiService
                    
                    # Create a mock response
                    mock_response = MagicMock()
                    mock_response.text = "System is healthy. No concerns. Keep monitoring."
                    
                    mock_model = MagicMock()
                    mock_model.generate_content.return_value = mock_response
                    mock_genai.GenerativeModel.return_value = mock_model
                    
                    service = GeminiService()
                    # Manually set configured state since we're mocking
                    service._configured = True
                    service._model = mock_model
                    
                    result = await service.generate_insight(sample_summary_data)
                    
                    assert result["status"] == "success"
                    assert "insight" in result
                    assert "timestamp" in result


class TestKafkaProducerService:
    """Tests for Kafka producer service"""
    
    def test_produce_event(self):
        """Test producing an event to Kafka with Avro serialization"""
        with patch('app.services.kafka_service.Producer') as MockProducer:
            mock_producer_instance = MagicMock()
            MockProducer.return_value = mock_producer_instance
            
            from app.services.kafka_service import KafkaProducerService
            
            service = KafkaProducerService()
            # Include all required fields for CloudEvent Avro schema
            event = {
                "specversion": "1.0",
                "id": "test-123",
                "type": "test.event",
                "source": "https://test.com/demo",
                "time": "2024-01-01T00:00:00Z",
                "data": {"test": True},
                "severity": "info",
                "category": "test"
            }
            
            service.produce_event(event)
            
            mock_producer_instance.produce.assert_called_once()
            mock_producer_instance.flush.assert_called_once()
