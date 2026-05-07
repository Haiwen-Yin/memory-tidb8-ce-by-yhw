---
name: memory-tidb8-ce-by-yhw-changelog
version: 0.1.1
description: "Version History for TiDB CE Memory System Skill"
author: "Haiwen Yin (胖头鱼 🐟 / yhw)"
---

# CHANGELOG - memory-tidb8-ce-by-yhw

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.1.1] - 2026-05-07

### Added
- ✅ **vec_cosine_distance() SQL function support** - Native vector similarity queries in TiDB CE v8.5.6
- ✅ ORDER BY distance sorting capability in database layer
- ✅ CAST JSON to VECTOR conversion for storing embeddings
- ✅ Complete SQL-based vector search examples with verification results
- ✅ Updated documentation with actual test data from production cluster

### Changed
- ⬆️ **Version bump**: v0.1.0 → v0.1.1
- 🔄 Updated SKILL.md with accurate TiDB CE capabilities (removed misleading TiFlash SQL config info)
- 🔄 Simplified documentation structure - removed unnecessary planning documents

### Removed
- ❌ Removed `SKILLS/tiflash-configuration-guide.md` - Not applicable for TiDB CE (SQL TiFlash config unsupported)
- ❌ Removed `RELEASE_NOTES.md` - Created during troubleshooting session, not core content
- ❌ Removed `ROADMAP.md` - Planning document no longer relevant after v0.1.1 updates
- ❌ Removed verification-only scripts (`verify_vec_function.py`, `verify_vector_search.py`)

### Fixed
- 🐛 Corrected understanding of TiDB CE capabilities based on official documentation testing
- 🐛 Updated cluster topology with actual node information (4 TiKV nodes confirmed)

## [v0.1.0] - 2026-05-05

### Added
- Initial release of TiDB Community Edition v8.5+ Memory System skill
- Core table schema definitions (memory_nodes, memory_edges, memories)
- Task management system tables (task_plans, task_steps, snapshots, tool_calls)
- Python embedding provider abstraction layer for multi-model support
- Schema deployment tools and utilities
- Vector similarity calculation functions

### Features
- HTAP (Hybrid Transactional/Analytical Processing) capabilities
- PD Auto Partitioning for automatic load balancing
- MySQL compatibility with existing SQL syntax
- TiCDC Change Data Capture for real-time backup

---

**Maintainer**: Haiwen Yin (胖头鱼 🐟 / yhw)  
**Contact**: https://blog.csdn.net/yhw1809 | https://github.com/Haiwen-Yin
