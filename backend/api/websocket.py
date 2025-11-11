"""
WebSocket endpoint for real-time updates
Pushes alerts and score changes to frontend
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import logging
import json
from utils.redis_client import redis_client, CHANNEL_SCORE_UPDATED, CHANNEL_ALERT_CREATED

logger = logging.getLogger(__name__)

router = APIRouter()

# Active WebSocket connections
active_connections: List[WebSocket] = []


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates
    Frontend connects and receives push notifications
    """
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"✅ WebSocket connected, total: {len(active_connections)}")
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Anaya Watchtower"
        })
        
        # Keep connection alive and listen for messages
        while True:
            # Frontend can send ping messages
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_text("pong")
                
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"❌ WebSocket disconnected, remaining: {len(active_connections)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


async def broadcast_message(message: dict):
    """Broadcast message to all connected WebSocket clients"""
    if not active_connections:
        return
    
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            # Remove dead connections
            active_connections.remove(connection)


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