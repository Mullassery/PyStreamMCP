#[derive(Debug, Clone)]
pub struct EnrichedRequest {
    pub query: String,
}

pub struct ContextEnricher;

impl ContextEnricher {
    pub fn new() -> Self {
        Self
    }
}

impl Default for ContextEnricher {
    fn default() -> Self {
        Self::new()
    }
}
