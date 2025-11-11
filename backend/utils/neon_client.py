"""
Neon Data API client for HTTP-based database queries.
Alternative to connection pooling for serverless environments.
"""
import httpx
import asyncio
from typing import Any, Dict, List, Optional
from config import settings
import logging

logger = logging.getLogger(__name__)

class NeonDataAPIClient:
    """HTTP client for Neon's Data API."""
    
    def __init__(self):
        self.base_url = settings.NEON_DATA_API_URL
        self.api_key = settings.NEON_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } if self.api_key else {}
    
    async def execute(
        self, 
        query: str, 
        params: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a SQL query via Neon Data API.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
        
        Returns:
            Response dict with 'rows' and 'fields' keys
        """
        if not self.base_url:
            logger.warning("Neon Data API URL not configured, skipping query")
            return {"rows": [], "fields": []}
        
        payload = {
            "query": query,
            "params": params or []
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Neon Data API error: {e}")
            raise
    
    async def query(
        self, 
        query: str, 
        params: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return rows as dicts.
        
        Args:
            query: SQL SELECT query
            params: Query parameters
        
        Returns:
            List of row dicts
        """
        result = await self.execute(query, params)
        rows = result.get("rows", [])
        fields = result.get("fields", [])
        
        # Convert rows to dicts
        return [
            {field["name"]: value for field, value in zip(fields, row)}
            for row in rows
        ]
    
    async def insert(
        self, 
        table: str, 
        data: Dict[str, Any]
    ) -> Optional[int]:
        """
        Insert a row and return the inserted ID (if RETURNING id).
        
        Args:
            table: Table name
            data: Column-value dict
        
        Returns:
            Inserted row ID or None
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join([f"${i+1}" for i in range(len(data))])
        values = list(data.values())
        
        query = f"""
            INSERT INTO {table} ({columns})
            VALUES ({placeholders})
            RETURNING id
        """
        
        result = await self.execute(query, values)
        rows = result.get("rows", [])
        return rows[0][0] if rows else None
    
    async def update(
        self, 
        table: str, 
        data: Dict[str, Any],
        where: str,
        where_params: Optional[List[Any]] = None
    ) -> int:
        """
        Update rows and return count of affected rows.
        
        Args:
            table: Table name
            data: Column-value dict to update
            where: WHERE clause (without 'WHERE' keyword)
            where_params: Parameters for WHERE clause
        
        Returns:
            Number of rows updated
        """
        set_clause = ", ".join([
            f"{col} = ${i+1}" 
            for i, col in enumerate(data.keys())
        ])
        values = list(data.values())
        
        # Adjust param numbers for WHERE clause
        where_offset = len(values)
        if where_params:
            values.extend(where_params)
        
        query = f"""
            UPDATE {table}
            SET {set_clause}
            WHERE {where}
        """
        
        result = await self.execute(query, values)
        # Neon returns rowCount in some responses
        return result.get("rowCount", 0)
    
    async def health_check(self) -> bool:
        """Check if Neon Data API is reachable."""
        try:
            await self.query("SELECT 1 as health")
            logger.info("✅ Neon Data API health check passed")
            return True
        except Exception as e:
            logger.error(f"❌ Neon Data API health check failed: {e}")
            return False

# Singleton instance
neon_client = NeonDataAPIClient()
