// Token Budget System - Stage 2
// Tiered token budgets with intent-based allocation and multiplier support

use crate::selective_retrieval::types::*;
use crate::{Error, Result};
use serde::{Deserialize, Serialize};

/// Token budget tier (hard limits, never exceeded)
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum BudgetTier {
    /// Minimal: 50-100 tokens (factual lookups, definitions)
    Minimal { min: u32, max: u32 },
    /// Standard: 500-1000 tokens (understanding, examples)
    Standard { min: u32, max: u32 },
    /// Large: 2000-3000 tokens (detailed analysis, trade-offs)
    Large { min: u32, max: u32 },
    /// Comprehensive: 5000-8000 tokens (full context, alternatives)
    Comprehensive { min: u32, max: u32 },
}

impl BudgetTier {
    /// Get min tokens for this tier
    pub fn min(&self) -> u32 {
        match self {
            BudgetTier::Minimal { min, .. } => *min,
            BudgetTier::Standard { min, .. } => *min,
            BudgetTier::Large { min, .. } => *min,
            BudgetTier::Comprehensive { min, .. } => *min,
        }
    }

    /// Get max tokens for this tier
    pub fn max(&self) -> u32 {
        match self {
            BudgetTier::Minimal { max, .. } => *max,
            BudgetTier::Standard { max, .. } => *max,
            BudgetTier::Large { max, .. } => *max,
            BudgetTier::Comprehensive { max, .. } => *max,
        }
    }

    /// Get multiplier ceiling for this tier
    pub fn multiplier_ceiling(&self) -> f64 {
        // Allow multipliers to expand tier, but cap expansion
        match self {
            BudgetTier::Minimal => 1.5,      // Can expand to 150 (1.5x)
            BudgetTier::Standard => 1.5,     // Can expand to 1500 (1.5x)
            BudgetTier::Large => 1.5,        // Can expand to 4500 (1.5x)
            BudgetTier::Comprehensive => 1.3, // Can expand to 10400 (1.3x)
        }
    }

    /// Get name of tier
    pub fn name(&self) -> &'static str {
        match self {
            BudgetTier::Minimal { .. } => "Minimal",
            BudgetTier::Standard { .. } => "Standard",
            BudgetTier::Large { .. } => "Large",
            BudgetTier::Comprehensive { .. } => "Comprehensive",
        }
    }
}

/// Token budget manager
pub struct TokenBudget {
    config: BudgetConfig,
}

/// Configuration for token budgets
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BudgetConfig {
    /// Enable strict enforcement (fail if over budget)
    pub strict_mode: bool,
    /// Log when approaching budget
    pub warn_at_percent: u32,
}

impl Default for BudgetConfig {
    fn default() -> Self {
        Self {
            strict_mode: false,
            warn_at_percent: 90,
        }
    }
}

impl TokenBudget {
    /// Create new token budget manager
    pub fn new(config: BudgetConfig) -> Result<Self> {
        Ok(Self { config })
    }

    /// Assign tier based on query complexity
    pub fn assign_tier(&self, complexity: QueryComplexity) -> Result<BudgetTier> {
        Ok(match complexity {
            QueryComplexity::Simple => BudgetTier::Minimal { min: 50, max: 100 },
            QueryComplexity::Moderate => BudgetTier::Standard { min: 500, max: 1000 },
            QueryComplexity::Complex => BudgetTier::Large { min: 2000, max: 3000 },
            QueryComplexity::VeryComplex => BudgetTier::Comprehensive { min: 5000, max: 8000 },
        })
    }

    /// Allocate tokens within tier based on intent
    pub fn allocate_for_intent(
        &self,
        tier: &BudgetTier,
        intent: &QueryIntent,
    ) -> Result<u32> {
        let min = tier.min();
        let max = tier.max();
        let range = max - min;

        let allocation = match intent {
            QueryIntent::Factual => min, // Minimal info needed
            QueryIntent::Conceptual => min + (range / 3), // Mid-range
            QueryIntent::Detailed => min + (range * 2 / 3), // High range
            QueryIntent::Complex => max, // Full budget
        };

        Ok(allocation)
    }

    /// Calculate final budget with multiplier
    pub fn calculate_final_budget(
        &self,
        intent_allocation: u32,
        tier: &BudgetTier,
        multiplier_factor: f64,
    ) -> Result<u32> {
        let expanded = (intent_allocation as f64 * multiplier_factor) as u32;
        let ceiling = (tier.max() as f64 * tier.multiplier_ceiling()) as u32;

        // Cap at ceiling
        let final_budget = expanded.min(ceiling);

        Ok(final_budget)
    }

    /// Select content items up to token budget
    pub async fn select_within_budget(
        &self,
        items: Vec<ContentItem>,
        budget: u32,
    ) -> Result<Vec<ContentItem>> {
        let mut selected = vec![];
        let mut used_tokens = 0u32;

        for item in items {
            if used_tokens + item.tokens > budget {
                // Budget exhausted, stop
                break;
            }

            used_tokens += item.tokens;
            selected.push(item);
        }

        if self.config.strict_mode && used_tokens > budget {
            return Err(Error::Generic(format!(
                "Token budget exceeded: {} > {}",
                used_tokens, budget
            )));
        }

        Ok(selected)
    }

    /// Get budget stats for debugging
    pub fn budget_stats(&self, used: u32, budget: u32) -> BudgetStats {
        let percent_used = if budget > 0 {
            (used as f64 / budget as f64 * 100.0) as u32
        } else {
            0
        };

        BudgetStats {
            used_tokens: used,
            total_budget: budget,
            percent_used,
            remaining: budget.saturating_sub(used),
        }
    }
}

/// Budget statistics
#[derive(Debug, Clone)]
pub struct BudgetStats {
    pub used_tokens: u32,
    pub total_budget: u32,
    pub percent_used: u32,
    pub remaining: u32,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tier_assignment() {
        let config = BudgetConfig::default();
        let budget = TokenBudget::new(config).unwrap();

        let tier = budget.assign_tier(QueryComplexity::Moderate).unwrap();
        assert_eq!(tier.min(), 500);
        assert_eq!(tier.max(), 1000);
    }

    #[test]
    fn test_intent_allocation() {
        let config = BudgetConfig::default();
        let budget = TokenBudget::new(config).unwrap();
        let tier = BudgetTier::Standard { min: 500, max: 1000 };

        let factual = budget.allocate_for_intent(&tier, &QueryIntent::Factual).unwrap();
        let complex = budget.allocate_for_intent(&tier, &QueryIntent::Complex).unwrap();

        assert!(factual < complex); // Factual uses less
    }

    #[test]
    fn test_multiplier_expansion() {
        let config = BudgetConfig::default();
        let budget = TokenBudget::new(config).unwrap();
        let tier = BudgetTier::Standard { min: 500, max: 1000 };

        let base = 750u32;
        let expanded = budget.calculate_final_budget(base, &tier, 2.0).unwrap();

        // 750 * 2.0 = 1500, but capped at 1000 * 1.5 = 1500
        assert!(expanded <= 1500);
    }

    #[tokio::test]
    async fn test_select_within_budget() {
        let config = BudgetConfig::default();
        let budget = TokenBudget::new(config).unwrap();

        let items = vec![
            ContentItem {
                id: "1".to_string(),
                item_type: ItemType::WebSection,
                content: "First".to_string(),
                tokens: 300,
                metadata: ItemMetadata {
                    source: "test".to_string(),
                    relevance_hint: 0.9,
                    timestamp: 0,
                    informativeness: 0.8,
                    tags: vec![],
                },
            },
            ContentItem {
                id: "2".to_string(),
                item_type: ItemType::WebSection,
                content: "Second".to_string(),
                tokens: 400,
                metadata: ItemMetadata {
                    source: "test".to_string(),
                    relevance_hint: 0.7,
                    timestamp: 0,
                    informativeness: 0.7,
                    tags: vec![],
                },
            },
            ContentItem {
                id: "3".to_string(),
                item_type: ItemType::WebSection,
                content: "Third".to_string(),
                tokens: 500,
                metadata: ItemMetadata {
                    source: "test".to_string(),
                    relevance_hint: 0.5,
                    timestamp: 0,
                    informativeness: 0.5,
                    tags: vec![],
                },
            },
        ];

        let selected = budget.select_within_budget(items, 700).await.unwrap();

        assert_eq!(selected.len(), 2); // First two fit, third exceeds budget
        assert_eq!(selected[0].id, "1");
        assert_eq!(selected[1].id, "2");
    }
}
