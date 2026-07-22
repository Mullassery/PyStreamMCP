// Quality Policies & SLA Enforcement - Stage 3
// Defines and enforces quality SLAs

use crate::Result;
use serde::{Deserialize, Serialize};

/// Quality policy
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QualityPolicy {
    pub min_quality_score: f64,      // 0-1, default 0.75
    pub min_confidence: f64,          // 0-1, default 0.7
    pub max_latency_ms: u32,         // Default 500ms
    pub enforce_strict: bool,         // Fail on violation vs warn
}

impl Default for QualityPolicy {
    fn default() -> Self {
        Self {
            min_quality_score: 0.75,
            min_confidence: 0.7,
            max_latency_ms: 500,
            enforce_strict: false,
        }
    }
}

/// SLA configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SLAConfig {
    pub quality_sla: f64,     // Minimum quality (0-1)
    pub latency_sla_ms: u32,  // Maximum latency (ms)
    pub availability_sla: f64, // Availability percentage
}

impl Default for SLAConfig {
    fn default() -> Self {
        Self {
            quality_sla: 0.8,
            latency_sla_ms: 100,
            availability_sla: 0.99,
        }
    }
}

/// Policy enforcer
pub struct PolicyEnforcer {
    policy: QualityPolicy,
    sla_config: SLAConfig,
    violations: Vec<PolicyViolation>,
}

/// Policy violation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyViolation {
    pub policy_type: String,
    pub expected: String,
    pub actual: String,
    pub timestamp: i64,
}

/// SLA check result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SLACheckResult {
    pub quality_met: bool,
    pub latency_met: bool,
    pub overall_met: bool,
    pub violations: Vec<String>,
}

impl PolicyEnforcer {
    /// Create new policy enforcer
    pub fn new(policy: QualityPolicy) -> Result<Self> {
        Ok(Self {
            policy,
            sla_config: SLAConfig::default(),
            violations: Vec::new(),
        })
    }

    /// Check SLA compliance
    pub fn check_sla(&self, quality_score: f64, latency_ms: u32) -> Result<SLACheckResult> {
        let quality_met = quality_score >= self.policy.min_quality_score;
        let latency_met = latency_ms <= self.policy.max_latency_ms;
        let overall_met = quality_met && latency_met;

        let mut violations = vec![];

        if !quality_met {
            violations.push(format!(
                "Quality {} < minimum {}",
                quality_score, self.policy.min_quality_score
            ));
        }

        if !latency_met {
            violations.push(format!(
                "Latency {}ms > maximum {}ms",
                latency_ms, self.policy.max_latency_ms
            ));
        }

        Ok(SLACheckResult {
            quality_met,
            latency_met,
            overall_met,
            violations,
        })
    }

    /// Enforce policy (fail or warn based on mode)
    pub fn enforce_policy(
        &mut self,
        quality_score: f64,
        latency_ms: u32,
    ) -> Result<PolicyEnforcementResult> {
        let sla_result = self.check_sla(quality_score, latency_ms)?;

        if !sla_result.overall_met {
            if self.policy.enforce_strict {
                // Strict mode: fail immediately
                return Ok(PolicyEnforcementResult {
                    allowed: false,
                    enforced: true,
                    reason: format!("SLA violations: {}", sla_result.violations.join("; ")),
                });
            } else {
                // Warning mode: log but allow
                self.record_violations(&sla_result.violations);
                return Ok(PolicyEnforcementResult {
                    allowed: true,
                    enforced: false,
                    reason: format!("SLA warnings: {}", sla_result.violations.join("; ")),
                });
            }
        }

        Ok(PolicyEnforcementResult {
            allowed: true,
            enforced: false,
            reason: "SLA met".to_string(),
        })
    }

    /// Record policy violations
    fn record_violations(&mut self, violations: &[String]) {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs() as i64;

        for violation in violations {
            self.violations.push(PolicyViolation {
                policy_type: "sla".to_string(),
                expected: "SLA compliance".to_string(),
                actual: violation.clone(),
                timestamp: now,
            });
        }
    }

    /// Get violation history
    pub fn violation_history(&self) -> Vec<PolicyViolation> {
        self.violations.clone()
    }

    /// Clear violations
    pub fn clear_violations(&mut self) {
        self.violations.clear();
    }

    /// Get compliance rate
    pub fn get_compliance_rate(&self) -> f64 {
        if self.violations.is_empty() {
            1.0
        } else {
            // Simplified: assume we evaluate every second
            let successful = 100; // Hypothetical
            let total = successful + self.violations.len();
            (successful as f64) / (total as f64)
        }
    }

    /// Update policy
    pub fn update_policy(&mut self, policy: QualityPolicy) {
        self.policy = policy;
    }
}

/// Policy enforcement result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyEnforcementResult {
    pub allowed: bool,
    pub enforced: bool,
    pub reason: String,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_check_sla_pass() {
        let enforcer = PolicyEnforcer::new(QualityPolicy::default()).unwrap();
        let result = enforcer.check_sla(0.9, 200).unwrap();

        assert!(result.quality_met);
        assert!(result.latency_met);
        assert!(result.overall_met);
        assert!(result.violations.is_empty());
    }

    #[test]
    fn test_check_sla_fail_quality() {
        let enforcer = PolicyEnforcer::new(QualityPolicy::default()).unwrap();
        let result = enforcer.check_sla(0.5, 200).unwrap();

        assert!(!result.quality_met);
        assert!(result.latency_met);
        assert!(!result.overall_met);
        assert!(!result.violations.is_empty());
    }

    #[test]
    fn test_check_sla_fail_latency() {
        let enforcer = PolicyEnforcer::new(QualityPolicy::default()).unwrap();
        let result = enforcer.check_sla(0.9, 1000).unwrap();

        assert!(result.quality_met);
        assert!(!result.latency_met);
        assert!(!result.overall_met);
        assert!(!result.violations.is_empty());
    }

    #[test]
    fn test_enforce_policy_strict() {
        let mut policy = QualityPolicy::default();
        policy.enforce_strict = true;
        let mut enforcer = PolicyEnforcer::new(policy).unwrap();

        let result = enforcer.enforce_policy(0.5, 200).unwrap();
        assert!(!result.allowed);
        assert!(result.enforced);
    }

    #[test]
    fn test_enforce_policy_relaxed() {
        let mut policy = QualityPolicy::default();
        policy.enforce_strict = false;
        let mut enforcer = PolicyEnforcer::new(policy).unwrap();

        let result = enforcer.enforce_policy(0.5, 200).unwrap();
        assert!(result.allowed);
        assert!(!result.enforced);
    }

    #[test]
    fn test_violation_history() {
        let mut policy = QualityPolicy::default();
        policy.enforce_strict = false;
        let mut enforcer = PolicyEnforcer::new(policy).unwrap();

        enforcer.enforce_policy(0.5, 200).unwrap();
        enforcer.enforce_policy(0.6, 1000).unwrap();

        let history = enforcer.violation_history();
        assert!(!history.is_empty());
    }
}
