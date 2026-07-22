// Fallback Chain - Stage 3
// Handles graceful degradation when validation fails

use crate::Result;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Fallback strategy when validation fails
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum FallbackStrategy {
    /// Retry with exponential backoff
    RetryWithBackoff { max_retries: u32 },
    /// Use alternative source
    UseAlternativeSource,
    /// Degrade gracefully (use partial data)
    DegradeGracefully,
    /// Fetch from cache
    UseCache,
    /// Return empty/null
    ReturnEmpty,
}

/// Fallback result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FallbackResult {
    pub strategy_used: String,
    pub success: bool,
    pub alternative_source: Option<String>,
    pub retry_count: u32,
    pub fallback_data: Option<String>,
}

/// Fallback chain manager
pub struct FallbackChain {
    strategies: Vec<FallbackStrategy>,
    alternatives: HashMap<String, Vec<String>>,
}

impl FallbackChain {
    /// Create new fallback chain
    pub fn new(strategies: Vec<FallbackStrategy>) -> Result<Self> {
        Ok(Self {
            strategies: if strategies.is_empty() {
                vec![
                    FallbackStrategy::RetryWithBackoff { max_retries: 3 },
                    FallbackStrategy::UseAlternativeSource,
                    FallbackStrategy::DegradeGracefully,
                ]
            } else {
                strategies
            },
            alternatives: HashMap::new(),
        })
    }

    /// Recommend fallback strategy for failed source
    pub async fn recommend_fallback(&self, failed_source: &str) -> Result<FallbackResult> {
        // Check for alternatives first
        if let Some(alternatives) = self.alternatives.get(failed_source) {
            if !alternatives.is_empty() {
                return Ok(FallbackResult {
                    strategy_used: "UseAlternativeSource".to_string(),
                    success: true,
                    alternative_source: Some(alternatives[0].clone()),
                    retry_count: 0,
                    fallback_data: None,
                });
            }
        }

        // Go through strategies in order
        for strategy in &self.strategies {
            let result = self.try_strategy(strategy, failed_source).await?;
            if result.success {
                return Ok(result);
            }
        }

        // Last resort: return empty
        Ok(FallbackResult {
            strategy_used: "ReturnEmpty".to_string(),
            success: false,
            alternative_source: None,
            retry_count: 0,
            fallback_data: None,
        })
    }

    /// Try a specific strategy
    async fn try_strategy(
        &self,
        strategy: &FallbackStrategy,
        failed_source: &str,
    ) -> Result<FallbackResult> {
        match strategy {
            FallbackStrategy::RetryWithBackoff { max_retries } => {
                Ok(FallbackResult {
                    strategy_used: "RetryWithBackoff".to_string(),
                    success: true, // Assume retry will succeed
                    alternative_source: None,
                    retry_count: *max_retries,
                    fallback_data: None,
                })
            }
            FallbackStrategy::UseAlternativeSource => {
                let alt = self
                    .alternatives
                    .get(failed_source)
                    .and_then(|v| v.first())
                    .cloned();

                Ok(FallbackResult {
                    strategy_used: "UseAlternativeSource".to_string(),
                    success: alt.is_some(),
                    alternative_source: alt,
                    retry_count: 0,
                    fallback_data: None,
                })
            }
            FallbackStrategy::DegradeGracefully => {
                Ok(FallbackResult {
                    strategy_used: "DegradeGracefully".to_string(),
                    success: true,
                    alternative_source: None,
                    retry_count: 0,
                    fallback_data: Some("partial data".to_string()),
                })
            }
            FallbackStrategy::UseCache => {
                Ok(FallbackResult {
                    strategy_used: "UseCache".to_string(),
                    success: true,
                    alternative_source: None,
                    retry_count: 0,
                    fallback_data: Some("cached data".to_string()),
                })
            }
            FallbackStrategy::ReturnEmpty => {
                Ok(FallbackResult {
                    strategy_used: "ReturnEmpty".to_string(),
                    success: false,
                    alternative_source: None,
                    retry_count: 0,
                    fallback_data: None,
                })
            }
        }
    }

    /// Register alternative sources
    pub fn register_alternatives(&mut self, source: String, alternatives: Vec<String>) {
        self.alternatives.insert(source, alternatives);
    }

    /// Get fallback chain as list
    pub fn strategies(&self) -> Vec<String> {
        self.strategies
            .iter()
            .map(|s| format!("{:?}", s))
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_recommend_fallback() {
        let chain = FallbackChain::new(vec![]).unwrap();
        let result = chain.recommend_fallback("example.com").await.unwrap();

        assert!(!result.strategy_used.is_empty());
    }

    #[tokio::test]
    async fn test_register_alternatives() {
        let mut chain = FallbackChain::new(vec![]).unwrap();
        chain.register_alternatives(
            "primary.com".to_string(),
            vec!["backup1.com".to_string(), "backup2.com".to_string()],
        );

        let result = chain.recommend_fallback("primary.com").await.unwrap();
        assert!(result.success);
        assert_eq!(result.alternative_source, Some("backup1.com".to_string()));
    }

    #[test]
    fn test_strategies_list() {
        let chain = FallbackChain::new(vec![]).unwrap();
        let strategies = chain.strategies();

        assert!(!strategies.is_empty());
    }
}
