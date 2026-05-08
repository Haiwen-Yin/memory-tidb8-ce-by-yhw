---
name: memory-tidb8-ce-by-yhw
version: 0.1.2
description: "TiDB Community Edition v8.5+ AI Agent Memory System - Multi-Agent Architecture Support"
author: "Haiwen Yin (胖头鱼 🐟 / yhw)"
license: "Apache License, Version 2.0"
created: "2026-05-05"
updated: "2026-05-08"
---

# memory-tidb8-ce-by-yhw — TiDB Community Edition v8.5+ AI Agent Memory System

**Version**: v0.1.2 (Multi-Agent Architecture Edition)  
**Created**: 2026-05-05  
**Updated**: 2026-05-08
**Author**: Haiwen Yin (胖头鱼 🐟 / yhw)  
**License**: Apache License, Version 2.0

---

## 🎯 Overview

A universal memory system for AI Agents built on **TiDB Community Edition v8.5+**, featuring native SQL vector search capabilities with `vec_cosine_distance()` function for semantic similarity queries and knowledge graph management.

### Key Features (v0.1.2 Multi-Agent Update)

- ✅ Native VECTOR(1024) type support
- ✅ **SQL-based vec_cosine_distance() function** - Direct vector similarity queries in SQL
- ✅ ORDER BY distance sorting in database layer
- ✅ CAST JSON to VECTOR conversion for storage
- ✅ HTAP (Hybrid Transactional/Analytical Processing) capabilities
- ✅ PD Auto Partitioning for automatic load balancing
- ✅ **Multi-Agent Architecture** — Agent orchestration, collaboration framework, shared context

---

## 📋 Architecture

### Core Memory System

```
┌────────────────────────────────────────────────────────────┐
│                    Application Layer (Python/Java)         │
│  Embedding Generation → Text Vector Conversion             │
│  SQL Query Building with vec_cosine_distance()             │
├────────────────────────────────────────────────────────────┤
│                    TiDB Cluster (v8.5+)                    │
│                                                            │
│  ┌──────────┐    ┌──────────┐    ┌───────────┐             │
│  │ TiDB Svr │◄──►│ PD       │◄──►│ TiKV      │             │
│  │(SQL/Calc)│    │(Metadata)│    │(Row Store)│             │
│  └──────────┘    └──────────┘    └───────────┘             │
│                                                            │
│  vec_cosine_distance() SQL Function                        │
│  → Native Vector Similarity Query                          │
└────────────────────────────────────────────────────────────┘
```

### Multi-Agent Architecture (v0.1.2+)

```
┌─────────────────────────────────────────────────────────────┐
│                   Agent Orchestrator Layer                  │
│  ┌───────────┐    ┌──────────┐    ┌──────────┐              │
│  │Coordinator│ ←→ │Specialist│ ←→ │ Worker   │              │
│  │ (01)      │    │ (DB-01)  │    │ (Task-02)│              │
│  └─────┬─────┘    └────┬─────┘    └────┬─────┘              │
│        │               │               │                    │
│   ┌────▼───────────────▼───────────────▼────┐               │
│   │         Collaboration & State Layer     │               │
│   │  collaboration_requests | shared_context│               │
│   │  coordination_log     | agent_cache     │               │
│   └─────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Schema Design

### Core Memory Tables (Original)

#### memory_nodes — Agent Memory Nodes

```sql
CREATE TABLE memory_nodes (
    node_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    node_type VARCHAR(50) NOT NULL COMMENT 'type: memory/task/plan',
    content TEXT NOT NULL COMMENT 'memory content or task description',
    embedding VECTOR(1024) COMMENT 'text embedding vector',
    metadata JSON COMMENT 'additional metadata',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_node_type (node_type),
    INDEX idx_created_at (created_at)
);
```

#### memory_edges — Graph Relationships

```sql
CREATE TABLE memory_edges (
    edge_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    source_node_id BIGINT NOT NULL,
    target_node_id BIGINT NOT NULL,
    relationship_type VARCHAR(50),
    properties JSON COMMENT 'edge attributes',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_node_id) REFERENCES memory_nodes(node_id),
    FOREIGN KEY (target_node_id) REFERENCES memory_nodes(node_id),
    INDEX idx_source (source_node_id),
    INDEX idx_target (target_node_id)
);
```

### Multi-Agent Tables (v0.1.2+)

#### agent_registry — Agent Registry

```sql
CREATE TABLE agent_registry (
    _id BIGINT PRIMARY KEY AUTO_INCREMENT,
    agent_id VARCHAR(128) UNIQUE NOT NULL,
    agent_name VARCHAR(256) NOT NULL,
    description TEXT,
    model_config JSON COMMENT 'AI model configuration',
    role VARCHAR(32) DEFAULT 'general' COMMENT 'coordinator|specialist|worker|evaluator',
    capabilities JSON,
    status VARCHAR(32) DEFAULT 'active' COMMENT 'active|inactive|paused|decommissioned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    metadata JSON,
    INDEX idx_agent_id (agent_id),
    INDEX idx_status (status),
    INDEX idx_role (role)
);
```

#### agent_session — Session Management

```sql
CREATE TABLE agent_session (
    _id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(128) UNIQUE NOT NULL,
    agent_id BIGINT COMMENT 'Reference to agent_registry._id',
    task_context JSON COMMENT 'Task context and requirements',
    state VARCHAR(32) DEFAULT 'initialized' COMMENT 'initialized|active|suspended|completed|failed',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP NULL,
    memory_snapshot_id BIGINT,
    FOREIGN KEY (agent_id) REFERENCES agent_registry(_id),
    INDEX idx_session_id (session_id),
    INDEX idx_agent_id (agent_id),
    INDEX idx_state (state)
);
```

#### collaboration_request — Multi-Agent Collaboration

```sql
CREATE TABLE collaboration_request (
    _id BIGINT PRIMARY KEY AUTO_INCREMENT,
    request_id VARCHAR(128) UNIQUE NOT NULL,
    initiator_agent_id BIGINT COMMENT 'Agent making the request',
    target_agent_ids JSON COMMENT 'Array of agent IDs to collaborate with',
    task_description TEXT NOT NULL,
    priority INT DEFAULT 5 COMMENT 'Priority level: 1-10',
    status VARCHAR(32) DEFAULT 'pending' COMMENT 'pending|assigned|in_progress|completed|rejected',
    result JSON COMMENT 'Collaboration outcome and deliverables',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (initiator_agent_id) REFERENCES agent_registry(_id),
    INDEX idx_request_id (request_id),
    INDEX idx_status (status)
);
```

#### shared_context — Inter-Agent Communication

```sql
CREATE TABLE shared_context (
    _id BIGINT PRIMARY KEY AUTO_INCREMENT,
    context_key VARCHAR(256) UNIQUE NOT NULL,
    context_value JSON NOT NULL,
    ttl_seconds INT COMMENT 'Time-to-live in seconds; 0 = persistent',
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by BIGINT COMMENT 'Agent that created this context',
    INDEX idx_context_key (context_key),
    INDEX idx_ttl (ttl_seconds)
);
```

#### coordination_log — Activity Audit Trail

```sql
CREATE TABLE coordination_log (
    _id BIGINT PRIMARY KEY AUTO_INCREMENT,
    request_id VARCHAR(128) COMMENT 'Reference to collaboration_request.request_id',
    agent_id BIGINT COMMENT 'Agent performing the action',
    action_type VARCHAR(64) COMMENT 'Type of coordination: assign|delegate|query|notify|confirm',
    payload JSON COMMENT 'Action-specific data',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_request_id (request_id),
    INDEX idx_timestamp (timestamp)
);
```

#### agent_cache — Performance Caching

```sql
CREATE TABLE agent_cache (
    _id BIGINT PRIMARY KEY AUTO_INCREMENT,
    cache_key VARCHAR(256) UNIQUE NOT NULL,
    cached_value JSON NOT NULL,
    hit_count INT DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cache_key (cache_key)
);
```

#### agent_metrics — Performance Monitoring

```sql
CREATE TABLE agent_metrics (
    _id BIGINT PRIMARY KEY AUTO_INCREMENT,
    agent_id BIGINT COMMENT 'Agent being monitored',
    metric_name VARCHAR(128) NOT NULL COMMENT 'tokens_used|tasks_completed|error_rate|latency_ms',
    metric_value DECIMAL(20,4) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agent_registry(_id),
    INDEX idx_agent_id (agent_id),
    INDEX idx_timestamp (timestamp)
);
```

### Multi-Agent Architecture Usage (v0.1.2+)

#### Agent Registration and Management

```python
from scripts.multi_agent_api import (
    AgentRegistryAPI, 
    AgentConfig,
    AgentRole
)

registry = AgentRegistryAPI()

# Register a coordinator agent
coordinator_config = AgentConfig(
    agent_id="coordinator-01",
    name="Task Orchestrator",
    role=AgentRole.COORDINATOR,
    description="Main task coordination agent"
)
registry.register_agent(coordinator_config)

# Register a specialist agent
specialist_config = AgentConfig(
    agent_id="specialist-db-01",
    name="Database Specialist",
    role=AgentRole.SPECIALIST,
    capabilities=["schema_analysis", "query_optimization"]
)
registry.register_agent(specialist_config)

# List all agents by role
all_agents = registry.list_agents()
db_specialists = registry.list_agents(role=AgentRole.SPECIALIST)
```

#### Session Management

```python
from scripts.multi_agent_api import (
    SessionAPI, 
    SessionState
)

session_api = SessionAPI()

# Create a new execution session
task_context = {"objective": "Optimize database schema"}
session_api.create_session("session-001", coordinator.agent_id, task_context)

# Update session state during execution
session_api.update_session_state("session-001", SessionState.ACTIVE)

# Complete or fail the session
session_api.update_session_state("session-001", SessionState.COMPLETED)
```

#### Collaboration and Task Delegation

```python
from scripts.multi_agent_api import (
    CollaborationAPI, 
    CollaborationRequest
)

collaboration_api = CollaborationAPI()

# Submit a collaboration request
request = CollaborationRequest(
    request_id="collab-001",
    initiator_agent_id=coordinator.agent_id,
    target_agents=[specialist_config.agent_id],
    task_description="Analyze and optimize database schema for performance"
)

# Submit the request (creates collaboration_request record)
request_id = collaboration_api.submit_request(request)

# Assign to specific agent (optional)
collaboration_api.assign_request(request_id, specialist_config.agent_id)
```

#### Shared Context Access

```python
from scripts.multi_agent_api import SharedContextAPI

context_api = SharedContextAPI()

# Store shared context for other agents with TTL
context_api.set_context("db_schema_status", {
    "status": "ready",
    "optimization_suggestions": ["add_index", "refactor_table"]
}, ttl_seconds=3600)  # 1 hour TTL

# Retrieve shared context from another agent
shared_data = context_api.get_context("db_schema_status")
```

#### System Monitoring and Metrics

```python
from scripts.multi_agent_api import MonitoringAPI

monitoring_api = MonitoringAPI()

# Record metrics for an agent
monitoring_api.record_metric(specialist_config.agent_id, "tasks_completed", 42)
monitoring_api.record_metric(specialist_config.agent_id, "error_rate", 0.05)

# Check system health status
health_status = monitoring_api.get_system_health()
print(f"Active agents: {health_status['active_agents']}")
```


---

## 📦 Installation & Deployment

### Prerequisites

- **Database**: TiDB Community Edition 8.5+ (HTAP enabled with TiFlash)
- **Python**: 3.8+ with `pymysql` and `numpy` libraries
- **Network**: Access to TiDB server (port 4000 by default)

### Deploy TiDB Cluster

```bash
# Using tiup playground (recommended for testing)
tiup playground v8.5.6 --db 1 --pd 3 --kv 3 --tiflash 1

# Or download from: https://pingkai.cn/download#tidb-community
```

### Install Python Dependencies

```bash
pip install pymysql numpy
```

### Apply Schema

Use the DDL statements from SKILL.md to create all tables and indexes.

---

## 🔧 Usage Examples

### Vector Similarity Search

```python
from scripts.vector_similarity import (
    cosine_similarity,
    find_similar_nodes,
    embedding_to_text
)

# Calculate cosine similarity between two vectors
vec_a = [0.1, 0.2, 0.3]
vec_b = [0.15, 0.25, 0.35]
similarity = cosine_similarity(vec_a, vec_b)

# Find similar nodes in database
similar_nodes = find_similar_nodes(
    query_vector=your_embedding,
    limit=10
)
```

### Multi-Agent Architecture (v0.1.2+)

#### Agent Registration

```python
from scripts.multi_agent_api import (
    AgentRegistryAPI,
    AgentConfig,
    AgentRole
)

registry = AgentRegistryAPI()

# Register a coordinator agent
coordinator_config = AgentConfig(
    agent_id="coordinator-01",
    name="Task Orchestrator",
    role=AgentRole.COORDINATOR,
    description="Main task coordination agent"
)
registry.register_agent(coordinator_config)

# Register a specialist agent
specialist_config = AgentConfig(
    agent_id="specialist-db-01",
    name="Database Specialist",
    role=AgentRole.SPECIALIST,
    capabilities=["schema_analysis", "query_optimization"]
)
registry.register_agent(specialist_config)

# List all agents
all_agents = registry.list_agents()
```

#### Session Management

```python
from scripts.multi_agent_api import SessionAPI, SessionState

session_api = SessionAPI()

# Create a new session
task_context = {"objective": "Optimize database schema"}
session_api.create_session("session-001", coordinator.agent_id, task_context)

# Update session state
session_api.update_session_state("session-001", SessionState.ACTIVE)
```

#### Collaboration and Task Delegation

```python
from scripts.multi_agent_api import CollaborationAPI, CollaborationRequest

collaboration_api = CollaborationAPI()

# Submit a collaboration request
request = CollaborationRequest(
    request_id="collab-001",
    initiator_agent_id=coordinator.agent_id,
    target_agents=[specialist_config.agent_id],
    task_description="Analyze and optimize database schema for performance"
)

request_id = collaboration_api.submit_request(request)

# Assign to specific agent (optional)
collaboration_api.assign_request(request_id, specialist_config.agent_id)
```

#### Shared Context Access

```python
from scripts.multi_agent_api import SharedContextAPI

context_api = SharedContextAPI()

# Store shared context for other agents
context_api.set_context("db_schema_status", {
    "status": "ready",
    "optimization_suggestions": ["add_index", "refactor_table"]
}, ttl_seconds=3600)  # 1 hour TTL

# Retrieve shared context from another agent
shared_data = context_api.get_context("db_schema_status")
```

---

## 📊 Testing Status

This system is in **initial development phase**. Key components need validation:

| Component | Status | Notes |
|-----------|--------|-------|
| Schema DDL (nodes/edges/memories) | ✅ Ready for testing | Syntax verified |
| SQL JSON views | ✅ Ready for testing | Basic query format checked |
| Recursive CTEs | ⚠️ Needs real data | Graph traversal patterns documented |
| Vector search (app-layer) | ⚠️ Needs benchmarking | Requires TiDB deployment with TiFlash |
| HTAP performance | 🔬 To be measured | TiFlash acceleration benefits TBD |
| Multi-Agent Architecture | 📝 Ready for integration testing | v0.1.2 release candidate |

---

## 📁 Directory Structure

```
memory-tidb8-ce-by-yhw/
├── SKILL.md              # Complete skill documentation (this file)
├── README.md             # Project overview and quick start guide
├── LICENSE               # Apache License 2.0
├── NOTICE                # Copyright notice for Haiwen Yin/yhw
├── CHANGELOG.md          # Version history
├── VERSION               # Current version string
├── scripts/              # Helper scripts
│   ├── init_memory_system.sql    # Core schema DDL (original)
│   ├── multi_agent_schema.sql    # Multi-Agent tables (v0.1.2+)
│   ├── schema_loader.py          # Schema deployment utility
│   ├── task_plan_api.py          # Task plan management API
│   ├── vector_similarity.py      # Vector similarity calculations
│   ├── multi_agent_api.py        # Multi-Agent orchestration API (v0.1.2+)
│   └── ...                       # Additional utilities
├── references/           # External documentation references
└── *.md                  # Test reports, release notes, etc.
```

---

## 📚 Related Documentation

- [TiDB CE Download](https://pingkai.cn/download#tidb-community) — Community Edition download links
- [TiDB Documentation](https://pingkai.cn/docs/tidb/stable/) — Official documentation entry point
- [TiFlash Overview](https://pingkai.cn/docs/tidb/stable/tiflash-overview) — Columnar storage features

---

## 👤 Author & Maintainer

**Haiwen Yin (胖头鱼 🐟)**  
Oracle/PostgreSQL/MySQL ACE Database Expert

- **Blog**: https://blog.csdn.net/yhw1809
- **GitHub**: https://github.com/Haiwen-Yin

---

## 📝 License

This project is licensed under the [Apache License, Version 2.0](LICENSE).

---

**Last Updated**: 2026-05-08 v0.1.2 (Multi-Agent Architecture Edition)
