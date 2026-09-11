# Research: Intelligent Database Discovery & Semantic Understanding for PyStreamMCP

**Date:** 2026-07-22  
**Status:** Research Complete  
**Recommendation:** Core subsystem, integrated into v0.5 (parallel with web knowledge) + v1.0

---

## Executive Summary

**Problem:** PyStreamMCP discovers context from external sources (web, APIs, caches) but remains blind to the most valuable knowledge: **internal databases**. Current discovery is reactive (agent asks → search). Ideal model is proactive (system knows database schema → optimizes queries before agent asks).

**Opportunity:** Database discovery as a core subsystem enables:
1. **Query Planning Intelligence** — "Given customer database, show me 5 ways to find churning users" (vs. "search for churn")
2. **Semantic Understanding** — Infer "this is e-commerce" from table names + column patterns, not hardcoded rules
3. **Cost Optimization** — Route queries to cheapest source (Postgres vs. BigQuery vs. Redis cache)
4. **Quality Gates** — Validate schema + data freshness before agent uses it
5. **Multi-Database Awareness** — Orchestrate queries across Postgres (operational), BigQuery (analytics), Elasticsearch (search)

**Why Not Optional:** Database knowledge is **foundational** to agent intelligence. Without it, PyStreamMCP optimizes blind (50% gains). With it, PyStreamMCP orchestrates (70%+ gains + better routing decisions).

**Strategic Fit:**
- **Complements web knowledge** (v0.5-v1.0 work): Web finds external answers; databases find internal truth
- **Integrates with StatGuardian** (v2.3): Quality gates apply equally to schema + data
- **Powers OKF catalog** (v0.4+): Discovered databases become portable tools
- **Enables multi-agent coordination** (v1.1+): Fair-share allocation requires knowing which agent owns which database

---

## Architecture: Database Discovery as Core Subsystem

### Design Principles

1. **Safety First** — Read-only by default, never destructive, respect existing auth
2. **Opportunistic** — Reuse existing connections, prefer app credentials
3. **Transparent** — Full audit trail of discovery (what was learned + when + how)
4. **Semantic** — Understand *meaning* (this is a customer table), not just structure
5. **Cost-Aware** — Every discovery action tracked in token budget + latency budget
6. **Pluggable** — SQLite, Postgres, MySQL, Mongo, BigQuery, Snowflake, Redis all supported equally

### Three-Layer Architecture

```
Layer 1: Discovery (Connect & Introspect)
├─ Environment scanning (POSTGRES_URL, .env, connection pools)
├─ Connection pooling (reuse app auth, never steal credentials)
├─ Safe introspection (information_schema, system catalogs)
└─ Async parallel scanning (10 databases simultaneously)

Layer 2: Semantic Understanding (Infer Meaning)
├─ Schema analysis (tables, columns, constraints, relationships)
├─ Naming pattern detection (customer_id → foreign key hint)
├─ Temporal signal detection (created_at, updated_at → transaction semantics)
├─ Cardinality analysis (1:1, 1:N, N:N inference)
├─ Domain classification (e-commerce? healthcare? finance?)
└─ Quality heuristics (NULL patterns, distributions, anomalies)

Layer 3: Knowledge Graph (Persistent Understanding)
├─ Entities (tables + columns + types + constraints)
├─ Relationships (foreign keys + inferred many-to-many)
├─ Temporal properties (when last changed, change frequency)
├─ Quality metadata (staleness, completeness, cardinality)
├─ Domain tags (auto-inferred: "payment_processing", "user_identity")
└─ Integration with OKF (exportable as .md documents)
```

### Safety Guardrails

```rust
// Core principle: Never destructive
pub struct DatabaseConnection {
    // ✅ Safe operations only
    pub async fn list_tables(&self) -> Result<Vec<TableSchema>> { }
    pub async fn infer_relationships(&self) -> Result<Vec<Relationship>> { }
    pub async fn sample_data(&self, table: &str, limit: usize) -> Result<Vec<Row>> { }
    pub async fn analyze_distribution(&self, table: &str, column: &str) -> Result<Distribution> { }
    
    // ❌ NEVER exposed (enforced by type system)
    // - CREATE / DROP / TRUNCATE
    // - UPDATE / INSERT / DELETE
    // - Administrative operations
    // - Credential access
}
```

---

## Part 1: Database Discovery Patterns

### 1.1 Safe Connection Discovery

**Problem:** How to find databases without hardcoding connections or stealing credentials?

**Solution Pattern:**

```
Discovery Sequence (non-destructive):
1. Environment scanning
   ├─ Read .env files (if app present)
   ├─ Check process env vars (POSTGRES_URL, DATABASE_URL)
   ├─ Look for Docker Compose, K8s secrets (metadata-only)
   └─ Scan for connection pool configs (Django, SQLAlchemy)

2. Existing connection reuse
   ├─ Ask app: "What databases are you connected to?"
   ├─ Introspect app connection pools
   ├─ Use app's existing credentials (never intercept)
   └─ Respect app's connection isolation policies

3. Permission scoping
   ├─ Check what current user can access
   ├─ Distinguish between schema introspection (always safe)
   │  vs. data access (requires explicit permission)
   └─ Audit every access attempt

4. Fallback to metadata
   ├─ If live introspection fails, use cached metadata
   ├─ Query last-cached schema (hours/days old)
   └─ Mark as "stale but usable"
```

**Example: PostgreSQL Discovery**

```python
class PostgreSQLDiscovery:
    """Safe PostgreSQL introspection (read-only)."""
    
    async def discover(self, connection_url: str) -> DatabaseProfile:
        """Discover schema without accessing data."""
        
        async with create_pool(connection_url) as pool:
            # 1. List all schemas (metadata, read-only)
            schemas = await self._list_schemas(pool)
            
            # 2. Introspect each schema (information_schema only)
            tables = await self._list_tables(pool, schemas)
            
            # 3. Get column definitions (no data access)
            columns = await self._list_columns(pool, tables)
            
            # 4. Find foreign keys (from catalog, not scanning data)
            relationships = await self._find_relationships(pool, tables)
            
            # 5. Get table stats (pg_stat_user_tables, read-only)
            stats = await self._get_table_stats(pool, tables)
            
            return DatabaseProfile(
                tables=tables,
                columns=columns,
                relationships=relationships,
                stats=stats,
                discovered_at=now()
            )
    
    async def _list_schemas(self, pool) -> List[str]:
        """List all schemas (safe: metadata only)."""
        async with pool.acquire() as conn:
            query = """
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
            """
            return await conn.fetch(query)
    
    async def _find_relationships(self, pool, tables) -> List[Relationship]:
        """Find relationships from catalog (safe: read-only metadata)."""
        async with pool.acquire() as conn:
            query = """
                SELECT
                    constraint_name,
                    table_name,
                    column_name,
                    referenced_table_name,
                    referenced_column_name
                FROM information_schema.referential_constraints
                WHERE constraint_schema NOT IN ('pg_catalog', 'information_schema')
            """
            return await conn.fetch(query)
```

### 1.2 Read-Only Mode Defaults

**Pattern: Three-Tier Access Model**

```rust
pub enum AccessLevel {
    /// Tier 1: Schema only (100% safe, always allowed)
    SchemaIntrospection {
        /// Table/column definitions, constraints, relationships
        /// Accessed via: information_schema, pg_catalog, DESCRIBE
        /// Token cost: ~50 tokens per 1000 tables
        /// Latency: <100ms
    },
    
    /// Tier 2: Sampled data (safe with limits, requires opt-in)
    SampledAnalysis {
        /// Sample N rows for distribution/quality analysis
        /// Safety: LIMIT 100 per table, no aggregates
        /// Requires: explicit config + permission gate
        /// Token cost: ~200 tokens per sample
        /// Latency: 100-500ms
    },
    
    /// Tier 3: Full queries (NEVER exposed to discovery)
    FullData {
        /// Not part of discovery system
        /// Agent queries directly via application
    },
}
```

### 1.3 Existing Connection Reuse

**Pattern: Application Connection Injection**

```python
class DatabaseDiscovery:
    """Discover databases using app's existing connections."""
    
    def __init__(self, 
                 app_connections: Dict[str, Connection],
                 max_introspection_time_ms: int = 5000):
        """
        Args:
            app_connections: Dict of "alias" → active connection
                E.g. {"postgres_prod": postgres_conn, "elasticsearch": es_client}
            max_introspection_time_ms: Timeout for any single discovery op
        """
        self.connections = app_connections
        self.max_time = max_introspection_time_ms
    
    async def discover_all(self) -> DatabasePortfolio:
        """Discover all databases app is connected to."""
        
        tasks = [
            self._discover_one(alias, conn) 
            for alias, conn in self.connections.items()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return DatabasePortfolio(
            databases=[r for r in results if not isinstance(r, Exception)],
            errors={k: str(e) for k, e in zip(self.connections.keys(), results) 
                   if isinstance(e, Exception)},
            timestamp=now()
        )
    
    async def _discover_one(self, alias: str, conn) -> DatabaseProfile:
        """Discover single database (with timeout protection)."""
        try:
            profile = await asyncio.wait_for(
                self._introspect(conn),
                timeout=self.max_time / 1000
            )
            return profile.with_alias(alias)
        except asyncio.TimeoutError:
            # Mark as "introspection took too long, use cached metadata"
            return DatabaseProfile.cached()
        except Exception as e:
            # Log but don't fail (one DB failure shouldn't block others)
            logger.warning(f"Failed to discover {alias}: {e}")
            raise
```

### 1.4 Tools & Patterns by Database Type

| Database | Discovery Method | Safety | Cost | Tools |
|----------|------------------|--------|------|-------|
| **PostgreSQL** | `information_schema` queries | 100% safe | ~50 tokens | Foreign keys, constraints, stats from `pg_stat_user_tables` |
| **MySQL** | `information_schema` + `SHOW TABLES` | 100% safe | ~50 tokens | Foreign keys from `information_schema.referential_constraints` |
| **MongoDB** | `db.listCollections()`, sampled docs | 95% safe (sampling) | ~100 tokens | Collection indexes, BSON schema from sample docs |
| **BigQuery** | REST API metadata calls | 100% safe | ~20 tokens (free tier) | Dataset/table metadata, schema, partitioning info |
| **Snowflake** | `INFORMATION_SCHEMA` views | 100% safe | $0 (metadata-only) | Database/schema/table hierarchies, column stats |
| **Elasticsearch** | `_mapping`, `_stats` APIs | 100% safe | ~10 tokens | Index mappings, field types, doc count estimates |
| **Redis** | `INFO`, `COMMAND`, key pattern scan | 95% safe (pattern scan only) | ~50 tokens | Key patterns, memory usage, expiration hints |
| **DuckDB** | `information_schema` | 100% safe | ~10 tokens | Tables, columns, foreign keys (in-process) |

---

## Part 2: Semantic Understanding Patterns

### 2.1 Schema Understanding Pipeline

```
Raw Schema
    ↓
[Extract Structure]
    ├─ Table names (customers, orders, products)
    ├─ Column names + types (customer_id INTEGER, email VARCHAR)
    ├─ Constraints (NOT NULL, UNIQUE, PRIMARY KEY, FOREIGN KEY)
    └─ Indexes
    ↓
[Infer Semantics]
    ├─ Naming patterns (customer_id → likely foreign key to customers.id)
    ├─ Type patterns (email VARCHAR(255) → email field)
    ├─ Temporal signals (created_at TIMESTAMP → transactional)
    ├─ Cardinality hints (status ENUM(active, inactive) → low cardinality dimension)
    └─ Domain detection (payment_method, churn_score → finance)
    ↓
[Build Understanding]
    ├─ Entity relationships (1:1, 1:N, N:N)
    ├─ Business semantics ("this table represents customers")
    ├─ Data quality signals (% nulls, date ranges, categorical distributions)
    └─ Temporal properties (updated daily? real-time? weekly snapshots?)
    ↓
[Persistent Knowledge]
    └─ Knowledge graph (queryable, exportable as OKF)
```

### 2.2 Semantic Inference Rules

**Example: Column Type → Semantic Meaning**

```python
class SemanticInference:
    """Infer business meaning from data patterns."""
    
    # Naming patterns
    NAMING_PATTERNS = {
        r'^id$|_id$': ColumnSemantic.ID,
        r'^(created|inserted|timestamp)': ColumnSemantic.CREATED_AT,
        r'^(updated|modified|changed)': ColumnSemantic.UPDATED_AT,
        r'^deleted': ColumnSemantic.DELETED_AT,
        r'^(email|mail)': ColumnSemantic.EMAIL,
        r'^(phone|mobile|telephone)': ColumnSemantic.PHONE,
        r'^(amount|price|cost|revenue)': ColumnSemantic.NUMERIC_FINANCIAL,
        r'^(status|state)': ColumnSemantic.STATUS,
        r'^(active|is_|enabled)': ColumnSemantic.BOOLEAN_FLAG,
        r'^(count|total|sum)': ColumnSemantic.AGGREGATED,
    }
    
    # Type patterns
    TYPE_PATTERNS = {
        ('email', 'VARCHAR'): ColumnSemantic.EMAIL,
        ('timestamp', 'TIMESTAMP'): ColumnSemantic.TEMPORAL,
        ('enum', 'ENUM'): ColumnSemantic.CATEGORICAL,
        ('float|decimal', 'NUMERIC'): ColumnSemantic.NUMERIC_MEASUREMENT,
        ('boolean', 'BOOLEAN'): ColumnSemantic.BOOLEAN_FLAG,
    }
    
    @staticmethod
    def infer_column_meaning(column: ColumnSchema) -> ColumnSemantic:
        """Infer what a column represents."""
        
        # 1. Check naming patterns
        for pattern, semantic in SemanticInference.NAMING_PATTERNS.items():
            if re.search(pattern, column.name.lower()):
                return semantic
        
        # 2. Check type patterns
        for (type_match, sql_type), semantic in SemanticInference.TYPE_PATTERNS.items():
            if re.search(type_match, column.type.lower()) and sql_type in column.sql_type:
                return semantic
        
        # 3. Check cardinality (low = dimension, high = fact)
        if column.distinct_count < 100:
            return ColumnSemantic.CATEGORICAL_DIMENSION
        elif column.distinct_count > 1_000_000:
            return ColumnSemantic.HIGH_CARDINALITY_ID
        else:
            return ColumnSemantic.MEASURE
    
    @staticmethod
    def infer_table_domain(table: TableSchema) -> Domain:
        """Infer business domain from table + column patterns."""
        
        column_names = {col.name.lower() for col in table.columns}
        
        # E-commerce signals
        if any(signal in column_names for signal in 
               ['customer_id', 'order_id', 'product_id', 'sku']):
            return Domain.ECOMMERCE
        
        # Healthcare signals
        if any(signal in column_names for signal in 
               ['patient_id', 'diagnosis', 'prescription', 'med_code']):
            return Domain.HEALTHCARE
        
        # Finance signals
        if any(signal in column_names for signal in 
               ['account_id', 'transaction', 'balance', 'interest_rate']):
            return Domain.FINANCE
        
        # Default: generic data table
        return Domain.GENERIC
```

### 2.3 Entity-Relationship Graph

**Data Structure: Semantic-Aware Schema**

```python
@dataclass
class SemanticSchema:
    """Complete semantic understanding of a database."""
    
    # Core structure
    database_name: str
    tables: List[SemanticTable]
    relationships: List[SemanticRelationship]
    
    # Temporal properties
    discovered_at: datetime
    last_updated_at: Optional[datetime]  # When schema last changed
    update_frequency: Optional[Frequency]  # Daily? Real-time?
    
    # Quality properties
    completeness_score: float  # % of tables introspected
    freshness_score: float  # Metadata freshness
    total_row_count: int  # Estimated
    estimated_size_gb: float
    
    # Domain classification
    primary_domain: Domain
    secondary_domains: List[Domain]
    
    # Temporal patterns
    has_transaction_tables: bool  # has created_at/updated_at
    has_time_series: bool  # Date-partitioned fact tables
    has_snapshots: bool  # Weekly/monthly snapshots
    
    def to_okf_document(self) -> str:
        """Export as portable OKF markdown."""
        return f"""
        # {self.database_name}
        
        **Type:** {self.primary_domain}  
        **Tables:** {len(self.tables)}  
        **Relationships:** {len(self.relationships)}  
        **Discovered:** {self.discovered_at}
        
        ## Tables ({self.total_row_count:,} total rows)
        
        {self._format_table_list()}
        
        ## Relationships
        
        {self._format_relationships()}
        
        ## Quality
        
        - Completeness: {self.completeness_score:.1%}
        - Freshness: {self.freshness_score:.1%}
        - Size: {self.estimated_size_gb:.1f} GB
        """

@dataclass
class SemanticTable:
    """Table with semantic understanding."""
    
    name: str
    columns: List[SemanticColumn]
    primary_keys: List[str]
    
    # Semantics
    semantic_type: TableType  # ENTITY, FACT, DIMENSION, JUNCTION, SNAPSHOT
    business_name: str  # "Customer Records" (inferred from table name)
    estimated_row_count: int
    last_modified: Optional[datetime]
    
    # Quality hints
    null_patterns: Dict[str, float]  # column → % null
    cardinality_patterns: Dict[str, int]  # column → distinct count
    temporal_properties: TemporalProperties  # when updated, frequency

@dataclass
class SemanticColumn:
    """Column with semantic understanding."""
    
    name: str
    sql_type: str
    nullable: bool
    
    # Semantics
    semantic_type: ColumnSemantic  # ID, TIMESTAMP, EMAIL, etc.
    is_key: bool  # Part of primary key?
    is_foreign_key: bool  # Points to another table?
    is_temporal: bool  # created_at, updated_at, etc?
    
    # Quality metrics
    distinct_count: Optional[int]  # Cardinality
    null_count: Optional[int]
    min_value: Optional[str]  # For numeric/temporal
    max_value: Optional[str]
    
    # Statistics
    storage_bytes: Optional[int]
    index_present: bool

@dataclass
class SemanticRelationship:
    """Relationship between tables."""
    
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    
    # Relationship properties
    cardinality: Cardinality  # ONE_TO_ONE, ONE_TO_MANY, MANY_TO_MANY
    is_explicit: bool  # Foreign key constraint exists?
    is_inferred: bool  # Inferred from naming patterns?
    confidence: float  # 0.5-1.0 for inferred relationships
    
    # Business properties
    relationship_name: str  # "customer has orders"
    join_condition: str  # SQL condition
```

### 2.4 Data Quality Heuristics

**Pattern: Quick Quality Scoring Without Full Scans**

```python
class QualityAnalyzer:
    """Estimate data quality without scanning entire dataset."""
    
    async def analyze_table_quality(self, table: SemanticTable) -> QualityScore:
        """Quick quality assessment using metadata + sampling."""
        
        signals = []
        
        # 1. Schema completeness (all columns have types?)
        completeness = len([c for c in table.columns if c.sql_type]) / len(table.columns)
        signals.append(('completeness', completeness))
        
        # 2. NULL patterns (high nulls in key columns = quality risk)
        for column in table.columns:
            if column.null_count > 0 and column.is_key:
                # Key columns should never be null
                risk_score = min(column.null_count / table.estimated_row_count, 1.0)
                signals.append(('null_in_key', 1.0 - risk_score))
        
        # 3. Temporal signals (recent updates = freshness)
        if table.last_modified:
            hours_old = (now() - table.last_modified).total_seconds() / 3600
            if hours_old < 24:
                freshness = 1.0
            elif hours_old < 168:  # 1 week
                freshness = 0.8
            elif hours_old < 30 * 24:  # 1 month
                freshness = 0.5
            else:
                freshness = 0.2
            signals.append(('temporal_freshness', freshness))
        
        # 4. Cardinality consistency (tables with extreme ratios = data issues)
        for column in table.columns:
            if column.distinct_count:
                cardinality_ratio = column.distinct_count / table.estimated_row_count
                # Normal: 0.01 to 100x (some columns low card, some high)
                # Anomaly: >1M cardinality with <1M rows (data quality issue)
                if cardinality_ratio > 2.0:
                    signals.append(('cardinality_anomaly', 0.7))
        
        # 5. Composite score (weighted average)
        weights = {'completeness': 0.2, 'temporal_freshness': 0.3, 
                  'null_in_key': 0.3, 'cardinality_anomaly': 0.2}
        
        score = sum(signal_score * weights.get(signal_name, 0.0) 
                   for signal_name, signal_score in signals)
        
        return QualityScore(
            overall=score,
            breakdown={name: score for name, score in signals},
            factors=list(weights.keys())
        )
    
    async def distinguish_schemas(self, 
                                  tables: List[SemanticTable]) -> SchemaClassification:
        """Distinguish operational vs. analytical schemas."""
        
        # Heuristics:
        # Operational: lots of small tables, frequent writes, low latency indexes
        # Analytical: few large tables, infrequent writes, wide tables
        
        avg_row_count = statistics.mean(t.estimated_row_count for t in tables)
        avg_column_count = statistics.mean(len(t.columns) for t in tables)
        
        write_frequency = sum(1 for t in tables if t.last_modified and 
                            (now() - t.last_modified).total_seconds() < 3600) / len(tables)
        
        if avg_row_count < 1_000_000 and avg_column_count < 50 and write_frequency > 0.5:
            return SchemaClassification.OPERATIONAL
        elif avg_row_count > 100_000_000 and avg_column_count > 200 and write_frequency < 0.1:
            return SchemaClassification.ANALYTICAL
        else:
            return SchemaClassification.HYBRID
```

---

## Part 3: Knowledge Graph Structure & Persistence

### 3.1 OKF Schema Documents

**Example: Database OKF Export**

```yaml
# systems/postgres_prod.md
---
type: mcp-system
title: PostgreSQL Production
system_id: postgres_prod
database_type: postgresql
discovered_at: 2026-07-22T10:30:00Z
tables_count: 128
row_count_total: 2500000
estimated_size_gb: 45.2
primary_domain: ecommerce
temporal_properties:
  has_transaction_tables: true
  update_frequency: real_time
---

# PostgreSQL Production

## Overview
Production OLTP database for e-commerce platform.

**Key Stats:**
- 128 tables
- 2.5M total rows
- 45.2 GB size
- Real-time updates
- Discovered: 2026-07-22

## Table Groups

### Customer Entity Group (15 tables)
- `customers` — Customer master records (1:1 dimension)
- `customer_addresses` — Customer addresses (1:many relationship)
- `customer_preferences` — Preferences (1:1 dimension)
- `customer_segments` — Segment assignments (many:many)

### Order Processing (22 tables)
- `orders` — Order facts (high-cardinality)
- `order_items` — Order line items (1:many)
- `order_statuses` — Status history (1:many)
- `order_payments` — Payment records (1:many)

### Data Quality
- Completeness: 95%
- Freshness: Real-time
- Key NULL rates:
  - customers.email: 0.1% (acceptable)
  - orders.customer_id: 0.0% (good)

## Inferred Relationships

```
customers (1) ──→ (N) orders
       ↓
       ├─→ customer_addresses
       ├─→ customer_preferences
       └─→ customer_segments

orders (1) ──→ (N) order_items
      ↓
      ├─→ order_payments
      ├─→ order_statuses
      └─→ order_tracking
```

## Domain Classification
**Primary:** E-Commerce  
**Signals:**
- customer_id, order_id, product_id foreign keys
- payment_method, checkout_step columns
- inventory tables (products, stock, skus)

## Temporal Properties
- **Real-time updates:** orders, order_items, order_statuses
- **Daily snapshots:** customer_segments, inventory_snapshots
- **Static reference:** products, categories (rarely change)
```

### 3.2 Storage Architecture

**Pattern: Hybrid Persistent + In-Memory**

```rust
pub struct DatabaseKnowledgeGraph {
    // In-memory index (fast lookups)
    tables_by_name: HashMap<String, SemanticTable>,
    relationships_by_source: HashMap<String, Vec<SemanticRelationship>>,
    domain_index: HashMap<Domain, Vec<String>>, // domain → table names
    
    // Persistent storage (git-trackable)
    okf_catalog: PathBuf,  // ./mcp_catalog/databases/
    schema_cache: PathBuf, // ./mcp_catalog/schemas/
    
    // Metadata
    last_discovery: DateTime<Utc>,
    discovery_ttl: Duration,
}

impl DatabaseKnowledgeGraph {
    /// Refresh discovery periodically
    pub async fn refresh_if_stale(&mut self, stale_after: Duration) -> Result<()> {
        if self.last_discovery.elapsed() > stale_after {
            self.discover_all().await?;
        }
        Ok(())
    }
    
    /// Query the knowledge graph (offline-capable)
    pub fn find_tables_by_domain(&self, domain: Domain) -> Vec<&SemanticTable> {
        self.domain_index
            .get(&domain)
            .map(|names| {
                names.iter()
                    .filter_map(|name| self.tables_by_name.get(name))
                    .collect()
            })
            .unwrap_or_default()
    }
    
    pub fn find_relationships(&self, from_table: &str) -> Vec<&SemanticRelationship> {
        self.relationships_by_source
            .get(from_table)
            .map(|rels| rels.iter().collect())
            .unwrap_or_default()
    }
    
    /// Export as OKF (for version control + sharing)
    pub async fn export_to_okf(&self) -> Result<()> {
        for (db_name, profile) in &self.databases {
            let okf_doc = profile.to_okf_document();
            let path = self.okf_catalog.join("databases").join(format!("{}.md", db_name));
            tokio::fs::write(&path, okf_doc).await?;
        }
        Ok(())
    }
}
```

---

## Part 4: Integration Architecture with PyStreamMCP

### 4.1 Query Planning with Database Knowledge

**Current (v0.4):**
```
Agent: "Show me top customers"
    ↓
PyStreamMCP discovers sources (blind search)
    ├─ Web search (external)
    ├─ API cache (external)
    └─ ??? (internal databases unknown)
    ↓
Optimize & return context
```

**With database discovery (v1.0):**
```
Agent: "Show me top customers"
    ↓
DatabaseKnowledgeGraph finds:
    ├─ customers table (e-commerce domain, 1M rows, real-time)
    ├─ customer_ltv table (daily snapshot, 1M rows)
    ├─ customer_segments table (customer → segment mapping)
    └─ order_facts table (for LTV calculation source)
    ↓
Query Planner decides:
    ├─ Query customers table (primary source, fresh, low cost)
    ├─ Join with customer_segments (enrichment)
    ├─ Order by ltv (ranking)
    └─ Optional: include web sources for industry benchmarks?
    ↓
StatGuardian validates:
    ├─ customers table: schema ✓, freshness ✓, quality score: 0.95
    ├─ customer_ltv table: schema ✓, freshness ✓, quality score: 0.92
    ✓ All sources pass validation gates
    ↓
Optimize & return context
```

### 4.2 Cost Optimization with Database Routing

**Pattern: Multi-Database Query Routing**

```python
class MultiDatabaseRouter:
    """Route queries to optimal database."""
    
    def __init__(self, 
                 postgres: DatabaseConnection,
                 bigquery: DatabaseConnection,
                 elasticsearch: DatabaseConnection):
        self.databases = {
            "postgres_prod": postgres,      # Low latency, expensive storage
            "bigquery_analytics": bigquery, # High latency, cheap for aggregates
            "elasticsearch": elasticsearch, # Fast text search
        }
    
    async def route_query(self, 
                         query: QueryPlan,
                         knowledge_graph: DatabaseKnowledgeGraph) -> RoutingDecision:
        """Decide which database(s) to query."""
        
        # Analyze query intent
        if query.intent == QueryIntent.TextSearch:
            # Text search → Elasticsearch
            return RoutingDecision.PRIMARY(self.databases["elasticsearch"])
        
        elif query.intent == QueryIntent.AggregateAnalytics:
            # Aggregates of large dataset → BigQuery
            # (cheaper than scanning Postgres)
            tables = knowledge_graph.find_tables_by_domain(query.domain)
            if any(t.estimated_row_count > 10_000_000 for t in tables):
                return RoutingDecision.PRIMARY(self.databases["bigquery_analytics"])
        
        elif query.intent == QueryIntent.RealtimeTransactional:
            # Real-time data → Postgres (lower latency)
            return RoutingDecision.PRIMARY(self.databases["postgres_prod"])
        
        # Multi-database strategy: Postgres for fresh data + BigQuery for historical
        return RoutingDecision.HYBRID([
            (self.databases["postgres_prod"], 0.7),    # 70% from Postgres
            (self.databases["bigquery_analytics"], 0.3) # 30% from BigQuery
        ])
```

### 4.3 StatGuardian Integration

**Pattern: Quality Gates for Database Sources**

```python
# PyStreamMCP discovery returns:
discovered_sources = [
    DiscoveredSource(
        name="customers",
        source_type=SourceType.Table(table_name="customers", database="postgres"),
        relevance_score=0.95,
        estimated_tokens=1500,
    ),
    DiscoveredSource(
        name="customer_segments",
        source_type=SourceType.Table(table_name="customer_segments", database="postgres"),
        relevance_score=0.80,
        estimated_tokens=500,
    ),
]

# StatGuardian validates before inclusion:
quality_gates = {
    "customers": ValidationGate(
        dataset_id="postgres.customers",
        min_quality_score=0.90,
        require_schema_freshness=True,
        max_staleness=timedelta(hours=1),
    ),
    "customer_segments": ValidationGate(
        dataset_id="postgres.customer_segments",
        min_quality_score=0.85,
        require_schema_freshness=True,
        max_staleness=timedelta(hours=24),  # Daily snapshot OK
    ),
}

# PyStreamMCP calls StatGuardian for each source
validated_sources = []
for source in discovered_sources:
    gate = quality_gates.get(source.name)
    if gate:
        result = await statguardian.validate(gate, source)
        if result.passes:
            validated_sources.append(source)
        else:
            # Skip source (quality too low)
            logger.info(f"Skipping {source.name}: {result.reason}")
```

---

## Part 5: Phasing Strategy

### Phase 0: Foundation (Parallel with v0.5, 4 weeks)

**Objective:** Database discovery prototype + knowledge graph baseline

**Scope:**
- PostgreSQL + MongoDB connection discovery (environment + pools)
- Basic schema introspection (tables, columns, constraints)
- Simple relationship inference (naming patterns)
- OKF export skeleton
- Read-only safety enforced at type level

**Deliverables:**
- `core/src/database/discovery.rs` (PostgreSQL introspection)
- `core/src/database/semantic.rs` (Naming pattern rules)
- `core/src/database/knowledge_graph.rs` (In-memory graph)
- `python/pystreammcp/database/discovery.py` (Python wrapper)
- 15 unit tests
- Example: `examples/discover_postgres.rs`

**Hours:** 120 hours  
**LOC:** ~1500 Rust + 600 Python  
**Tests:** 15 unit + 3 integration

**Dependencies:** None (can run parallel to v0.5)

### Phase 1: Semantic Understanding (v1.0, 8 weeks)

**Objective:** Production-grade semantic inference + quality heuristics

**Scope:**
- Extended semantic inference (domain classification, temporal patterns)
- Data quality analysis without full scans (cardinality, null patterns)
- Entity-relationship graph completion
- Support for Postgres + MySQL + BigQuery + MongoDB
- OKF catalog generation (50+ example domains)
- StatGuardian integration (validation gates for databases)

**Deliverables:**
- `core/src/database/semantic/inference.rs` (Semantic rules engine)
- `core/src/database/quality.rs` (Quality heuristics)
- `core/src/database/multidb/router.rs` (Database routing)
- `python/pystreammcp/database/semantic.py` (Python API)
- `mcp_catalog/databases/` (50+ OKF example schemas)
- 40 unit tests + 15 integration tests
- Docs: "Database Discovery Setup" guide

**Hours:** 200 hours  
**LOC:** ~2500 Rust + 1200 Python  
**Tests:** 40 unit + 15 integration

**Dependencies:** Phase 0 + StatGuardian 2.3+ (for validation gates)

### Phase 2: Advanced Features (v1.1+, 10 weeks)

**Objective:** Persistent lineage tracking + predictive optimization

**Scope:**
- Lineage tracking (which table modified which column?)
- Change detection (schema drift alerts)
- Predictive data freshness (when will this table be stale?)
- Advanced relationship inference (N:N detection via junction tables)
- Query optimization hints (which index would help?)
- Multi-database federation (query planning across DBs)

**Deliverables:**
- `core/src/database/lineage.rs` (Column-level lineage)
- `core/src/database/change_detection.rs` (Schema drift)
- `core/src/database/predictive.rs` (Freshness forecasting)
- 30 unit tests + 10 integration tests
- Docs: "Advanced Database Intelligence" guide

**Hours:** 240 hours  
**LOC:** ~3000 Rust + 1500 Python  
**Tests:** 30 unit + 10 integration

**Dependencies:** Phase 1 + OKF mature (v1.0+)

---

## Success Metrics

| Phase | Metric | Target | Validation |
|-------|--------|--------|------------|
| **Phase 0** | Database discovery accuracy | >95% (table detection) | Manual validation against actual DB |
| **Phase 0** | Relationship inference precision | >80% (no false positives) | Compare inferred vs. explicit FKs |
| **Phase 0** | Performance: introspection <500ms | 10 tables per 100ms | Benchmark on Postgres/MongoDB |
| **Phase 1** | Semantic inference accuracy | >85% (domain classification) | 50 test schemas with ground truth |
| **Phase 1** | Quality score correlation | >0.8 (vs. manual assessment) | Correlation with StatGuardian scores |
| **Phase 1** | OKF export coverage | 50+ example schemas | Community feedback on catalog |
| **Phase 1** | StatGuardian integration tests | 15+ scenarios | All validation gates working |
| **Phase 2** | Lineage completeness | >90% (column-level) | Compare vs. dbt lineage graphs |
| **Phase 2** | Change detection sensitivity | >95% (catch schema changes) | Pre/post schema diff validation |

---

## Critical Design Decisions

### Decision 1: Core or Optional?

**Question:** Should database discovery be a CORE subsystem or optional backend?

**Answer:** **CORE subsystem** (non-negotiable for v1.0)

**Rationale:**
1. **Most valuable context is internal** — Agents benefit 10x more from "customer_ltv table" than generic web search
2. **Strategic positioning** — Without this, PyStreamMCP = "nice optimization layer"; with this = "query intelligence platform"
3. **Foundation for multi-agent** — v1.1 fair-share allocation requires knowing which agent owns which database
4. **Complements web knowledge** — Web finds external answers; databases find internal truth (complementary, not redundant)

### Decision 2: Read-Only vs. Generative

**Question:** Should database discovery only read schemas, or also suggest optimizations?

**Answer:** **Read schemas, suggest optimizations** (two-tier model)

**Tier 1 (v1.0): Read-Only**
- Discover existing tables, columns, relationships
- Analyze quality, freshness, cardinality
- Never create/modify/delete anything

**Tier 2 (v1.1+): Generative**
- Suggest missing indexes ("adding index on customer_id would speed queries")
- Recommend materialized views ("pre-compute top_customers")
- Flag schema anti-patterns ("N:1 normalization issue in orders")
- **Always advisory** — never execute (humans approve first)

### Decision 3: Latency Budget

**Question:** How much query latency can discovery add?

**Answer:** **<500ms total, <100ms per database**

**Breakdown:**
- PostgreSQL introspection: <100ms (information_schema is fast)
- MongoDB discovery: <100ms (listCollections is fast)
- Relationship inference: <100ms (compute-heavy, but cached)
- Quality analysis: <100ms (sample-based, not full scan)
- Total: <400ms for typical multi-database environment

**Caching:** Results cached for 1-24 hours (configurable by update frequency)

---

## Risk Mitigation

| Risk | Severity | Mitigation |
|------|----------|-----------|
| **Credential leakage** | Critical | Never store credentials; always reuse app connections |
| **Performance regression** | High | <500ms latency cap enforced; discovery runs async, cached |
| **Schema too large** | Medium | Sampling + streaming; don't load entire schema at once |
| **Multi-database conflicts** | Medium | Namespace tables by database (postgres.customers vs. bigquery.customers) |
| **Stale metadata** | Medium | TTL-based refresh (1-24hrs default); explicit refresh on error |

---

## Competitive Positioning

| Capability | PyStreamMCP v0.4 | PyStreamMCP v1.0 (with DB Discovery) | Competitors |
|---|---|---|---|
| **Discover internal databases** | No | Yes ✓ | LangChain (partial via tools) |
| **Semantic understanding** | No | Yes ✓ | DBT (not agent-friendly) |
| **Multi-database routing** | No | Yes ✓ | None in OSS market |
| **Quality gates for DB** | No | Yes (StatGuardian) ✓ | Unique |
| **OKF catalog** | Yes (web) | Yes (web + databases) ✓ | Unique |
| **Query optimization** | 60-75% (web) | 60-75% (web + DB intelligent routing) ✓ | LangChain 40-50% |

**Differentiator:** First OSS agent framework with semantic database intelligence + multi-database routing. Enables agents to "understand" their data before querying it.

---

## Next Steps

1. **Design review** — Validate architecture with team (week 1)
2. **Dependency audit** — Verify OSS licenses for sqlalchemy, asyncpg, pymongo (week 1)
3. **Phase 0 spike** — Build minimal PoC (PostgreSQL discovery) (week 2)
4. **Roadmap update** — Publish schedule (Phase 0 parallel with v0.5, Phase 1 in v1.0) (week 2)
5. **Begin Phase 0** — Start discovery implementation (week 3)

---

## Documents to Produce

- **[DATABASE_DISCOVERY_IMPLEMENTATION.md](DATABASE_DISCOVERY_IMPLEMENTATION.md)** — Step-by-step guide for Phase 0 + Phase 1
- **[DATABASE_DISCOVERY_SAFETY.md](DATABASE_DISCOVERY_SAFETY.md)** — Security considerations + credential handling
- **[DATABASE_SEMANTIC_RULES.md](DATABASE_SEMANTIC_RULES.md)** — Comprehensive rule library for inference
- **[MULTIDB_QUERY_ROUTING.md](MULTIDB_QUERY_ROUTING.md)** — Query planning with multiple databases

---

**TL;DR:** Database discovery is the missing piece that transforms PyStreamMCP from a "query optimizer" into a "query intelligence platform." By understanding internal databases semantically, PyStreamMCP can orchestrate agents across multiple sources (Postgres + BigQuery + Elasticsearch) with 70%+ token reduction + better routing decisions. Phase 0 (4 weeks) builds foundation; Phase 1 (8 weeks) production-ready; Phase 2 (10 weeks) advanced lineage + optimization. Core subsystem, not optional. Ready to start.
