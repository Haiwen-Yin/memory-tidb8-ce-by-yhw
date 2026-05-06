# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
## [Unreleased]
### Added
- Initial release of TiDB Community Edition v8.5+ Memory System for AI Agents
- Core schema design (memory_nodes, memory_edges, memories tables)
- Task plan system with persistent state management
- Vector similarity calculation framework using Python/NumPy
- Full-text search support (version-dependent on TiDB build)
- HTAP capabilities leveraging TiFlash columnar storage
- GitHub repository structure with CI/CD pipeline configuration
- CONTRIBUTING.md guidelines for contributors
- .gitignore file excluding common development artifacts

### Architecture
- Property Graph management via recursive CTEs for relationship navigation
- Vector similarity retrieval through application-layer cosine calculation
- Structured JSON views for API-friendly data consumption
- Memory decomposition tables replacing Oracle AI DB native features

## [0.1.0] - 2026-05-06 (Initial Release)

### Added
- Initial project structure and documentation
- Complete schema design with all core tables
- Architecture diagram and implementation patterns
- Python cosine similarity calculator for vector operations
- Graph traversal SQL templates using WITH RECURSIVE CTEs
- JSON view definitions for API consumption
- Indexing strategy recommendations
- Deployment checklist with verification steps

### Notes
- This version represents initial architectural exploration and design validation
- Not recommended for production use without thorough testing
- All DDL statements require validation on actual TiDB deployment
- Vector search performance needs benchmarking
- Graph traversal scalability under heavy load untested
