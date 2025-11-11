"""
Database models for Anaya Watchtower
SQLAlchemy async models for Postgres
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class RBICircular(Base):
    """Stores RBI circular metadata and processing status"""
    __tablename__ = "rbi_circulars"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    circular_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    date_published = Column(DateTime, nullable=False)
    url = Column(String(1000), nullable=True)
    pdf_url = Column(String(1000), nullable=True)
    blob_storage_path = Column(String(500), nullable=True)
    
    # Processing status
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    raw_text = Column(Text, nullable=True)
    parsed_at = Column(DateTime, nullable=True)
    
    # Embeddings info
    chunks_count = Column(Integer, default=0)
    embedded_at = Column(DateTime, nullable=True)
    
    # Metadata
    category = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    policy_diffs = relationship("PolicyDiff", back_populates="circular")
    agent_logs = relationship("AgentLog", back_populates="circular")


class CompanyPolicy(Base):
    """Stores company's compliance policies for RAG comparison"""
    __tablename__ = "company_policies"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_name = Column(String(200), nullable=False)
    policy_version = Column(String(50), nullable=False)
    section_number = Column(String(50), nullable=True)
    section_title = Column(String(300), nullable=True)
    content = Column(Text, nullable=False)
    
    # Embeddings
    embedding_id = Column(String(100), nullable=True)
    
    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    policy_diffs = relationship("PolicyDiff", back_populates="policy")


class PolicyDiff(Base):
    """Stores detected policy differences from new RBI circulars"""
    __tablename__ = "policy_diffs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    circular_id = Column(String(36), ForeignKey("rbi_circulars.id"), nullable=False)
    policy_id = Column(String(36), ForeignKey("company_policies.id"), nullable=False)
    
    # Diff details
    diff_type = Column(String(50), nullable=False)  # new_requirement, updated_threshold, conflicting
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    affected_section = Column(String(200), nullable=True)
    description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=True)
    
    # Status
    status = Column(String(50), default="pending")  # pending, reviewed, resolved, ignored
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    circular = relationship("RBICircular", back_populates="policy_diffs")
    policy = relationship("CompanyPolicy", back_populates="policy_diffs")


class ComplianceScore(Base):
    """Tracks overall compliance score over time"""
    __tablename__ = "compliance_scores"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    score = Column(Float, nullable=False)
    total_circulars = Column(Integer, default=0)
    pending_reviews = Column(Integer, default=0)
    critical_issues = Column(Integer, default=0)
    high_issues = Column(Integer, default=0)
    
    # Breakdown by category
    score_breakdown = Column(JSON, nullable=True)  # {"kyc": 85, "aml": 92, ...}
    
    calculated_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)


class AgentLog(Base):
    """Logs all agent activities for debugging and audit trail"""
    __tablename__ = "agent_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_name = Column(String(100), nullable=False, index=True)
    action = Column(String(200), nullable=False)
    status = Column(String(50), nullable=False)  # success, failed, in_progress
    
    # Context
    circular_id = Column(String(36), ForeignKey("rbi_circulars.id"), nullable=True)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Relationships
    circular = relationship("RBICircular", back_populates="agent_logs")


class Alert(Base):
    """Stores compliance alerts sent to Slack or shown in dashboard"""
    __tablename__ = "alerts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_type = Column(String(50), nullable=False)  # new_circular, policy_diff, score_change, anomaly
    severity = Column(String(20), nullable=False)  # critical, high, medium, low, info
    title = Column(String(300), nullable=False)
    message = Column(Text, nullable=False)
    
    # Related entities
    circular_id = Column(String(100), nullable=True)
    policy_diff_id = Column(String(36), nullable=True)
    
    # Status
    sent_to_slack = Column(Boolean, default=False)
    slack_sent_at = Column(DateTime, nullable=True)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
