// Structured Logging - Stage 4
// JSON structured logging for compliance and debugging

use serde::{Deserialize, Serialize};

/// Log level
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum LogLevel {
    Debug,
    Info,
    Warn,
    Error,
}

impl std::fmt::Display for LogLevel {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            LogLevel::Debug => write!(f, "DEBUG"),
            LogLevel::Info => write!(f, "INFO"),
            LogLevel::Warn => write!(f, "WARN"),
            LogLevel::Error => write!(f, "ERROR"),
        }
    }
}

/// Audit log entry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditLog {
    pub timestamp: i64,
    pub level: LogLevel,
    pub message: String,
    pub trace_id: Option<String>,
    pub context: std::collections::HashMap<String, String>,
}

/// Structured logger
pub struct StructuredLogger {
    config: LogConfig,
}

#[derive(Debug, Clone)]
pub struct LogConfig {
    pub enabled: bool,
    pub level: String,
    pub format: String,
}

impl StructuredLogger {
    /// Create new structured logger
    pub fn new(config: LogConfig) -> crate::Result<Self> {
        Ok(Self { config })
    }

    /// Log message
    pub fn log(&self, level: LogLevel, message: &str, trace_id: Option<&str>) -> crate::Result<()> {
        if !self.config.enabled {
            return Ok(());
        }

        let timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs() as i64;

        let entry = AuditLog {
            timestamp,
            level,
            message: message.to_string(),
            trace_id: trace_id.map(|s| s.to_string()),
            context: std::collections::HashMap::new(),
        };

        if self.config.format == "json" {
            if let Ok(json) = serde_json::to_string(&entry) {
                println!("{}", json);
            }
        } else {
            println!("[{}] {} - {}", level, timestamp, message);
        }

        Ok(())
    }

    /// Log debug message
    pub fn debug(&self, message: &str) -> crate::Result<()> {
        self.log(LogLevel::Debug, message, None)
    }

    /// Log info message
    pub fn info(&self, message: &str) -> crate::Result<()> {
        self.log(LogLevel::Info, message, None)
    }

    /// Log warning message
    pub fn warn(&self, message: &str) -> crate::Result<()> {
        self.log(LogLevel::Warn, message, None)
    }

    /// Log error message
    pub fn error(&self, message: &str) -> crate::Result<()> {
        self.log(LogLevel::Error, message, None)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_structured_logger() {
        let config = LogConfig {
            enabled: true,
            level: "INFO".to_string(),
            format: "json".to_string(),
        };
        let logger = StructuredLogger::new(config).unwrap();

        logger.info("Test message").unwrap();
        logger.warn("Warning message").unwrap();
    }
}
