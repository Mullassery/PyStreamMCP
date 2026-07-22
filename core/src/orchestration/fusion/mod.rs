#[derive(Debug, Clone)]
pub struct Deduplicator;

pub struct FusionEngine;

impl FusionEngine {
    pub fn new() -> Self {
        Self
    }
}

impl Default for FusionEngine {
    fn default() -> Self {
        Self::new()
    }
}
