#[derive(Debug, Clone)]
pub struct RetrievalStage;

pub struct RetrievalExecutor;

impl RetrievalExecutor {
    pub fn new() -> Self {
        Self
    }
}

impl Default for RetrievalExecutor {
    fn default() -> Self {
        Self::new()
    }
}
