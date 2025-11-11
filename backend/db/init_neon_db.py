"""
Initialize Neon database schema
Run this script to create all tables in Neon
"""
import asyncio
import sys
sys.path.append('..')

from utils.neon_client import neon_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_schema():
    """Create all tables in Neon"""
    
    # Read SQL file
    with open('neon_schema.sql', 'r') as f:
        sql_statements = f.read()
    
    # Split by semicolon and execute each statement
    statements = [s.strip() for s in sql_statements.split(';') if s.strip() and not s.strip().startswith('--')]
    
    for i, statement in enumerate(statements, 1):
        if statement:
            try:
                logger.info(f"Executing statement {i}/{len(statements)}...")
                await neon_client.execute(statement + ';')
                logger.info(f"✅ Statement {i} executed")
            except Exception as e:
                logger.error(f"❌ Statement {i} failed: {e}")
                logger.error(f"Statement: {statement[:100]}...")
    
    logger.info("🎉 Neon database initialization complete!")


if __name__ == "__main__":
    asyncio.run(init_schema())
