-- Neon Database Schema for Anaya Watchtower
-- Execute this in Neon SQL Editor or via Neon Data API

-- RBI Circulars Table
CREATE TABLE IF NOT EXISTS rbi_circulars (
    id VARCHAR(36) PRIMARY KEY,
    circular_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    date_published TIMESTAMP NOT NULL,
    url VARCHAR(1000),
    pdf_url VARCHAR(1000),
    blob_storage_path VARCHAR(500),
    
    -- Processing status
    status VARCHAR(50) DEFAULT 'pending',
    raw_text TEXT,
    parsed_at TIMESTAMP,
    
    -- Embeddings info
    chunks_count INTEGER DEFAULT 0,
    embedded_at TIMESTAMP,
    
    -- Metadata
    category VARCHAR(100),
    tags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_circulars_circular_id ON rbi_circulars(circular_id);
CREATE INDEX IF NOT EXISTS idx_circulars_date ON rbi_circulars(date_published DESC);
CREATE INDEX IF NOT EXISTS idx_circulars_status ON rbi_circulars(status);

-- Company Policies Table
CREATE TABLE IF NOT EXISTS company_policies (
    id VARCHAR(36) PRIMARY KEY,
    policy_name VARCHAR(200) NOT NULL,
    policy_version VARCHAR(50) NOT NULL,
    section_number VARCHAR(50),
    section_title VARCHAR(300),
    content TEXT NOT NULL,
    
    -- Embeddings
    embedding_id VARCHAR(100),
    
    -- Metadata
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_policies_active ON company_policies(is_active);

-- Policy Diffs Table
CREATE TABLE IF NOT EXISTS policy_diffs (
    id VARCHAR(36) PRIMARY KEY,
    circular_id VARCHAR(36) REFERENCES rbi_circulars(id),
    policy_id VARCHAR(36) REFERENCES company_policies(id),
    
    -- Diff details
    diff_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    affected_section VARCHAR(200),
    description TEXT NOT NULL,
    recommendation TEXT,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_diffs_circular ON policy_diffs(circular_id);
CREATE INDEX IF NOT EXISTS idx_diffs_status ON policy_diffs(status);
CREATE INDEX IF NOT EXISTS idx_diffs_severity ON policy_diffs(severity);

-- Compliance Scores Table
CREATE TABLE IF NOT EXISTS compliance_scores (
    id VARCHAR(36) PRIMARY KEY,
    score FLOAT NOT NULL,
    total_circulars INTEGER DEFAULT 0,
    pending_reviews INTEGER DEFAULT 0,
    critical_issues INTEGER DEFAULT 0,
    high_issues INTEGER DEFAULT 0,
    
    -- Breakdown by category
    score_breakdown JSONB,
    
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_scores_calculated ON compliance_scores(calculated_at DESC);

-- Agent Logs Table
CREATE TABLE IF NOT EXISTS agent_logs (
    id VARCHAR(36) PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL,
    action VARCHAR(200) NOT NULL,
    status VARCHAR(50) NOT NULL,
    
    -- Context
    circular_id VARCHAR(36) REFERENCES rbi_circulars(id),
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    
    -- Timing
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds FLOAT
);

CREATE INDEX IF NOT EXISTS idx_logs_agent ON agent_logs(agent_name);
CREATE INDEX IF NOT EXISTS idx_logs_started ON agent_logs(started_at DESC);

-- Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    id VARCHAR(36) PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(300) NOT NULL,
    message TEXT NOT NULL,
    
    -- Related entities
    circular_id VARCHAR(100),
    policy_diff_id VARCHAR(36),
    
    -- Status
    sent_to_slack BOOLEAN DEFAULT false,
    slack_sent_at TIMESTAMP,
    acknowledged BOOLEAN DEFAULT false,
    acknowledged_at TIMESTAMP,
    acknowledged_by VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(alert_type);

-- Insert sample company policy for testing
INSERT INTO company_policies (id, policy_name, policy_version, section_number, section_title, content, is_active)
VALUES (
    'policy-001',
    'KYC and Customer Onboarding Policy',
    'v2.1',
    '3.2',
    'Video KYC Limits',
    'Video KYC is permitted for account opening with a maximum limit of ₹50,000 for initial funding. Customer must complete full KYC within 30 days. Re-KYC is required every 10 years for low-risk customers.',
    true
)
ON CONFLICT (id) DO NOTHING;
