"""
Agent Manager - Orchestrates all 5 Anaya agents
Handles scheduling, coordination, and lifecycle management
"""
import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from agents.regulatory_watch import RegulatoryWatchAgent
from agents.policy_automation import PolicyAutomationAgent
from agents.audit_prep import AuditPrepAgent
from agents.transaction_monitor import TransactionMonitorAgent
from agents.advisory import AdvisoryAgent
from utils.slack_notifier import slack_notifier

logger = logging.getLogger(__name__)


class AgentManager:
    """
    Manages the 5 Anaya AI Agents:
    1. Anaya Radar (Regulatory Watch)
    2. Anaya Draft (Policy Automation)
    3. Anaya Score (Audit Prep)
    4. Anaya Sentinel (Transaction Monitor)
    5. Anaya Counsel (Advisory)
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.agents = {
            'radar': RegulatoryWatchAgent(),
            'draft': PolicyAutomationAgent(),
            'score': AuditPrepAgent(),
            'sentinel': TransactionMonitorAgent(),
            'counsel': AdvisoryAgent()
        }
        self.is_running = False
        
    async def start(self):
        """Start all agents and scheduler"""
        if self.is_running:
            logger.warning("⚠️ Agent Manager already running")
            return
            
        logger.info("🚀 Starting Anaya Agent Manager...")
        
        # Start individual agents as background tasks (non-blocking)
        try:
            # Start agents with continuous monitoring loops in background
            asyncio.create_task(self.agents['radar'].start())
            asyncio.create_task(self.agents['sentinel'].start())
            
            # Policy automation and audit prep don't have continuous loops
            # They will be triggered by scheduler
            
            # Advisory agent is on-demand only
            
            logger.info("✅ All agents initialized")
        except Exception as e:
            logger.error(f"❌ Failed to start agents: {e}")
            raise
        
        # Schedule periodic tasks
        self._schedule_tasks()
        
        # Start scheduler
        self.scheduler.start()
        self.is_running = True
        
        logger.info("✅ Agent Manager started successfully")
        await slack_notifier.send_notification(
            title="🤖 Anaya Agent Manager Started",
            message="All 5 agents are now active and monitoring compliance.",
            severity="info"
        )
        
    async def stop(self):
        """Stop all agents and scheduler"""
        logger.info("🛑 Stopping Agent Manager...")
        
        try:
            await self.agents['radar'].stop()
            await self.agents['sentinel'].stop()
            
            self.scheduler.shutdown()
            self.is_running = False
            
            logger.info("✅ Agent Manager stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping agents: {e}")
            
    def _schedule_tasks(self):
        """Schedule all periodic agent tasks"""
        
        # 1. Anaya Radar - Check RBI website every 30 minutes
        self.scheduler.add_job(
            self._run_radar_check,
            trigger=IntervalTrigger(minutes=30),
            id='radar_check',
            name='Anaya Radar - RBI Circular Check',
            replace_existing=True
        )
        logger.info("📡 Scheduled: Anaya Radar (every 30 minutes)")
        
        # 2. Anaya Score - Calculate compliance score daily at 6 AM
        self.scheduler.add_job(
            self._run_score_calculation,
            trigger=CronTrigger(hour=6, minute=0),
            id='score_calculation',
            name='Anaya Score - Daily Compliance Score',
            replace_existing=True
        )
        logger.info("📊 Scheduled: Anaya Score (daily at 6 AM)")
        
        # 3. Anaya Sentinel - Monitor transactions every 5 minutes
        self.scheduler.add_job(
            self._run_sentinel_monitor,
            trigger=IntervalTrigger(minutes=5),
            id='sentinel_monitor',
            name='Anaya Sentinel - Transaction Monitor',
            replace_existing=True
        )
        logger.info("🛡️ Scheduled: Anaya Sentinel (every 5 minutes)")
        
        # 4. Anaya Draft runs on-demand when new circulars detected (via Redis pubsub)
        logger.info("📝 Anaya Draft: Listening for new circulars via Redis")
        
        # 5. Anaya Counsel is on-demand via API
        logger.info("💡 Anaya Counsel: Available via /api/chat endpoint")
        
    async def _run_radar_check(self):
        """Run Anaya Radar to check for new RBI circulars"""
        try:
            logger.info("🔍 Anaya Radar: Checking RBI website...")
            # The agent's background task will handle this
            # Just log the scheduled check
        except Exception as e:
            logger.error(f"❌ Anaya Radar failed: {e}")
            await slack_notifier.send_notification(
                title="⚠️ Anaya Radar Error",
                message=f"Failed to check RBI website: {str(e)}",
                severity="high"
            )
            
    async def _run_score_calculation(self):
        """Run Anaya Score to calculate compliance"""
        try:
            logger.info("📊 Anaya Score: Calculating compliance score...")
            await self.agents['score'].calculate_compliance_score()
            logger.info("✅ Anaya Score: Calculation complete")
        except Exception as e:
            logger.error(f"❌ Anaya Score failed: {e}")
            await slack_notifier.send_notification(
                title="⚠️ Anaya Score Error",
                message=f"Failed to calculate compliance score: {str(e)}",
                severity="high"
            )
            
    async def _run_sentinel_monitor(self):
        """Run Anaya Sentinel to monitor transactions"""
        try:
            logger.info("🛡️ Anaya Sentinel: Monitoring transactions...")
            # Sentinel runs continuously in background
            # This is just a health check
        except Exception as e:
            logger.error(f"❌ Anaya Sentinel failed: {e}")
            
    async def trigger_agent(self, agent_name: str) -> dict:
        """Manually trigger a specific agent"""
        agent_map = {
            'radar': self._run_radar_check,
            'score': self._run_score_calculation,
            'sentinel': self._run_sentinel_monitor
        }
        
        if agent_name not in agent_map:
            raise ValueError(f"Unknown agent: {agent_name}")
            
        logger.info(f"🎯 Manually triggering agent: {agent_name}")
        await agent_map[agent_name]()
        
        return {
            "agent": agent_name,
            "status": "triggered",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def get_status(self) -> dict:
        """Get status of all agents"""
        return {
            "manager_running": self.is_running,
            "agents": {
                "radar": {
                    "name": "Anaya Radar",
                    "status": "active" if self.is_running else "stopped",
                    "description": "Monitors RBI website for new circulars"
                },
                "draft": {
                    "name": "Anaya Draft",
                    "status": "listening" if self.is_running else "stopped",
                    "description": "Auto-generates policy updates"
                },
                "score": {
                    "name": "Anaya Score",
                    "status": "active" if self.is_running else "stopped",
                    "description": "Calculates compliance scores"
                },
                "sentinel": {
                    "name": "Anaya Sentinel",
                    "status": "monitoring" if self.is_running else "stopped",
                    "description": "Monitors transactions in real-time"
                },
                "counsel": {
                    "name": "Anaya Counsel",
                    "status": "ready",
                    "description": "Provides compliance advisory"
                }
            },
            "next_scheduled_jobs": [
                {
                    "job_id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in self.scheduler.get_jobs()
            ] if self.is_running else []
        }


# Global agent manager instance
agent_manager = AgentManager()
