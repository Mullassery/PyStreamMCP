use serde::{Deserialize, Serialize};
use super::super::capabilities::MCPServerProfile;

/// Ranking breakdown for transparency
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RankingBreakdown {
    pub success_rate: (f32, f32),       // (value, weight: 0.35)
    pub domain_expertise: (f32, f32),   // (value, weight: 0.25)
    pub latency: (f32, f32),            // (value, weight: 0.15)
    pub cost_efficiency: (f32, f32),    // (value, weight: 0.10)
    pub data_freshness: (f32, f32),     // (value, weight: 0.10)
    pub availability: (f32, f32),       // (value, weight: 0.05)
}

impl RankingBreakdown {
    /// Calculate overall score from components
    pub fn overall_score(&self) -> f32 {
        self.success_rate.0 * self.success_rate.1
            + self.domain_expertise.0 * self.domain_expertise.1
            + self.latency.0 * self.latency.1
            + self.cost_efficiency.0 * self.cost_efficiency.1
            + self.data_freshness.0 * self.data_freshness.1
            + self.availability.0 * self.availability.1
    }

    /// Format as human-readable string
    pub fn explain(&self) -> String {
        format!(
            "Success rate: {:.1}% ({:.2}w) + Expertise: {:.1}% ({:.2}w) + Latency: {:.1}% ({:.2}w) + Cost: {:.1}% ({:.2}w) + Freshness: {:.1}% ({:.2}w) + Availability: {:.1}% ({:.2}w) = {:.2}",
            self.success_rate.0 * 100.0, self.success_rate.1,
            self.domain_expertise.0 * 100.0, self.domain_expertise.1,
            self.latency.0 * 100.0, self.latency.1,
            self.cost_efficiency.0 * 100.0, self.cost_efficiency.1,
            self.data_freshness.0 * 100.0, self.data_freshness.1,
            self.availability.0 * 100.0, self.availability.1,
            self.overall_score()
        )
    }
}

/// Ranked tool with breakdown
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolRanking {
    pub server_id: String,
    pub server_name: String,
    pub score: f32,
    pub rank: usize,
    pub breakdown: RankingBreakdown,
    pub explanation: String,
}

impl ToolRanking {
    pub fn new(
        server_id: String,
        server_name: String,
        score: f32,
        rank: usize,
        breakdown: RankingBreakdown,
    ) -> Self {
        Self {
            server_id,
            server_name,
            score,
            rank,
            breakdown: breakdown.clone(),
            explanation: breakdown.explain(),
        }
    }
}

/// Tool ranker with detailed scoring
pub struct ToolRanker;

impl ToolRanker {
    /// Rank a list of servers
    pub fn rank(servers: &[MCPServerProfile]) -> Vec<ToolRanking> {
        let mut rankings: Vec<ToolRanking> = servers
            .iter()
            .map(|server| Self::rank_single(server))
            .collect();

        // Sort by score descending
        rankings.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap_or(std::cmp::Ordering::Equal));

        // Assign ranks
        for (i, ranking) in rankings.iter_mut().enumerate() {
            ranking.rank = i + 1;
        }

        rankings
    }

    fn rank_single(server: &MCPServerProfile) -> ToolRanking {
        let success_rate = server.metadata.success_rate;
        let domain_expertise = server
            .capabilities
            .iter()
            .map(|c| c.domain_expertise)
            .max_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal))
            .unwrap_or(0.5);
        let latency = server.metadata.latency_score();
        let cost = server.metadata.cost_score();
        let freshness = server.metadata.data_freshness;
        let availability = server.metadata.health.score();

        let breakdown = RankingBreakdown {
            success_rate: (success_rate, 0.35),
            domain_expertise: (domain_expertise, 0.25),
            latency: (latency, 0.15),
            cost_efficiency: (cost, 0.10),
            data_freshness: (freshness, 0.10),
            availability: (availability, 0.05),
        };

        let score = breakdown.overall_score();

        ToolRanking::new(
            server.id.clone(),
            server.name.clone(),
            score,
            0, // Will be set after sorting
            breakdown,
        )
    }

    /// Get top N tools
    pub fn top_n(servers: &[MCPServerProfile], n: usize) -> Vec<ToolRanking> {
        let mut rankings = Self::rank(servers);
        rankings.truncate(n);
        rankings
    }

    /// Filter by minimum score
    pub fn with_min_score(servers: &[MCPServerProfile], min_score: f32) -> Vec<ToolRanking> {
        Self::rank(servers)
            .into_iter()
            .filter(|ranking| ranking.score >= min_score)
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::orchestration::capabilities::{Capability, ServerMetadata, ServerHealth};
    use crate::orchestration::intent::IntentCategory;

    fn create_test_server(
        id: &str,
        success_rate: f32,
        latency_ms: f32,
    ) -> MCPServerProfile {
        let mut server = MCPServerProfile::new(
            id.to_string(),
            format!("{} MCP", id),
            "1.0.0".to_string(),
            format!("Test server {}", id),
        )
        .with_capabilities(vec![Capability::new(
            "test".to_string(),
            IntentCategory::Research,
            vec!["test".to_string()],
            0.8,
        )]);

        server.metadata.success_rate = success_rate;
        server.metadata.latency_avg_ms = latency_ms;
        server.metadata.health = ServerHealth::Healthy;

        server
    }

    #[test]
    fn test_ranking_breakdown_score() {
        let breakdown = RankingBreakdown {
            success_rate: (0.9, 0.35),
            domain_expertise: (0.8, 0.25),
            latency: (0.9, 0.15),
            cost_efficiency: (0.8, 0.10),
            data_freshness: (0.7, 0.10),
            availability: (1.0, 0.05),
        };

        let score = breakdown.overall_score();
        assert!(score > 0.8 && score < 1.0);
    }

    #[test]
    fn test_tool_ranker_single() {
        let server = create_test_server("arxiv", 0.9, 100.0);
        let ranking = ToolRanker::rank_single(&server);

        assert_eq!(ranking.server_id, "arxiv");
        assert!(ranking.score > 0.0 && ranking.score <= 1.0);
    }

    #[test]
    fn test_tool_ranker_multiple() {
        let servers = vec![
            create_test_server("arxiv", 0.95, 50.0),
            create_test_server("scholar", 0.80, 200.0),
            create_test_server("google", 0.85, 100.0),
        ];

        let rankings = ToolRanker::rank(&servers);
        assert_eq!(rankings.len(), 3);
        // First should be highest score
        assert_eq!(rankings[0].rank, 1);
        assert!(rankings[0].score >= rankings[1].score);
    }

    #[test]
    fn test_tool_ranker_top_n() {
        let servers = vec![
            create_test_server("arxiv", 0.95, 50.0),
            create_test_server("scholar", 0.80, 200.0),
            create_test_server("google", 0.85, 100.0),
        ];

        let top2 = ToolRanker::top_n(&servers, 2);
        assert_eq!(top2.len(), 2);
    }

    #[test]
    fn test_tool_ranker_min_score() {
        let servers = vec![
            create_test_server("arxiv", 0.95, 50.0),
            create_test_server("scholar", 0.50, 500.0),
        ];

        let filtered = ToolRanker::with_min_score(&servers, 0.75);
        assert_eq!(filtered.len(), 1);
        assert_eq!(filtered[0].server_id, "arxiv");
    }
}
