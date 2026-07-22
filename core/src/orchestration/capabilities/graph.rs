use std::collections::{HashMap, VecDeque};

/// Node in the capability graph
#[derive(Debug, Clone)]
pub struct CapabilityNode {
    pub name: String,
    pub related: Vec<String>,
    pub similarity_scores: HashMap<String, f32>,
}

impl CapabilityNode {
    pub fn new(name: String) -> Self {
        Self {
            name,
            related: vec![],
            similarity_scores: HashMap::new(),
        }
    }
}

/// Directed graph of related capabilities
pub struct CapabilityGraph {
    nodes: HashMap<String, CapabilityNode>,
    edges: HashMap<(String, String), f32>, // (cap1, cap2) -> similarity score
}

impl CapabilityGraph {
    pub fn new() -> Self {
        Self {
            nodes: HashMap::new(),
            edges: HashMap::new(),
        }
    }

    /// Add a capability to the graph
    pub fn add_node(&mut self, name: String) {
        self.nodes.entry(name).or_insert_with_key(CapabilityNode::new);
    }

    /// Add a relationship between two capabilities
    pub fn add_edge(&mut self, from: String, to: String, similarity: f32) {
        // Ensure both nodes exist
        self.add_node(from.clone());
        self.add_node(to.clone());

        // Add edge
        self.edges.insert((from.clone(), to.clone()), similarity);

        // Update nodes
        if let Some(node) = self.nodes.get_mut(&from) {
            if !node.related.contains(&to) {
                node.related.push(to.clone());
            }
            node.similarity_scores.insert(to, similarity);
        }
    }

    /// Find capabilities related to a given capability
    pub fn find_related(&self, capability: &str, threshold: f32) -> Vec<(String, f32)> {
        self.nodes
            .get(capability)
            .map(|node| {
                node.related
                    .iter()
                    .filter_map(|related| {
                        self.edges
                            .get(&(capability.to_string(), related.clone()))
                            .copied()
                            .filter(|&score| score >= threshold)
                            .map(|score| (related.clone(), score))
                    })
                    .collect()
            })
            .unwrap_or_default()
    }

    /// Find the shortest path between two capabilities
    pub fn find_path(&self, from: &str, to: &str) -> Option<Vec<String>> {
        if from == to {
            return Some(vec![from.to_string()]);
        }

        let mut queue = VecDeque::new();
        let mut visited = HashMap::new();
        let mut parent = HashMap::new();

        queue.push_back(from.to_string());
        visited.insert(from.to_string(), true);

        while let Some(current) = queue.pop_front() {
            if current == to {
                // Reconstruct path
                let mut path = vec![to.to_string()];
                let mut node = to.to_string();
                while let Some(p) = parent.get(&node) {
                    path.push(p.clone());
                    node = p.clone();
                }
                path.reverse();
                return Some(path);
            }

            if let Some(node) = self.nodes.get(&current) {
                for related in &node.related {
                    if !visited.contains_key(related) {
                        visited.insert(related.clone(), true);
                        parent.insert(related.clone(), current.clone());
                        queue.push_back(related.clone());
                    }
                }
            }
        }

        None
    }

    /// Get all nodes
    pub fn nodes(&self) -> Vec<String> {
        self.nodes.keys().cloned().collect()
    }

    /// Get node count
    pub fn node_count(&self) -> usize {
        self.nodes.len()
    }

    /// Get edge count
    pub fn edge_count(&self) -> usize {
        self.edges.len()
    }

    /// Find capabilities by substring
    pub fn search(&self, pattern: &str) -> Vec<String> {
        self.nodes
            .keys()
            .filter(|name| name.contains(pattern))
            .cloned()
            .collect()
    }

    /// Rank capabilities by relevance (using edge weights)
    pub fn rank_by_relevance(&self, start: &str, max_depth: usize) -> Vec<(String, f32)> {
        let mut results = vec![];
        let mut visited = HashMap::new();
        let mut queue = VecDeque::new();

        queue.push_back((start.to_string(), 1.0, 0usize));
        visited.insert(start.to_string(), true);

        while let Some((current, score, depth)) = queue.pop_front() {
            if depth > 0 {
                results.push((current.clone(), score));
            }

            if depth < max_depth {
                if let Some(node) = self.nodes.get(&current) {
                    for related in &node.related {
                        if !visited.contains_key(related) {
                            visited.insert(related.clone(), true);

                            let edge_score = self
                                .edges
                                .get(&(current.clone(), related.clone()))
                                .copied()
                                .unwrap_or(0.5);
                            let new_score = score * edge_score;

                            queue.push_back((related.clone(), new_score, depth + 1));
                        }
                    }
                }
            }
        }

        results.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        results
    }
}

impl Default for CapabilityGraph {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_graph_add_node() {
        let mut graph = CapabilityGraph::new();
        graph.add_node("research".to_string());
        assert_eq!(graph.node_count(), 1);
    }

    #[test]
    fn test_graph_add_edge() {
        let mut graph = CapabilityGraph::new();
        graph.add_edge("research".to_string(), "papers".to_string(), 0.9);
        assert_eq!(graph.node_count(), 2);
        assert_eq!(graph.edge_count(), 1);
    }

    #[test]
    fn test_graph_find_related() {
        let mut graph = CapabilityGraph::new();
        graph.add_edge("research".to_string(), "papers".to_string(), 0.9);
        graph.add_edge("research".to_string(), "academic".to_string(), 0.8);

        let related = graph.find_related("research", 0.7);
        assert_eq!(related.len(), 2);
    }

    #[test]
    fn test_graph_find_path() {
        let mut graph = CapabilityGraph::new();
        graph.add_edge("research".to_string(), "papers".to_string(), 0.9);
        graph.add_edge("papers".to_string(), "academic".to_string(), 0.8);

        let path = graph.find_path("research", "academic");
        assert!(path.is_some());
        assert_eq!(path.unwrap().len(), 3);
    }

    #[test]
    fn test_graph_find_path_direct() {
        let mut graph = CapabilityGraph::new();
        graph.add_node("research".to_string());

        let path = graph.find_path("research", "research");
        assert!(path.is_some());
        assert_eq!(path.unwrap(), vec!["research"]);
    }

    #[test]
    fn test_graph_find_path_not_found() {
        let mut graph = CapabilityGraph::new();
        graph.add_node("research".to_string());
        graph.add_node("robotics".to_string());

        let path = graph.find_path("research", "robotics");
        assert!(path.is_none());
    }

    #[test]
    fn test_graph_search() {
        let mut graph = CapabilityGraph::new();
        graph.add_node("research".to_string());
        graph.add_node("papers".to_string());
        graph.add_node("robotics".to_string());

        let results = graph.search("research");
        assert_eq!(results.len(), 1);

        let results = graph.search("r");
        assert!(results.len() > 1);
    }

    #[test]
    fn test_graph_rank_by_relevance() {
        let mut graph = CapabilityGraph::new();
        graph.add_edge("research".to_string(), "papers".to_string(), 0.9);
        graph.add_edge("papers".to_string(), "academic".to_string(), 0.8);

        let ranked = graph.rank_by_relevance("research", 2);
        assert!(ranked.len() > 0);
        // First result should have highest score
        assert!(ranked[0].1 > ranked.get(1).map(|r| r.1).unwrap_or(0.0));
    }
}
