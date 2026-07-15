use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// MCP (Model Context Protocol) support for agent integration.
///
/// PyStreamMCP exposes its intelligence as MCP tools and resources
/// that agents can discover and use.

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MCPTool {
    pub id: String,
    pub name: String,
    pub description: String,
    pub input_schema: serde_json::Value,
    pub output_schema: Option<serde_json::Value>,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MCPResource {
    pub uri: String,
    pub name: String,
    pub description: Option<String>,
    pub mime_type: String,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MCPPrompt {
    pub name: String,
    pub description: String,
    pub arguments: Vec<PromptArgument>,
    pub template: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PromptArgument {
    pub name: String,
    pub description: Option<String>,
    pub required: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MCPMessageType {
    CallTool { tool_id: String, arguments: HashMap<String, serde_json::Value> },
    AccessResource { uri: String },
    RequestPrompt { name: String, arguments: HashMap<String, serde_json::Value> },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MCPCapabilities {
    pub supports_tools: bool,
    pub supports_resources: bool,
    pub supports_prompts: bool,
    pub supports_sampling: bool,
}

impl MCPTool {
    /// Create a query optimization tool
    pub fn query_optimizer() -> Self {
        let now = chrono::Utc::now();
        MCPTool {
            id: "optimize_query".to_string(),
            name: "Optimize Query".to_string(),
            description: "Plan and optimize a query for token efficiency".to_string(),
            input_schema: serde_json::json!({
                "type": "object",
                "properties": {
                    "query_text": { "type": "string" },
                    "agent_id": { "type": "string" },
                    "max_tokens": { "type": "integer" }
                },
                "required": ["query_text", "agent_id"]
            }),
            output_schema: Some(serde_json::json!({
                "type": "object",
                "properties": {
                    "contexts": { "type": "array" },
                    "tokens_saved": { "type": "integer" },
                    "cost_reduction_percent": { "type": "number" }
                }
            })),
            created_at: now,
        }
    }

    /// Create a context discovery tool
    pub fn discover_context() -> Self {
        let now = chrono::Utc::now();
        MCPTool {
            id: "discover_context".to_string(),
            name: "Discover Context".to_string(),
            description: "Discover relevant context for a query".to_string(),
            input_schema: serde_json::json!({
                "type": "object",
                "properties": {
                    "query_text": { "type": "string" },
                    "limit": { "type": "integer" }
                },
                "required": ["query_text"]
            }),
            output_schema: Some(serde_json::json!({
                "type": "object",
                "properties": {
                    "sources": { "type": "array" },
                    "total_available_tokens": { "type": "integer" }
                }
            })),
            created_at: now,
        }
    }

    /// Create a cost metrics tool
    pub fn cost_metrics() -> Self {
        let now = chrono::Utc::now();
        MCPTool {
            id: "cost_metrics".to_string(),
            name: "Cost Metrics".to_string(),
            description: "Get cost reduction metrics for a query".to_string(),
            input_schema: serde_json::json!({
                "type": "object",
                "properties": {
                    "query_id": { "type": "string" }
                },
                "required": ["query_id"]
            }),
            output_schema: Some(serde_json::json!({
                "type": "object",
                "properties": {
                    "baseline_tokens": { "type": "integer" },
                    "optimized_tokens": { "type": "integer" },
                    "reduction_percent": { "type": "number" },
                    "cost_saved": { "type": "number" }
                }
            })),
            created_at: now,
        }
    }
}

impl MCPResource {
    pub fn new(uri: impl Into<String>, name: impl Into<String>, mime_type: impl Into<String>) -> Self {
        MCPResource {
            uri: uri.into(),
            name: name.into(),
            description: None,
            mime_type: mime_type.into(),
            created_at: chrono::Utc::now(),
        }
    }

    pub fn with_description(mut self, desc: impl Into<String>) -> Self {
        self.description = Some(desc.into());
        self
    }
}

impl MCPCapabilities {
    pub fn all() -> Self {
        MCPCapabilities {
            supports_tools: true,
            supports_resources: true,
            supports_prompts: true,
            supports_sampling: true,
        }
    }

    pub fn tools_only() -> Self {
        MCPCapabilities {
            supports_tools: true,
            supports_resources: false,
            supports_prompts: false,
            supports_sampling: false,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_query_optimizer_tool() {
        let tool = MCPTool::query_optimizer();
        assert_eq!(tool.name, "Optimize Query");
        assert!(tool.input_schema["properties"]["query_text"].is_object());
    }

    #[test]
    fn test_discover_context_tool() {
        let tool = MCPTool::discover_context();
        assert_eq!(tool.name, "Discover Context");
        assert!(tool.output_schema.is_some());
    }

    #[test]
    fn test_cost_metrics_tool() {
        let tool = MCPTool::cost_metrics();
        assert_eq!(tool.id, "cost_metrics");
    }

    #[test]
    fn test_mcp_resource_creation() {
        let resource = MCPResource::new(
            "context://customers/ltv",
            "Customer LTV",
            "application/json",
        )
        .with_description("Customer lifetime value data");

        assert_eq!(resource.uri, "context://customers/ltv");
        assert!(resource.description.is_some());
    }

    #[test]
    fn test_mcp_capabilities() {
        let caps = MCPCapabilities::all();
        assert!(caps.supports_tools);
        assert!(caps.supports_sampling);
    }
}
