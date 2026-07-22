#[derive(Debug, Clone)]
pub struct SynthesizedResponse;

pub struct Synthesizer;

impl Synthesizer {
    pub fn new() -> Self {
        Self
    }
}

impl Default for Synthesizer {
    fn default() -> Self {
        Self::new()
    }
}
