#!/usr/bin/env python3
"""Initialize database tables"""
import asyncio
from db.migrations import run_migrations

if __name__ == "__main__":
    asyncio.run(run_migrations())
    print("✅ Database initialized successfully!")
