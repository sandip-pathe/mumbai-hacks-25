"""
WebSocket endpoint for real-time updates
Pushes alerts and score changes to frontend
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Set
import asyncio
import logging
import json
from utils.redis_client import redis_client, CHANNEL_SCORE_UPDATED, CHANNEL_ALERT_CREATED

logger = logging.getLogger(__name__)

router = APIRouter()

# Active WebSocket connections (using Set for O(1) removal)
active_connections: Set[WebSocket] = set()

# Heartbeat interval (seconds)
HEARTBEAT_INTERVAL = 30


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates
    Frontend connects and receives push notifications with heartbeat
    """
    await websocket.accept()
    active_connections.add(websocket)
    logger.info(f"✅ WebSocket connected, total: {len(active_connections)}")
    
    # Create heartbeat task
    async def send_heartbeat():
        try:
            while True:
                await asyncio.sleep(HEARTBEAT_INTERVAL)
                if websocket in active_connections:
                    await websocket.send_json({"type": "ping"})
        except:
            pass
    
    heartbeat_task = asyncio.create_task(send_heartbeat())
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Anaya Watchtower"
        })
        
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            
            # Respond to pings
            if data == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        active_connections.discard(websocket)
        heartbeat_task.cancel()
        logger.info(f"❌ WebSocket disconnected, remaining: {len(active_connections)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        active_connections.discard(websocket)
        heartbeat_task.cancel()


async def broadcast_message(message: dict):
    """Broadcast message to all connected WebSocket clients"""
    if not active_connections:
        return
    
    # Create list to track dead connections
    dead_connections = set()
    
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.warning(f"Failed to send to WebSocket: {e}")
            dead_connections.add(connection)
    
    # Remove dead connections
    active_connections.difference_update(dead_connections)


# Redis event listeners
async def listen_for_redis_events():
    """Subscribe to Redis events and push via WebSocket"""
    async def handle_score_update(data: dict):
        await broadcast_message({
            "type": "score_updated",
            "data": data
        })
    
    async def handle_alert_created(data: dict):
        await broadcast_message({
            "type": "alert_created",
            "data": data
        })
    
    await redis_client.subscribe(CHANNEL_SCORE_UPDATED, handle_score_update)
    await redis_client.subscribe(CHANNEL_ALERT_CREATED, handle_alert_created)