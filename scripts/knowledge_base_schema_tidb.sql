-- TiDB Knowledge Base Schema v1.0.0
-- Compatible with: oracle-memory-by-yhw v1.0.0
-- Author: yhw (胖头鱼 🐟)
-- Database: TiDB Community Edition v8.5+

-- ============================================
-- 1. KNOWLEDGE_CONCEPTS - Knowledge Concepts Table
-- ============================================
CREATE TABLE IF NOT EXISTS knowledge_concepts (
    CONCEPT_ID BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Knowledge concept unique identifier',
    CONCEPT_NAME VARCHAR(255) NOT NULL COMMENT 'Concept name/title',
    CONCEPT_TYPE VARCHAR(50) NOT NULL COMMENT 'Type: FACT/RULE/PATTERN/EXPERIENCE/PRINCIPLE',
    CATEGORY VARCHAR(100) COMMENT 'Concept category for grouping',
    TITLE VARCHAR(255) COMMENT 'Alternative title',
    DESCRIPTION TEXT COMMENT 'Detailed concept description',
    CONTENT TEXT COMMENT 'Full concept content',
    SOURCE_TYPE VARCHAR(50) COMMENT 'Source: MANUAL/EXPERIENCE_DISTILLATION/IMPORTED',
    SOURCE_MEMORY_IDS TEXT COMMENT 'Source memory node IDs (JSON array)',
    CONFIDENCE DECIMAL(3,2) DEFAULT 0.80 COMMENT 'Confidence score (0.00-1.00)',
    VALIDATION_STATUS VARCHAR(30) DEFAULT 'PENDING' COMMENT 'PENDING/VALIDATED/REJECTED',
    EMBEDDING TEXT COMMENT 'Vector embedding (JSON array)',
    TAGS TEXT COMMENT 'Tags (JSON array)',
    METADATA TEXT COMMENT 'Additional metadata (JSON)',
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update',
    VALIDATED_AT TIMESTAMP NULL COMMENT 'Validation completion',
    DEPRECATED_AT TIMESTAMP NULL COMMENT 'Deprecation timestamp',
    VERSION INT DEFAULT 1 COMMENT 'Version number',
    IS_CURRENT VARCHAR(1) DEFAULT 'Y' COMMENT 'Y/N: Is this the current version?',
    
    INDEX idx_conceptcept_name (CONCEPT_NAME),
    INDEX idx_concept_type (CONCEPT_TYPE),
    INDEX idx_category (CATEGORY),
    INDEX idx_validation_status (VALIDATION_STATUS),
    INDEX idx_confidence (CONFIDENCE),
    INDEX idx_created_at (CREATED_AT),
    INDEX idx_is_current (IS_CURRENT)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 2. KNOWLEDGE_GRAPH - Knowledge Relationship Table
-- ============================================
CREATE TABLE IF NOT EXISTS knowledge_graph (
    RELATIONSHIP_ID BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Relationship unique identifier',
    SOURCE_CONCEPT_ID BIGINT NOT NULL COMMENT 'Source concept ID',
    TARGET_CONCEPT_ID BIGINT NOT NULL COMMENT 'Target concept ID',
    RELATIONSHIP_TYPE VARCHAR(50) NOT NULL COMMENT 'Type: IS_A/PART_OF/CAUSES/ENABLES/CONTRADICTS/SUPPORTS',
    RELATIONSHIP_STRENGTH DECIMAL(3,2) DEFAULT 0.90 COMMENT 'Relationship strength (0.00-1.00)',
    PROPERTIES TEXT COMMENT 'Additional properties (JSON)',
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update',
    SOURCE_TYPE VARCHAR(50) COMMENT 'Source: MANUAL/INFERRED/IMPORTED',
    CONFIDENCE DECIMAL(3,2) DEFAULT 0.80 COMMENT 'Confidence score',
    
    INDEX idx_source (SOURCE_CONCEPT_ID),
    INDEX idx_target (TARGET_CONCEPT_ID),
    INDEX idx_relationship_type (RELATIONSHIP_TYPE),
    INDEX idx_strength (RELATIONSHIP_STRENGTH),
    
    FOREIGN KEY (SOURCE_CONCEPT_ID) REFERENCES knowledge_concepts(CONCEPT_ID) ON DELETE CASCADE,
    FOREIGN KEY (TARGET_CONCEPT_ID) REFERENCES knowledge_concepts(CONCEPT_ID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 3. KNOWLEDGE_TAGS - Tag Management Table
-- ============================================
CREATE TABLE IF NOT EXISTS knowledge_tags (
    TAG_ID BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Tag unique identifier',
    CONCEPT_ID BIGINT NOT NULL COMMENT 'Related concept ID',
    TAG_NAME VARCHAR(100) NOT NULL COMMENT 'Tag name',
    TAG_VALUE VARCHAR(255) COMMENT 'Tag value',
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    
    INDEX idx_concept_id (CONCEPT_ID),
    INDEX idx_tag_name (TAG_NAME),
    
    FOREIGN KEY (CONCEPT_ID) REFERENCES knowledge_concepts(CONCEPT_ID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 4. KNOWLEDGE_VERSIONS - Version Control Table
-- ============================================
CREATE TABLE IF NOT EXISTS knowledge_versions (
    VERSION_ID BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Version unique identifier',
    CONCEPT_ID BIGINT NOT NULL COMMENT 'Related concept ID',
    OLD_VERSION INT COMMENT 'Previous version number',
    NEW_VERSION INT COMMENT 'New version number',
    CHANGES TEXT COMMENT 'Change description (JSON)',
    CHANGE_TYPE VARCHAR(30) COMMENT 'CREATE/UPDATE/DELETE/DEPRECATE',
    CHANGED_BY VARCHAR(100) COMMENT 'Who made the change',
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Change timestamp',
    
    INDEX idx_concept_id (CONCEPT_ID),
    INDEX idx_created_at (CREATED_AT),
    
    FOREIGN KEY (CONCEPT_ID) REFERENCES knowledge_concepts(CONCEPT_ID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 5. KNOWLEDGE_VALIDATION - Validation Workflow Table
-- ============================================
CREATE TABLE IF NOT EXISTS knowledge_validation (
    VALIDATION_ID BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Validation unique identifier',
    CONCEPT_ID BIGINT NOT NULL COMMENT 'Related concept ID',
    STATUS VARCHAR(30) DEFAULT 'PENDING' COMMENT 'PENDING/IN_PROGRESS/APPROVED/REJECTED',
    REVIEWER VARCHAR(100) COMMENT 'Reviewer name',
    REVIEW_NOTES TEXT COMMENT 'Review notes',
    REVIEWED_AT TIMESTAMP NULL COMMENT 'Review completion',
    REQUESTED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Request timestamp',
    
    INDEX idx_concept_id (CONCEPT_ID),
    INDEX idx_status (STATUS),
    INDEX idx_requested_at (REQUESTED_AT),
    
    FOREIGN KEY (CONCEPT_ID) REFERENCES knowledge_concepts(CONCEPT_ID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 6. KNOWLEDGE_CITATIONS - Citation Tracking Table
-- ============================================
CREATE TABLE IF NOT EXISTS knowledge_citations (
    CITATION_ID BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Citation unique identifier',
    CONCEPT_ID BIGINT NOT NULL COMMENT 'Citing concept ID',
    CITED_CONCEPT_ID BIGINT NOT NULL COMMENT 'Cited concept ID',
    CITATION_TYPE VARCHAR(50) COMMENT 'SUPPORTS/CONTRADICTS/EXTENDS',
    CONTEXT_TEXT TEXT COMMENT 'Citation context',
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    
    INDEX idx_concept_id (CONCEPT_ID),
    INDEX idx_cited_concept_id (CITED_CONCEPT_ID),
    
    FOREIGN KEY (CONCEPT_ID) REFERENCES knowledge_concepts(CONCEPT_ID) ON DELETE CASCADE,
    FOREIGN KEY (CITED_CONCEPT_ID) REFERENCES knowledge_concepts(CONCEPT_ID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 7. KNOWLEDGE_AUDIT_LOG - Audit Trail Table
-- ============================================
CREATE TABLE IF NOT EXISTS knowledge_audit_log (
    AUDIT_ID BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Audit unique identifier',
    CONCEPT_ID BIGINT COMMENT 'Related concept ID (NULL for system events)',
    OPERATION VARCHAR(50) NOT NULL COMMENT 'Create/Update/Delete/Validate',
    OPERATION_TYPE VARCHAR(50) COMMENT 'CONCEPT/RELATIONSHIP/VALIDATION',
    DETAILS TEXT COMMENT 'Operation details (JSON)',
    PERFORMED_BY VARCHAR(100) COMMENT 'Who performed the operation',
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Operation timestamp',
    
    INDEX idx_concept_id (CONCEPT_ID),
    INDEX idx_operation (OPERATION),
    INDEX idx_created_at (CREATED_AT),
    
    FOREIGN KEY (CONCEPT_ID) REFERENCES knowledge_concepts(CONCEPT_ID) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 8. VIEW: KNOWLEDGE_GRAPH_NAMES_V - Join with Concept Names
-- ============================================
CREATE OR REPLACE VIEW knowledge_graph_names_v AS
SELECT 
    g.RELATIONSHIP_ID,
    g.SOURCE_CONCEPT_ID,
    s.CONCEPT_NAME AS SOURCE_CONCEPT_NAME,
    g.TARGET_CONCEPT_ID,
    t.CONCEPT_NAME AS TARGET_CONCEPT_NAME,
    g.RELATIONSHIP_TYPE,
    g.RELATIONSHIP_STRENGTH,
    g.CONFIDENCE,
    g.CREATED_AT
FROM knowledge_graph g
JOIN knowledge_concepts s ON g.SOURCE_CONCEPT_ID = s.CONCEPT_ID
JOIN knowledge_concepts t ON g.TARGET_CONCEPT_ID = t.CONCEPT_ID;

-- ============================================
-- 9. VIEW: KNOWLEDGE_CONCEPTS_SUMMARY_V - Concept Summary
-- ============================================
CREATE OR REPLACE VIEW knowledge_concepts_summary_v AS
SELECT 
    c.CONCEPT_ID,
    c.CONCEPT_NAME,
    c.CONCEPT_TYPE,
    c.CATEGORY,
    c.VALIDATION_STATUS,
    c.CONFIDENCE,
    c.CREATED_AT,
    c.UPDATED_AT,
    (SELECT COUNT(*) FROM knowledge_graph WHERE SOURCE_CONCEPT_ID = c.CONCEPT_ID) AS outgoing_relationships,
    (SELECT COUNT(*) FROM knowledge_graph WHERE TARGET_CONCEPT_ID = c.CONCEPT_ID) AS incoming_relationships,
    (SELECT COUNT(*) FROM knowledge_tags WHERE CONCEPT_ID = c.CONCEPT_ID) AS tag_count,
    (SELECT COUNT(*) FROM knowledge_versions WHERE CONCEPT_ID = c.CONCEPT_ID) AS version_count
FROM knowledge_concepts c;

-- ============================================
-- 10. VIEW: KNOWLEDGE_GRAPH_METRICS_V - Graph Analytics
-- ============================================
CREATE OR REPLACE VIEW knowledge_graph_metrics_v AS
SELECT 
    RELATIONSHIP_TYPE,
    COUNT(*) AS relationship_count,
    AVG(RELATIONSHIP_STRENGTH) AS avg_strength,
    AVG(CONFIDENCE) AS avg_confidence,
    MIN(CREATED_AT) AS first_created,
    MAX(CREATED_AT) AS last_created
From knowledge_graph
GROUP BY RELATIONSHIP_TYPE;

-- ============================================
-- Schema Deployment Complete
-- ============================================
SELECT 'Knowledge Base Schema v1.0.0 deployed successfully' AS status,
       NOW() AS deployment_time;
