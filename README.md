# memory-tidb8-ce-by-yhw — TiDB Community Edition v8.5+ AI Agent Memory System

**Version**: v1.0.0 (Knowledge Base System Production Release)  
**Created**: 2026-05-05  
**Updated**: 2026-05-11  
**Author**: Haiwen Yin (胖头鱼 🐟 / yhw)  
**License**: Apache License, Version 2.0

---

## Overview

A universal memory system for AI Agents built on **TiDB Community Edition v8.5+**, featuring complete Knowledge Base system with native vector search capabilities, knowledge graph management, and Multi-Agent architecture support.

### Key Features (v1.0.0)

#### Knowledge Base System
- **Knowledge Concepts** - Stable knowledge entities (FACT/RULE/PATTERN/EXPERIENCE/PRINCIPLE)
- **Knowledge Graph** - Property graph-based relationship management (IS_A/PART_OF/CAUSES/ENABLES/CONTRADICTS/SUPPORTS)
- **Version Control** - Complete version history for knowledge concepts
- **Validation Workflow** - Knowledge validation and approval process
- **Audit Trail** - Complete audit logging for all operations
- **Citation Tracking** - Knowledge concept citation relationships

#### Hybrid Search
- **Text Search** - Keyword-based full-text search
- **Semantic Search** - Vector similarity-based semantic search (application-layer implementation)
- **Graph Traversal** - Knowledge graph relationship queries

#### Multi-Agent Architecture
- **Agent Registry** - Centralized agent registration and discovery
- **Memory Visibility Control** - Three visibility levels (SHARED/PRIVATE/COLLABORATIVE)
- **Session Management** - Active session tracking with context preservation
- **Access Audit Trail** - Complete logging of memory access operations
- **Collaboration Workflow** - Request/approve mechanism for agent-to-agent knowledge sharing

---

## Quick Start

### Prerequisites

- **Database**: TiDB Community Edition 8.5+ (HTAP enabled with TiFlash)
- **Python**: 3.8+ with `pymysql` and `numpy` libraries
- **Network**: Access to TiDB server (port 4000 by default)

### Install Dependencies

```bash
pip install pymysql numpy requests
```

### Deploy Schema

```bash
# Create database
mysql -h10.10.10.142 -P4000 -uroot -ptidb#123 -e "CREATE DATABASE IF NOT EXISTS memory;"

# Deploy Knowledge Base Schema
mysql -h10.10.10.142 -P4000 -uroot -ptidb#123 -D memory < scripts/knowledge_base_schema_tidb.sql

# Verify deployment
mysql -h10.10.10.142 -P4000 -uroot -ptidb#123 -D memory -e "SHOW TABLES LIKE 'knowledge%';"
```

### Run Tests

```bash
python3 scripts/test_tidb_v1.0.0_complete.py
```

---

## Usage Examples

### Knowledge Base Operations

```python
from scripts.knowledge_base_api_tidb import KnowledgeBaseAPI

# Initialize API
kb = KnowledgeBaseAPI()

# Create a knowledge concept
concept = kb.create_concept(
    concept_name="TiDB CE 8.5.6",
    concept_type="FACT",
    description="TiDB Community Edition v8.5.6 with native vector search",
    category="database",
    confidence=0.95,
    tags=["tidb", "vector", "database"],
    metadata={"version": "8.5.6", "license": "Apache 2.0"}
)
print(f"Created concept: {concept}")

# Create a relationship
relationship = kb.create_relationship(
    source_concept_id=concept['concept_id'],
    target_concept_id=other_concept_id,
    relationship_type="SUPPORTS",
    strength=0.90,
    confidence=0.85
)

# Text search
results = kb.search_by_text(keyword="TiDB", limit=10)

# Semantic search
similar_concepts = kb.search_similar_concepts(
    query_text="TiDB vector database",
    limit=5,
    threshold=0.75
)

# Get concept with graph
concept_with_graph = kb.get_concept_with_graph(concept_id=concept['concept_id'])

# Get statistics
stats = kb.get_statistics()
print(f"Total concepts: {stats['total_concepts']}")
print(f"Total relationships: {stats['total_relationships']}")
```

### Multi-Agent Operations

```python
from scripts.multi_agent_api import (
    AgentRegistryAPI,
    AgentConfig,
    AgentRole
)

# Register a coordinator agent
registry = AgentRegistryAPI()
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
db_specialists = registry.list_agents(role=AgentRole.SPECIALIST)
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

# Submit request
request_id = collaboration_api.submit_request(request)

# Assign to specific agent (optional)
collaboration_api.assign_request(request_id, specialist_config.agent_id)
```

### Shared Context Access

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

---

## Architecture

### Knowledge Base System

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer (Python/Java)          │
│  Embedding Generation → Text Vector Conversion              │
│  SQL Query Building with vec_cosine_distance()              │
├─────────────────────────────────────────────────────────────┤
│                    TiDB Cluster (v8.5+)                     │
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌───────────┐              │
│  │ TiDB Svr │◄──►│ PD       │◄──►│ TiKV      │              │
│  │(SQL/Calc)│    │(Metadata)│    │(Row Store)│              │
│  └──────────┘    └──────────┘    └───────────┘              │
│                                                             │
│  vec_cosine_distance() SQL Function                         │
│  → Native Vector Similarity Query                           │
└─────────────────────────────────────────────────────────────┘
```

### Multi-Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Agent Orchestrator Layer                  │
│  ┌───────────┐    ┌──────────┐    ┌──────────┐              │
│  │Coordinator│ ←→ │Specialist│ ←→ │Worker    │              │
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

## Testing Status

### v1.0.0 Complete Test Suite (9 Tests)

| Test | Status | Description |
|------|--------|-------------|
| Database Connection | ✅ Pass | TiDB v8.5.6 (10.10.10.142:4000) |
| Create Knowledge Concepts | ✅ Pass | Created 4 test concepts with tags and embeddings |
| Update Knowledge Concept | ✅ Pass | Updated concept description and confidence |
| Create Knowledge Relationships | ✅ Pass | Created 3 test relationships |
| Text Search | ✅ Pass | Keyword search working (4 results found) |
| Semantic Search | ✅ Pass | Application-layer semantic search working (2 similar concepts found) |
| Get Concept with Graph | ✅ Pass | Graph relationship queries working |
| Get Statistics | ✅ Pass | Knowledge base statistics working |
| Delete Knowledge Concept | ✅ Pass | Cascading delete working (FK constraint fixed) |

**Total**: 9/9 Pass (100%)

---

## Directory Structure

```
memory-tidb8-ce-by-yhw/
├── SKILL.md              # Complete skill documentation
├── README.md             # Project overview and quick start guide
├── LICENSE               # Apache License 2.0
├── NOTICE                # Copyright notice for Haiwen Yin/yhw
├── CHANGELOG.md          # Version history
├── VERSION               # Current version string
├── scripts/              # Helper scripts
│   ├── init_memory_system.sql    # Core schema DDL (original)
│   ├── knowledge_base_schema_tidb.sql  # Knowledge Base Schema (v1.0.0)
│   ├── knowledge schema_api_tidb.py     # Knowledge Base Python API (v1.0.0)
│   ├── multi_agent_schema.sql    # Multi-Agent tables
│   ├── schema_loader.py          # Schema deployment utility
│   ├── task_plan_api.py          # Task plan management API
│   ├── vector_similarity.py      # Vector similarity calculations
│   ├── multi_agent_api.py        # Multi-Agent orchestration API
│   └── ...                       # Additional utilities
├── references/           # External documentation references
└── test_tidb_v1.0.0_complete.py  # Complete test suite
```

---

## Related Documentation

- [TiDB CE Download](https://pingcap.com/download/community) — Community Edition download links
- [TiDB Documentation](https://docs.pingcap.com/tidb/stable/) — Official documentation entry point
- [TiFlash Overview](https://docs.pingcap.com/tidb/stable/tiflash-overview) — Columnar storage features
- [oracle-memory-by-yhw v1.0.0](../oracle-memory-by-yhw/) — Original version reference

---

## Author & Maintainer

**Haiwen Yin (胖头鱼 🐟)**  
Oracle/PostgreSQL/MySQL ACE Database Expert

- **Blog**: https://blog.csdn.net/yhw1809
- **GitHub**: https://github.com/Haiwen-Yin

---

## License

This project is licensed under [Apache License, Version 2.0](LICENSE).

---

**Last Updated**: 2026-05-11 v1.0.0 (Knowledge Base System Production Release)
