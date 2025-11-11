"""
Slack notification sender
Sends alerts to configured Slack webhook
"""
import httpx
from config import settings
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Send formatted notifications to Slack via webhook"""
    
    def __init__(self):
        self.webhook_url = settings.SLACK_WEBHOOK_URL
        self.enabled = bool(self.webhook_url and self.webhook_url != "https://hooks.slack.com/services/YOUR/WEBHOOK/URL")
        
        if not self.enabled:
            logger.warning("⚠️ Slack webhook not configured, notifications disabled")
    
    async def send_notification(
        self,
        title: str,
        message: str,
        severity: str = "info",
        fields: Dict[str, str] = None
    ) -> bool:
        """
        Send notification to Slack
        
        Args:
            title: Bold notification title
            message: Main message text
            severity: critical | high | medium | low | info
            fields: Optional dict of additional fields to display
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug(f"Slack disabled, would send: {title}")
            return False
        
        try:
            # Color based on severity
            color_map = {
                "critical": "#FF0000",  # Red
                "high": "#FF6B35",      # Orange
                "medium": "#FFD23F",    # Yellow
                "low": "#4ECDC4",       # Teal
                "info": "#3DDC97"       # Green
            }
            color = color_map.get(severity, "#3DDC97")
            
            # Emoji based on severity
            emoji_map = {
                "critical": "🚨",
                "high": "⚠️",
                "medium": "⚡",
                "low": "📋",
                "info": "ℹ️"
            }
            emoji = emoji_map.get(severity, "📢")
            
            # Build Slack message payload
            payload = {
                "text": f"{emoji} *{title}*",
                "attachments": [
                    {
                        "color": color,
                        "text": message,
                        "footer": "Anaya Watchtower",
                        "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
                        "ts": int(datetime.utcnow().timestamp())
                    }
                ]
            }
            
            # Add fields if provided
            if fields:
                payload["attachments"][0]["fields"] = [
                    {"title": k, "value": v, "short": True}
                    for k, v in fields.items()
                ]
            
            # Send POST request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Slack notification sent: {title}")
                    return True
                else:
                    logger.error(f"❌ Slack API error: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Failed to send Slack notification: {e}")
            return False
    
    async def send_new_circular_alert(
        self,
        circular_id: str,
        title: str,
        url: str,
        date_published: str
    ):
        """Send alert for new RBI circular detected"""
        await self.send_notification(
            title="🆕 New RBI Circular Detected",
            message=f"*{title}*\n\nCircular ID: {circular_id}\nPublished: {date_published}",
            severity="info",
            fields={
                "URL": url,
                "Status": "Processing..."
            }
        )
    
    async def send_policy_diff_alert(
        self,
        circular_title: str,
        diff_type: str,
        severity: str,
        description: str,
        affected_section: str
    ):
        """Send alert for policy difference detected"""
        await self.send_notification(
            title="📊 Policy Impact Detected",
            message=f"*{circular_title}*\n\n{description}",
            severity=severity,
            fields={
                "Type": diff_type.replace("_", " ").title(),
                "Affected Section": affected_section,
                "Action Required": "Review & Update Policy"
            }
        )
    
    async def send_compliance_score_alert(
        self,
        old_score: float,
        new_score: float,
        reason: str
    ):
        """Send alert for compliance score change"""
        change = new_score - old_score
        direction = "increased" if change > 0 else "decreased"
        severity = "info" if change >= 0 else "medium"
        
        await self.send_notification(
            title=f"📈 Compliance Score {direction.title()}",
            message=f"Score {direction} from **{old_score:.1f}%** to **{new_score:.1f}%**\n\nReason: {reason}",
            severity=severity,
            fields={
                "Change": f"{change:+.1f}%",
                "New Score": f"{new_score:.1f}%"
            }
        )
    
    async def send_anomaly_alert(
        self,
        anomaly_type: str,
        description: str,
        details: Dict[str, str]
    ):
        """Send alert for transaction anomaly"""
        await self.send_notification(
            title="🔍 Transaction Anomaly Detected",
            message=f"*{anomaly_type}*\n\n{description}",
            severity="high",
            fields=details
        )


# Global Slack notifier instance
slack_notifier = SlackNotifier()
