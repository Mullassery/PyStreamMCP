use crate::{Query, Discovery, Result};
use rusqlite::Connection;
use std::sync::{Arc, Mutex};

pub struct Repository {
    conn: Arc<Mutex<Connection>>,
}

impl Repository {
    pub fn new(conn: Connection) -> Result<Self> {
        super::init_schema(&conn)?;
        Ok(Repository {
            conn: Arc::new(Mutex::new(conn)),
        })
    }

    pub fn save_query(&self, query: &Query) -> Result<()> {
        let conn = self.conn.lock().map_err(|_| {
            crate::Error::StorageError("Failed to acquire lock".to_string())
        })?;

        let intent_json = serde_json::to_string(&query.intent)?;

        conn.execute(
            "INSERT OR REPLACE INTO queries (id, text, agent_id, intent, created_at)
             VALUES (?1, ?2, ?3, ?4, ?5)",
            rusqlite::params![
                &query.id,
                &query.text,
                &query.agent_id,
                intent_json,
                query.created_at.to_rfc3339(),
            ],
        )?;

        Ok(())
    }

    pub fn get_query(&self, query_id: &str) -> Result<Option<Query>> {
        let conn = self.conn.lock().map_err(|_| {
            crate::Error::StorageError("Failed to acquire lock".to_string())
        })?;

        let mut stmt = conn.prepare(
            "SELECT id, text, agent_id, intent, created_at FROM queries WHERE id = ?1",
        )?;

        let query = stmt.query_row(rusqlite::params![query_id], |row| {
            let intent_json: String = row.get(3)?;

            Ok(Query {
                id: row.get(0)?,
                text: row.get(1)?,
                agent_id: row.get(2)?,
                intent: serde_json::from_str(&intent_json).unwrap_or_default(),
                constraints: Default::default(),
                metadata: Default::default(),
                created_at: chrono::DateTime::parse_from_rfc3339(&row.get::<_, String>(4)?)
                    .unwrap()
                    .with_timezone(&chrono::Utc),
            })
        });

        match query {
            Ok(q) => Ok(Some(q)),
            Err(rusqlite::Error::QueryReturnedNoRows) => Ok(None),
            Err(e) => Err(e.into()),
        }
    }

    pub fn save_discovery(&self, discovery: &Discovery) -> Result<()> {
        let conn = self.conn.lock().map_err(|_| {
            crate::Error::StorageError("Failed to acquire lock".to_string())
        })?;

        conn.execute(
            "INSERT OR REPLACE INTO discoveries (id, query_id, total_available_tokens, created_at)
             VALUES (?1, ?2, ?3, ?4)",
            rusqlite::params![
                &discovery.id,
                &discovery.query_id,
                discovery.total_available_tokens,
                discovery.created_at.to_rfc3339(),
            ],
        )?;

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_query_storage() -> Result<()> {
        let conn = rusqlite::Connection::open_in_memory()?;
        let repo = Repository::new(conn)?;

        let query = Query::new("Test query", "agent_1");
        repo.save_query(&query)?;

        let retrieved = repo.get_query(&query.id)?;
        assert!(retrieved.is_some());
        assert_eq!(retrieved.unwrap().text, "Test query");

        Ok(())
    }

    #[test]
    fn test_discovery_storage() -> Result<()> {
        let conn = rusqlite::Connection::open_in_memory()?;
        let repo = Repository::new(conn)?;

        let query = Query::new("Test", "agent_1");
        repo.save_query(&query)?;

        let discovery = Discovery::new(&query.id);
        repo.save_discovery(&discovery)?;

        Ok(())
    }
}
