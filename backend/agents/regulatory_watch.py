"""
Regulatory Watch Agent
Monitors RBI website for new circulars via RSS, scraping, or email
Downloads PDFs and triggers processing pipeline
"""
import feedparser
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import asyncio
import logging
from typing import List, Dict, Any
import re
from config import settings
from db.database import AsyncSessionLocal
from db.models import RBICircular, AgentLog
from utils.redis_client import redis_client, CHANNEL_NEW_CIRCULAR
from utils.slack_notifier import slack_notifier
import uuid

logger = logging.getLogger(__name__)


class RegulatoryWatchAgent:
    """
    Agent that monitors RBI for new regulatory circulars
    Methods: RSS feed, web scraping, email notifications
    """
    
    def __init__(self):
        self.name = "RegulatoryWatchAgent"
        self.check_interval = settings.RBI_CHECK_INTERVAL_MINUTES * 60  # Convert to seconds
        self.running = False
    
    async def start(self):
        """Start continuous monitoring"""
        self.running = True
        logger.info(f"🔍 {self.name} started, checking every {settings.RBI_CHECK_INTERVAL_MINUTES} minutes")
        
        while self.running:
            try:
                await self.check_for_new_circulars()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ {self.name} error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info(f"🛑 {self.name} stopped")
    
    async def check_for_new_circulars(self):
        """Check RBI sources for new circulars"""
        start_time = datetime.utcnow()
        
        async with AsyncSessionLocal() as db:
            try:
                # Log agent action
                log = AgentLog(
                    id=str(uuid.uuid4()),
                    agent_name=self.name,
                    action="check_new_circulars",
                    status="in_progress",
                    started_at=start_time
                )
                db.add(log)
                await db.commit()
                
                # Try RSS feed first (fastest)
                new_circulars = await self.check_rss_feed()
                
                # If RSS fails or empty, try scraping
                if not new_circulars:
                    new_circulars = await self.scrape_circulars_page()
                
                # Process new circulars
                for circular_data in new_circulars:
                    await self.process_new_circular(circular_data, db)
                
                # Update log
                log.status = "success"
                log.completed_at = datetime.utcnow()
                log.duration_seconds = (log.completed_at - start_time).total_seconds()
                log.output_data = {"circulars_found": len(new_circulars)}
                await db.commit()
                
                logger.info(f"✅ {self.name} check complete: {len(new_circulars)} new circulars")
                
            except Exception as e:
                logger.error(f"❌ {self.name} check failed: {e}")
                log.status = "failed"
                log.error_message = str(e)
                await db.commit()
    
    async def check_rss_feed(self) -> List[Dict[str, Any]]:
        """Check RBI RSS feed for new circulars"""
        try:
            # Note: RBI doesn't have a perfect RSS feed, this is a simulated approach
            # In production, you'd use actual RBI RSS if available
            logger.info("📡 Checking RBI RSS feed...")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(settings.RBI_RSS_FEED_URL, timeout=30) as response:
                    if response.status != 200:
                        logger.warning(f"RSS feed returned {response.status}")
                        return []
                    
                    content = await response.text()
            
            # Parse RSS (if RBI had proper RSS)
            # feed = feedparser.parse(content)
            # For now, we'll scrape instead
            return []
            
        except Exception as e:
            logger.warning(f"RSS feed check failed: {e}, falling back to scraping")
            return []
    
    async def scrape_circulars_page(self) -> List[Dict[str, Any]]:
        """Scrape RBI circulars page for new entries"""
        try:
            logger.info("🕷️ Scraping RBI circulars page...")
            
            # RBI Master Circulars page URL
            url = "https://www.rbi.org.in/Scripts/BS_ViewMasCirculardetails.aspx"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch RBI page: {response.status}")
                        return []
                    
                    html = await response.text()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find circular links (adjust selectors based on actual RBI HTML structure)
            circulars = []
            
            # Look for tables or lists containing circulars
            # RBI structure varies, here's a generic approach
            links = soup.find_all('a', href=re.compile(r'.*circular.*\.pdf', re.I))
            
            for link in links[:5]:  # Limit to last 5 for demo
                title = link.get_text(strip=True)
                pdf_url = link.get('href')
                
                # Make URL absolute
                if pdf_url and not pdf_url.startswith('http'):
                    pdf_url = f"https://www.rbi.org.in{pdf_url}"
                
                # Extract date from nearby elements (RBI pages typically show dates)
                date_text = self._extract_date_near_link(link)
                
                circular_id = self._generate_circular_id(pdf_url)
                
                circulars.append({
                    "circular_id": circular_id,
                    "title": title,
                    "date_published": date_text or datetime.utcnow(),
                    "url": url,
                    "pdf_url": pdf_url
                })
            
            logger.info(f"📄 Found {len(circulars)} circular entries")
            return circulars
            
        except Exception as e:
            logger.error(f"❌ Scraping failed: {e}")
            return []
    
    def _extract_date_near_link(self, link_element) -> datetime:
        """Extract date from elements near the circular link"""
        try:
            # Look in parent row or nearby td elements
            parent = link_element.find_parent('tr')
            if parent:
                # Find date patterns like "dd-mm-yyyy" or "dd/mm/yyyy"
                text = parent.get_text()
                date_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})', text)
                if date_match:
                    date_str = date_match.group(1)
                    # Try parsing
                    for fmt in ['%d-%m-%Y', '%d/%m/%Y']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except:
                            continue
            
            # Default to recent date
            return datetime.utcnow() - timedelta(days=1)
            
        except:
            return datetime.utcnow()
    
    def _generate_circular_id(self, url: str) -> str:
        """Generate unique circular ID from URL"""
        # Extract meaningful identifier from URL
        match = re.search(r'([A-Z0-9-]+)\.pdf', url, re.I)
        if match:
            return f"RBI-{match.group(1)}"
        else:
            # Fallback to hash
            import hashlib
            return f"RBI-{hashlib.md5(url.encode()).hexdigest()[:12]}"
    
    async def process_new_circular(self, circular_data: Dict[str, Any], db):
        """Process a newly discovered circular"""
        try:
            circular_id = circular_data['circular_id']
            
            # Check if already exists
            from sqlalchemy import select
            result = await db.execute(
                select(RBICircular).where(RBICircular.circular_id == circular_id)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                logger.debug(f"Circular {circular_id} already exists, skipping")
                return
            
            # Create new circular record
            circular = RBICircular(
                id=str(uuid.uuid4()),
                circular_id=circular_id,
                title=circular_data['title'],
                date_published=circular_data['date_published'],
                url=circular_data['url'],
                pdf_url=circular_data['pdf_url'],
                status="pending"
            )
            
            db.add(circular)
            await db.commit()
            
            logger.info(f"📥 New circular saved: {circular_id}")
            
            # Publish Redis event
            await redis_client.publish(CHANNEL_NEW_CIRCULAR, {
                "event_type": "new_circular_detected",
                "circular_id": circular.id,
                "circular_number": circular_id,
                "title": circular.title,
                "pdf_url": circular.pdf_url
            })
            
            # Send Slack notification
            await slack_notifier.send_new_circular_alert(
                circular_id=circular_id,
                title=circular.title,
                url=circular.url,
                date_published=str(circular.date_published.date())
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to process circular: {e}")
    
    async def check_email_notifications(self):
        """Check email for RBI circular notifications (optional)"""
        # Implement IMAP email checking if RBI sends alerts
        # For now, placeholder
        pass