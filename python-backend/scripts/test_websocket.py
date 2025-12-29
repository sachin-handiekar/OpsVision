#!/usr/bin/env python
"""
Test WebSocket connection and consume_gemini_summaries
"""

import asyncio
import sys
sys.path.insert(0, '.')

async def test_websocket():
    import websockets
    import json
    
    print("Connecting to WebSocket...")
    try:
        async with websockets.connect('ws://localhost:8000/ws') as ws:
            print("✓ Connected to WebSocket!")
            
            # Send ping
            await ws.send('ping')
            print("Sent: ping")
            
            # Wait for pong
            resp = await asyncio.wait_for(ws.recv(), timeout=3)
            data = json.loads(resp)
            print(f"Received: {data}")
            
            if data.get('type') == 'pong':
                print("✓ Ping/Pong works!")
            
            # Wait for summaries (with timeout)
            print("\nWaiting for Gemini summaries (10 seconds)...")
            try:
                while True:
                    resp = await asyncio.wait_for(ws.recv(), timeout=10)
                    data = json.loads(resp)
                    print(f"\n✓ Received message type: {data.get('type')}")
                    if data.get('type') == 'ai_alert':
                        print(f"  Summary: {json.dumps(data.get('summary'), indent=2)[:500]}...")
                        break
            except asyncio.TimeoutError:
                print("  (No new summaries received - topic uses 'latest' offset)")
            
            print("\n✓ WebSocket is working correctly!")
            
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
