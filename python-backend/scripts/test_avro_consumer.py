#!/usr/bin/env python
"""
Test Avro deserialization from gemini_summary topic with Schema Registry
"""

import json
import sys
from datetime import datetime

sys.path.insert(0, '.')

from app.config import (
    KAFKA_CONFIG, 
    GEMINI_SUMMARY_TOPIC,
    SCHEMA_REGISTRY_URL,
    SCHEMA_REGISTRY_CONFIG
)
from confluent_kafka import Consumer, KafkaError

def main():
    print("=" * 60)
    print(f"Testing Avro Consumer for: {GEMINI_SUMMARY_TOPIC}")
    print(f"Schema Registry: {SCHEMA_REGISTRY_URL}")
    print("=" * 60)
    
    # Set up Avro deserializer
    deserializer = None
    try:
        from confluent_kafka.schema_registry import SchemaRegistryClient
        from confluent_kafka.schema_registry.avro import AvroDeserializer
        from confluent_kafka.serialization import SerializationContext, MessageField
        
        sr_client = SchemaRegistryClient(SCHEMA_REGISTRY_CONFIG)
        deserializer = AvroDeserializer(sr_client)
        print("✓ Schema Registry client created")
        print("✓ Avro deserializer ready")
    except Exception as e:
        print(f"✗ Error setting up Avro: {e}")
        return
    
    # Set up consumer
    consumer_config = KAFKA_CONFIG.copy()
    consumer_config.update({
        'group.id': f'avro-test-{datetime.now().strftime("%H%M%S")}',
        'auto.offset.reset': 'earliest',
    })
    
    consumer = Consumer(consumer_config)
    consumer.subscribe([GEMINI_SUMMARY_TOPIC])
    print(f"✓ Subscribed to {GEMINI_SUMMARY_TOPIC}")
    print("\nWaiting for messages (Ctrl+C to stop)...\n")
    
    message_count = 0
    
    try:
        while True:
            msg = consumer.poll(timeout=2.0)
            
            if msg is None:
                print(".", end="", flush=True)
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"\n[End of partition {msg.partition()}]")
                else:
                    print(f"\n[ERROR] {msg.error()}")
                continue
            
            message_count += 1
            print(f"\n\n{'=' * 50}")
            print(f"[MESSAGE #{message_count}]")
            print(f"  Offset: {msg.offset()}")
            
            # Deserialize with Avro
            try:
                ctx = SerializationContext(msg.topic(), MessageField.VALUE)
                record = deserializer(msg.value(), ctx)
                print(f"  ✓ Avro deserialized successfully!")
                print(f"  Content:")
                print(json.dumps(record, indent=4, default=str))
            except Exception as e:
                print(f"  ✗ Avro error: {e}")
                print(f"  Raw hex: {msg.value()[:50].hex()}...")
            
            print("=" * 50)
    
    except KeyboardInterrupt:
        print(f"\n\nTotal messages: {message_count}")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
