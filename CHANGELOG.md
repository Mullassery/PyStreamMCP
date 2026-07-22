# Changelog

All notable changes to PyStreamMCP will be documented in this file.

## [1.1.0] - 2026-07-22

### Added
- **Layer 1: Intent Understanding** - Intelligent query classification and entity extraction
  - IntentClassifier with 13 intent categories
  - EntityExtractor with pattern-based entity recognition
  - Urgency detection for token budget allocation
  - 16 comprehensive tests

- **Layer 2: Capability Registry** - Central registry of MCP servers and capabilities
  - MCPServerProfile with capability tagging and performance metadata
  - CapabilityRegistry with O(1) intent/capability lookups
  - CapabilityGraph for discovering related capabilities
  - 20+ comprehensive tests

- **Layer 3: Tool Selection & Ranking** - Intelligent tool selection and ranking
  - ToolSelector with primary/secondary/fallback categorization
  - ToolRanker with 6-factor scoring formula
  - PerformanceTracker with statistical aggregation
  - 25+ comprehensive tests

- **Foundation Modules** - Cohesive, strong architectural foundation
  - `error.rs`: Unified OrchestrationError with 10 error variants and rich context
  - `traits.rs`: 8 core traits + 3 trait compositions for shared semantics
  - `metrics.rs`: 7 semantic types for type-safe metrics (Score, Latency, Cost, etc.)
  - `validation.rs`: Comprehensive input validation framework
  - 25+ tests for foundation

### Architecture Improvements
- Unified error handling: All errors flow through OrchestrationError + Result<T>
- Shared abstractions: Trait-based design (Scoreable, Rankable, Confidence, etc.)
- Type safety: Semantic types prevent mixing incompatible metrics
- Input validation: All inputs validated at boundaries
- Extensibility: Trait-based composition enables new features

### Statistics
- Total: 3,890 LOC with 86+ tests
- Layers 1-3: 2,990 LOC with 61+ tests
- Foundation: 900 LOC with 25+ tests
- All tests passing

### Breaking Changes
None - fully backward compatible

### Documentation
- INTELLIGENT_RETRIEVAL_IMPLEMENTATION_PLAN.md - Detailed retrieval layer vision (18K words)
- MCP_ORCHESTRATION_HUB_DETAILED_PROMPT.md - Detailed orchestration layer vision (23K words)
- LAYERS_1_2_3_COMPLETE.md - Completion report for Layers 1-3
- ORCHESTRATION_REFACTORING_PLAN.md - Comprehensive refactoring guide
- COHESION_IMPROVEMENTS_SUMMARY.md - Foundation improvements summary
- ORCHESTRATION_IMPLEMENTATION_STATUS.md - Implementation status and examples

---

## [1.0.0] - 2026-07-21

### Added
- Initial stable release with query planning, discovery, and optimization
- Token budget enforcement
- Cost optimization strategies (6 techniques)
- Early termination for efficient context retrieval
- Basic latency/confidence constraints
- 58 unit tests + 65 integration tests
- OKF native support
- StatGuardian integration

[Unreleased]: https://github.com/Mullassery/PyStreamMCP/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/Mullassery/PyStreamMCP/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Mullassery/PyStreamMCP/releases/tag/v1.0.0
