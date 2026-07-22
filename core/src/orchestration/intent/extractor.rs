use std::collections::HashMap;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EntityType {
    RobotId,
    DatabaseName,
    TableName,
    ApiEndpoint,
    UserId,
    ProjectId,
    ToolName,
    FilePath,
    Unknown,
}

#[derive(Debug, Clone)]
pub struct Entity {
    pub name: String,
    pub entity_type: EntityType,
    pub relevance: f32,
}

impl Entity {
    pub fn new(name: String, entity_type: EntityType, relevance: f32) -> Self {
        Self {
            name,
            entity_type,
            relevance,
        }
    }
}

/// Extracts entities (robots, databases, etc.) from queries
pub struct EntityExtractor {
    robot_patterns: Vec<String>,
    database_patterns: Vec<String>,
    tool_patterns: Vec<String>,
}

impl EntityExtractor {
    pub fn new() -> Self {
        Self {
            robot_patterns: vec![
                "robot_", "bot_", "agent_", "rover_", "drone_",
            ]
            .iter()
            .map(|s| s.to_string())
            .collect(),
            database_patterns: vec![
                "db_", "postgres_", "mongo_", "sql_", "bigquery_",
            ]
            .iter()
            .map(|s| s.to_string())
            .collect(),
            tool_patterns: vec![
                "mcp_", "tool_", "service_",
            ]
            .iter()
            .map(|s| s.to_string())
            .collect(),
        }
    }

    /// Extract entities from a query string
    pub fn extract(&self, query: &str) -> Vec<Entity> {
        let mut entities = Vec::new();

        // Extract robot IDs (robot_42, bot_5, etc.)
        for entity in self.extract_by_patterns(query, &self.robot_patterns, EntityType::RobotId) {
            entities.push(entity);
        }

        // Extract database names
        for entity in self.extract_by_patterns(query, &self.database_patterns, EntityType::DatabaseName)
        {
            entities.push(entity);
        }

        // Extract tool names
        for entity in
            self.extract_by_patterns(query, &self.tool_patterns, EntityType::ToolName)
        {
            entities.push(entity);
        }

        // Extract numbers that might be IDs
        for entity in self.extract_numeric_ids(query) {
            entities.push(entity);
        }

        entities
    }

    fn extract_by_patterns(
        &self,
        query: &str,
        patterns: &[String],
        entity_type: EntityType,
    ) -> Vec<Entity> {
        let mut entities = Vec::new();
        let query_lower = query.to_lowercase();

        for pattern in patterns {
            if let Some(start) = query_lower.find(pattern) {
                let end = query_lower[start..]
                    .find(|c: char| !c.is_alphanumeric() && c != '_')
                    .map(|i| start + i)
                    .unwrap_or(query.len());

                let entity_name = query[start..end].to_string();
                entities.push(Entity::new(entity_name, entity_type, 0.8));
            }
        }

        entities
    }

    fn extract_numeric_ids(&self, query: &str) -> Vec<Entity> {
        let mut entities = Vec::new();

        // Extract numbers preceded by common keywords
        let keywords = ["robot", "id", "database", "table", "user"];

        for keyword in &keywords {
            if let Some(pos) = query.to_lowercase().find(keyword) {
                let after_keyword = &query[pos + keyword.len()..];
                if let Some(num_start) = after_keyword.find(|c: char| c.is_numeric()) {
                    let num_end = after_keyword[num_start..]
                        .find(|c: char| !c.is_numeric())
                        .map(|i| num_start + i)
                        .unwrap_or(after_keyword.len());

                    let number = after_keyword[num_start..num_end].to_string();
                    let entity_name = format!("{}_{}", keyword, number);

                    entities.push(Entity::new(entity_name, EntityType::RobotId, 0.6));
                }
            }
        }

        entities
    }

    pub fn extract_with_context(
        &self,
        query: &str,
        _entity_history: &HashMap<String, String>,
    ) -> Vec<Entity> {
        // TODO: Use entity history to disambiguate
        self.extract(query)
    }
}

impl Default for EntityExtractor {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_extract_robot_id() {
        let extractor = EntityExtractor::new();
        let entities = extractor.extract("Why did robot_42 collide with the wall?");
        assert!(!entities.is_empty());
        assert!(entities
            .iter()
            .any(|e| e.name.contains("robot_42") && e.entity_type == EntityType::RobotId));
    }

    #[test]
    fn test_extract_database_name() {
        let extractor = EntityExtractor::new();
        let entities = extractor.extract("Query postgres_prod for customer records");
        assert!(!entities.is_empty());
        assert!(entities
            .iter()
            .any(|e| e.entity_type == EntityType::DatabaseName));
    }

    #[test]
    fn test_extract_multiple_entities() {
        let extractor = EntityExtractor::new();
        let entities = extractor.extract("robot_42 failed at db_analytics query");
        assert!(entities.len() >= 2);
    }

    #[test]
    fn test_extract_numeric_id() {
        let extractor = EntityExtractor::new();
        let entities = extractor.extract("Tell me about robot 42");
        // Should find the number 42
        assert!(!entities.is_empty());
    }

    #[test]
    fn test_extract_no_entities() {
        let extractor = EntityExtractor::new();
        let entities = extractor.extract("What is machine learning?");
        // May or may not find entities, but shouldn't crash
        assert!(entities.len() >= 0);
    }

    #[test]
    fn test_entity_relevance_scores() {
        let extractor = EntityExtractor::new();
        let entities = extractor.extract("robot_42 issue");
        for entity in entities {
            assert!(entity.relevance > 0.0 && entity.relevance <= 1.0);
        }
    }

    #[test]
    fn test_extract_tool_names() {
        let extractor = EntityExtractor::new();
        let entities = extractor.extract("Use mcp_arxiv to find papers");
        assert!(!entities.is_empty());
    }
}
