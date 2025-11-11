"""
Transaction Monitor Agent
Simulates anomaly detection for demo purposes
In production, would connect to real transaction data
"""
import asyncio
import logging
import random
from datetime import datetime
import uuid
from typing import Dict, Any
from db.database import AsyncSessionLocal
from db.models import Alert, AgentLog
from utils.redis_client import redis_client, CHANNEL_ANOMALY_DETECTED
from utils.slack_notifier import slack_notifier

logger = logging.getLogger(__name__)


class TransactionMonitorAgent:
    """
    Agent that monitors transactions for suspicious patterns
    (Mocked for demo - shows system architecture)
    """
    
    def __init__(self):
        self.name = "TransactionMonitorAgent"
        self.running = False
    
    async def start(self):
        """Start monitoring (simulated)"""
        self.running = True
        logger.info(f"🔍 {self.name} started (demo mode)")
        
        # Simulate occasional anomalies for demo
        asyncio.create_task(self._simulate_anomalies())
    
    async def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info(f"🛑 {self.name} stopped")
    
    async def _simulate_anomalies(self):
        """Generate fake anomalies for demo purposes"""
        while self.running:
            await asyncio.sleep(300)  # Every 5 minutes
            
            # 20% chance to generate anomaly
            if random.random() < 0.2:
                await self.generate_demo_anomaly()
    
    async def generate_demo_anomaly(self):
        """Create a fake anomaly alert"""
        anomaly_types = [
            {
                "type": "High-Value Transaction",
                "description": "Transaction of ₹25,00,000 detected from new customer account",
                "details": {
                    "Amount": "₹25,00,000",
                    "Account Age": "3 days",
                    "Customer ID": f"CUST{random.randint(10000, 99999)}"
                }
            },
            {
                "type": "Structuring Pattern",
                "description": "Multiple transactions just below ₹10L threshold detected",
                "details": {
                    "Transactions": "7 in 24 hours",
                    "Total Amount": "₹68,50,000",
                    "Customer ID": f"CUST{random.randint(10000, 99999)}"
                }
            },
            {
                "type": "International Wire Transfer",
                "description": "Large international transfer to high-risk jurisdiction",
                "details": {
                    "Amount": "$45,000 USD",
                    "Destination": "Country: XYZ",
                    "Customer ID": f"CUST{random.randint(10000, 99999)}"
                }
            }
        ]
        
        anomaly = random.choice(anomaly_types)
        
        async with AsyncSessionLocal() as db:
            try:
                # Create alert
                alert = Alert(
                    id=str(uuid.uuid4()),
                    alert_type="anomaly",
                    severity="high",
                    title=anomaly['type'],
                    message=anomaly['description'],
                    created_at=datetime.utcnow()
                )
                db.add(alert)
                await db.commit()
                
                logger.info(f"⚠️ Anomaly detected: {anomaly['type']}")
                
                # Send Slack notification
                await slack_notifier.send_anomaly_alert(
                    anomaly_type=anomaly['type'],
                    description=anomaly['description'],
                    details=anomaly['details']
                )
                
                # Publish event
                await redis_client.publish(CHANNEL_ANOMALY_DETECTED, {
                    "event_type": "anomaly_detected",
                    "alert_id": alert.id,
                    "anomaly_type": anomaly['type']
                })
                
            except Exception as e:
                logger.error(f"❌ Failed to create anomaly alert: {e}")