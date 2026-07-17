"""Machine learning module for PyStreamMCP.

Advanced optimization using learned models:
- Relevance scoring
- Intent detection
- Query classification
- Auto prompt tagging
- Cost-quality tradeoffs
"""

from .tagging import (
    PromptClassifier,
    PromptIntent,
    PromptComplexity,
    PromptAnalysis,
    PromptTag,
)

__all__ = [
    "PromptClassifier",
    "PromptIntent",
    "PromptComplexity",
    "PromptAnalysis",
    "PromptTag",
    "RelevanceModel",
    "IntentDetector",
    "QueryClassifier",
    "ModelTrainer",
]
