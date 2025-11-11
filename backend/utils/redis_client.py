"""Wrapper re-exporting the clean Redis client implementation.

This file intentionally keeps a tiny import surface so the rest of the
codebase can import `from utils.redis_client import redis_client` without
needing to know about the implementation module.
"""

from ._redis_client_impl import (
    redis_client,
    CHANNEL_NEW_CIRCULAR,
    CHANNEL_POLICY_UPDATED,
    CHANNEL_SCORE_UPDATED,
    CHANNEL_ALERT_CREATED,
    CHANNEL_ANOMALY_DETECTED,
)

__all__ = [
    "redis_client",
    "CHANNEL_NEW_CIRCULAR",
    "CHANNEL_POLICY_UPDATED",
    "CHANNEL_SCORE_UPDATED",
    "CHANNEL_ALERT_CREATED",
    "CHANNEL_ANOMALY_DETECTED",
]
