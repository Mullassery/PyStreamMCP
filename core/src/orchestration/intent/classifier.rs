use std::collections::HashMap;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum IntentCategory {
    Research,
    Documentation,
    CodeGeneration,
    DatabaseQuery,
    RoboticsDebug,
    SimulationAnalysis,
    GISAnalysis,
    WebSearch,
    ImageAnalysis,
    VideoAnalysis,
    SensorReplay,
    LogAnalysis,
    KnowledgeRetrieval,
}

#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
pub enum Urgency {
    Normal,
    High,
    Critical,
}

impl Urgency {
    pub fn token_multiplier(&self) -> f32 {
        match self {
            Urgency::Normal => 1.0,
            Urgency::High => 1.5,
            Urgency::Critical => 2.0,
        }
    }
}

#[derive(Debug, Clone)]
pub struct Entity {
    pub name: String,
    pub entity_type: String,
    pub relevance: f32,
}

#[derive(Debug, Clone)]
pub struct IntentResult {
    pub primary: IntentCategory,
    pub secondary: Vec<IntentCategory>,
    pub confidence: f32,
    pub entities: Vec<Entity>,
    pub urgency: Urgency,
}

impl IntentResult {
    pub fn new(primary: IntentCategory, confidence: f32) -> Self {
        Self {
            primary,
            secondary: vec![],
            confidence,
            entities: vec![],
            urgency: Urgency::Normal,
        }
    }

    pub fn with_secondary(mut self, secondary: Vec<IntentCategory>) -> Self {
        self.secondary = secondary;
        self
    }

    pub fn with_entities(mut self, entities: Vec<Entity>) -> Self {
        self.entities = entities;
        self
    }

    pub fn with_urgency(mut self, urgency: Urgency) -> Self {
        self.urgency = urgency;
        self
    }
}

/// Intent classifier that categorizes queries into semantic buckets
pub struct IntentClassifier {
    patterns: HashMap<String, IntentCategory>,
    keywords: HashMap<IntentCategory, Vec<String>>,
}

impl IntentClassifier {
    pub fn new() -> Self {
        let mut keywords = HashMap::new();

        // Research intent
        keywords.insert(
            IntentCategory::Research,
            vec![
                "paper", "research", "study", "academic", "arxiv", "scholar",
                "conference", "journal", "findings", "analysis",
            ]
            .iter()
            .map(|s| s.to_string())
            .collect(),
        );

        // Documentation intent
        keywords.insert(
            IntentCategory::Documentation,
            vec![
                "doc", "tutorial", "how", "guide", "example", "readme", "install",
                "setup", "configuration", "api", "reference",
            ]
            .iter()
            .map(|s| s.to_string())
            .collect(),
        );

        // Code generation intent
        keywords.insert(
            IntentCategory::CodeGeneration,
            vec![
                "code", "generate", "fix", "bug", "debug", "implement", "write",
                "function", "method", "error",
            ]
            .iter()
            .map(|s| s.to_string())
            .collect(),
        );

        // Database query intent
        keywords.insert(
            IntentCategory::DatabaseQuery,
            vec![
                "database", "query", "sql", "table", "record", "data", "columns",
                "rows", "analytics", "structured",
            ]
            .iter()
            .map(|s| s.to_string())
            .collect(),
        );

        // Robotics debug intent
        keywords.insert(
            IntentCategory::RoboticsDebug,
            vec![
                "robot", "collision", "replay", "failure", "crash", "motor", "sensor",
                "trajectory", "anomaly", "malfunction",
            ]
            .iter()
            .map(|s| s.to_string())
            .collect(),
        );

        // Simulation analysis intent
        keywords.insert(
            IntentCategory::SimulationAnalysis,
            vec![
                "simulation", "sim", "virtual", "performance", "latency", "throughput",
                "behavior", "model",
            ]
            .iter()
            .map(|s| s.to_string())
            .collect(),
        );

        // GIS analysis intent
        keywords.insert(
            IntentCategory::GISAnalysis,
            vec![
                "map", "location", "gis", "geographic", "coordinates", "gps", "terrain",
                "geospatial",
            ]
            .iter()
            .map(|s| s.to_string())
            .collect(),
        );

        // Web search intent
        keywords.insert(
            IntentCategory::WebSearch,
            vec![
                "search", "find", "look", "web", "internet", "google", "browse",
                "information",
            ]
            .iter()
            .map(|s| s.to_string())
            .collect(),
        );

        // Image analysis intent
        keywords.insert(
            IntentCategory::ImageAnalysis,
            vec![
                "image", "photo", "picture", "vision", "detect", "recognize", "object",
                "visual",
            ]
            .iter()
            .map(|s| s.to_string())
            .collect(),
        );

        // Video analysis intent
        keywords.insert(
            IntentCategory::VideoAnalysis,
            vec![
                "video", "frame", "recording", "playback", "footage", "temporal",
                "sequence",
            ]
            .iter()
            .map(|s| s.to_string())
            .collect(),
        );

        // Sensor replay intent
        keywords.insert(
            IntentCategory::SensorReplay,
            vec![
                "sensor", "replay", "imu", "accelerometer", "gyroscope", "camera",
                "lidar", "telemetry",
            ]
            .iter()
            .map(|s| s.to_string())
            .collect(),
        );

        // Log analysis intent
        keywords.insert(
            IntentCategory::LogAnalysis,
            vec![
                "log", "logs", "error", "warning", "trace", "debug", "event",
                "exception",
            ]
            .iter()
            .map(|s| s.to_string())
            .collect(),
        );

        // Knowledge retrieval intent
        keywords.insert(
            IntentCategory::KnowledgeRetrieval,
            vec![
                "know", "fact", "knowledge", "fact", "graph", "information",
                "definition",
            ]
            .iter()
            .map(|s| s.to_string())
            .collect(),
        );

        Self {
            patterns: HashMap::new(),
            keywords,
        }
    }

    /// Classify a query into intent categories
    pub fn classify(&self, query: &str) -> IntentResult {
        let query_lower = query.to_lowercase();
        let mut scores: HashMap<IntentCategory, f32> = HashMap::new();

        // Score each intent based on keyword matches
        for (intent, keywords) in &self.keywords {
            let mut score = 0.0f32;
            let mut matched_keywords = 0;

            for keyword in keywords {
                if query_lower.contains(keyword) {
                    score += 1.0;
                    matched_keywords += 1;
                }
            }

            if matched_keywords > 0 {
                score = score / keywords.len() as f32;
                scores.insert(*intent, score);
            }
        }

        // Find primary intent (highest score)
        let primary = scores
            .iter()
            .max_by(|a, b| a.1.partial_cmp(b.1).unwrap_or(std::cmp::Ordering::Equal))
            .map(|(k, _)| *k)
            .unwrap_or(IntentCategory::WebSearch);

        let primary_confidence = scores.get(&primary).copied().unwrap_or(0.0);

        // Find secondary intents (second highest, if significant)
        let mut secondary = vec![];
        let mut sorted: Vec<_> = scores.iter().collect();
        sorted.sort_by(|a, b| b.1.partial_cmp(a.1).unwrap_or(std::cmp::Ordering::Equal));

        for (intent, score) in sorted.iter().skip(1).take(2) {
            if **score > 0.3 && **intent != primary {
                secondary.push(**intent);
            }
        }

        // Detect urgency from query
        let urgency = self.detect_urgency(&query_lower);

        IntentResult {
            primary,
            secondary,
            confidence: primary_confidence,
            entities: vec![],
            urgency,
        }
    }

    /// Classify with conversation history context
    pub fn classify_with_context(&self, query: &str, _history: &[String]) -> IntentResult {
        // TODO: Incorporate history to disambiguate intent
        self.classify(query)
    }

    fn detect_urgency(&self, query_lower: &str) -> Urgency {
        if query_lower.contains("critical") || query_lower.contains("urgent") {
            Urgency::Critical
        } else if query_lower.contains("important")
            || query_lower.contains("asap")
            || query_lower.contains("production")
        {
            Urgency::High
        } else {
            Urgency::Normal
        }
    }
}

impl Default for IntentClassifier {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_intent_classification_research() {
        let classifier = IntentClassifier::new();
        let result = classifier.classify("Find recent robotics papers on sim-to-real transfer");
        assert_eq!(result.primary, IntentCategory::Research);
        assert!(result.confidence > 0.5);
    }

    #[test]
    fn test_intent_classification_database() {
        let classifier = IntentClassifier::new();
        let result = classifier.classify("Query the database for customer records");
        assert_eq!(result.primary, IntentCategory::DatabaseQuery);
    }

    #[test]
    fn test_intent_classification_robotics_debug() {
        let classifier = IntentClassifier::new();
        let result = classifier.classify("Why did my robot collide with the wall?");
        assert_eq!(result.primary, IntentCategory::RoboticsDebug);
    }

    #[test]
    fn test_intent_classification_web_search() {
        let classifier = IntentClassifier::new();
        let result = classifier.classify("Search for information about machine learning");
        assert_eq!(result.primary, IntentCategory::WebSearch);
    }

    #[test]
    fn test_intent_classification_code_generation() {
        let classifier = IntentClassifier::new();
        let result = classifier.classify("Generate a function to calculate fibonacci");
        assert_eq!(result.primary, IntentCategory::CodeGeneration);
    }

    #[test]
    fn test_intent_classification_documentation() {
        let classifier = IntentClassifier::new();
        let result = classifier.classify("Show me the API documentation");
        assert_eq!(result.primary, IntentCategory::Documentation);
    }

    #[test]
    fn test_intent_classification_log_analysis() {
        let classifier = IntentClassifier::new();
        let result = classifier.classify("Analyze the error logs from last night");
        assert_eq!(result.primary, IntentCategory::LogAnalysis);
    }

    #[test]
    fn test_urgency_detection_critical() {
        let classifier = IntentClassifier::new();
        let result = classifier.classify("CRITICAL: Production system down, find root cause");
        assert_eq!(result.urgency, Urgency::Critical);
    }

    #[test]
    fn test_urgency_detection_high() {
        let classifier = IntentClassifier::new();
        let result = classifier.classify("Production database query - need ASAP");
        assert_eq!(result.urgency, Urgency::High);
    }

    #[test]
    fn test_urgency_detection_normal() {
        let classifier = IntentClassifier::new();
        let result = classifier.classify("Can you find some research papers?");
        assert_eq!(result.urgency, Urgency::Normal);
    }

    #[test]
    fn test_secondary_intents() {
        let classifier = IntentClassifier::new();
        let result = classifier.classify("Find robotics research papers and analyze simulation data");
        assert_eq!(result.primary, IntentCategory::Research);
        assert!(!result.secondary.is_empty());
    }

    #[test]
    fn test_confidence_score() {
        let classifier = IntentClassifier::new();
        let result1 = classifier.classify("Find papers");
        let result2 = classifier.classify("What is the meaning of life?");
        // Clear intent should have higher confidence than ambiguous
        assert!(result1.confidence >= result2.confidence);
    }
}
