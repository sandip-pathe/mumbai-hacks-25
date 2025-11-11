"""
Policy Automation Agent
Listens for new circulars, parses PDFs, runs RAG comparison with policies
Generates policy diffs and updates
"""
import asyncio
import logging
from datetime import datetime
import uuid
from typing import Dict, Any
from db.database import AsyncSessionLocal
from db.models import RBICircular, CompanyPolicy, PolicyDiff, AgentLog
from utils.redis_client import redis_client, CHANNEL_NEW_CIRCULAR, CHANNEL_POLICY_UPDATED
from utils.azure_client import azure_client
from utils.chroma_store import chroma_store
from utils.pdf_parser import parse_pdf_with_pdfplumber
from utils.slack_notifier import slack_notifier
from sqlalchemy import select
import os

logger = logging.getLogger(__name__)


class PolicyAutomationAgent:
    """
    Agent that processes new circulars:
    1. Downloads and parses PDF
    2. Embeds circular text in Chroma
    3. Runs RAG comparison with company policies
    4. Generates policy diffs
    """
    
    def __init__(self):
        self.name = "PolicyAutomationAgent"
    
    async def start(self):
        """Subscribe to new_circular events"""
        logger.info(f"🤖 {self.name} started, listening for circulars...")
        await redis_client.subscribe(CHANNEL_NEW_CIRCULAR, self.handle_new_circular)
    
    async def handle_new_circular(self, event: Dict[str, Any]):
        """Process new circular event"""
        start_time = datetime.utcnow()
        circular_id = event.get("circular_id")
        
        logger.info(f"📄 {self.name} processing circular: {circular_id}")
        
        async with AsyncSessionLocal() as db:
            try:
                # Log action
                log = AgentLog(
                    id=str(uuid.uuid4()),
                    agent_name=self.name,
                    action="process_circular",
                    status="in_progress",
                    circular_id=circular_id,
                    input_data=event,
                    started_at=start_time
                )
                db.add(log)
                await db.commit()
                
                # Get circular from DB
                result = await db.execute(select(RBICircular).where(RBICircular.id == circular_id))
                circular = result.scalar_one_or_none()
                
                if not circular:
                    raise Exception(f"Circular {circular_id} not found")
                
                # Update status
                circular.status = "processing"
                await db.commit()
                
                # Step 1: Download PDF (simulate for demo)
                pdf_text = await self.download_and_parse_pdf(circular)
                
                # Step 2: Store text in DB
                circular.raw_text = pdf_text
                circular.parsed_at = datetime.utcnow()
                await db.commit()
                
                # Step 3: Chunk and embed
                chunks = chroma_store.chunk_text(pdf_text, chunk_size=1000, overlap=200)
                await chroma_store.add_circular_chunks(
                    circular_id=circular.circular_id,
                    chunks=chunks,
                    metadata={
                        "title": circular.title,
                        "date": str(circular.date_published),
                        "circular_id": circular.circular_id
                    }
                )
                circular.chunks_count = len(chunks)
                circular.embedded_at = datetime.utcnow()
                await db.commit()
                
                # Step 4: Compare with policies
                await self.compare_with_policies(circular, db)
                
                # Step 5: Mark as completed
                circular.status = "completed"
                await db.commit()
                
                # Update log
                log.status = "success"
                log.completed_at = datetime.utcnow()
                log.duration_seconds = (log.completed_at - start_time).total_seconds()
                log.output_data = {"chunks_created": len(chunks)}
                await db.commit()
                
                # Publish policy_updated event
                await redis_client.publish(CHANNEL_POLICY_UPDATED, {
                    "event_type": "policy_analysis_complete",
                    "circular_id": circular.id
                })
                
                logger.info(f"✅ {self.name} completed for circular {circular.circular_id}")
                
            except Exception as e:
                logger.error(f"❌ {self.name} failed: {e}")
                log.status = "failed"
                log.error_message = str(e)
                await db.commit()
    
    async def download_and_parse_pdf(self, circular: RBICircular) -> str:
        """Download PDF and extract text"""
        try:
            # For demo, simulate PDF download
            # In production, use aiohttp to download from circular.pdf_url
            logger.info(f"📥 Downloading PDF from {circular.pdf_url}")
            
            # Simulate: Create a fake PDF text for demo
            demo_text = f"""
            Reserve Bank of India
            {circular.title}
            Date: {circular.date_published}
            
            CIRCULAR NO: {circular.circular_id}
            
            This circular updates the KYC requirements for financial institutions.
            
            Key Changes:
            1. Video KYC limit increased from ₹50,000 to ₹1,00,000
            2. Re-KYC cycle reduced from 10 years to 8 years
            3. Additional documents required for high-risk customers
            4. Aadhaar linkage mandatory for all new accounts from next quarter
            
            Compliance Timeline: Effective immediately, full implementation within 90 days.
            
            [Rest of circular text...]
            """
            
            # In production, download and parse:
            # pdf_path = await self.download_pdf_file(circular.pdf_url)
            # parsed = await azure_client.parse_pdf_with_document_intelligence(pdf_path)
            # return parsed['text']
            
            return demo_text
            
        except Exception as e:
            logger.error(f"❌ PDF download/parse failed: {e}")
            raise
    
    async def compare_with_policies(self, circular: RBICircular, db):
        """Compare circular with existing company policies using RAG"""
        try:
            # Get all active policies
            result = await db.execute(
                select(CompanyPolicy).where(CompanyPolicy.is_active == True)
            )
            policies = result.scalars().all()
            
            logger.info(f"🔍 Comparing circular with {len(policies)} policies...")
            
            for policy in policies:
                # Use Azure OpenAI to analyze
                analysis = await azure_client.analyze_circular_content(
                    circular_text=circular.raw_text[:4000],
                    policy_content=policy.content
                )
                
                # If impact detected, create policy diff
                if analysis.get("has_impact", False) and analysis.get("diff_type") != "no_impact":
                    diff = PolicyDiff(
                        id=str(uuid.uuid4()),
                        circular_id=circular.id,
                        policy_id=policy.id,
                        diff_type=analysis.get("diff_type", "unknown"),
                        severity=analysis.get("severity", "medium"),
                        affected_section=analysis.get("affected_section", "N/A"),
                        description=analysis.get("description", "Policy impact detected"),
                        recommendation=analysis.get("recommendation", "Review and update policy"),
                        status="pending"
                    )
                    db.add(diff)
                    await db.commit()
                    
                    logger.info(f"⚠️ Policy diff created: {diff.diff_type} ({diff.severity})")
                    
                    # Send Slack alert
                    await slack_notifier.send_policy_diff_alert(
                        circular_title=circular.title,
                        diff_type=diff.diff_type,
                        severity=diff.severity,
                        description=diff.description,
                        affected_section=diff.affected_section
                    )
            
        except Exception as e:
            logger.error(f"❌ Policy comparison failed: {e}")