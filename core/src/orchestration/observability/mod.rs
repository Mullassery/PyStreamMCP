#[derive(Debug, Clone)]
pub struct DecisionTrace;

pub struct DecisionTracer;

impl DecisionTracer {
    pub fn new() -> Self {
        Self
    }
}

impl Default for DecisionTracer {
    fn default() -> Self {
        Self::new()
    }
}
