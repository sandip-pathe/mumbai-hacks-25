"""
Audit Prep Agent
Calculates compliance scores based on policy diffs and circular analysis
Updates scores in real-time as new circulars are processed
"""
import asyncio
import logging
from datetime import datetime
import uuid
from typing import Dict, Any
from db.database import AsyncSessionLocal
from db.models import ComplianceScore, PolicyDiff, Alert, AgentLog
from utils.redis_client import redis_client, CHANNEL_POLICY_UPDATED, CHANNEL_SCORE_UPDATED
from utils.slack_notifier import slack_notifier
from sqlalchemy import select, func

logger = logging.getLogger(__name__)


class AuditPrepAgent:
    """
    Agent that calculates and updates compliance scores
    Triggers on policy_updated events
    """
    
    def __init__(self):
        self.name = "AuditPrepAgent"
    
    async def start(self):
        """Subscribe to policy_updated events"""
        logger.info(f"📊 {self.name} started, monitoring policy changes...")
        await redis_client.subscribe(CHANNEL_POLICY_UPDATED, self.handle_policy_update)
    
    async def handle_policy_update(self, event: Dict[str, Any]):
        """Recalculate compliance score after policy analysis"""
        start_time = datetime.utcnow()
        
        logger.info(f"📈 {self.name} calculating compliance score...")
        
        async with AsyncSessionLocal() as db:
            try:
                # Log action
                log = AgentLog(
                    id=str(uuid.uuid4()),
                    agent_name=self.name,
                    action="calculate_score",
                    status="in_progress",
                    input_data=event,
                    started_at=start_time
                )
                db.add(log)
                await db.commit()
                
                # Get previous score
                result = await db.execute(
                    select(ComplianceScore).order_by(ComplianceScore.calculated_at.desc()).limit(1)
                )
                previous_score = result.scalar_one_or_none()
                old_score = previous_score.score if previous_score else 82.0
                
                # Calculate new score
                new_score = await self.calculate_compliance_score(db)
                
                # Create new score record
                score_record = ComplianceScore(
                    id=str(uuid.uuid4()),
                    score=new_score['overall'],
                    total_circulars=new_score['total_circulars'],
                    pending_reviews=new_score['pending_reviews'],
                    critical_issues=new_score['critical_issues'],
                    high_issues=new_score['high_issues'],
                    score_breakdown=new_score['breakdown'],
                    calculated_at=datetime.utcnow(),
                    notes=f"Updated after circular processing"
                )
                db.add(score_record)
                await db.commit()
                
                logger.info(f"✅ Compliance score updated: {new_score['overall']:.1f}%")
                
                # Create alert if significant change
                score_change = new_score['overall'] - old_score
                if abs(score_change) >= 2.0:  # Alert if >2% change
                    alert = Alert(
                        id=str(uuid.uuid4()),
                        alert_type="score_change",
                        severity="medium" if score_change < 0 else "info",
                        title=f"Compliance Score {'Decreased' if score_change < 0 else 'Increased'}",
                        message=f"Score changed from {old_score:.1f}% to {new_score['overall']:.1f}% ({score_change:+.1f}%)",
                        created_at=datetime.utcnow()
                    )
                    db.add(alert)
                    await db.commit()
                    
                    # Send Slack notification
                    await slack_notifier.send_compliance_score_alert(
                        old_score=old_score,
                        new_score=new_score['overall'],
                        reason="New circular processed and policy impact analyzed"
                    )
                
                # Update log
                log.status = "success"
                log.completed_at = datetime.utcnow()
                log.duration_seconds = (log.completed_at - start_time).total_seconds()
                log.output_data = {"new_score": new_score['overall']}
                await db.commit()
                
                # Publish score_updated event
                await redis_client.publish(CHANNEL_SCORE_UPDATED, {
                    "event_type": "score_updated",
                    "score": new_score['overall'],
                    "change": score_change
                })
                
            except Exception as e:
                logger.error(f"❌ {self.name} failed: {e}")
                log.status = "failed"
                log.error_message = str(e)
                await db.commit()
    
    async def calculate_compliance_score(self, db) -> Dict[str, Any]:
        """
        Calculate overall compliance score based on policy diffs
        Formula: Start at 100, deduct points for critical/high issues
        """
        try:
            # Count policy diffs by severity
            result = await db.execute(
                select(
                    PolicyDiff.severity,
                    func.count(PolicyDiff.id)
                ).group_by(PolicyDiff.severity)
            )
            severity_counts = dict(result.all())
            
            critical_count = severity_counts.get('critical', 0)
            high_count = severity_counts.get('high', 0)
            medium_count = severity_counts.get('medium', 0)
            low_count = severity_counts.get('low', 0)
            
            # Count pending reviews
            result = await db.execute(
                select(func.count(PolicyDiff.id)).where(PolicyDiff.status == 'pending')
            )
            pending_reviews = result.scalar()
            
            # Score calculation (deduct points)
            base_score = 100.0
            score = base_score
            score -= critical_count * 8.0   # -8% per critical issue
            score -= high_count * 4.0       # -4% per high issue
            score -= medium_count * 2.0     # -2% per medium issue
            score -= low_count * 0.5        # -0.5% per low issue
            
            # Ensure score doesn't go below 0
            score = max(0, score)
            
            # Category breakdown (simulate for demo)
            breakdown = {
                "kyc_aml": max(70, score - 5 + (critical_count * -3)),
                "digital_lending": max(70, score + 2),
                "payments": max(70, score - 1),
                "cyber_security": max(70, score + 1),
                "data_privacy": max(70, score)
            }
            
            return {
                "overall": score,
                "total_circulars": critical_count + high_count + medium_count + low_count,
                "pending_reviews": pending_reviews,
                "critical_issues": critical_count,
                "high_issues": high_count,
                "breakdown": breakdown
            }
            
        except Exception as e:
            logger.error(f"❌ Score calculation failed: {e}")
            return {
                "overall": 75.0,
                "total_circulars": 0,
                "pending_reviews": 0,
                "critical_issues": 0,
                "high_issues": 0,
                "breakdown": {}
            }