-- TiDB Community Edition v8.5+ Memory System - DDL Schema
-- Version: v0.1.0
-- Author: Haiwen Yin (胖头鱼 🐟 / yhw)
-- License: Apache 2.0

-- ============================================================
-- Core Tables for AI Agent Memory System
-- ============================================================

-- Drop existing tables if they exist (for re-deployment)
DROP TABLE IF EXISTS memories;
DROP TABLE IF EXISTS memory_edges;
DROP TABLE IF EXISTS memory_nodes;

-- ============================================================
-- Table: memory_nodes — Agent Memory Nodes
-- Stores individual memory entries with metadata and embeddings
-- ============================================================
CREATE TABLE memory_nodes (
    node_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    node_type VARCHAR(50) NOT NULL COMMENT 'type: memory/task/plan',
    content TEXT NOT NULL COMMENT 'memory content or task description',
    embedding VARBINARY(4096) COMMENT 'text embedding vector (1024 dims × 4 bytes)',
    metadata JSON COMMENT 'additional metadata as JSON object',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_node_type (node_type),
    INDEX idx_created_at (created_at)
);

-- ============================================================
-- Table: memory_edges — Graph Relationships  
-- Defines connections between memory nodes with properties
-- ============================================================
CREATE TABLE memory_edges (
    edge_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    source_node_id BIGINT NOT NULL COMMENT 'source node reference',
    target_node_id BIGINT NOT NULL COMMENT 'target node reference',
    relationship_type VARCHAR(50) COMMENT 'edge type: related_to/contains/etc',
    properties JSON COMMENT 'edge attributes and weights',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (source_node_id) REFERENCES memory_nodes(node_id),
    FOREIGN KEY (target_node_id) REFERENCES memory_nodes(node_id),
    INDEX idx_source (source_node_id),
    INDEX idx_target (target_node_id),
    INDEX idx_relationship_type (relationship_type)
);

-- ============================================================
-- Table: memories — Memory Content with Tags
-- Stores detailed memory content and associated tags
-- ============================================================
CREATE TABLE memories (
    memory_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    node_id BIGINT NOT NULL COMMENT 'reference to parent node',
    content TEXT NOT NULL COMMENT 'full memory text content',
    tags JSON COMMENT 'memory tags as array of strings',
    metadata JSON COMMENT 'content storage metadata',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (node_id) REFERENCES memory_nodes(node_id),
    INDEX idx_node_id (node_id),
    INDEX idx_tags_partial (tags(255)) -- Partial index for tag filtering
);

-- ============================================================
-- Table: task_plans — Task Plan Management System
-- Stores AI agent task plans with state tracking
-- ============================================================
CREATE TABLE IF NOT EXISTS task_plans (
    plan_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    plan_name VARCHAR(100) NOT NULL,
    plan_type VARCHAR(50) DEFAULT 'task' COMMENT 'type: task/plan/workflow',
    description TEXT,
    status VARCHAR(20) DEFAULT 'PENDING' COMMENT 'PENDING/RUNNING/SUCCESS/FAILED/CANCELLED/PAUSED',
    goal TEXT NOT NULL,
    steps JSON COMMENT 'task execution steps as array',
    metadata JSON COMMENT 'plan metadata and configuration',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_status (status),
    INDEX idx_plan_type (plan_type),
    INDEX idx_created_at (created_at)
);

-- ============================================================
-- Table: task_steps — Task Execution Steps Tracking
-- Records individual step execution within a task plan
-- ============================================================
CREATE TABLE IF NOT EXISTS task_steps (
    step_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    plan_id BIGINT NOT NULL,
    step_order INT NOT NULL COMMENT 'execution order number',
    step_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING' COMMENT 'PENDING/RUNNING/SUCCESS/FAILED/CANCELLED',
    input_data JSON COMMENT 'step input parameters',
    output_data JSON COMMENT 'step execution results',
    duration_ms INT COMMENT 'execution time in milliseconds',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (plan_id) REFERENCES task_plans(plan_id),
    INDEX idx_plan_id (plan_id),
    INDEX idx_status (status),
    INDEX idx_step_order (step_order)
);

-- ============================================================
-- Table: task_context_snapshots — Breakpoint Recovery
-- Saves context state for resuming after failures
-- ============================================================
CREATE TABLE IF NOT EXISTS task_context_snapshots (
    snapshot_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    plan_id BIGINT NOT NULL,
    step_id BIGINT COMMENT 'associated step ID',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context_snapshot JSON NOT NULL COMMENT 'full agent context at this point',
    
    FOREIGN KEY (plan_id) REFERENCES task_plans(plan_id),
    INDEX idx_plan_id (plan_id),
    INDEX idx_timestamp (timestamp)
);

-- ============================================================
-- Table: task_tool_calls — Tool Execution Audit Trail
-- Records all tool calls made during task execution
-- ============================================================
CREATE TABLE IF NOT EXISTS task_tool_calls (
    call_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    plan_id BIGINT NOT NULL,
    step_id BIGINT COMMENT 'associated step ID',
    tool_name VARCHAR(100) NOT NULL,
    input_params JSON COMMENT 'tool invocation parameters',
    output_result JSON COMMENT 'tool execution result',
    duration_ms INT COMMENT 'execution time in milliseconds',
    error_message TEXT COMMENT 'error details if failed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (plan_id) REFERENCES task_plans(plan_id),
    INDEX idx_plan_id (plan_id),
    INDEX idx_tool_name (tool_name),
    INDEX idx_created_at (created_at)
);

-- ============================================================
-- Table: task_dependencies — Task Relationship Definitions
-- Defines dependencies between different task plans
-- ============================================================
CREATE TABLE IF NOT EXISTS task_dependencies (
    dependency_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    source_plan_id BIGINT NOT NULL COMMENT 'dependent plan',
    target_plan_id BIGINT NOT NULL COMMENT 'dependency source',
    dependency_type VARCHAR(20) DEFAULT 'HARD' COMMENT 'HARD/SOFT/EXCLUSIVE/RECOMMENDED',
    condition JSON COMMENT 'dependency triggering conditions',
    
    FOREIGN KEY (source_plan_id) REFERENCES task_plans(plan_id),
    FOREIGN KEY (target_plan_id) REFERENCES task_plans(plan_id),
    INDEX idx_source_plan (source_plan_id),
    INDEX idx_target_plan (target_plan_id)
);

-- ============================================================
-- Verification Queries - Run after DDL execution
-- ============================================================
-- SELECT 'memory_nodes' as table_name, COUNT(*) as rows FROM memory_nodes;
-- SELECT 'memory_edges' as table_name, COUNT(*) as rows FROM memory_edges;
-- SELECT 'memories' as table_name, COUNT(*) as rows FROM memories;
