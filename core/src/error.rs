use thiserror::Error;

pub type Result<T> = std::result::Result<T, Error>;

#[derive(Error, Debug)]
pub enum Error {
    #[error("Query not found: {0}")]
    QueryNotFound(String),

    #[error("Context not found: {0}")]
    ContextNotFound(String),

    #[error("Discovery error: {0}")]
    DiscoveryError(String),

    #[error("Optimization error: {0}")]
    OptimizationError(String),

    #[error("Query planning failed: {0}")]
    PlanningError(String),

    #[error("Token budget exceeded: {0}")]
    TokenBudgetExceeded(String),

    #[error("Validation gate failed: {0}")]
    ValidationGateFailed(String),

    #[error("Storage error: {0}")]
    StorageError(String),

    #[error("Database error: {0}")]
    DatabaseError(#[from] rusqlite::Error),

    #[error("Serialization error: {0}")]
    SerializationError(#[from] serde_json::Error),

    #[error("Configuration error: {0}")]
    ConfigError(String),

    #[error("Timeout: {0}")]
    Timeout(String),
}

// NOTE: Architectural Boundaries
// PyStreamMCP focuses exclusively on agent intelligence:
// ✓ Query planning and optimization
// ✓ Context discovery
// ✓ Cost optimization (token reduction)
// ✓ MCP (Model Context Protocol) integration
//
// We deliberately do NOT have:
// ✗ Data validation (StatGuardian owns validation)
// ✗ Data activation (PyReverseETL owns activation)
// ✗ Audience creation (ClusterAudienceKit owns segmentation)
// ✗ Journey orchestration (PyCustomerJourney owns journeys)
//
// Integration:
// → Consumes validated data from StatGuardian
// → Uses activated context from PyReverseETL
// → Works with agent frameworks and LLMs
