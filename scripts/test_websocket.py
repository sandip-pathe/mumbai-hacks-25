#!/usr/bin/env python3
"""
WebSocket Test Script
Tests the WebSocket connection to verify:
1. Connection establishment
2. Handshake message
3. Heartbeat/ping-pong
4. Message broadcasting
"""
import asyncio
import json
import websockets

WS_URL = "ws://localhost:8000/ws"

async def test_websocket():
    print("🔌 Connecting to WebSocket...")
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ Connected!")
            
            # Wait for initial handshake
            message = await websocket.recv()
            data = json.loads(message)
            print(f"📨 Received: {data}")
            
            if data.get("type") == "connected":
                print("✅ Handshake successful!")
            
            # Send a ping
            print("\n📤 Sending ping...")
            await websocket.send("ping")
            
            # Wait for pong
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            print(f"📨 Received: {response_data}")
            
            if response_data.get("type") == "pong":
                print("✅ Ping-pong working!")
            
            # Keep connection open and listen for heartbeats
            print("\n👂 Listening for server heartbeats (30s interval)...")
            print("   Press Ctrl+C to stop\n")
            
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                if data.get("type") == "ping":
                    print("💓 Server heartbeat received, responding with pong...")
                    await websocket.send("pong")
                else:
                    print(f"📨 Event: {data}")
                    
    except websockets.exceptions.ConnectionClosed:
        print("❌ Connection closed")
    except asyncio.TimeoutError:
        print("⏱️ Timeout waiting for response")
    except KeyboardInterrupt:
        print("\n👋 Disconnecting...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
