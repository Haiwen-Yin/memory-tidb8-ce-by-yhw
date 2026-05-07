# TiDB Community Edition v8.5+ Memory System

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## 🎯 Overview

A universal memory system for AI Agents built on **TiDB Community Edition 8.5+**, providing:

- ✅ HTAP (Hybrid Transactional/Analytical Processing) for real-time memory + analysis
- ✅ Semantic search via application-layer vector similarity with TiFlash acceleration
- ✅ Knowledge graph relationship management via recursive CTEs
- ✅ Full-text search capabilities
- ✅ Task plan system with persistent state management

---

## Architecture

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

- **Vector Similarity Search**: Application-layer cosine similarity with TiFlash acceleration
- **Knowledge Graph Management**: Property graph relationships via recursive CTEs
- **Full-text Search**: Native text indexing capabilities
- **Task Plan System**: Persistent task execution with state management
- **Real-time Analytics**: HTAP enables simultaneous OLTP and OLAP queries

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

## Testing Status

This system is in **initial development phase**. Key components need validation:

| Component | Status | Notes |
|-----------|--------|-------|
| Schema DDL (nodes/edges/memories) | ✅ Ready for testing | Syntax verified |
| SQL JSON views | ✅ Ready for testing | Basic query format checked |
| Recursive CTEs | ⚠️ Needs real data | Graph traversal patterns documented |
| Vector search (app-layer) | ⚠️ Needs benchmarking | Requires TiDB deployment with TiFlash |
| HTAP performance | 🔬 To be measured | TiFlash acceleration benefits TBD |

---

## Directory Structure

```
memory-tidb8-ce-by-yhw/
├── SKILL.md              # Complete skill documentation
├── README.md             # This file - project overview
├── LICENSE               # Apache License 2.0
├── NOTICE                # Copyright notice
├── CHANGELOG.md          # Version history
├── scripts/              # Helper scripts
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

**Last Updated**: 2026-05-05 v0.1.0 (Initial Release)