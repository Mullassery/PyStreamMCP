#!/bin/bash
# install_and_serve.sh - Quick start script for PyStreamMCP server

set -e

echo "🚀 PyStreamMCP Workflow Integration Setup"
echo "=========================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION found"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q pystreammcp flask

echo "✓ Dependencies installed"

# Show available commands
echo ""
echo "✨ PyStreamMCP is ready!"
echo ""
echo "Available options:"
echo ""
echo "1. Start REST API Server (for Temporal, Airflow, n8n, Power Automate, etc):"
echo "   python -m pystreammcp.server"
echo ""
echo "2. Use CLI (for shell scripts, UiPath, Automation Anywhere):"
echo "   pystreammcp query 'Your query here'"
echo ""
echo "3. View integration examples:"
echo "   cat examples/workflow_integrations.md"
echo ""
echo "4. Run a test query:"
echo "   pystreammcp query 'Top customers by LTV' retrieve test_agent"
echo ""
echo "=========================================="
echo ""

# Optionally start server
if [ "$1" == "--serve" ]; then
    echo "Starting REST API server on http://localhost:8000..."
    python -m pystreammcp.server
fi

if [ "$1" == "--test" ]; then
    echo "Running test query..."
    pystreammcp query "Test optimization query" retrieve test_agent
    echo "✓ Test successful!"
    echo ""
    echo "Try the other options above to get started"
fi
