// Token Multiplier System - Stage 2
// Developer-configurable keyword-based token budget expansion

use crate::Result;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Token multiplier rule (keyword → expansion factor)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MultiplierRule {
    /// Keyword to trigger this multiplier
    pub keyword: String,
    /// Expansion factor (e.g., 2.0 = 2x budget)
    pub multiplier: f64,
    /// Category for grouping (optional)
    pub category: Option<String>,
}

impl MultiplierRule {
    /// Create new multiplier rule
    pub fn new(keyword: impl Into<String>, multiplier: f64) -> Self {
        Self {
            keyword: keyword.into(),
            multiplier,
            category: None,
        }
    }

    /// Add category
    pub fn with_category(mut self, category: impl Into<String>) -> Self {
        self.category = Some(category.into());
        self
    }
}

/// Token multiplier engine
pub struct TokenMultiplier {
    rules: HashMap<String, (f64, Option<String>)>,
}

impl TokenMultiplier {
    /// Create new multiplier engine with rules
    pub fn new(rules: Vec<MultiplierRule>) -> Result<Self> {
        let mut map = HashMap::new();

        for rule in rules {
            map.insert(rule.keyword.to_lowercase(), (rule.multiplier, rule.category));
        }

        // Add default multiplier rules
        let defaults = Self::default_rules();
        for (keyword, multiplier, category) in defaults {
            let key = keyword.to_lowercase();
            if !map.contains_key(&key) {
                map.insert(key, (multiplier, category));
            }
        }

        Ok(Self { rules: map })
    }

    /// Get default multiplier rules
    fn default_rules() -> Vec<(&'static str, f64, Option<&'static str>)> {
        vec![
            // Critical scenarios: 2x
            ("critical", 2.0, Some("priority")),
            ("emergency", 2.0, Some("priority")),
            ("urgent", 2.0, Some("priority")),
            ("production_incident", 2.0, Some("priority")),
            ("data_loss", 2.0, Some("priority")),
            // Domain-specific: 1.5x
            ("financial", 1.5, Some("domain")),
            ("compliance", 1.5, Some("domain")),
            ("legal", 1.5, Some("domain")),
            ("security", 1.5, Some("domain")),
            ("medical", 1.5, Some("domain")),
            ("healthcare", 1.5, Some("domain")),
            // Debug/Analysis: 1.2x
            ("debug", 1.2, Some("analysis")),
            ("troubleshoot", 1.2, Some("analysis")),
            ("analyze", 1.2, Some("analysis")),
            ("investigate", 1.2, Some("analysis")),
            ("root_cause", 1.2, Some("analysis")),
        ]
    }

    /// Calculate multiplier for query
    pub fn calculate_multiplier(&self, query: &str) -> Result<f64> {
        let query_lower = query.to_lowercase();

        // Find all matching keywords
        let mut matches: Vec<(String, f64)> = self
            .rules
            .iter()
            .filter_map(|(keyword, (multiplier, _))| {
                if query_lower.contains(keyword) {
                    Some((keyword.clone(), *multiplier))
                } else {
                    None
                }
            })
            .collect();

        // Take highest multiplier (don't stack)
        if let Some((_, multiplier)) = matches.iter().max_by(|a, b| {
            a.1.partial_cmp(&b.1)
                .unwrap_or(std::cmp::Ordering::Equal)
        }) {
            Ok(*multiplier)
        } else {
            Ok(1.0) // No multiplier
        }
    }

    /// Add custom rule
    pub fn add_rule(&mut self, rule: MultiplierRule) {
        self.rules.insert(
            rule.keyword.to_lowercase(),
            (rule.multiplier, rule.category),
        );
    }

    /// Get all rules
    pub fn get_rules(&self) -> Vec<(String, f64, Option<String>)> {
        self.rules
            .iter()
            .map(|(k, (m, c))| (k.clone(), *m, c.clone()))
            .collect()
    }

    /// Get rules by category
    pub fn get_rules_by_category(&self, category: &str) -> Vec<(String, f64)> {
        self.rules
            .iter()
            .filter_map(|(k, (m, c))| {
                if c.as_ref().map_or(false, |cat| cat == category) {
                    Some((k.clone(), *m))
                } else {
                    None
                }
            })
            .collect()
    }

    /// Clear all custom rules (keep defaults)
    pub fn reset_to_defaults(&mut self) {
        self.rules.clear();
        for (keyword, multiplier, category) in Self::default_rules() {
            self.rules.insert(
                keyword.to_lowercase(),
                (
                    multiplier,
                    category.map(|c| c.to_string()),
                ),
            );
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_rules() {
        let multiplier = TokenMultiplier::new(vec![]).unwrap();

        // Should have default rules
        let rules = multiplier.get_rules();
        assert!(!rules.is_empty());
    }

    #[test]
    fn test_calculate_multiplier_critical() {
        let multiplier = TokenMultiplier::new(vec![]).unwrap();

        let factor = multiplier.calculate_multiplier("CRITICAL bug in production").unwrap();
        assert_eq!(factor, 2.0);
    }

    #[test]
    fn test_calculate_multiplier_financial() {
        let multiplier = TokenMultiplier::new(vec![]).unwrap();

        let factor = multiplier.calculate_multiplier("Financial compliance requirements").unwrap();
        assert_eq!(factor, 1.5);
    }

    #[test]
    fn test_calculate_multiplier_debug() {
        let multiplier = TokenMultiplier::new(vec![]).unwrap();

        let factor = multiplier.calculate_multiplier("Debug troubleshooting guide").unwrap();
        assert_eq!(factor, 1.2);
    }

    #[test]
    fn test_no_multiplier() {
        let multiplier = TokenMultiplier::new(vec![]).unwrap();

        let factor = multiplier.calculate_multiplier("regular query").unwrap();
        assert_eq!(factor, 1.0);
    }

    #[test]
    fn test_highest_multiplier_wins() {
        let multiplier = TokenMultiplier::new(vec![]).unwrap();

        // Query has both critical (2.0) and debug (1.2) keywords
        let factor = multiplier.calculate_multiplier("debug critical incident").unwrap();
        assert_eq!(factor, 2.0); // Takes highest
    }

    #[test]
    fn test_add_custom_rule() {
        let mut multiplier = TokenMultiplier::new(vec![]).unwrap();

        let rule = MultiplierRule::new("blockchain", 3.0).with_category("emerging");
        multiplier.add_rule(rule);

        let factor = multiplier.calculate_multiplier("blockchain analysis").unwrap();
        assert_eq!(factor, 3.0);
    }

    #[test]
    fn test_get_rules_by_category() {
        let multiplier = TokenMultiplier::new(vec![]).unwrap();

        let priority_rules = multiplier.get_rules_by_category("priority");
        assert!(!priority_rules.is_empty());

        // All should have 2.0 multiplier
        for (_, multiplier_factor) in priority_rules {
            assert_eq!(multiplier_factor, 2.0);
        }
    }

    #[test]
    fn test_case_insensitive() {
        let multiplier = TokenMultiplier::new(vec![]).unwrap();

        let factor1 = multiplier.calculate_multiplier("CRITICAL").unwrap();
        let factor2 = multiplier.calculate_multiplier("critical").unwrap();
        let factor3 = multiplier.calculate_multiplier("Critical").unwrap();

        assert_eq!(factor1, factor2);
        assert_eq!(factor2, factor3);
    }
}
