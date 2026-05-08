# TiDB Community Edition v8.5+ Memory System with Multi-Agent Architecture

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-v0.1.2-green.svg)](VERSION)

## 🎯 Overview

A universal memory system for AI Agents built on **TiDB Community Edition 8.5+**, providing:

- ✅ HTAP (Hybrid Transactional/Analytical Processing) for real-time memory + analysis
- ✅ Semantic search via application-layer vector similarity with TiFlash acceleration
- ✅ Knowledge graph relationship management via recursive CTEs
- ✅ Full-text search capabilities
- ✅ Task plan system with persistent state management
- ✅ **Multi-Agent Architecture** (v0.1.2+) — Agent orchestration, collaboration, and coordination

---

## Architecture

### Core Memory System

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer (Python/Java)          │
│  Embedding Generation → Text Vector Conversion              │
│  Cosine Similarity Calculation                              │
│  Graph Traversal via Recursive CTEs                         │
├─────────────────────────────────────────────────────────────┤
│                    TiDB Cluster (v8.5+)                     │
│  TiDB Server ↔ PD (Metadata) → TiKV (Row Store)             │
│                          ↕                                  │
│                    TiFlash (Columnar Storage)               │
└─────────────────────────────────────────────────────────────┘
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

## Requirements

- **Database**: TiDB Community Edition 8.5+ (HTAP enabled with TiFlash)
- **Python**: 3.8+ with `pymysql` and `numpy` libraries
- **Network**: Access to TiDB server (port 4000 by default)
- **PD Cluster**: Placement Driver for metadata management

---

## Quick Start

### 1. Deploy TiDB Cluster

```bash
# Using tiup playground (recommended for testing)
tiup playground v8.5.6 --db 1 --pd 3 --kv 3 --tiflash 1

# Or download from: https://pingkai.cn/download#tidb-community
```

### 2. Install Prerequisites

```bash
# Python dependencies
pip install pymysql numpy

# TiDB client (optional)
sudo apt update && sudo apt install -y mysql-client
```

### 3. Configure Environment Variables

```bash
export TIDB_HOST=127.0.0.1
export TIDB_PORT=4000
export TIDB_USER=root@memcluster  
export TIDB_PASS=your_password
export TIDB_DATABASE=memory_cluster
```

### 4. Apply Schema

Use the DDL statements from SKILL.md to create all tables and indexes.

---

## Features

### Core Memory System
- **Vector Similarity Search**: Application-layer cosine similarity with TiFlash acceleration
- **Knowledge Graph Management**: Property graph relationships via recursive CTEs
- **Full-text Search**: Native text indexing capabilities
- **Task Plan System**: Persistent task execution with state management
- **Real-time Analytics**: HTAP enables simultaneous OLTP and OLAP queries

### Multi-Agent Architecture (v0.1.2+)
- **Agent Registry**: Dynamic agent registration with role classification (coordinator, specialist, worker, evaluator)
- **Session Management**: Agent execution lifecycle tracking with state transitions
- **Collaboration Framework**: Cross-agent task delegation and result aggregation
- **Shared Context**: Inter-agent communication through shared key-value stores
- **Monitoring & Metrics**: Performance tracking for all registered agents

---

## Installation

### Prerequisites

| Component | Requirement | Notes |
|-----------|-------------|-------|
| Database | TiDB 8.5+ | With TiFlash for columnar acceleration |
| Python | 3.8+ | With pymysql, numpy packages |
| Network | Port 4000 accessible | Default TiDB port |

### Quick Start

```bash
# Deploy TiDB cluster (testing only)
tiup playground v8.5.6 --db 1 --pd 3 --kv 3 --tiflash 1

# Copy skill files to your workspace
cp -r memory-tidb8-ce-by-yhw/ ~/.hermes/skills/

# Install Python dependencies
pip install pymysql numpy

# Configure environment variables
export TIDB_HOST=127.0.0.1
export TIDB_PORT=4000
export TIDB_USER=root@memcluster  
export TIDB_PASS=your_password
```

---

## Usage

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

### Task Plan Management

```python
from scripts.task_plan_api import (
    create_task_plan,
    resume_task,
    search_completed_tasks
)

# Create a new task plan
plan_id = create_task_plan(
    plan_name="my_task",
    plan_type="task",
    description="Task description"
)

# Resume an existing task
result = resume_task(plan_id)

# Search completed tasks
tasks = search_completed_tasks({
    "status": "completed",
    "type": "task"
})
```

### Schema Management

```python
from scripts.schema_loader import (
    apply_schema,
    check_schema_exists
)

# Check if schema exists
exists = check_schema_exists()

# Apply or update schema
apply_schema(dry_run=False)
```

---

## Multi-Agent Architecture Usage (v0.1.2+)

### Agent Registration

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

### Session Management

```python
from scripts.multi_agent_api import SessionAPI, SessionState

session_api = SessionAPI()

# Create a new session
task_context = {"objective": "Optimize database schema"}
session_api.create_session("session-001", coordinator.agent_id, task_context)

# Update session state
session_api.update_session_state("session-001", SessionState.ACTIVE)
```

### Collaboration and Task Delegation

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

### Shared Context Access

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

### System Monitoring

```python
from scripts.multi_agent_api import MonitoringAPI

monitoring_api = MonitoringAPI()

# Record metrics for an agent
monitoring_api.record_metric(specialist_config.agent_id, "tasks_completed", 42)
monitoring_api.record_metric(specialist_config.agent_id, "error_rate", 0.05)

# Check system health
health_status = monitoring_api.get_system_health()
print(f"Active agents: {health_status['active_agents']}")
```

---

## Testing Status

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

## Directory Structure

```
memory-tidb8-ce-by-yhw/
├── SKILL.md              # Complete skill documentation
├── README.md             # This file - project overview
├── LICENSE               # Apache License 2.0
├── NOTICE                # Copyright notice
├── CHANGELOG.md          # Version history
├── VERSION               # Current version
├── scripts/              # Helper scripts
│   ├── init_memory_system.sql    # Core schema DDL
│   ├── multi_agent_schema.sql    # Multi-Agent tables (v0.1.2+)
│   ├── schema_loader.py          # Schema deployment utility
│   ├── task_plan_api.py          # Task plan management API
│   ├── vector_similarity.py      # Vector similarity calculations
│   ├── multi_agent_api.py        # Multi-Agent orchestration API (v0.1.2+)
│   └── ...                       # Additional utilities
├── references/           # External references
└── *.md                  # Test reports, etc.
```

---

## Related Documentation

- [TiDB CE Download](https://pingkai.cn/download#tidb-community) — Community Edition download links
- [TiDB Documentation](https://pingkai.cn/docs/tidb/stable/) — Official documentation entry point
- [TiFlash Overview](https://pingkai.cn/docs/tidb/stable/tiflash-overview) — Columnar storage features

---

## Author & Maintainer

**Haiwen Yin (胖头鱼 🐟)**  
Oracle/PostgreSQL/MySQL ACE Database Expert

- **Blog**: https://blog.csdn.net/yhw1809
- **GitHub**: https://github.com/Haiwen-Yin

---

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).

---

**Last Updated**: 2026-05-08 v0.1.2 (Multi-Agent Architecture Edition)