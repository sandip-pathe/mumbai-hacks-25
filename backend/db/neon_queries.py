"""
Neon Data API query helpers
Wrapper functions for common database operations using HTTP-based Neon Data API
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.neon_client import neon_client
import uuid
import logging

logger = logging.getLogger(__name__)


# ========== RBI CIRCULARS ==========

async def create_circular(
    circular_id: str,
    title: str,
    date_published: datetime,
    url: Optional[str] = None,
    pdf_url: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new RBI circular record"""
    query = """
        INSERT INTO rbi_circulars (id, circular_id, title, date_published, url, pdf_url, status, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING *
    """
    id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    result = await neon_client.query(
        query,
        [id, circular_id, title, date_published.isoformat(), url, pdf_url, "pending", now.isoformat(), now.isoformat()]
    )
    return result[0] if result else None


async def get_circular_by_id(circular_id: str) -> Optional[Dict[str, Any]]:
    """Get circular by UUID"""
    query = "SELECT * FROM rbi_circulars WHERE id = $1"
    result = await neon_client.query(query, [circular_id])
    return result[0] if result else None


async def get_circular_by_circular_id(circular_id: str) -> Optional[Dict[str, Any]]:
    """Get circular by circular_id (e.g., RBI-ABC-123)"""
    query = "SELECT * FROM rbi_circulars WHERE circular_id = $1"
    result = await neon_client.query(query, [circular_id])
    return result[0] if result else None


async def update_circular(id: str, updates: Dict[str, Any]) -> bool:
    """Update circular fields"""
    set_clause = ", ".join([f"{k} = ${i+2}" for i, k in enumerate(updates.keys())])
    query = f"UPDATE rbi_circulars SET {set_clause}, updated_at = ${len(updates)+2} WHERE id = $1"
    
    params = [id] + list(updates.values()) + [datetime.utcnow().isoformat()]
    await neon_client.execute(query, params)
    return True


async def list_circulars(limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """List recent circulars"""
    query = "SELECT * FROM rbi_circulars ORDER BY date_published DESC LIMIT $1 OFFSET $2"
    return await neon_client.query(query, [limit, offset])


# ========== COMPLIANCE SCORES ==========

async def create_compliance_score(
    score: float,
    total_circulars: int,
    pending_reviews: int,
    critical_issues: int,
    high_issues: int,
    score_breakdown: Optional[Dict] = None
) -> Dict[str, Any]:
    """Create a new compliance score record"""
    query = """
        INSERT INTO compliance_scores (id, score, total_circulars, pending_reviews, critical_issues, high_issues, score_breakdown, calculated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING *
    """
    id = str(uuid.uuid4())
    result = await neon_client.query(
        query,
        [id, score, total_circulars, pending_reviews, critical_issues, high_issues, score_breakdown, datetime.utcnow().isoformat()]
    )
    return result[0] if result else None


async def get_latest_compliance_score() -> Optional[Dict[str, Any]]:
    """Get the most recent compliance score"""
    query = "SELECT * FROM compliance_scores ORDER BY calculated_at DESC LIMIT 1"
    result = await neon_client.query(query, [])
    return result[0] if result else None


# ========== POLICY DIFFS ==========

async def create_policy_diff(
    circular_id: str,
    policy_id: str,
    diff_type: str,
    severity: str,
    affected_section: str,
    description: str,
    recommendation: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new policy diff"""
    query = """
        INSERT INTO policy_diffs (id, circular_id, policy_id, diff_type, severity, affected_section, description, recommendation, status, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        RETURNING *
    """
    id = str(uuid.uuid4())
    result = await neon_client.query(
        query,
        [id, circular_id, policy_id, diff_type, severity, affected_section, description, recommendation, "pending", datetime.utcnow().isoformat()]
    )
    return result[0] if result else None


async def list_policy_diffs(status: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """List policy diffs with optional status filter"""
    if status:
        query = "SELECT * FROM policy_diffs WHERE status = $1 ORDER BY created_at DESC LIMIT $2"
        return await neon_client.query(query, [status, limit])
    else:
        query = "SELECT * FROM policy_diffs ORDER BY created_at DESC LIMIT $1"
        return await neon_client.query(query, [limit])


# ========== ALERTS ==========

async def create_alert(
    alert_type: str,
    severity: str,
    title: str,
    message: str,
    circular_id: Optional[str] = None,
    policy_diff_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new alert"""
    query = """
        INSERT INTO alerts (id, alert_type, severity, title, message, circular_id, policy_diff_id, sent_to_slack, acknowledged, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        RETURNING *
    """
    id = str(uuid.uuid4())
    result = await neon_client.query(
        query,
        [id, alert_type, severity, title, message, circular_id, policy_diff_id, False, False, datetime.utcnow().isoformat()]
    )
    return result[0] if result else None


async def list_alerts(severity: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """List alerts with optional severity filter"""
    if severity:
        query = "SELECT * FROM alerts WHERE severity = $1 ORDER BY created_at DESC LIMIT $2"
        return await neon_client.query(query, [severity, limit])
    else:
        query = "SELECT * FROM alerts ORDER BY created_at DESC LIMIT $1"
        return await neon_client.query(query, [limit])


# ========== AGENT LOGS ==========

async def create_agent_log(
    agent_name: str,
    action: str,
    status: str = "in_progress",
    circular_id: Optional[str] = None,
    input_data: Optional[Dict] = None
) -> str:
    """Create a new agent log, returns the log ID"""
    query = """
        INSERT INTO agent_logs (id, agent_name, action, status, circular_id, input_data, started_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id
    """
    id = str(uuid.uuid4())
    await neon_client.execute(
        query,
        [id, agent_name, action, status, circular_id, input_data, datetime.utcnow().isoformat()]
    )
    return id


async def update_agent_log(
    log_id: str,
    status: str,
    output_data: Optional[Dict] = None,
    error_message: Optional[str] = None,
    duration_seconds: Optional[float] = None
) -> bool:
    """Update agent log with completion status"""
    query = """
        UPDATE agent_logs 
        SET status = $2, output_data = $3, error_message = $4, duration_seconds = $5, completed_at = $6
        WHERE id = $1
    """
    await neon_client.execute(
        query,
        [log_id, status, output_data, error_message, duration_seconds, datetime.utcnow().isoformat()]
    )
    return True


async def list_agent_logs(agent_name: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """List agent logs with optional agent filter"""
    if agent_name:
        query = "SELECT * FROM agent_logs WHERE agent_name = $1 ORDER BY started_at DESC LIMIT $2"
        return await neon_client.query(query, [agent_name, limit])
    else:
        query = "SELECT * FROM agent_logs ORDER BY started_at DESC LIMIT $1"
        return await neon_client.query(query, [limit])


# ========== COMPANY POLICIES ==========

async def get_active_policies() -> List[Dict[str, Any]]:
    """Get all active company policies"""
    query = "SELECT * FROM company_policies WHERE is_active = true"
    return await neon_client.query(query, [])


async def get_policy_by_id(policy_id: str) -> Optional[Dict[str, Any]]:
    """Get policy by ID"""
    query = "SELECT * FROM company_policies WHERE id = $1"
    result = await neon_client.query(query, [policy_id])
    return result[0] if result else None
