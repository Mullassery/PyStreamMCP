pub mod error;
pub mod query;
pub mod context;
pub mod discovery;
pub mod optimization;
pub mod storage;
pub mod statguardian;

pub use error::{Error, Result};
pub use query::Query;
pub use context::{Context, ContextType};
pub use discovery::Discovery;
pub use optimization::{OptimizationStrategy, CostMetrics};
pub use storage::Repository;
pub use statguardian::{ValidationGate, ValidationResult, ValidationStatus};
