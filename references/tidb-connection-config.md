# TiDB Connection Configuration & Knowledge Base Deployment

**Author**: Haiwen Yin (胖头鱼 🐟 / yhw)  
**Last Updated**: 2026-05-11 v1.0.0

---

## 🌐 TiDB Server Configuration

### Production Environment

- **Server IP**: 10.10.10.142 (NOT 10.10.10.132 - that was OceanBase CE)
- **MySQL Protocol Port**: 4000
- **User**: root
- **Password**: tidb#123
- **Database**: memory
- **TiDB Version**: 8.0.11-TiDB-v8.5.6

### Connection String

```bash
mysql -h10.10.10.142 -P4000 -uroot -ptidb#123 -D memory
```

### Python Connection

```python
import pymysql

conn = pymysql.connect(
    host='10.10.10.142',
    port=4000,
    user='root',
    password='tidb#123',
    database='memory',
    charset='utf8mb4'
)
```

---

## 📋 Knowledge Base Schema Deployment (v1.0.0)

### Schema File Location

```
/root/.hermes/skills/memory-tidb8-ce-by-yhw/scripts/knowledge_base_schema_tidb.sql
```

### Deployment Steps

1. **Create Database**
```bash
mysql -h10.10.10.142 -P4000 -uroot -ptidb#123 -e "CREATE DATABASE IF NOT EXISTS memory;"
```

2. **Deploy Schema**
```bash
mysql -h10.10.10.142 -P4000 -uroot -ptidb#123 -D memory < scripts/knowledge_base_schema_tidb.sql
```

3. **Verify Deployment**
```bash
# Check tables count (should be 7)
mysql -h10.10.10.142 -P4000 -uroot -ptidb#123 -D memory -e "
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema='memory' AND table_name LIKE 'knowledge%';
"

# Check views count (should be 4)
mysql -h10.10.10.142 -P4000 -uroot -ptidb#123 -D memory -e "
SELECT COUNT(*) FROM information_schema.views 
WHERE table_schema='memory';
"
```

### Schema Tables (7 Core Tables)

1. **knowledge_concepts** - Knowledge concepts main table
2. **knowledge_graph** - Knowledge relationships table
3. **knowledge_tags** - Tag management table
4. **knowledge_versions** - Version control table
5. **knowledge_validation** - Validation workflow table
6. **knowledge_citations** - Citation tracking table
7. **knowledge_audit_log** - Audit trail table

### Views (4 Analytical Views)

1. **knowledge_graph_names_v** - Relations with concept names
2. **knowledge_concepts_summary_v** - Concept summary with edge counts
3. **knowledge_graph_metrics_v** - Graph analytics by relationship type
4. **knowledge_concepts_with_graph_v** - Full concept + graph view

---

## 🐍 Python API Usage

### API File Location

```
/root/.hermes/skills/memory-tidb8-ce-by-yhw/scripts/knowledge_base_api_tidb.py
```

### Quick Start Example

```python
import sys
sys.path.insert(0, '/root/.hermes/skills/memory-tidb8-ce-by-yhw/scripts')
from knowledge_base_api_tidb import KnowledgeBaseAPI

# Initialize API
kb = KnowledgeBaseAPI(
    host='10.10.10.142',
    port=4000,
    user='root',
    password='tidb#123',
    database='memory'
)

# Create a knowledge concept
concept = kb.create_concept(
    concept_name="TiDB CE 8.5.6",
    concept_type="FACT",
    description="TiDB Community Edition v8.5.6 with native vector search",
    category="database",
    confidence=0.95,
    tags=["tidb", "vector", "database"]
)

# Text search
results = kb.search_by_text(keyword="TiDB", limit=10)

# Get statistics
stats = kb.get_statistics()
print(f"Total concepts: {stats['total_concepts']}")
print(f"Total relationships: {stats['total_relationships']}")
```

### API Functions (8 Core Functions)

| Function | Description | Returns |
|----------|-------------|----------|
| `create_concept()` | Create new knowledge concept | Dict with concept_id |
| `update_concept()` | Update existing concept | Dict with concept_id |
| `delete_concept()` | Delete concept (cascade) | Dict with concept_id |
| `create_relationship()` | Create knowledge graph relation | Dict with relationship_id |
| `search_by_text()` | Keyword search in concepts | List of matching concepts |
| `search_similar_concepts()` | Semantic similarity search | List with similarity scores |
| `get_concept_with_graph()` | Get concept + relationships | Dict with graph data |
| `get_statistics()` | System-wide statistics | Dict with counts |

---

## ⚠️ Common Pitfalls

### 1. Incorrect Server IP

**Problem**: Using 10.10.10.132 (OceanBase CE) instead of 10.10.10.142 (TiDB)

**Symptoms**:
```
ERROR 2003 (HY000): Can't connect to MySQL server on '10.10.10.132:4000'
```

**Solution**: Always use 10.10.10.142 for TiDB connections

### 2. Wrong Password

**Problem**: Using OceanBase password (`OceanBase#123`) instead of TiDB password

**Symptoms**:
```
ERROR 1045 (28000): Access denied for user 'root'@'10.10.10.135'
```

**Solution**: Always use `tidb#123` for TiDB root user

### 3. Foreign Key Constraint on Delete

**Problem**: Deleting concept fails due to audit_log FK constraint

**Root Cause**: Audit log references concept_id; deleting concept first violates FK

**Solution**: Insert audit log record BEFORE deleting concept (fixed in v1.0.0)

```python
# ✅ CORRECT ORDER
cursor.execute("INSERT INTO knowledge_audit_log ...")  # Log first
cursor.execute("DELETE FROM knowledge_concepts ...")  # Then delete

# ❌ WRONG ORDER (fails)
cursor.execute("DELETE FROM knowledge_concepts ...")  # Delete first
cursor.execute("INSERT INTO knowledge_audit_log ...")  # Log after (fails)
```

### 4. Embedding API Dependency

**Problem**: Semantic search fails if embedding API unavailable

**Symptoms**: Warning message "Failed to generate embedding", empty results

**Impact**: Text search still works; semantic search returns empty list

**Solution**: Handle exception gracefully, don't fail entire operation

---

## ✅ v1.0.0 Test Results (100% Pass)

| Test | Status | Notes |
|-------|--------|-------|
| Database Connection | ✅ Pass | 10.10.10.142:4000 |
| Create Knowledge Concepts | ✅ Pass | 4 concepts with tags + embeddings |
| Update Knowledge Concepts | ✅ Pass | Description + confidence updated |
| Create Knowledge Relationships | ✅ Pass | 3 relations created |
| Text Search | ✅ Pass | 4 results found |
| Semantic Search | ✅ Pass | 2 similar concepts found |
| Get Concept with Graph | ✅ Pass | Graph traversal working |
| Get Statistics | ✅ Pass | Stats working |
| Delete Knowledge Concepts | ✅ Pass | Cascade delete working |

---

## 📦 Test Suite Location

```
/tmp/test_tidb_v1.0.0_complete.py
```

### Running Tests

```bash
python3 /tmp/test_tidb_v1.0.0_complete.py
```

---

## 🔄 Version Comparison

| Feature | v0.1.2 | v1.0.0 |
|----------|--------|---------|
| Knowledge Base System | ❌ | ✅ |
| Knowledge Concepts Table | ❌ | ✅ |
| Knowledge Graph Table | ❌ | ✅ |
| Version Control | ❌ | ✅ |
| Validation Workflow | ❌ | ✅ |
| Audit Trail | ❌ | ✅ |
| Citation Tracking | ❌ | ✅ |
| Text Search | ❌ | ✅ |
| Semantic Search | ❌ | ✅ |
| Multi-Agent Architecture | ✅ | ✅ |
| Test Suite Coverage | Basic | Complete (9/9 tests) |

---

**Last Updated**: 2026-05-11 v1.0.0  
**Author**: Haiwen Yin (胖头鱼 🐟 / yhw)
