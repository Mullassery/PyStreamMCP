#[derive(Debug, Clone)]
pub struct MemoryEntry {
    pub query: String,
}

pub struct MemoryStore;

impl MemoryStore {
    pub fn new() -> Self {
        Self
    }
}

impl Default for MemoryStore {
    fn default() -> Self {
        Self::new()
    }
}

pub struct MemoryLookup;
