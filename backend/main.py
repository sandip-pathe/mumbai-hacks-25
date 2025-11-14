"""
Anaya Watchtower - FastAPI Main Application
Multi-agent AI system for fintech compliance
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio
from config import settings
from db.database import init_db, close_db
from db.migrations import run_migrations
from utils.redis_client import redis_client
from utils.chroma_store import chroma_store
from utils.neon_client import neon_client
from graph.workflow import compliance_workflow
from api.routes import router as api_router
from api.websocket import router as ws_router, listen_for_redis_events
from agents.agent_manager import agent_manager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan - startup and shutdown logic
    """
    logger.info("🚀 Starting Anaya Watchtower...")
    
    try:
        # Step 1: Initialize database (optional - skip if using Neon Data API)
        if settings.DATABASE_URL and not settings.NEON_DATA_API_URL:
            # Using traditional SQLAlchemy connection
            await init_db()
            await run_migrations()
            logger.info("✅ PostgreSQL database initialized")
        elif settings.NEON_DATA_API_URL:
            # Using Neon Data API (HTTP-based, no SQLAlchemy connection needed)
            neon_healthy = await neon_client.health_check()
            if neon_healthy:
                logger.info("✅ Neon Data API connected")
            else:
                logger.warning("⚠️ Neon Data API health check failed (continuing anyway)")
        else:
            logger.warning("⚠️ No database configured (neither PostgreSQL nor Neon Data API)")
        
        # Step 2: Connect to Redis
        await redis_client.connect()
        
        # Step 3: Connect to Qdrant vector store (non-fatal)
        try:
            await chroma_store.connect()
        except Exception as e:
            # chroma_store.connect already logs; keep startup going so DB and
            # other services are usable even if Qdrant is down.
            logger.warning(f"Qdrant connection non-fatal failure: {e}")
        
        # Step 4: Initialize LangGraph workflow
        logger.info("✅ LangGraph compliance workflow initialized")
        
        # Step 5: Start Agent Manager (manages all 5 agents)
        logger.info("🤖 Starting Anaya Agent Manager...")
        await agent_manager.start()
        
        # Start WebSocket event listener
        asyncio.create_task(listen_for_redis_events())
        
        logger.info("✅ All systems operational!")
        logger.info(f"🌐 API running at http://localhost:8080")
        logger.info(f"📡 WebSocket at ws://localhost:8080/ws")
        
        yield  # Application runs here
        
    finally:
        # Shutdown
        logger.info("🛑 Shutting down Anaya Watchtower...")
        
        await agent_manager.stop()
        await redis_client.disconnect()
        
        # Close database only if using SQLAlchemy connection
        if settings.DATABASE_URL and not settings.NEON_DATA_API_URL:
            await close_db()
        
        logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Anaya Watchtower API",
    description="Multi-Agent AI System for Fintech Compliance",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api", tags=["API"])
app.include_router(ws_router, tags=["WebSocket"])


@app.get("/health")
async def health_check():
    """Health check endpoint (convenience, also available at /api/health)"""
    return {"status": "healthy", "service": "Anaya Watchtower"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Anaya Watchtower",
        "status": "operational",
        "version": "1.0.0",
        "features": {
            "langgraph": True,
            "mcp_tools": True,
            "neon_data_api": bool(settings.NEON_DATA_API_URL),
            "qdrant_cloud": bool(settings.QDRANT_URL)
        },
        "agents": [
            "RegulatoryWatchAgent",
            "PolicyAutomationAgent",
            "AuditPrepAgent",
            "TransactionMonitorAgent",
            "AdvisoryAgent"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )