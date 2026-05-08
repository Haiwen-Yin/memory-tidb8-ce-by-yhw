-- TiDB Multi-Agent Architecture Schema
-- Part of Memory-TiDB8 CE v0.1.2 (Multi-Agent Edition)
-- Author: 胖头鱼 🐟
-- License: Apache-2.0

-- =============================================
-- AGENT REGISTRY TABLES
-- =============================================

CREATE TABLE IF NOT EXISTS agent_registry (
    _id BIGINT PRIMARY KEY AUTO_INCREMENT,
    agent_id VARCHAR(128) UNIQUE NOT NULL COMMENT 'Unique identifier for the agent',
    agent_name VARCHAR(256) NOT NULL COMMENT 'Display name of the agent',
    description TEXT COMMENT 'Agent purpose and capabilities description',
    model_config JSON COMMENT 'AI model configuration (provider, model name, parameters)',
    role VARCHAR(64) DEFAULT 'general' COMMENT 'Agent role: coordinator | specialist | worker | evaluator',
    capabilities JSON COMMENT 'List of agent capabilities in structured format',
    status VARCHAR(32) DEFAULT 'active' COMMENT 'Status: active | inactive | paused | decommissioned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    metadata JSON COMMENT 'Additional agent configuration metadata',
    
    INDEX idx_agent_id (agent_id),
    INDEX idx_status (status),
    INDEX idx_role (role)
) COMMENT='Registry of all AI agents in the multi-agent system';

CREATE TABLE IF NOT EXISTS agent_session (
    _id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(128) UNIQUE NOT NULL COMMENT 'Unique session identifier',
    agent_id BIGINT COMMENT 'Reference to agent_registry._id',
    task_context JSON COMMENT 'Task context and requirements for this session',
    state VARCHAR(64) DEFAULT 'initialized' COMMENT 'Session state: initialized | active | suspended | completed | failed',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP NULL,
    memory_snapshot_id BIGINT COMMENT 'Reference to last task_plan snapshot',
    
    FOREIGN KEY (agent_id) REFERENCES agent_registry(_id),
    INDEX idx_session_id (session_id),
    INDEX idx_agent_id (agent_id),
    INDEX idx_state (state)
) COMMENT='Session tracking for each agent execution';

-- =============================================
-- COOPERATION AND ORCHESTRATION TABLES
-- =============================================

CREATE TABLE IF NOT EXISTS collaboration_request (
    _id BIGINT PRIMARY KEY AUTO_INCREMENT,
    request_id VARCHAR(128) UNIQUE NOT NULL,
    initiator_agent_id BIGINT COMMENT 'Agent making the request',
    target_agent_ids JSON COMMENT 'Array of agent IDs to collaborate with',
    task_description TEXT NOT NULL,
    priority INT DEFAULT 5 COMMENT 'Priority level: 1 (highest) - 10 (lowest)',
    status VARCHAR(32) DEFAULT 'pending' COMMENT 'Status: pending|assigned|in_progress|completed|rejected',
    result JSON COMMENT 'Collaboration outcome and deliverables',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (initiator_agent_id) REFERENCES agent_registry(_id),
    INDEX idx_request_id (request_id),
    INDEX idx_status (status)
) COMMENT='Requests for multi-agent collaboration';

CREATE TABLE IF NOT EXISTS coordination_log (
    _id BIGINT PRIMARY KEY AUTO_INCREMENT,
    request_id VARCHAR(128) COMMENT 'Reference to collaboration_request.request_id',
    agent_id BIGINT COMMENT 'Agent performing the action',
    action_type VARCHAR(64) COMMENT 'Type of coordination: assign | delegate | query | notify | confirm',
    payload JSON COMMENT 'Action-specific data',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_request_id (request_id),
    INDEX idx_timestamp (timestamp)
) COMMENT='Audit log for agent coordination activities';

-- =============================================
-- SHARED STATE AND CACHE TABLES
-- =============================================

CREATE TABLE IF NOT EXISTS shared_context (
    _id BIGINT PRIMARY KEY AUTO_INCREMENT,
    context_key VARCHAR(256) UNIQUE NOT NULL,
    context_value JSON NOT NULL,
    ttl_seconds INT COMMENT 'Time-to-live in seconds (0 = persistent)',
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by BIGINT COMMENT 'Agent that created this context',
    
    INDEX idx_context_key (context_key),
    INDEX idx_ttl (ttl_seconds)
) COMMENT='Shared state between agents for collaboration';

CREATE TABLE IF NOT EXISTS agent_cache (
    _id BIGINT PRIMARY KEY AUTO_INCREMENT,
    cache_key VARCHAR(256) UNIQUE NOT NULL,
    cached_value JSON NOT NULL,
    hit_count INT DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_cache_key (cache_key)
) COMMENT='Performance cache for frequently accessed data';

-- =============================================
-- SYSTEM METRICS AND MONITORING TABLES
-- =============================================

CREATE TABLE IF NOT EXISTS agent_metrics (
    _id BIGINT PRIMARY KEY AUTO_INCREMENT,
    agent_id BIGINT COMMENT 'Agent being monitored',
    metric_name VARCHAR(128) NOT NULL COMMENT 'Performance metric type (tokens_used|tasks_completed|error_rate|latency_ms)',
    metric_value DECIMAL(20,4) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (agent_id) REFERENCES agent_registry(_id),
    INDEX idx_agent_id (agent_id),
    INDEX idx_timestamp (timestamp)
) COMMENT='Performance metrics for all agents';

CREATE TABLE IF NOT EXISTS system_health (
    _id BIGINT PRIMARY KEY AUTO_INCREMENT,
    check_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    memory_usage DECIMAL(10,2) COMMENT 'Memory usage percentage',
    cpu_usage DECIMAL(10,2) COMMENT 'CPU usage percentage',
    active_agents INT DEFAULT 0 COMMENT 'Number of currently active agents',
    pending_requests INT DEFAULT 0 COMMENT 'Requests waiting to be processed',
    status VARCHAR(32) DEFAULT 'healthy' COMMENT 'System health status (healthy|degraded|critical)',
    
    INDEX idx_timestamp (`timestamp`)
) COMMENT='System health monitoring data';

-- =============================================
-- VERIFICATION QUERIES (Run manually after deployment)
-- =============================================
-- Uncomment these queries to verify table creation:
-- SELECT 'Agent Registry Tables:' AS check_name;
-- SHOW TABLES LIKE '%agent%';
-- 
-- SELECT 'Collaboration Tables:' AS check_name;
-- SHOW TABLES LIKE '%collab%';
