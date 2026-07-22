pub mod intent;
pub mod capabilities;
pub mod selection;
pub mod optimization;
pub mod enrichment;
pub mod memory;
pub mod execution;
pub mod fusion;
pub mod synthesis;
pub mod escalation;
pub mod observability;
pub mod learning;

pub use intent::{IntentClassifier, IntentResult, IntentCategory, Entity, EntityExtractor};
pub use capabilities::{CapabilityRegistry, MCPServerProfile, Capability};
pub use selection::{ToolSelector, ToolSelection, SelectedTool};
pub use optimization::{QueryOptimizer, OptimizedQuery};
pub use enrichment::{ContextEnricher, EnrichedRequest};
pub use memory::{MemoryStore, MemoryEntry, MemoryLookup};
pub use execution::{RetrievalExecutor, RetrievalStage};
pub use fusion::{Deduplicator, FusionEngine};
pub use synthesis::{Synthesizer, SynthesizedResponse};
pub use escalation::{EscalationManager, EscalationChain};
pub use observability::{DecisionTracer, DecisionTrace};
pub use learning::{LearningEngine, RoutingPattern};

/// Main orchestration hub that coordinates all layers
pub struct MCPOrchestrationHub {
    pub intent_classifier: IntentClassifier,
    pub entity_extractor: EntityExtractor,
    pub capability_registry: CapabilityRegistry,
    pub tool_selector: ToolSelector,
    pub query_optimizer: QueryOptimizer,
    pub context_enricher: ContextEnricher,
    pub memory_layer: MemoryStore,
}

impl MCPOrchestrationHub {
    pub fn new() -> Self {
        Self {
            intent_classifier: IntentClassifier::new(),
            entity_extractor: EntityExtractor::new(),
            capability_registry: CapabilityRegistry::new(),
            tool_selector: ToolSelector::new(),
            query_optimizer: QueryOptimizer::new(),
            context_enricher: ContextEnricher::new(),
            memory_layer: MemoryStore::new(),
        }
    }
}
