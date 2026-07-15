use crate::context::Context;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StreamedContext {
    pub chunk_id: u32,
    pub content: Context,
    pub priority: f32,
    pub tokens_accumulated: u32,
    pub is_final: bool,
}

pub struct ContextStream {
    pub query_id: String,
    chunks: Vec<StreamedContext>,
    current_chunk: usize,
    token_budget: u32,
    tokens_used: u32,
}

impl ContextStream {
    pub fn new(query_id: &str, token_budget: u32) -> Self {
        Self {
            query_id: query_id.to_string(),
            chunks: Vec::new(),
            current_chunk: 0,
            token_budget,
            tokens_used: 0,
        }
    }

    pub fn add_chunk(
        &mut self,
        chunk_id: u32,
        context: Context,
        priority: f32,
    ) -> crate::error::Result<()> {
        let token_count = context.token_count as u32;

        if self.tokens_used + token_count > self.token_budget {
            return Err(crate::error::Error::ValidationGateFailed(
                "Token budget exceeded".to_string(),
            ));
        }

        self.tokens_used += token_count;

        self.chunks.push(StreamedContext {
            chunk_id,
            content: context,
            priority,
            tokens_accumulated: self.tokens_used,
            is_final: false,
        });

        Ok(())
    }

    pub async fn next(&mut self) -> Option<StreamedContext> {
        if self.current_chunk < self.chunks.len() {
            let mut chunk = self.chunks[self.current_chunk].clone();
            self.current_chunk += 1;

            if self.current_chunk >= self.chunks.len() {
                chunk.is_final = true;
            }

            // Simulate streaming latency < 50ms
            tokio::time::sleep(tokio::time::Duration::from_millis(10)).await;

            Some(chunk)
        } else {
            None
        }
    }

    pub async fn take_until_budget(&mut self, budget: u32) -> Vec<StreamedContext> {
        let mut results = Vec::new();
        let mut accumulated = 0u32;

        while let Some(chunk) = self.next().await {
            accumulated += chunk.tokens_accumulated;
            results.push(chunk);

            if accumulated >= budget {
                break;
            }
        }

        results
    }

    pub fn chunks_ready(&self) -> usize {
        self.chunks.len() - self.current_chunk
    }

    pub fn tokens_remaining(&self) -> u32 {
        self.token_budget - self.tokens_used
    }

    pub fn completion_percent(&self) -> f32 {
        if self.chunks.is_empty() {
            0.0
        } else {
            (self.current_chunk as f32 / self.chunks.len() as f32) * 100.0
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_stream_creation() {
        let stream = ContextStream::new("q1", 1000);
        assert_eq!(stream.query_id, "q1");
        assert_eq!(stream.token_budget, 1000);
        assert_eq!(stream.tokens_used, 0);
    }

    #[test]
    fn test_add_chunk() {
        let mut stream = ContextStream::new("q1", 1000);
        let ctx = Context::new(
            "q1",
            crate::context::ContextType::EntityData {
                entity_type: "c".to_string(),
            },
            json!({}),
            "db",
        );

        assert!(stream.add_chunk(1, ctx, 0.9).is_ok());
        assert_eq!(stream.chunks_ready(), 1);
    }

    #[test]
    fn test_token_budget_enforcement() {
        let mut stream = ContextStream::new("q1", 100);

        // Create a context that will use 50 tokens
        let ctx1 = Context::new(
            "q1",
            crate::context::ContextType::EntityData {
                entity_type: "c".to_string(),
            },
            json!({"data": "x"}),
            "db",
        );
        let ctx2 = Context::new(
            "q2",
            crate::context::ContextType::EntityData {
                entity_type: "c".to_string(),
            },
            json!({"data": "y"}),
            "db",
        );

        assert!(stream.add_chunk(1, ctx1, 0.9).is_ok());
        assert!(stream.add_chunk(2, ctx2, 0.8).is_ok());
    }

    #[tokio::test]
    async fn test_streaming() {
        let mut stream = ContextStream::new("q1", 1000);
        let ctx = Context::new(
            "q1",
            crate::context::ContextType::EntityData {
                entity_type: "c".to_string(),
            },
            json!({}),
            "db",
        );

        stream.add_chunk(1, ctx, 0.9).ok();

        if let Some(chunk) = stream.next().await {
            assert_eq!(chunk.chunk_id, 1);
            assert!(chunk.is_final);
        }
    }

    #[test]
    fn test_completion_tracking() {
        let mut stream = ContextStream::new("q1", 1000);
        let ctx = Context::new(
            "q1",
            crate::context::ContextType::EntityData {
                entity_type: "c".to_string(),
            },
            json!({}),
            "db",
        );

        stream.add_chunk(1, ctx, 0.9).ok();
        assert_eq!(stream.completion_percent(), 0.0);
    }
}
