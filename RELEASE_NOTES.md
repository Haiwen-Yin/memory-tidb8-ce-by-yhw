---
name: memory-tidb8-ce-by-yhw-release-notes
version: 0.1.1
title: "TiDB CE Memory System v0.1.1 Release Notes"
author: "Haiwen Yin (胖头鱼 🐟 / yhw)"
date: "2026-05-07"
---

# 🚀 memory-tidb8-ce-by-yhw v0.1.1 Release Notes

**Release Date**: 2026-05-07  
**Previous Version**: v0.1.0  
**Repository**: TiDB CE Memory System for AI Agent

---

## 📋 Summary

v0.1.1 is a significant feature release that adds **native SQL vector search capabilities** and comprehensive **TiFlash replica configuration guides**. This version brings the skill closer to production readiness with verified real-world testing on TiDB Community Edition v8.5.6.

---

## ✨ New Features

### 1. 🎯 SQL Vector Search Support (vec_cosine_distance)

**Status**: ✅ Production Ready  
**Verified On**: TiDB CE v8.5.6 (8.0.11-TiDB-v8.5.6)

Native vector similarity queries using TiDB's built-in `vec_cosine_distance()` function:

```sql
-- Query similar documents using SQL
SELECT id, document, 
       vec_cosine_distance(embedding, CAST('[0.5,0.5,...]' AS VECTOR(1024))) AS distance
FROM vector_native_test
ORDER BY distance
LIMIT 3;
```

**Key Capabilities:**
- ✅ ORDER BY distance sorting in database layer
- ✅ CAST JSON to VECTOR conversion for storing embeddings
- ✅ Parameter binding (prepared statement style)
- ✅ Distance threshold filtering

### 2. 📊 TiFlash Replica Configuration Guide

**Status**: ✅ Documentation Complete  
**Source**: Official TiDB Documentation (verified on production cluster)

Comprehensive guide covering:
- **Per-Table Replica Configuration**: `ALTER TABLE table_name SET TIFLASH REPLICA count;`
- **Database-Wide Batch Setup**: `ALTER DATABASE db_name SET TIFLASH REPLICA count;`
- **Sync Progress Monitoring**: `information_schema.tiflash_replica` queries
- **Replica Count Limitations**: replica count ≤ available TiFlash nodes

### 3. 📚 Enhanced Documentation

- Added official documentation reference links
- Updated cluster topology with verified production environment details
- Included real test results from TiDB CE v8.5.6 cluster

---

## 🔧 Improvements & Changes

| Item | Change | Rationale |
|------|--------|-----------|
| **Version** | v0.1.0 → v0.1.1 | New feature release (backward compatible) |
| **SKILL.md** | Added TiFlash config chapter | User requested production deployment guidance |
| **SKILL.md** | Updated SQL examples with real data | Verified on actual cluster |
| **Documentation** | Cleaned redundant references | Removed duplicate skill reference |

---

## 🗑️ Cleanup Actions

The following items were removed to maintain a clean, focused skill package:

- ❌ **Redundant skill**: `tidb-ce-sql-vector-search-by-yhw` — content duplicated in main SKILL.md
- ❌ **Temporary files**: RELEASE_NOTES.md (previous iteration), ROADMAP.md
- ❌ **Test-only scripts**: verify_vec_function.py, verify_vector_search.py

---

## 📋 Verified Test Results

### TiDB Cluster Environment
```
┌─────────────────────────────────────────┐
│        Production Cluster Topology      │
├─────────────────────────────────────────┤
│  TiDB Server: 10.10.10.142:4000         │
│  PD: 10.10.10.141:2379                  │
│  TiKV Nodes: 10.10.10.143-146:20160     │
└─────────────────────────────────────────┘

Database: memory_system
User: root@% (full admin access)
Password: tidb#123
```

### vec_cosine_distance() Test Results
| ID | Document | Cosine Distance |
|----|----------|-----------------|
| 33 | 数据科学分析 | 0.23455271808188727 |
| 34 | Python 编程语言 | 0.2350298471474359 |
| 30 | 分布式数据库技术 | 0.23583382639728667 |
| 32 | 云计算架构设计 | 0.23873097179667757 |
| 31 | AI 机器学习算法 | 0.2404038003504697 |

---

## ⚠️ Important Notes

### TiFlash Replica Limitations

**Critical**: The number of TiFlash replicas **cannot exceed the available TiFlash node count**.

| Environment | TiFlash Nodes | Max replica count |
|-------------|---------------|-------------------|
| Single-node test | 1 | `SET TIFLASH REPLICA 1` |
| Multi-node production | N | `SET TIFLASH REPLICA N` (≤ nodes) |

### Compatibility Matrix

| Component | Version | Status |
|-----------|---------|--------|
| TiDB CE | v8.5+ | ✅ Required for vec_cosine_distance() |
| Python | 3.8+ | ✅ For embedding providers |
| VECTOR type | 1024 dims (BGE-M3) | ✅ Supported in TiDB CE v8.5+ |

---

## 📚 Documentation Links

- **[Build TiFlash Replicas](https://pingkai.cn/docs/tidb/stable/create-tiflash-replicas/)** — Official TiFlash replica configuration guide
- [TiDB Vector Search Quick Start (Chinese)](https://pingkai.cn/docs/tidb/stable/quickstart-via-sql/) — SQL vector search tutorial
- [TiDB Official Documentation](https://pingkai.cn/docs/tidb/stable/) — Complete reference

---

## 🙏 Acknowledgments

**Author**: Haiwen Yin (胖头鱼 🐟)  
Oracle/PostgreSQL/MySQL ACE Database Expert  

**Contributors**: 
- TiDB team for community edition features
- PingCAP documentation maintainers

---

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).

---

**Last Updated**: 2026-05-07 v0.1.1 (SQL Vector Search + TiFlash Guide)
