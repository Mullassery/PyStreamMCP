#[derive(Debug, Clone)]
pub struct RoutingPattern;

pub struct LearningEngine;

impl LearningEngine {
    pub fn new() -> Self {
        Self
    }
}

impl Default for LearningEngine {
    fn default() -> Self {
        Self::new()
    }
}
