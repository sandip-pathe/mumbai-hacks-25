"""
Database connection and session management
Async SQLAlchemy setup for PostgreSQL
Note: This module is only used when DATABASE_URL is configured.
For Neon Data API, use the neon_client module instead.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from config import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Create async engine only if DATABASE_URL is configured
engine: Optional[create_async_engine] = None
AsyncSessionLocal: Optional[async_sessionmaker] = None

if settings.DATABASE_URL:
    # For Neon, we need to configure SSL separately
    connect_args = {}
    if 'neon.tech' in settings.DATABASE_URL or 'sslmode=require' in settings.DATABASE_URL:
        connect_args = {"ssl": "require"}
    
    # Remove ssl/sslmode parameters from URL if present and ensure asyncpg driver
    clean_url = settings.DATABASE_URL.replace('?ssl=true', '').replace('&ssl=true', '')
    clean_url = clean_url.replace('?sslmode=require', '').replace('&sslmode=require', '')
    # Ensure we're using asyncpg driver for async SQLAlchemy
    if clean_url.startswith('postgresql://'):
        clean_url = clean_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
    
    engine = create_async_engine(
        clean_url,
        echo=settings.ENVIRONMENT == "development",
        poolclass=NullPool,
        future=True,
        connect_args=connect_args
    )
    
    # Create async session factory
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )


async def get_db() -> AsyncSession:
    """
    Dependency for FastAPI routes to get database session
    Usage: db: AsyncSession = Depends(get_db)
    """
    if not AsyncSessionLocal:
        raise RuntimeError("Database not configured. Use DATABASE_URL or switch to Neon Data API.")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database connection and verify connectivity"""
    if not engine:
        logger.warning("⚠️ Database engine not initialized (DATABASE_URL not set)")
        return
        
    try:
        async with engine.begin() as conn:
            logger.info("✅ Database connection established")
            # Test query - use text() so SQLAlchemy treats it as an executable
            result = await conn.execute(text("SELECT 1"))
            logger.info(f"✅ Database is responsive: {result.scalar()}")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise


async def close_db():
    """Close database connections gracefully"""
    if not engine:
        return
        
    await engine.dispose()
    logger.info("✅ Database connections closed")
