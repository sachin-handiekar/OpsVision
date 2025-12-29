#!/usr/bin/env python
"""
Test script to verify consumption from Confluent Cloud Flink table
Run: python scripts/test_consumer.py
"""

import json
import sys
from datetime import datetime

# Add parent dir to path for imports
sys.path.insert(0, '.')

from app.config import KAFKA_CONFIG, GEMINI_SUMMARY_TOPIC
from confluent_kafka import Consumer, KafkaError

def main():
    print(f"=" * 60)
    print(f"Testing Kafka Consumer for: {GEMINI_SUMMARY_TOPIC}")
    print(f"Bootstrap servers: {KAFKA_CONFIG.get('bootstrap.servers')}")
    print(f"Security: {KAFKA_CONFIG.get('security.protocol', 'PLAINTEXT')}")
    print(f"=" * 60)
    
    consumer_config = KAFKA_CONFIG.copy()
    consumer_config.update({
        'group.id': 'test-consumer-debug-' + datetime.now().strftime('%H%M%S'),
        'auto.offset.reset': 'earliest',  # Read from beginning
        'enable.auto.commit': False,
    })
    
    print(f"\nConsumer config:")
    for k, v in consumer_config.items():
        if 'secret' not in k.lower() and 'password' not in k.lower():
            print(f"  {k}: {v}")
    
    try:
        consumer = Consumer(consumer_config)
        print(f"\n✓ Consumer created successfully")
    except Exception as e:
        print(f"\n✗ Failed to create consumer: {e}")
        return
    
    try:
        consumer.subscribe([GEMINI_SUMMARY_TOPIC])
        print(f"✓ Subscribed to topic: {GEMINI_SUMMARY_TOPIC}")
    except Exception as e:
        print(f"\n✗ Failed to subscribe: {e}")
        consumer.close()
        return
    
    print(f"\n[{datetime.now().isoformat()}] Waiting for messages...")
    print("(Press Ctrl+C to stop)\n")
    
    message_count = 0
    poll_count = 0
    
    try:
        while True:
            msg = consumer.poll(timeout=2.0)
            poll_count += 1
            
            if msg is None:
                if poll_count % 5 == 0:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Still waiting... (polled {poll_count} times)")
                continue
            
            if msg.error():
                error_code = msg.error().code()
                if error_code == KafkaError._PARTITION_EOF:
                    print(f"[INFO] Reached end of partition {msg.partition()}")
                elif error_code == KafkaError.UNKNOWN_TOPIC_OR_PART:
                    print(f"[ERROR] Topic '{GEMINI_SUMMARY_TOPIC}' does not exist!")
                    break
                else:
                    print(f"[ERROR] {msg.error()}")
                continue
            
            message_count += 1
            print(f"\n{'=' * 50}")
            print(f"[MESSAGE #{message_count}] {datetime.now().isoformat()}")
            print(f"  Topic: {msg.topic()}")
            print(f"  Partition: {msg.partition()}")
            print(f"  Offset: {msg.offset()}")
            print(f"  Key: {msg.key()}")
            print(f"  Headers: {msg.headers()}")
            
            raw_value = msg.value()
            print(f"  Raw bytes length: {len(raw_value) if raw_value else 0}")
            
            # Try JSON first
            try:
                value = json.loads(raw_value.decode('utf-8'))
                print(f"  Value (JSON):")
                print(json.dumps(value, indent=4))
            except:
                # Try showing as hex for Avro
                print(f"  Value (hex): {raw_value[:100].hex()}...")
                print(f"  Value (raw attempt): {raw_value[:200]}")
            
            print(f"{'=' * 50}")
    
    except KeyboardInterrupt:
        print(f"\n\nStopped. Total messages received: {message_count}")
    finally:
        consumer.close()
        print("Consumer closed.")


if __name__ == "__main__":
    main()
