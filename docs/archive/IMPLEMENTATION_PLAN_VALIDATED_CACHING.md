# Implementation Plan: Validated Semantic Caching for PyStreamMCP v0.3

**Date:** 2026-07-17  
**Priority:** P0 (High Impact)  
**Timeline:** 4 weeks  
**Approach:** Leverage StatGuardian's schema validation + drift detection

---

## Executive Summary

Build validated semantic caching layer for PyStreamMCP by:
1. Creating semantic cache (weeks 1-2)
2. Integrating StatGuardian for schema validation (weeks 2-3)
3. Adding intelligent cache validation (weeks 3-4)

**Result:** 50-80% token reduction + production-safe (no silent failures)

---

## Part 1: Architecture Overview

### Three-Layer Architecture

```
┌─────────────────────────────────────────┐
│  Semantic Cache Layer                   │
│  ├─ Cache entries with embeddings       │
│  ├─ Schema hash tracking                │
│  └─ Similarity matching                 │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│  StatGuardian Integration               │
│  ├─ Schema validation (exists?)         │
│  ├─ Drift detection (changed?)          │
│  ├─ Constraint checking (valid?)        │
│  └─ Change history tracking             │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│  Intelligent Validation Checker         │
│  ├─ Validate before returning cache     │
│  ├─ Calculate confidence scores         │
│  ├─ Safe degradation decisions          │
│  └─ Audit trail logging                 │
└─────────────────────────────────────────┘
```

### Integration Points

```
PyStreamMCP Query Pipeline:

Query
  ↓
[NEW] Semantic Cache Layer
  ├─ Create embeddings
  ├─ Search similar past queries
  └─ Get candidate cache entry
  ↓
[NEW] StatGuardian Validation
  ├─ Load cached schema definition
  ├─ Load current schema definition
  ├─ Call StatGuardian.validate_schema()
  ├─ Call StatGuardian.detect_drift()
  └─ Get validation result
  ↓
[NEW] Intelligent Validation Checker
  ├─ Assess change severity
  ├─ Calculate confidence score
  ├─ Make decision (VALID/DEGRADED/INVALID)
  └─ Return with metadata
  ↓
IF VALID: Return cache + metadata ✓
IF DEGRADED: Return cache + warning
IF INVALID: Recompute with fresh schema ✓
```

---

## Part 2: Detailed Component Design

### Component 1: Semantic Cache (Weeks 1-2)

**Files to create:**
- `openanchor/caching/semantic_cache.py` (400 lines)
- `openanchor/caching/cache_entry.py` (200 lines)
- `openanchor/caching/embeddings.py` (300 lines)

**Semantic Cache Class:**

```python
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
import numpy as np

@dataclass
class SemanticCacheEntry:
    """Single cached semantic analysis."""
    entry_id: str
    
    # What was analyzed
    schema_id: str
    schema_definition: Dict[str, Any]
    schema_embedding: np.ndarray  # (1536,) vector
    schema_hash: str  # SHA256(schema_definition)
    
    # Query context
    query_intent: str  # "RETRIEVE", "AGGREGATE", etc.
    query_embedding: np.ndarray  # (1536,) vector
    
    # Cached results
    analysis: Dict[str, Any]  # Schema analysis results
    discovered_sources: List[Dict]  # Discovered tables/columns
    optimization_suggestion: str  # Recommended technique
    
    # Metadata for validation
    cached_at: datetime
    statguardian_schema_version: int
    ttl_seconds: int = 86400  # 24 hours
    
    def is_fresh(self) -> bool:
        """Check if cache entry is still within TTL."""
        age = (datetime.utcnow() - self.cached_at).total_seconds()
        return age < self.ttl_seconds

class SemanticCache:
    """Semantic cache with similarity-based retrieval."""
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        self.embedder = EmbeddingModel(embedding_model)
        self.entries: Dict[str, SemanticCacheEntry] = {}
        self.embeddings_index = None  # For similarity search
    
    def cache_analysis(
        self,
        schema_id: str,
        schema_definition: Dict[str, Any],
        query: Query,
        analysis: Dict[str, Any],
        discovered_sources: List[Dict],
    ) -> SemanticCacheEntry:
        """Cache schema analysis result."""
        
        # Create embeddings
        schema_emb = self.embedder.embed_schema(schema_definition)
        query_emb = self.embedder.embed_query(query)
        
        # Create hash for schema
        schema_hash = hashlib.sha256(
            json.dumps(schema_definition, sort_keys=True).encode()
        ).hexdigest()
        
        # Create cache entry
        entry = SemanticCacheEntry(
            entry_id=str(uuid.uuid4()),
            schema_id=schema_id,
            schema_definition=schema_definition,
            schema_embedding=schema_emb,
            schema_hash=schema_hash,
            query_intent=query.intent.value,
            query_embedding=query_emb,
            analysis=analysis,
            discovered_sources=discovered_sources,
            optimization_suggestion=analysis.get("optimization"),
            cached_at=datetime.utcnow(),
            statguardian_schema_version=0,  # Will be set by validator
        )
        
        # Store
        self.entries[entry.entry_id] = entry
        
        return entry
    
    def find_similar(
        self,
        schema_id: str,
        query: Query,
        threshold: float = 0.85,
    ) -> Optional[SemanticCacheEntry]:
        """Find similar cached analysis."""
        
        query_emb = self.embedder.embed_query(query)
        
        # Find entries for same schema
        candidates = [
            e for e in self.entries.values()
            if e.schema_id == schema_id and e.is_fresh()
        ]
        
        if not candidates:
            return None
        
        # Calculate similarity scores
        similarities = []
        for entry in candidates:
            # Cosine similarity
            sim = np.dot(query_emb, entry.query_embedding) / (
                np.linalg.norm(query_emb) * np.linalg.norm(entry.query_embedding)
            )
            similarities.append((sim, entry))
        
        # Return best match if above threshold
        best_sim, best_entry = max(similarities, key=lambda x: x[0])
        if best_sim >= threshold:
            return best_entry
        
        return None
```

**Embedding Model:**

```python
from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    """Converts schemas/queries to embeddings."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def embed_schema(self, schema_def: Dict[str, Any]) -> np.ndarray:
        """Convert schema to embedding."""
        
        # Extract key schema information
        text_parts = []
        
        if "tables" in schema_def:
            for table in schema_def["tables"]:
                text_parts.append(f"table {table['name']}")
                for col in table.get("columns", []):
                    text_parts.append(f"{col['name']} {col['type']}")
                for rel in table.get("relationships", []):
                    text_parts.append(f"relates to {rel['target_table']}")
        
        schema_text = " ".join(text_parts)
        
        # Embed
        embedding = self.model.encode(schema_text)
        return embedding.astype(np.float32)
    
    def embed_query(self, query: Query) -> np.ndarray:
        """Convert query to embedding."""
        
        text_parts = [
            query.text,
            f"intent {query.intent.value}",
        ]
        
        if query.metadata:
            text_parts.extend(query.metadata.values())
        
        query_text = " ".join(str(p) for p in text_parts)
        
        # Embed
        embedding = self.model.encode(query_text)
        return embedding.astype(np.float32)
```

**Tests (15 tests):**

```python
# tests/test_semantic_cache.py
class TestSemanticCache:
    def test_cache_entry_creation
    def test_cache_entry_freshness
    def test_cache_storage
    def test_find_similar_exact_match
    def test_find_similar_fuzzy_match
    def test_find_similar_below_threshold
    def test_similarity_scoring
    def test_multiple_cache_entries
    def test_cache_ttl_expiration
    def test_embedding_deterministic
    def test_schema_embedding_quality
    def test_query_embedding_quality
    def test_cache_isolation_by_schema
    def test_cache_memory_efficiency
    def test_concurrent_cache_access
```

---

### Component 2: StatGuardian Integration (Weeks 2-3)

**Files to create:**
- `openanchor/validation/statguardian_wrapper.py` (300 lines)
- `openanchor/validation/schema_change_detector.py` (400 lines)

**StatGuardian Wrapper:**

```python
from statguardian.validators.schema import SchemaValidator
from statguardian.stats.drift import DriftEngine
from typing import List, Dict, Any

class StatGuardianSchemaValidator:
    """Wrapper around StatGuardian for schema validation."""
    
    def __init__(self):
        self.validator = SchemaValidator()
        self.drift_engine = DriftEngine()
    
    def validate_schema_structure(
        self,
        current_df,  # Polars DataFrame
        schema_definition: Dict[str, Any],
    ) -> List[str]:
        """
        Validate that schema structure matches.
        Uses StatGuardian.SchemaValidator.
        
        Returns:
            List of violations (empty = valid)
        """
        
        # Convert schema_definition to FieldDef list
        field_defs = self._schema_to_fields(schema_definition)
        
        # Validate
        violations = self.validator.validate(current_df, field_defs)
        
        return [v.message for v in violations]
    
    def detect_schema_drift(
        self,
        reference_df,  # Original schema data
        current_df,     # Current schema data
        drift_rules: List[str],  # e.g., ["avg_change > 0.1"]
    ) -> Dict[str, Any]:
        """
        Detect schema/data drift.
        Uses StatGuardian.DriftEngine.
        
        Returns:
            {
                "drifted_columns": ["col1", "col2"],
                "psi_scores": {"col1": 0.15},
                "ks_stats": {"col1": 0.22},
                "severity": "MEDIUM",
            }
        """
        
        drift_results = self.drift_engine.evaluate(
            current_df,
            reference_df,
            drift_rules,
        )
        
        return {
            "drifted_columns": [
                r.column for r in drift_results if not r.passed
            ],
            "psi_scores": {r.column: r.psi for r in drift_results},
            "ks_stats": {r.column: r.ks_stat for r in drift_results},
            "severity": self._assess_drift_severity(drift_results),
        }
    
    def _schema_to_fields(self, schema_def: Dict) -> List:
        """Convert schema definition to StatGuardian FieldDef."""
        # Implementation converts schema to FieldDef list
        pass
    
    def _assess_drift_severity(self, results) -> str:
        """Assess overall drift severity."""
        # HIGH: Many columns drifted
        # MEDIUM: Some columns drifted
        # LOW: Minor drift
        pass
```

**Schema Change Detector:**

```python
class SchemaChangeDetector:
    """Detects schema changes using StatGuardian."""
    
    def __init__(self, sg_validator: StatGuardianSchemaValidator):
        self.sg = sg_validator
    
    def detect_changes(
        self,
        old_schema: Dict[str, Any],
        current_schema: Dict[str, Any],
    ) -> List[SchemaChange]:
        """
        Detect schema changes between two versions.
        
        Returns:
            List of SchemaChange objects with severity levels
        """
        
        changes = []
        
        # Structural changes (comparing schema definitions)
        changes.extend(self._detect_structural_changes(old_schema, current_schema))
        
        # Semantic changes (using StatGuardian validation)
        changes.extend(self._detect_semantic_changes(old_schema, current_schema))
        
        return changes
    
    def _detect_structural_changes(self, old, current) -> List[SchemaChange]:
        """Detect table/column additions/deletions."""
        changes = []
        
        old_tables = {t["name"]: t for t in old.get("tables", [])}
        curr_tables = {t["name"]: t for t in current.get("tables", [])}
        
        # New tables
        for table_name in curr_tables:
            if table_name not in old_tables:
                changes.append(SchemaChange(
                    type="TABLE_ADDED",
                    table=table_name,
                    severity="LOW",  # May help queries
                ))
        
        # Deleted tables
        for table_name in old_tables:
            if table_name not in curr_tables:
                changes.append(SchemaChange(
                    type="TABLE_DELETED",
                    table=table_name,
                    severity="HIGH",  # Breaks queries
                ))
        
        # Column changes
        for table_name in set(old_tables.keys()) & set(curr_tables.keys()):
            old_cols = {c["name"]: c for c in old_tables[table_name].get("columns", [])}
            curr_cols = {c["name"]: c for c in curr_tables[table_name].get("columns", [])}
            
            # New columns
            for col_name in curr_cols:
                if col_name not in old_cols:
                    changes.append(SchemaChange(
                        type="COLUMN_ADDED",
                        table=table_name,
                        column=col_name,
                        severity="LOW",
                    ))
            
            # Deleted columns
            for col_name in old_cols:
                if col_name not in curr_cols:
                    changes.append(SchemaChange(
                        type="COLUMN_DELETED",
                        table=table_name,
                        column=col_name,
                        severity="HIGH",
                    ))
            
            # Type changes
            for col_name in set(old_cols.keys()) & set(curr_cols.keys()):
                old_type = old_cols[col_name].get("type")
                curr_type = curr_cols[col_name].get("type")
                if old_type != curr_type:
                    changes.append(SchemaChange(
                        type="COLUMN_TYPE_CHANGED",
                        table=table_name,
                        column=col_name,
                        old_type=old_type,
                        new_type=curr_type,
                        severity="MEDIUM",
                    ))
        
        return changes
    
    def _detect_semantic_changes(self, old, current) -> List[SchemaChange]:
        """Detect relationship/index changes using StatGuardian."""
        # Use StatGuardian to compare constraints, indexes, etc.
        changes = []
        
        # Compare relationships
        old_rels = set((r["source"], r["target"]) for r in old.get("relationships", []))
        curr_rels = set((r["source"], r["target"]) for r in current.get("relationships", []))
        
        for rel in curr_rels - old_rels:
            changes.append(SchemaChange(
                type="RELATIONSHIP_ADDED",
                relationship=rel,
                severity="MEDIUM",
            ))
        
        for rel in old_rels - curr_rels:
            changes.append(SchemaChange(
                type="RELATIONSHIP_DELETED",
                relationship=rel,
                severity="MEDIUM",
            ))
        
        # Compare indexes
        old_idxs = set(idx["name"] for idx in old.get("indexes", []))
        curr_idxs = set(idx["name"] for idx in current.get("indexes", []))
        
        for idx in curr_idxs - old_idxs:
            changes.append(SchemaChange(
                type="INDEX_ADDED",
                index=idx,
                severity="LOW",
            ))
        
        for idx in old_idxs - curr_idxs:
            changes.append(SchemaChange(
                type="INDEX_DELETED",
                index=idx,
                severity="MEDIUM",
            ))
        
        return changes

@dataclass
class SchemaChange:
    type: str  # TABLE_ADDED, COLUMN_DELETED, etc.
    table: Optional[str] = None
    column: Optional[str] = None
    old_type: Optional[str] = None
    new_type: Optional[str] = None
    relationship: Optional[Tuple] = None
    index: Optional[str] = None
    severity: str = "MEDIUM"  # HIGH, MEDIUM, LOW
```

**Tests (20 tests):**

```python
# tests/test_statguardian_integration.py
class TestStatGuardianIntegration:
    def test_schema_validation_pass
    def test_schema_validation_missing_column
    def test_schema_validation_type_mismatch
    def test_drift_detection_psi
    def test_drift_detection_ks
    def test_detect_structural_changes_table_added
    def test_detect_structural_changes_table_deleted
    def test_detect_structural_changes_column_added
    def test_detect_structural_changes_column_deleted
    def test_detect_structural_changes_type_changed
    def test_detect_semantic_changes_relationship_added
    def test_detect_semantic_changes_index_deleted
    def test_change_severity_assessment
    def test_no_changes_empty_list
    def test_multiple_changes
    def test_complex_schema
    def test_statguardian_error_handling
    def test_statguardian_field_mapping
    def test_drift_severity_assessment
    def test_performance_large_schema
```

---

### Component 3: Intelligent Validation Checker (Weeks 3-4)

**Files to create:**
- `openanchor/validation/cache_validator.py` (500 lines)
- `openanchor/validation/validation_result.py` (200 lines)

**Cache Validator:**

```python
from enum import Enum
from dataclasses import dataclass

class CacheStatus(str, Enum):
    VALID = "valid"
    DEGRADED = "degraded"
    NEEDS_REVALIDATION = "needs_revalidation"
    INVALID = "invalid"
    FRESH = "fresh"

@dataclass
class ValidationResult:
    status: CacheStatus
    confidence: float  # 0.0-1.0
    changes: List[SchemaChange]
    recommendation: str  # USE_CACHE, RECOMPUTE, WARN
    reason: str = ""
    schema_version: int = 0

class IntelligentCacheValidator:
    """Validates cache entries before returning."""
    
    def __init__(
        self,
        cache: SemanticCache,
        detector: SchemaChangeDetector,
        sg_validator: StatGuardianSchemaValidator,
    ):
        self.cache = cache
        self.detector = detector
        self.sg = sg_validator
    
    def validate_cache_entry(
        self,
        cache_entry: SemanticCacheEntry,
        current_schema: Dict[str, Any],
    ) -> ValidationResult:
        """
        Validate if cache entry is still valid.
        
        Process:
        1. Compare schema hash
        2. Detect changes
        3. Assess impact
        4. Calculate confidence
        5. Return recommendation
        """
        
        # 1. Hash check (fast path)
        current_hash = hashlib.sha256(
            json.dumps(current_schema, sort_keys=True).encode()
        ).hexdigest()
        
        if current_hash == cache_entry.schema_hash:
            return ValidationResult(
                status=CacheStatus.VALID,
                confidence=1.0,
                changes=[],
                recommendation="USE_CACHE",
                reason="Schema hash unchanged",
            )
        
        # 2. Detect changes
        changes = self.detector.detect_changes(
            cache_entry.schema_definition,
            current_schema,
        )
        
        # 3. Assess impact
        invalidation_decision = self._assess_impact(changes, cache_entry)
        
        # 4. Calculate confidence
        confidence = self._calculate_confidence(changes, invalidation_decision)
        
        # 5. Return recommendation
        if invalidation_decision == "INVALIDATE":
            return ValidationResult(
                status=CacheStatus.INVALID,
                confidence=confidence,
                changes=changes,
                recommendation="RECOMPUTE",
                reason="High-severity changes affect cached tables",
            )
        
        elif invalidation_decision == "REVALIDATE":
            return ValidationResult(
                status=CacheStatus.DEGRADED,
                confidence=confidence,
                changes=changes,
                recommendation="WARN_OR_RECOMPUTE",
                reason="Medium-severity changes detected",
            )
        
        else:  # KEEP
            return ValidationResult(
                status=CacheStatus.VALID,
                confidence=confidence,
                changes=changes,
                recommendation="USE_CACHE",
                reason="Changes don't affect cached analysis",
            )
    
    def _assess_impact(
        self,
        changes: List[SchemaChange],
        cache_entry: SemanticCacheEntry,
    ) -> str:
        """Assess impact of changes on cache."""
        
        # High-severity changes always invalidate
        high_severity = [c for c in changes if c.severity == "HIGH"]
        if high_severity:
            return "INVALIDATE"
        
        # Check if changes affect cached tables
        cached_tables = self._extract_cached_tables(cache_entry)
        changed_tables = {c.table for c in changes if c.table}
        
        if changed_tables & cached_tables:
            # Medium-severity changes on cached tables
            return "REVALIDATE"
        
        # Low-severity changes on non-cached tables
        return "KEEP"
    
    def _calculate_confidence(
        self,
        changes: List[SchemaChange],
        decision: str,
    ) -> float:
        """Calculate confidence score (0.0-1.0)."""
        
        if not changes:
            return 1.0
        
        if decision == "INVALIDATE":
            return 0.0
        
        if decision == "REVALIDATE":
            # 0.6-0.8 depending on number/severity of changes
            low_severity = sum(1 for c in changes if c.severity == "LOW")
            total = len(changes)
            ratio = low_severity / total if total > 0 else 1.0
            return 0.6 + (ratio * 0.2)  # Range: 0.6-0.8
        
        # KEEP
        # High confidence if only low-severity changes
        low_severity = sum(1 for c in changes if c.severity == "LOW")
        total = len(changes)
        ratio = low_severity / total if total > 0 else 1.0
        return 0.8 + (ratio * 0.15)  # Range: 0.8-0.95
    
    def _extract_cached_tables(self, cache_entry: SemanticCacheEntry) -> Set[str]:
        """Extract tables referenced in cache entry."""
        tables = set()
        for source in cache_entry.discovered_sources:
            if "table" in source:
                tables.add(source["table"])
        return tables
    
    def validate_before_returning(
        self,
        cache_entry: SemanticCacheEntry,
        current_schema: Dict[str, Any],
    ) -> Tuple[Optional[Dict[str, Any]], ValidationResult]:
        """
        Validate and decide whether to return cache.
        
        Returns:
            (analysis_or_none, validation_result)
            - If None: Caller must recompute
            - If Dict: Cached analysis (check status for warnings)
        """
        
        validation = self.validate_cache_entry(cache_entry, current_schema)
        
        if validation.status == CacheStatus.VALID:
            return cache_entry.analysis, validation
        
        elif validation.status == CacheStatus.DEGRADED:
            if validation.confidence >= 0.75:
                # Still fairly confident - return with warning
                return cache_entry.analysis, validation
            else:
                # Low confidence - should recompute
                return None, validation
        
        else:  # INVALID
            # Must recompute
            return None, validation
```

**Tests (20 tests):**

```python
# tests/test_cache_validator.py
class TestCacheValidator:
    def test_validate_no_changes
    def test_validate_high_severity_change
    def test_validate_medium_severity_change
    def test_validate_low_severity_change
    def test_confidence_valid
    def test_confidence_degraded
    def test_confidence_invalid
    def test_validate_before_returning_valid
    def test_validate_before_returning_degraded_high
    def test_validate_before_returning_degraded_low
    def test_validate_before_returning_invalid
    def test_impact_assessment_table_deleted
    def test_impact_assessment_column_added
    def test_impact_assessment_non_cached_table_changed
    def test_extract_cached_tables
    def test_hash_comparison
    def test_multiple_changes_assessment
    def test_edge_case_empty_changes
    def test_edge_case_all_low_severity
    def test_performance_large_change_list
```

---

## Part 3: Integration Steps

### Step 1: Create Core Files (Week 1)

```bash
# Create package structure
mkdir -p openanchor/caching
mkdir -p openanchor/validation

# Create files
touch openanchor/caching/__init__.py
touch openanchor/caching/semantic_cache.py
touch openanchor/caching/cache_entry.py
touch openanchor/caching/embeddings.py

touch openanchor/validation/__init__.py
touch openanchor/validation/statguardian_wrapper.py
touch openanchor/validation/schema_change_detector.py
touch openanchor/validation/cache_validator.py
touch openanchor/validation/validation_result.py
```

### Step 2: Implement Components (Weeks 1-3)

Follow the three component design above in sequence:
- Week 1: Semantic cache (400+200+300 = 900 lines)
- Week 2: StatGuardian integration (300+400 = 700 lines)
- Week 3: Cache validator (500+200 = 700 lines)

### Step 3: Integrate with PyStreamMCP (Week 4)

**Modify discovery.py:**

```python
from openanchor.caching import SemanticCache
from openanchor.validation import IntelligentCacheValidator

class Discovery:
    def __init__(self, semantic_cache: Optional[SemanticCache] = None):
        self.cache = semantic_cache or SemanticCache()
        self.validator = IntelligentCacheValidator(
            self.cache,
            SchemaChangeDetector(),
            StatGuardianSchemaValidator(),
        )
    
    def discover_sources(self, schema, query):
        # Try cache first
        cache_entry = self.cache.find_similar(schema.id, query)
        
        if cache_entry:
            # Validate before returning
            analysis, validation = self.validator.validate_before_returning(
                cache_entry,
                schema.to_dict(),
            )
            
            if analysis:
                # Cache hit (valid or degraded)
                if validation.status == CacheStatus.DEGRADED:
                    logger.warning(f"Cache degraded: {validation.reason}")
                
                # Return cached sources
                return [
                    DiscoveredSource(**source)
                    for source in cache_entry.discovered_sources
                ]
        
        # Cache miss or invalid - compute fresh
        sources = self._discover_sources_fresh(schema, query)
        
        # Cache the result
        self.cache.cache_analysis(
            schema_id=schema.id,
            schema_definition=schema.to_dict(),
            query=query,
            analysis={"sources": sources},
            discovered_sources=[s.to_dict() for s in sources],
        )
        
        return sources
```

**Modify optimization.py:**

```python
class OptimizationStrategy:
    def __init__(self, semantic_cache: Optional[SemanticCache] = None):
        self.cache = semantic_cache
    
    def select_strategy(self, query, schema):
        if self.cache:
            # Use cache to inform strategy
            cache_entry = self.cache.find_similar(schema.id, query)
            if cache_entry:
                # Return suggested optimization from cache
                return OptimizationStrategy(
                    techniques=[cache_entry.optimization_suggestion],
                )
        
        # Default strategy
        return self._select_strategy_default(query, schema)
```

---

## Part 4: Testing Strategy

### Unit Tests (55 tests total)

- **Semantic Cache:** 15 tests
- **StatGuardian Integration:** 20 tests
- **Cache Validator:** 20 tests

### Integration Tests (10 tests)

- End-to-end cache hit → validate → return
- End-to-end cache miss → compute → cache
- End-to-end invalid cache → recompute
- Multiple schema versions
- Concurrent access patterns
- Performance benchmarks

### Manual Testing (before release)

- Test with real Snowflake warehouse
- Test with real PostgreSQL database
- Test with schema drift scenarios
- Test compliance/audit logging

---

## Part 5: Timeline & Milestones

```
Week 1: Semantic Cache Foundation
├─ Day 1-2: Setup, infrastructure
├─ Day 3-5: Implement SemanticCache, embeddings
└─ Milestone: 15 tests passing, cache working

Week 2: StatGuardian Integration
├─ Day 1-2: Wrapper, change detector
├─ Day 3-4: Integration with StatGuardian
└─ Milestone: 20 tests passing, validation working

Week 3: Intelligent Validation
├─ Day 1-3: Cache validator implementation
├─ Day 4: Integration with Discovery/Optimization
└─ Milestone: 20 tests passing, end-to-end working

Week 4: Polish & Release
├─ Day 1-2: Integration tests, manual testing
├─ Day 3: Documentation, README
├─ Day 4: Code review, optimization
└─ Milestone: v0.3.0 released, 65/65 tests passing
```

---

## Part 6: Success Criteria

### Code Quality
- ✓ 65+ tests, 100% passing
- ✓ Type hints throughout
- ✓ Zero mypy errors
- ✓ Black formatting

### Performance
- ✓ Cache lookup: <10ms
- ✓ Schema embedding: <100ms
- ✓ Validation: <5ms
- ✓ No regression in discovery latency

### Correctness
- ✓ Cache hit rate: 70-85%
- ✓ False cache hit rate: <2%
- ✓ Confidence scores accurate
- ✓ All scenarios tested

### Safety
- ✓ No silent failures
- ✓ Audit trail logged
- ✓ Safe degradation working
- ✓ Compliance ready

---

## Part 7: Deployment

### Before Release
- [ ] All tests passing
- [ ] Performance benchmarks done
- [ ] Documentation complete
- [ ] Code review completed

### Release Checklist
- [ ] Bump version to 0.3.0
- [ ] Create CHANGELOG entry
- [ ] Tag release on GitHub
- [ ] Deploy example notebook
- [ ] Announce in release notes

### Post-Release Monitoring
- [ ] Monitor cache hit rates
- [ ] Track validation accuracy
- [ ] Collect performance metrics
- [ ] Monitor user feedback

---

## Part 8: Dependencies & Compatibility

### New Dependencies
- `sentence-transformers` (already used in ML module)
- `numpy` (already available)
- `statguardian` (already in ecosystem)

### No new dependencies needed! ✓

### Compatibility
- Python 3.9+
- Works with PyStreamMCP v0.2+
- Works with StatGuardian v1.0+

---

## Conclusion

**This implementation plan delivers:**

✓ Production-safe semantic caching (validated)
✓ Leverages StatGuardian's existing capabilities
✓ 50-80% token reduction for data warehouses + databases
✓ No silent failures (always safe)
✓ Audit-trail & compliance-ready
✓ 4 weeks total, zero new dependencies
✓ 65+ tests, production-grade code quality

**Ready to start building.**
