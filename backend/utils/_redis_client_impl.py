"""
Internal Redis client implementation (kept separate so wrapper can be simple).
"""

import asyncio
import json
import logging
from typing import Callable, Dict, Any, Optional

import redis.asyncio as redis

from config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client for pub/sub messaging between agents"""

    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.client: Optional[redis.Redis] = None
        self.pubsubs: Dict[str, redis.client.PubSub] = {}
        self.subscribers: Dict[str, Callable] = {}

    async def connect(self):
        try:
            self.client = await redis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )
            await self.client.ping()
            logger.info("✅ Redis connected")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise

    async def disconnect(self):
        for p in list(self.pubsubs.values()):
            try:
                await p.close()
            except Exception:
                pass
        if self.client:
            await self.client.close()
        logger.info("✅ Redis disconnected")

    async def publish(self, channel: str, message: Dict[str, Any]):
        try:
            message_json = json.dumps(message)
            await self.client.publish(channel, message_json)
            logger.info(f"📤 Published to {channel}")
        except Exception as e:
            logger.error(f"❌ Publish failed: {e}")

    async def subscribe(self, channel: str, callback: Callable):
        try:
            if channel in self.pubsubs:
                logger.warning(f"Already subscribed to {channel}")
                return
            p = self.client.pubsub()
            await p.subscribe(channel)
            self.pubsubs[channel] = p
            self.subscribers[channel] = callback
            logger.info(f"📥 Subscribed to {channel}")
            asyncio.create_task(self._listen_to_channel(channel))
        except Exception as e:
            logger.error(f"❌ Subscribe failed: {e}")

    async def _listen_to_channel(self, channel: str):
        p = self.pubsubs.get(channel)
        if not p:
            logger.error(f"No pubsub for channel {channel}")
            return
        try:
            async for message in p.listen():
                if message.get("type") == "message":
                    try:
                        data = json.loads(message["data"])
                    except Exception:
                        data = message["data"]
                    callback = self.subscribers.get(channel)
                    if callback:
                        await callback(data)
        except Exception as e:
            logger.error(f"❌ Listener error on {channel}: {e}")

    async def set_cache(self, key: str, value: Any, expire_seconds: int = 3600):
        try:
            value_json = json.dumps(value)
            await self.client.setex(key, expire_seconds, value_json)
        except Exception as e:
            logger.error(f"❌ Cache set failed: {e}")

    async def get_cache(self, key: str) -> Any:
        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"❌ Cache get failed: {e}")
            return None


# Instance and constants
redis_client = RedisClient()

CHANNEL_NEW_CIRCULAR = "new_circular"
CHANNEL_POLICY_UPDATED = "policy_updated"
CHANNEL_SCORE_UPDATED = "score_updated"
CHANNEL_ALERT_CREATED = "alert_created"
CHANNEL_ANOMALY_DETECTED = "anomaly_detected"
