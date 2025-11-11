"""
FastAPI REST API Routes
Endpoints for frontend interaction
Using Neon Postgres via SQLAlchemy (traditional async DB connection)
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from db.database import get_db
from db.models import RBICircular, ComplianceScore, PolicyDiff, Alert, AgentLog
from agents.advisory import AdvisoryAgent
from pydantic import BaseModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize advisory agent
advisory_agent = AdvisoryAgent()


# ========== REQUEST/RESPONSE MODELS ==========

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    confidence: int

class ScoreResponse(BaseModel):
    score: float
    total_circulars: int
    pending_reviews: int
    critical_issues: int
    high_issues: int
    score_breakdown: dict
    calculated_at: str

class AlertResponse(BaseModel):
    id: str
    alert_type: str
    severity: str
    title: str
    message: str
    created_at: str


# ========== ENDPOINTS ==========

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Anaya Watchtower"}


@router.post("/ingest", status_code=202)
async def ingest_circular(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and ingest RBI circular PDF
    Triggers full processing pipeline
    """
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files allowed")
        
        # TODO: Implement full ingestion pipeline
        # 1. Save PDF
        # 2. Parse with Azure Document Intelligence
        # 3. Create circular record
        # 4. Trigger agent processing
        
        logger.info(f"📤 Ingesting PDF: {file.filename}")
        
        return {
            "message": "PDF ingestion started",
            "filename": file.filename,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/score", response_model=ScoreResponse)
async def get_compliance_score(db: AsyncSession = Depends(get_db)):
    """Get latest compliance score"""
    try:
        result = await db.execute(
            select(ComplianceScore).order_by(desc(ComplianceScore.calculated_at)).limit(1)
        )
        score = result.scalar_one_or_none()
        
        if not score:
            raise HTTPException(status_code=404, detail="No compliance score found")
        
        return ScoreResponse(
            score=score.score,
            total_circulars=score.total_circulars,
            pending_reviews=score.pending_reviews,
            critical_issues=score.critical_issues,
            high_issues=score.high_issues,
            score_breakdown=score.score_breakdown or {},
            calculated_at=score.calculated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    limit: int = 20,
    severity: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get recent alerts"""
    try:
        query = select(Alert).order_by(desc(Alert.created_at)).limit(limit)
        
        if severity:
            query = query.where(Alert.severity == severity)
        
        result = await db.execute(query)
        alerts = result.scalars().all()
        
        return [
            AlertResponse(
                id=alert.id,
                alert_type=alert.alert_type,
                severity=alert.severity,
                title=alert.title,
                message=alert.message,
                created_at=alert.created_at.isoformat()
            )
            for alert in alerts
        ]
        
    except Exception as e:
        logger.error(f"❌ Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/circulars")
async def get_circulars(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get recent RBI circulars"""
    try:
        result = await db.execute(
            select(RBICircular).order_by(desc(RBICircular.date_published)).limit(limit)
        )
        circulars = result.scalars().all()
        
        return [
            {
                "id": c.id,
                "circular_id": c.circular_id,
                "title": c.title,
                "date_published": c.date_published.isoformat(),
                "status": c.status,
                "url": c.url
            }
            for c in circulars
        ]
        
    except Exception as e:
        logger.error(f"❌ Failed to get circulars: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/policy-diffs")
async def get_policy_diffs(
    status: Optional[str] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get policy differences"""
    try:
        query = select(PolicyDiff).order_by(desc(PolicyDiff.created_at)).limit(limit)
        
        if status:
            query = query.where(PolicyDiff.status == status)
        
        result = await db.execute(query)
        diffs = result.scalars().all()
        
        return [
            {
                "id": d.id,
                "diff_type": d.diff_type,
                "severity": d.severity,
                "affected_section": d.affected_section,
                "description": d.description,
                "recommendation": d.recommendation,
                "status": d.status,
                "created_at": d.created_at.isoformat()
            }
            for d in diffs
        ]
        
    except Exception as e:
        logger.error(f"❌ Failed to get policy diffs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    """RAG-based compliance chatbot"""
    try:
        result = await advisory_agent.answer_query(request.query)
        
        return ChatResponse(
            answer=result['answer'],
            sources=result['sources'],
            confidence=result['confidence']
        )
        
    except Exception as e:
        logger.error(f"❌ Chat query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
async def get_agent_logs(
    agent_name: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get agent execution logs"""
    try:
        query = select(AgentLog).order_by(desc(AgentLog.started_at)).limit(limit)
        
        if agent_name:
            query = query.where(AgentLog.agent_name == agent_name)
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        return [
            {
                "id": log.id,
                "agent_name": log.agent_name,
                "action": log.action,
                "status": log.status,
                "started_at": log.started_at.isoformat(),
                "duration_seconds": log.duration_seconds,
                "error_message": log.error_message
            }
            for log in logs
        ]
        
    except Exception as e:
        logger.error(f"❌ Failed to get logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))