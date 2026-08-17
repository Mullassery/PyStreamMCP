# Installation Guide

## Quick Install

```bash
pip install PyStreamMCP
```

PyStreamMCP is a **pure Python package** — no Rust toolchain or C
compiler required, on any platform.

## Requirements

- Python 3.9+
- Any OS pip itself supports (macOS, Linux, Windows)

## Optional extras

Install only the extras you actually need:

```bash
pip install "PyStreamMCP[api]"              # FastAPI + Flask HTTP servers
pip install "PyStreamMCP[mcp]"              # MCP protocol client library
pip install "PyStreamMCP[langchain]"        # LangChain adapter
pip install "PyStreamMCP[llamaindex]"       # LlamaIndex adapter
pip install "PyStreamMCP[semantic-kernel]"  # Semantic Kernel adapter
pip install "PyStreamMCP[crewai]"           # CrewAI adapter
pip install "PyStreamMCP[pydantic-ai]"      # PydanticAI adapter
pip install "PyStreamMCP[haystack]"         # Haystack adapter
pip install "PyStreamMCP[all-integrations]" # every framework adapter above
pip install "PyStreamMCP[dev]"              # pytest + dev tooling
```

## Troubleshooting

### Python version issues
Ensure Python 3.9+:
```bash
python --version
```

## Next Steps

After installation:
1. See [README.md](../README.md) for quick start
2. Check [examples/](../examples/) for usage examples
3. Read [docs/](../docs/) for full documentation

For more help, see [full installation guide](INSTALL.md).
