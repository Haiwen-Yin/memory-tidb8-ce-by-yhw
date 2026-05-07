---
name: memory-tidb8-ce-by-yhw
version: 0.1.1
description: "TiDB Community Edition v8.5+ AI Agent Memory System - SQL Vector Search Support"
author: "Haiwen Yin (胖头鱼 🐟 / yhw)"
license: "Apache License, Version 2.0"
created: "2026-05-05"
updated: "2026-05-07"
---

# memory-tidb8-ce-by-yhw — TiDB Community Edition v8.5+ AI Agent Memory System

**Version**: v0.1.1 (SQL Vector Search Support - vec_cosine_distance)  
**Created**: 2026-05-05  
**Updated**: 2026-05-07
**Author**: Haiwen Yin (胖头鱼 🐟 / yhw)  
**License**: Apache License, Version 2.0

---

## 🎯 Overview

A universal memory system for AI Agents built on **TiDB Community Edition v8.5+**, featuring native SQL vector search capabilities with `vec_cosine_distance()` function for semantic similarity queries and knowledge graph management.

### Key Features (v0.1.1 Update)

- ✅ Native VECTOR(1024) type support
- ✅ **SQL-based vec_cosine_distance() function** - Direct vector similarity queries in SQL
- ✅ ORDER BY distance sorting in database layer
- ✅ CAST JSON to VECTOR conversion for storage
- ✅ HTAP (Hybrid Transactional/Analytical Processing) capabilities
- ✅ PD Auto Partitioning for automatic load balancing

---

## 📋 Architecture

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

---

## 📋 Schema Design

### Core Tables

#### memory_nodes — Agent Memory Nodes (Updated for v0.1.1)

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

#### memories — Memory Content with Tags

```sql
CREATE TABLE memories (
    memory_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    node_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    tags JSON COMMENT 'memory tags as array',
    metadata JSON COMMENT 'storage metadata',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (node_id) REFERENCES memory_nodes(node_id),
    INDEX idx_tags (tags(255)) -- Partial index for tag filtering
);
```

---

## 🔧 SQL Vector Search (v0.1.1 - NEW!)

### Using vec_cosine_distance() Function

TiDB CE v8.5.6 includes native `vec_cosine_distance()` function for vector similarity queries:

```sql
-- Query similar documents using SQL (v0.1.1 feature)
SELECT id, document, 
       vec_cosine_distance(embedding, CAST('[0.5,0.5,...]' AS VECTOR(1024))) AS distance
FROM vector_native_test
ORDER BY distance
LIMIT 3;

-- With parameter binding (prepared statement style)
SELECT node_id, content,
       vec_cosine_distance(embedding, CAST(? AS VECTOR(1024))) AS similarity_score
FROM memory_nodes
WHERE node_type = 'memory' AND embedding IS NOT NULL
ORDER BY similarity_score
LIMIT 10;

-- Filter by distance threshold
SELECT id, text_content, distance FROM (
    SELECT id, text_content, 
           vec_cosine_distance(embedding, CAST(? AS VECTOR(1024))) AS distance
    FROM vector_native_test
) t WHERE distance < 0.3 ORDER BY distance;
```

### Testing Results (Verified on TiDB CE v8.5.6)

**Test Environment:**
- TiDB Version: 8.0.11-TiDB-v8.5.6
- Database: memory_system
- Vector Type: VECTOR(1024)

**SQL Query Example:**
```sql
USE memory_system;
SELECT 
    id,
    text_content AS document,
    vec_cosine_distance(embedding, CAST('[0.5,...]' AS VECTOR(1024))) AS distance
FROM vector_native_test
ORDER BY distance
LIMIT 5;
```

**Query Results:**
| ID | Document (Text Content) | Cosine Distance |
|----|-------------------------|-----------------|
| 33 | Data Science Analysis | 0.23455271808188727 |
| 34 | Python Programming Language | 0.2350298471474359 |
| 30 | Distributed Database Technology | 0.23583382639728667 |
| 32 | Cloud Computing Architecture Design | 0.23873097179667757 |
| 31 | AI Machine Learning Algorithm | 0.2404038003504697 |

### Storing Vectors in SQL

```sql
-- Store vector using CAST conversion
INSERT INTO vector_native_test (text_content, embedding) 
VALUES ('AI Machine Learning Algorithm', CAST('[0.1, 0.2, ...]' AS VECTOR(1024)));

-- Using JSON array format with proper escaping
INSERT INTO memory_nodes (content, embedding) 
VALUES ('test content', CAST('[0.5,0.5,...]' AS VECTOR(1024)));
```

---

## 📋 Deployment Checklist

### Prerequisites

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **Database** | TiDB Community Edition v8.5+ | Minimum version for HTAP features |
| **Python** | 3.8+ | With pymysql, numpy packages (for embedding generation) |
| **Network** | Port 4000 (TiDB), 2379 (PD) accessible | Default ports |

### Current Deployment Status

> ✅ **DEPLOYED**: TiDB v8.5.6 Community Edition cluster (Production Environment)

**Cluster Topology:**
```
┌──────────────────────────────────────────────────────────────────────┐
│                      TiDB Cluster Production Environment             │
│                                                                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │
│  │   10.10.10.142  │    │   10.10.10.141  │    │   10.10.10.143  │   │
│  │                 │    │                 │    │                 │   │
│  │  ┌─────────────┐│    │  ┌─────────────┐│    │  ┌─────────────┐│   │
│  │  │   TiDB      ││    │  │     PD      ││    │  │    TiKV-1   ││   │
│  │  │   :4000     ││    │  │   :2379     ││    │  │   :20160    ││   │
│  │  └─────────────┘│    │  └─────────────┘│    │  └─────────────┘│   │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘   │
│           │                      │                      │            │
│           ▼                      ▼                      ▼            │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │
│  │   10.10.10.144  │    │   10.10.10.145  │    │   10.10.10.146  │   │
│  │                 │    │                 │    │                 │   │
│  │  ┌─────────────┐│    │  ┌─────────────┐│    │  ┌─────────────┐│   │
│  │  │    TiKV-2   ││    │  │    TiKV-3   ││    │  │    TiKV-4   ││   │
│  │  │   :20160    ││    │  │   :20160    ││    │  │   :20160    ││   │
│  │  └─────────────┘│    │  └─────────────┘│    │  └─────────────┘│   │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘

**Cluster Configuration:**
- **TiDB Server**: 10.10.10.142:4000 (SQL layer, handles queries)
- **PD (Placement Driver)**: 10.10.10.141:2379 (Metadata & scheduling)
- **TiKV Nodes**: 
  - 10.10.10.143:20160 (Node 1, Row Store)
  - 10.10.10.144:20160 (Node 2, Row Store)  
  - 10.10.10.145:20160 (Node 3, Row Store)
  - 10.10.10.146:20160 (Node 4, Row Store)

**Database Configuration:**
- **Database Name**: memory_system
- **Tenant**: root@% (full administrative access)
- **Password**: tidb#123
```

### Quick Start - Connect to Existing Cluster

```bash
# Using mysql client (TiDB compatible)
mysql -h 10.10.10.142 -P 4000 -u root -p'tidb#123' memory_system

# Or with Python directly
python3 scripts/schema_loader.py --host 10.10.10.142 --port 4000 --user root --password 'tidb#123'
```

### Configure Environment Variables

```bash
export TIDB_HOST=10.10.10.142
export TIDB_PORT=4000
export TIDB_USER=root
export TIDB_PASS=tidb#123
export TIDB_DATABASE=memory_system
```

---

## 📋 Directory Structure

```
memory-tidb8-ce-by-yhw/
├── SKILL.md              # This file — complete skill documentation
├── README.md             # Project overview and quick start guide
├── LICENSE               # Apache License 2.0
├── NOTICE                # Copyright notice
├── CHANGELOG.md          # Version history
├── RELEASE_NOTES.md      # v0.1.1 Release Notes (NEW!)
├── scripts/              # Helper scripts
│   ├── init_memory_system.sql    # DDL statements for schema creation
│   ├── schema_loader.py          # Python schema deployment tool
│   └── vector_similarity.py      # Cosine similarity calculator (application layer fallback)
├── references/           # External documentation links
```

---

## ⚠️ Testing Status & Environment

**Status**: ✅ **DEPLOYED AND VERIFIED** — TiDB v8.5.6 Community Edition  
**Deployment Date**: 2026-05-06 (Updated: 2026-05-07 for v0.1.1)  
**Cluster Address**: `10.10.10.142:4000` (TiDB), `10.10.10.141:2379` (PD)

**Verification Results:**

| Check | Status | Notes |
|-------|--------|-------|
| Cluster Health | ✅ All nodes running | 1 TiDB + 1 PD + 4 TiKV |
| Schema Deployed | ✅ Tables created | vector_native_test, memory_nodes, etc. |
| Connection Test | ✅ root@% / tidb#123 | Full access confirmed |
| vec_cosine_distance() Function | ✅ **VERIFIED WORKING** | Native SQL vector search available! |
| Vector Storage (VECTOR(1024)) | ✅ Supported | CAST JSON to VECTOR conversion works |

**Recommended**: Ready for production use — all schema validated, SQL vector search verified.

---

## 📋 TiFlash Replica Configuration Guide (Official Documentation)

### Configure Per-Table Replicas

```sql
-- Create TiFlash replica for specific table
ALTER TABLE table_name SET TIFLASH REPLICA count;

-- Example: Set to 1 replica (single-node environment)
ALTER TABLE memory_nodes SET TIFLASH REPLICA 1;
```

### Batch Configure Database-Wide Replicas

```sql
-- Create TiFlash replicas for all tables in database
ALTER DATABASE db_name SET TIFLASH REPLICA count;

-- Example
ALTER DATABASE memory_system SET TIFLASH REPLICA 1;
```

### Monitor Sync Progress

```sql
-- Check sync status for specific table
SELECT * FROM information_schema.tiflash_replica 
WHERE TABLE_SCHEMA = 'memory_system' AND TABLE_NAME = 'memory_nodes';

-- Check sync status for entire database
SELECT * FROM information_schema.tiflash_replica 
WHERE TABLE_SCHEMA = 'memory_system';
```

### Find Tables Without TiFlash Configuration

```sql
-- Find tables that have not been configured with TiFlash Replica yet
SELECT TABLE_NAME FROM information_schema.tables 
WHERE TABLE_SCHEMA = '<db_name>' 
AND TABLE_NAME NOT IN (
    SELECT TABLE_NAME FROM information_schema.tiflash_replica 
    WHERE TABLE_SCHEMA = '<db_name>'
);
```

### ⚠️ Replica Count Limitations

**Important:** TiFlash REPLICA count **cannot exceed the available TiFlash node count**!

| Environment | TiFlash Nodes | Recommended replica count |
|-------------|---------------|---------------------------|
| Single-node test environment | 1 | `SET TIFLASH REPLICA 1` |
| Multi-node production environment | N | `SET TIFLASH REPLICA N` (≤ nodes) |

### 📚 Official Documentation References

- **[Build TiFlash Replicas](https://pingkai.cn/docs/tidb/stable/create-tiflash-replicas/)** — Complete configuration guide
- [TiDB CE Download Page](https://pingkai.cn/download#tidb-community) — Community Edition download links
- [TiDB Official Documentation](https://pingkai.cn/docs/tidb/stable/) — Complete reference

---

## 📋 Related Documentation & Skills

### Primary Skills
- **memory-tidb8-ce-by-yhw** - Complete TiDB Memory System + SQL Vector Search (with vec_cosine_distance())

### External Documentation
- [TiDB Official Documentation](https://pingkai.cn/docs/tidb/stable/) — Complete reference guide
- [TiDB Vector Search Quick Start (Chinese)](https://pingkai.cn/docs/tidb/stable/quickstart-via-sql/) — SQL vector search tutorial
- [TiDB GitHub Repository](https://github.com/pingcap/tidb) — Source code and issues

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

**Last Updated**: 2026-05-07 v0.1.1 (SQL Vector Search Support)
