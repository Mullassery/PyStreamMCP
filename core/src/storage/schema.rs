use crate::Result;
use rusqlite::Connection;

pub fn init_schema(conn: &Connection) -> Result<()> {
    conn.execute_batch(
        "
        CREATE TABLE IF NOT EXISTS queries (
            id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            intent TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS contexts (
            id TEXT PRIMARY KEY,
            query_id TEXT NOT NULL,
            context_type TEXT NOT NULL,
            content TEXT NOT NULL,
            relevance_score REAL NOT NULL,
            token_count INTEGER NOT NULL,
            source TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (query_id) REFERENCES queries(id)
        );

        CREATE TABLE IF NOT EXISTS discoveries (
            id TEXT PRIMARY KEY,
            query_id TEXT NOT NULL,
            total_available_tokens INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (query_id) REFERENCES queries(id)
        );

        CREATE TABLE IF NOT EXISTS discovered_sources (
            id TEXT PRIMARY KEY,
            discovery_id TEXT NOT NULL,
            name TEXT NOT NULL,
            source_type TEXT NOT NULL,
            relevance_score REAL NOT NULL,
            estimated_tokens INTEGER NOT NULL,
            freshness_score REAL NOT NULL,
            availability TEXT NOT NULL,
            FOREIGN KEY (discovery_id) REFERENCES discoveries(id)
        );

        CREATE TABLE IF NOT EXISTS optimization_strategies (
            id TEXT PRIMARY KEY,
            query_id TEXT NOT NULL,
            strategy_type TEXT NOT NULL,
            techniques TEXT NOT NULL,
            expected_reduction_percent REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (query_id) REFERENCES queries(id)
        );

        CREATE TABLE IF NOT EXISTS cost_metrics (
            id TEXT PRIMARY KEY,
            query_id TEXT NOT NULL,
            baseline_tokens INTEGER NOT NULL,
            optimized_tokens INTEGER NOT NULL,
            reduction_percent REAL NOT NULL,
            baseline_latency_ms INTEGER NOT NULL,
            optimized_latency_ms INTEGER NOT NULL,
            quality_maintained BOOLEAN NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (query_id) REFERENCES queries(id)
        );

        CREATE INDEX IF NOT EXISTS idx_contexts_query ON contexts(query_id);
        CREATE INDEX IF NOT EXISTS idx_discoveries_query ON discoveries(query_id);
        CREATE INDEX IF NOT EXISTS idx_strategies_query ON optimization_strategies(query_id);
        CREATE INDEX IF NOT EXISTS idx_metrics_query ON cost_metrics(query_id);
        "
    )?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_schema_initialization() -> std::result::Result<(), Box<dyn std::error::Error>> {
        let conn = rusqlite::Connection::open_in_memory()?;
        init_schema(&conn)?;

        let mut stmt = conn.prepare("SELECT name FROM sqlite_master WHERE type='table'")?;
        let tables: Vec<String> = stmt
            .query_map([], |row| row.get(0))?
            .collect::<std::result::Result<Vec<_>, _>>()?;

        assert!(tables.contains(&"queries".to_string()));
        assert!(tables.contains(&"contexts".to_string()));
        assert!(tables.contains(&"discoveries".to_string()));
        assert!(tables.contains(&"optimization_strategies".to_string()));
        assert!(tables.contains(&"cost_metrics".to_string()));

        Ok(())
    }
}
