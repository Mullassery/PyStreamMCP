# PyStreamMCP

> **Selective intelligence pipeline for AI agents.** Four-stage token reduction achieving 90-95% reduction with production observability.

![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Tests](https://img.shields.io/badge/Tests-189%20Passing-brightgreen.svg)
![Distribution](https://img.shields.io/badge/Distribution-Wheels--Only-blue.svg)
![License](https://img.shields.io/badge/License-Proprietary-red.svg)

---

## Product Overview

**PyStreamMCP** is a proprietary, production-grade intelligent retrieval pipeline for AI agents. Achieve 90-95% token reduction through selective context and metadata filtering.

### Why AI Teams Choose This

**The Problem**:
- RAG systems waste tokens on irrelevant context
- Agents send too much data to LLMs
- Token budgets explode with large knowledge bases
- Cost scales with context, not solution complexity

**The Solution**:
- Stage 1: Metadata filtering (70-85% reduction)
- Stage 2: Contextual reranking (additional 70-80% reduction)
- Stage 3: Tiered token budgets (minimal + essential + nice-to-have)
- Stage 4: Cost attribution (understand where tokens go)

**Result**: 90-95% token reduction, better answers, 10x cheaper agents.

---

## Installation

```bash
pip install pystreammcp
# or with uv
uv pip install pystreammcp
```

### Requirements
- Python 3.10+
- Precompiled wheels

### Distribution Model

**Proprietary-first distribution**:
- ✅ Wheels-only via PyPI (no source code)
- ✅ Production-optimized retrieval
- ✅ 189 comprehensive tests
- ✅ Used in production AI agents

---

## Quick Start

```python
from pystreammcp import SelectiveIntelligence

# Initialize pipeline
pipeline = SelectiveIntelligence(
    metadata_filter_rate=0.75,  # Stage 1: 75% reduction
    rerank_threshold=0.65,       # Stage 2: similarity cutoff
    token_budget=2000,           # Max tokens for context
)

# Process query
context = pipeline.retrieve(
    query="How do I configure OAuth?",
    knowledge_base=docs,
    agent_budget='standard',  # or 'economy', 'premium'
)

# Use context with LLM
response = llm.generate(
    prompt=f"Question: {query}\nContext: {context}",
)

print(f"Tokens used: {len(context.split())} (90% reduction)")
print(f"Cost: ${response.cost:.4f}")
```

---

## Features

- **Stage 1 - Metadata Filtering**: 70-85% reduction
- **Stage 2 - Contextual Reranking**: Additional 70-80% reduction
- **Stage 3 - Tiered Budgets**: Minimal, essential, optional tiers
- **Stage 4 - Cost Attribution**: Full cost transparency
- **Agentic API**: Built for autonomous systems
- **Production Ready**: 189 tests, observability included

---

## Performance

- **Token reduction**: 90-95% vs naive retrieval
- **Quality**: Better answers with less context
- **Latency**: <100ms for retrieval + reranking
- **Cost**: 10x cheaper AI agent calls

---

## Quality & Testing

- **189 tests** passing
- **Production-grade** — production AI agents
- **Observability** — cost tracking, performance metrics

---

## Support

For production deployments: **mullassery@gmail.com**

---

**Version**: 1.0.0  
**License**: Proprietary  
**Distribution**: Wheels-only via PyPI  
**Python**: 3.10+  

Built for cost-efficient AI agents.
