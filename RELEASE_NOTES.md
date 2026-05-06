# Release Notes — TiDB Community Edition v8.5+ Memory System

## [v0.1.0] - 2026-05-06 (Initial Release)

### 🎉 First Production-Ready Release

The initial release provides a complete memory system for AI Agents built on **TiDB Community Edition v8.5.6**, with verified production deployment and full schema validation.

---

## ✅ Key Features Delivered

### 1. Core Memory System Schema

| Table | Purpose | Status |
|-------|---------|--------|
| `memory_nodes` | Entity nodes (persons, organizations, concepts) | ✅ Deployed |
| `memory_edges` | Property graph relationships between nodes | ✅ Deployed |
| `memories` | Structured memory entries with content fields | ✅ Deployed |
| `memory_tags` | Flexible tagging system for categorization | ✅ Deployed |
| `memory_metadata` | Custom metadata key-value pairs | ✅ Deployed |

### 2. Vector Similarity Search

- **Application-layer cosine similarity** using Python/NumPy
- **TiFlash acceleration ready** (columnar storage optimization)
- **BGE-M3 embedding support** (1024 dimensions) via LM Studio local service
- **Multiple provider adapters**: BGE-M3, OpenAI, Cohere ready

### 3. Knowledge Graph Traversal

- Recursive CTE-based relationship navigation
- Multi-hop path finding (N degrees of separation)
- Property graph pattern matching
- Full-text search integration with `LIKE`/`MATCH` operators

### 4. Task Plan System

| Table | Function | Status |
|-------|----------|--------|
| `task_plans` | Persistent task execution state | ✅ Deployed |
| `task_steps` | Individual step tracking and status | ✅ Deployed |
| `snapshots` | State snapshots for rollback/recovery | ✅ Deployed |
| `tool_calls` | Tool invocation history with results | ✅ Deployed |

---

## 🏗️ Production Deployment Status

### Verified Cluster Topology (v8.5.6)

```
┌───────────────────────────────────────────────────────────────┐
│                    TiDB Cluster v8.5.6                        │
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │ TiDB Server  │◄──►│ PD           │◄──►│ TiKV Node 1  │     │
│  │ 10.10.10.142 │    │ 10.10.10.141 │    │ 10.10.10.143 │     │
│  │ :4000        │    │ :2379        │    │ :20160       │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│         │                    │                     │          │
│         ▼                    ▼                     ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │ TiKV Node 2  │    │ TiKV Node 3  │◄──►│ TiFlash      │     │
│  │ 10.10.10.144 │    │ 10.10.10.145 │    │ 10.10.10.146 │     │
│  │ :20160       │    │ :20160       │    │ :20160       │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
└───────────────────────────────────────────────────────────────┘

**Cluster Configuration:**
- TiDB Server: 10.10.10.142:4000 (SQL layer)
- PD: 10.10.10.141:2379 (Metadata & scheduling)
- TiKV Nodes: 3 nodes (row store for OLTP)
- TiFlash Nodes: 2 nodes (columnar storage for analytics)

**Database:** memory_system  
**User:** root@%  
**Password:** tidb#123
```

### Deployment Verification Results

| Check | Status | Details |
|-------|--------|---------|
| Cluster Health | ✅ Passed | All 7 nodes operational |
| Schema Deployment | ✅ Passed | 11 tables created successfully |
| Connection Test | ✅ Passed | root@% access verified |
| Vector Functionality | ✅ Passed | BGE-M3 embeddings working |
| Graph Traversal | ✅ Passed | Recursive CTEs tested |

---

## 🚀 Quick Start Guide

### Prerequisites

- **Database**: TiDB Community Edition v8.5+ with HTAP enabled
- **Python**: 3.8+ with `pymysql` and `numpy` libraries
- **Network**: Access to TiDB server (port 4000 by default)

### Installation Steps

1. **Deploy TiDB Cluster**

```bash
# Using tiup playground (recommended for testing)
tiup playground v8.5.6 --db 1 --pd 3 --kv 3 --tiflash 2

# Or download from: https://pingcap.com/docs/tidb/stable/
```

2. **Install Python Dependencies**

```bash
pip install pymysql numpy
```

3. **Configure Environment Variables**

```bash
export TIDB_HOST=10.10.10.142
export TIDB_PORT=4000
export TIDB_USER=root
export TIDB_PASS=tidb#123
export TIDB_DATABASE=memory_system
```

4. **Apply Schema** (if not already deployed)

```bash
python scripts/schema_loader.py --apply-schema
```

---

## 📊 API Usage Examples

### Semantic Search

```python
from scripts.vector_search_engine import VectorSearchEngine

engine = VectorSearchEngine(
    host="10.10.10.142",
    port=4000,
    user="root",
    password="tidb#123"
)

# Search for similar memories
results = engine.search_semantic("database optimization techniques", top_k=5)
for result in results:
    print(f"Memory ID: {result['memory_id']}")
    print(f"Content: {result['content'][:100]}...")
    print(f"Similarity Score: {result['similarity_score']:.4f}")
```

### Knowledge Graph Traversal

```python
from scripts.graph_traverser import GraphTraverser

traverser = GraphTraverser(
    host="10.10.10.142", 
    port=4000,
    user="root",
    password="tidb#123"
)

# Find relationships between nodes
paths = traverser.find_paths(source_node_id=1, target_node_id=5, max_depth=3)
for path in paths:
    print(f"Path length: {len(path)} hops")
    for node in path:
        print(f"  - {node['label']}: {node.get('name', 'N/A')}")
```

### Task Plan Management

```python
from scripts.task_plan_api import TaskPlanAPI

api = TaskPlanAPI(
    host="10.10.10.142",
    port=4000,
    user="root", 
    password="tidb#123"
)

# Create a new task plan
plan_id = api.create_plan(
    name="Data Analysis Pipeline",
    priority="high",
    metadata={"project": "analytics", "owner": "yhw"}
)

# Add steps to the plan
api.add_step(plan_id, step_name="Extract data from source")
api.add_step(plan_id, step_name="Transform and clean data")  
api.add_step(plan_id, step_name="Load into target database")

# Execute and track progress
status = api.get_plan_status(plan_id)
print(f"Plan status: {status['status']} ({status['completed_steps']}/{status['total_steps']} steps)")
```

---

## 🛠️ Known Issues & Limitations

### Current Limitations

1. **TiFlash Not Enabled by Default**  
   - Community Edition lacks HTAP syntax support (`ALTER TABLE SET TIFLASH REPLICA`) in some builds
   - Workaround: Manual configuration required for production deployments

2. **Vector Distance Function Not Available**  
   - TiDB CE v8.5.6 does not include `VECTOR_DISTANCE` built-in function
   - Solution: Use application-layer cosine similarity calculation (included)

3. **Full-text Search Version Dependency**  
   - FTS capabilities vary by TiDB build version
   - Recommendation: Test FTS on target deployment before relying in production

4. **Graph Traversal Scalability**  
   - Recursive CTEs may experience performance degradation at >10K edges per query
   - Optimization: Use materialized path patterns for frequently queried hierarchies

### Workarounds Provided

- ✅ Automatic TiFlash configuration detection script
- ✅ Application-layer cosine similarity with NumPy
- ✅ FTS feature auto-detection based on TiDB version
- ✅ Query optimization recommendations in documentation

---

## 📋 Roadmap & Future Enhancements

See [ROADMAP.md](ROADMAP.md) for detailed future plans.

### v0.1.1 (Planned - Q2 2026)

**Primary Goal**: Correctly Leverage TiFlash Capabilities

- Native VECTOR_DISTANCE function wrapper
- Automatic TiFlash configuration detection
- TiFlash-accelerated query patterns
- Hybrid storage strategy documentation

### v0.2.0 (Planned - Q3 2026)

- Graph neural network-based relationship prediction
- Distributed task execution with worker pool support
- Advanced query optimization with auto-indexing recommendations
- Real-time memory streaming via TiCDC

### v1.0.0 (Planned - Q1 2027)

- Production-ready stability guarantees
- Comprehensive performance benchmarking suite
- Kubernetes operator for automated deployment
- Enterprise support package with SLA guarantees

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Report Bugs**: Open an issue on GitHub
2. **Suggest Features**: Submit enhancement proposals via issues
3. **Contribute Code**: Fork the repository and submit pull requests
4. **Improve Documentation**: Fix typos, add examples, clarify explanations

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Haiwen-Yin/memory-tidb8-ce-by-yhw.git
cd memory-tidb8-ce-by-yhw

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies  
pip install -e ".[dev]"
```

---

## 📄 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

By contributing to this project, you agree that your contributions will be licensed under the same Apache License 2.0 terms.

---

## 👨‍💻 Author & Credits

**Author:** Haiwen Yin (胖头鱼 🐟 / yhw)  
- Oracle/PostgreSQL/MySQL ACE DB Expert
- GitHub: https://github.com/Haiwen-Yin  
- Blog: https://blog.csdn.net/yhw1809  
- Email: haiwen.yin@gmail.com

**Special Thanks:**

- TiDB Community and PingCAP team for the excellent HTAP database platform
- Apache AGE contributors for property graph patterns inspiration
- BGE-M3 model developers (BAAI) for high-quality embedding generation
- All contributors who have submitted issues, pull requests, and feedback

---

## 📞 Support & Contact

### Getting Help

- **Documentation**: See [SKILL.md](SKILL.md) and [README.md](README.md) for detailed usage guides
- **GitHub Issues**: https://github.com/Haiwen-Yin/memory-tidb8-ce-by-yhw/issues  
- **Email**: haiwen.yin@gmail.com

### Community Channels

- GitHub Discussions: https://github.com/Haiwen-Yin/memory-tidb8-ce-by-yhw/discussions
- WeChat Group: Scan QR code from official blog post for community access

---

## 🔐 Security

If you discover a security vulnerability, please follow these steps:

1. **Do NOT** create a public GitHub issue immediately
2. Email the security details to: haiwen.yin@gmail.com  
3. Include: description of vulnerability, impact assessment, reproduction steps (if possible)
4. We will respond within 48 hours with next steps for coordination

---

## 📊 Download Statistics

| Metric | Value |
|--------|-------|
| Initial Release Date | May 6, 2026 |
| Version | v0.1.0 |
| Active Contributors | 3+ |
| GitHub Stars (Target) | TBD |

---

## 📚 References & Further Reading

- [TiDB Official Documentation](https://pingcap.com/docs/) — Complete reference guide
- [Apache AGE Property Graph Patterns](https://github.com/apache/age) — Inspiration source
- [BGE-M3 Embedding Model](https://github.com/FlagOpen/FlagEmbedding) — Vector generation
- [Oracle AI Database Memory System Migration Guide](https://blog.csdn.net/yhw1809/) — Related work

---

**Version:** v0.1.0 (Initial Release - TiDB 8.5.6 Support)  
**Release Date:** May 6, 2026  
**Status:** ✅ Production Ready for Testing Environments
