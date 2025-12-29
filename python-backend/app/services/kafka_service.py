# app/services/kafka_service.py
"""
Kafka producer and consumer services with Avro serialization
"""

import io
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from confluent_kafka import Producer, Consumer
import fastavro

from ..config import KAFKA_CONFIG, CLOUDEVENTS_TOPIC, GEMINI_SUMMARY_TOPIC

logger = logging.getLogger(__name__)

# Load Avro schema
SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "cloudevent.avsc"
with open(SCHEMA_PATH, "r") as f:
    CLOUDEVENT_SCHEMA = json.load(f)
PARSED_SCHEMA = fastavro.parse_schema(CLOUDEVENT_SCHEMA)


def serialize_avro(record: Dict[str, Any]) -> bytes:
    """Serialize a record to Avro binary format"""
    buffer = io.BytesIO()
    fastavro.schemaless_writer(buffer, PARSED_SCHEMA, record)
    return buffer.getvalue()


def deserialize_avro(data: bytes) -> Dict[str, Any]:
    """Deserialize Avro binary data to a record"""
    buffer = io.BytesIO(data)
    return fastavro.schemaless_reader(buffer, PARSED_SCHEMA)


def prepare_cloudevent(event: dict) -> dict:
    """Prepare a CloudEvent dict for Avro serialization.
    
    Converts the 'data' field to JSON string if it's a dict,
    and ensures all fields match the Avro schema.
    """
    # Convert data dict to JSON string for Avro
    data_value = event.get('data')
    if isinstance(data_value, dict):
        data_value = json.dumps(data_value)
    
    return {
        "specversion": event.get("specversion", "1.0"),
        "type": event["type"],
        "source": event["source"],
        "id": event["id"],
        "time": event["time"],
        "datacontenttype": event.get("datacontenttype", "application/json"),
        "subject": event.get("subject"),
        "data": data_value,
        "severity": event.get("severity"),
        "category": event.get("category"),
        "correlation_id": event.get("correlation_id"),
    }


class KafkaProducerService:
    """Kafka producer service for sending events with Avro serialization"""
    
    def __init__(self):
        self._producer: Optional[Producer] = None
    
    @property
    def producer(self) -> Producer:
        """Lazy initialization of Kafka producer"""
        if self._producer is None:
            self._producer = Producer(KAFKA_CONFIG)
            logger.info("Kafka producer initialized (Avro serialization enabled)")
        return self._producer
    
    def produce_event(self, event: dict, topic: str = CLOUDEVENTS_TOPIC) -> None:
        """Send an event to Kafka topic using Avro serialization"""
        # Prepare and serialize the event
        prepared_event = prepare_cloudevent(event)
        avro_bytes = serialize_avro(prepared_event)
        
        self.producer.produce(
            topic=topic,
            key=event.get('id', '').encode('utf-8'),
            value=avro_bytes
        )
        self.producer.flush()
        logger.debug(f"Event sent to {topic} (Avro): {event.get('id')}")
    
    def close(self) -> None:
        """Close the producer connection"""
        if self._producer:
            self._producer.flush()
            self._producer = None


class KafkaConsumerService:
    """Kafka consumer service for receiving Avro messages from Flink tables"""
    
    def __init__(self, group_id: str = 'demo-app-consumer', read_from_beginning: bool = False):
        self._consumer = None
        self._deserializer = None
        self._group_id = group_id
        self._use_avro = False
        self._read_from_beginning = read_from_beginning
        
        # Try to set up Avro deserializer if Schema Registry is configured
        try:
            from ..config import SCHEMA_REGISTRY_URL, SCHEMA_REGISTRY_CONFIG
            logger.info(f"Schema Registry URL: {SCHEMA_REGISTRY_URL}")
            logger.info(f"Schema Registry Config keys: {list(SCHEMA_REGISTRY_CONFIG.keys()) if SCHEMA_REGISTRY_CONFIG else 'None'}")
            
            if SCHEMA_REGISTRY_URL and SCHEMA_REGISTRY_CONFIG:
                from confluent_kafka.schema_registry import SchemaRegistryClient
                from confluent_kafka.schema_registry.avro import AvroDeserializer
                
                sr_client = SchemaRegistryClient(SCHEMA_REGISTRY_CONFIG)
                self._deserializer = AvroDeserializer(sr_client)
                self._use_avro = True
                logger.info("✓ Schema Registry configured - Avro deserialization enabled")
            else:
                logger.warning("Schema Registry not configured - will try JSON fallback")
        except ImportError as e:
            logger.warning(f"Schema Registry/Avro not available (install confluent-kafka[avro]): {e}")
        except Exception as e:
            logger.error(f"Schema Registry setup failed: {e}", exc_info=True)
    
    @property
    def consumer(self) -> Consumer:
        """Lazy initialization of Kafka consumer"""
        if self._consumer is None:
            # Use unique group ID if reading from beginning to avoid offset conflicts
            group_id = self._group_id
            if self._read_from_beginning:
                import time
                group_id = f"{self._group_id}-{int(time.time())}"
            
            consumer_config = KAFKA_CONFIG.copy()
            consumer_config.update({
                'group.id': group_id,
                'auto.offset.reset': 'earliest' if self._read_from_beginning else 'latest',
            })
            self._consumer = Consumer(consumer_config)
            self._consumer.subscribe([GEMINI_SUMMARY_TOPIC])
            offset_mode = 'earliest' if self._read_from_beginning else 'latest'
            logger.info(f"Kafka consumer initialized for {GEMINI_SUMMARY_TOPIC} (offset: {offset_mode})")
        return self._consumer
    
    def poll(self, timeout: float = 1.0):
        """Poll for new messages"""
        return self.consumer.poll(timeout=timeout)
    
    def deserialize_message(self, msg) -> Optional[dict]:
        """Deserialize a Kafka message, handling both Avro and JSON"""
        if msg is None or msg.error():
            return None
        
        raw_value = msg.value()
        if raw_value is None:
            return None
        
        # Try Avro deserialization first if configured
        if self._use_avro and self._deserializer:
            try:
                from confluent_kafka.serialization import SerializationContext, MessageField
                ctx = SerializationContext(msg.topic(), MessageField.VALUE)
                return self._deserializer(raw_value, ctx)
            except Exception as e:
                logger.debug(f"Avro deserialization failed, trying JSON: {e}")
        
        # Fall back to JSON
        try:
            return json.loads(raw_value.decode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to deserialize message: {e}")
            return None
    
    def close(self) -> None:
        """Close the consumer connection"""
        if self._consumer:
            self._consumer.close()
            self._consumer = None

# Global instances
kafka_producer = KafkaProducerService()
