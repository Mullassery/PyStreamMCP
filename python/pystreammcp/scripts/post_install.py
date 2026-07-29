"""
Post-installation message for PyStreamMCP
Displays when user runs: pip install pystreammcp
"""


def post_install():
    """Display post-install message"""
    message = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ PyStreamMCP v2.0.0 installed successfully!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS PyStreamMCP?
   Metadata-first orchestration layer with selective intelligence filtering.
   Reduces token usage by 90-95% while maintaining quality through intelligent
   tool routing and context-aware reranking.

🚀 GET STARTED IN 2 MINUTES:

   Step 1 — List available MCP tools:
   $ pystreammcp list-tools

   Step 2 — Connect to an MCP server:
   $ pystreammcp connect --mcp web_search

   Step 3 — View orchestration dashboard:
   $ pystreammcp dashboard

📚 KEY FEATURES YOU CAN DO:
   • Connect and route to multiple MCP tools (web search, code, file edit, etc.)
   • Metadata-first filtering: filter 90-95% of unnecessary tokens before processing
   • Context-aware reranking: send only high-value tools to LLM
   • Tool composition: chain multiple tools for complex workflows
   • Real-time orchestration dashboard with execution status
   • 90-95% cost reduction on token usage through intelligent filtering

📊 VIEW DASHBOARD:
   $ pystreammcp dashboard              # Interactive orchestration view
   $ pystreammcp dashboard --static     # Static snapshot
   $ pystreammcp dashboard --alerts     # Show alerts only

📖 LEARN MORE:
   Quick Start:    https://github.com/mullassery/pystreammcp#getting-started
   Architecture:   https://github.com/mullassery/pystreammcp/wiki/Architecture
   Examples:       https://github.com/mullassery/pystreammcp/tree/main/examples
   Issues:         https://github.com/mullassery/pystreammcp/issues

❓ GET HELP ANYTIME:
   $ pystreammcp --help
   $ pystreammcp --version
   $ pystreammcp query --help          # Help for specific command

⏱️  NEXT STEP: Run `pystreammcp list-tools` to see available MCP tools!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    print(message)


if __name__ == "__main__":
    post_install()
