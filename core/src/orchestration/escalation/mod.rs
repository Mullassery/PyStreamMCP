#[derive(Debug, Clone)]
pub struct EscalationChain;

pub struct EscalationManager;

impl EscalationManager {
    pub fn new() -> Self {
        Self
    }
}

impl Default for EscalationManager {
    fn default() -> Self {
        Self::new()
    }
}
