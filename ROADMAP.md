# Roadmap — TiDB Community Edition v8.5+ Memory System

**Version:** v0.1.0 (Initial Release)  
**Last Updated:** May 6, 2026  
**Author:** Haiwen Yin (胖头鱼 🐟 / yhw)  

---

## Current Status: v0.1.0 (Initial Release - TiDB 8.5.6 Support)

✅ **Released:** May 6, 2026  
✅ **Features:** Core schema, vector similarity search, knowledge graph traversal  
✅ **Limitation:** Application-layer cosine similarity only (no native VECTOR_DISTANCE)  

---

## Planned Features: v0.1.1 (TiFlash Integration — Q2 2026)

### Primary Goal: Correctly Leverage TiFlash Capabilities

The v0.1.1 release will focus on enabling proper HTAP workflows with TiFlash columnar acceleration for vector similarity queries.

#### Key Deliverables

**1. Native VECTOR_DISTANCE Function Wrapper**  
- Detect TiDB build support for `VECTOR_DISTANCE()` built-in function
- Automatic fallback to application-layer cosine similarity when unavailable
- Optimized query generation using native functions when supported

```sql
-- v0.1.1 will detect and use this automatically when available:
SELECT 
    memory_id, content, embedding,
    VECTOR_DISTANCE(embedding, CAST(? AS VECTOR(1024)), COSINE) as similarity_score
FROM memories_vectors
ORDER BY similarity_score DESC
LIMIT 5;
```

**2. Automatic TiFlash Configuration Detection**  
- Runtime detection of TiFlash replica status for all memory tables
- Auto-generate `ALTER TABLE ... SET TIFLASH REPLICA` commands when supported
- Provide manual configuration guide for Community Edition limitations

```python
# v0.1.1 will include:
from scripts.tiflash_config import detect_and_configure_tiflash

status = detect_and_configure_tiflash(
    host="127.0.0.1",
    port=4000,
    user="root@memcluster",
    password="your_password"
)

print(f"TiFlash status: {status['enabled']}")
print(f"Replica count: {status['replicas']}")
```

**3. TiFlash-Accelerated Query Patterns**  
- Pre-optimized SQL templates for columnar storage access patterns
- Automatic query rewriting to leverage TiFlash when available
- Performance benchmarking suite to measure acceleration benefits

```sql
-- Optimized pattern for v0.1.1:
SELECT /*+ READ_FROM_STORAGE(TIFLASH[memory_nodes]) */
    n.node_id, n.label, n.properties
FROM memory_nodes n
WHERE n.embedding_vector > CAST(? AS VECTOR(1024))
ORDER BY cosine_similarity(n.embedding_vector, ?) DESC;
```

**4. Hybrid Storage Strategy Documentation**  
- Guidelines for when to use row-store vs columnar storage
- Mixed workload optimization recommendations
- TiFlash replica placement strategies for different data volumes

#### Expected Performance Improvements

| Metric | v0.1.0 (Row Store) | v0.1.1 (TiFlash Enabled) | Improvement |
|--------|-------------------|-------------------------|-------------|
| Vector Search Latency (1K vectors) | ~200ms | ~50ms | 4x faster |
| Vector Search Latency (10K vectors) | ~1.5s | ~300ms | 5x faster |
| Graph Traversal (5 hops, 100 nodes) | ~800ms | ~200ms | 4x faster |
| Batch Memory Writes (100 ops) | ~50ms | ~70ms | Slight overhead expected |

*Note: Performance gains depend on data volume and cluster configuration.*

#### Technical Requirements for v0.1.1

- **TiDB Version:** v8.5.6+ with TiFlash component enabled
- **Cluster Topology:** Minimum 3-node setup (PD + TiKV + TiFlash)
- **Storage Engine:** Row store for OLTP, Columnar store for OLAP queries
- **Network Bandwidth:** ≥1Gbps recommended for TiFlash data streaming

#### Implementation Timeline

| Week | Task | Owner | Status |
|------|------|-------|--------|
| Week 1 | VECTOR_DISTANCE function detection logic | yhw | Planned |
| Week 2 | Automatic TiFlash configuration wizard | yhw | Planned |
| Week 3 | Query optimizer integration | yhw | Planned |
| Week 4 | Performance benchmarking & documentation | yhw | Planned |

---

## Future Releases: v0.2.0 (Q3 2026)

### Planned Enhancements

- **Graph Neural Network Integration:** Relationship prediction using GNN embeddings
- **Distributed Task Execution:** Worker pool support for parallel task execution
- **Advanced Query Optimization:** Auto-indexing recommendations based on query patterns
- **Real-time Memory Streaming:** TiCDC integration for live memory updates

### Technical Challenges

1. **GNN Embedding Generation:** Integration with external ML frameworks (PyTorch/TensorFlow)
2. **Distributed Coordination:** Ensuring consistency across multiple task workers
3. **Query Pattern Analysis:** Machine learning-based index recommendations

---

## Future Releases: v0.3.0 (Q4 2026)

### Planned Enhancements

- **Multi-Model Adapter:** Dynamic embedding model selection based on use case
- **Advanced Analytics Dashboard:** Web-based monitoring and query analysis
- **Kubernetes Operator:** Automated deployment and scaling for cloud-native environments
- **Enterprise Support Package:** SLA guarantees and priority support channel

### Technical Challenges

1. **Model Version Management:** Handling multiple embedding models simultaneously
2. **Web UI Development:** Real-time query visualization and performance metrics
3. **Cloud-Native Integration:** Kubernetes custom resources and operators

---

## Future Releases: v1.0.0 (Q1 2027)

### Production-Ready Features

- **Stability Guarantees:** Comprehensive testing across diverse deployment scenarios
- **Performance Benchmarking Suite:** Industry-standard benchmarks for memory systems
- **High Availability Architecture:** Automatic failover and disaster recovery mechanisms
- **Enterprise Feature Set:** Role-based access control, audit logging, encryption at rest

### Technical Challenges

1. **HA Configuration:** Multi-region replication and automatic failover testing
2. **Security Hardening:** Compliance with SOC2/ISO27001 requirements
3. **Scalability Testing:** Performance validation at 1M+ memory entries scale

---

## Community Contributions Welcome!

We welcome contributions to all roadmap items. If you're interested in contributing:

- **v0.1.1 TiFlash Integration:** Contact yhw for implementation details
- **GNN Support:** Reach out if you have ML framework integration experience
- **Web Dashboard:** UI/UX designers and frontend developers encouraged to contribute

### How to Contribute

1. Review [CONTRIBUTING.md](CONTRIBUTING.md) guidelines
2. Comment on relevant GitHub issues
3. Submit pull requests with test coverage

---

## Notes & Disclaimers

- **Timeline Flexibility:** All dates are estimates and may change based on development progress
- **Feature Scope:** Features listed above may be adjusted based on community feedback and technical feasibility
- **Community Edition Limitations:** Some features (e.g., HTAP syntax) may require workarounds in TiDB Community Edition

---

**Last Updated:** May 6, 2026  
**Next Review Date:** June 6, 2026  
**Maintainer:** Haiwen Yin (胖头鱼 🐟 / yhw) <haiwen.yin@gmail.com>
