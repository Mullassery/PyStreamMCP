#!/bin/bash
# Setup keyboard shortcuts for PyStreamMCP

add_shortcuts() {
  if [ -f ~/.zshrc ]; then
    RC_FILE=~/.zshrc
  elif [ -f ~/.bashrc ]; then
    RC_FILE=~/.bashrc
  else
    echo "❌ No shell config found"; return 1
  fi
  
  if grep -q "dash-pystreammcp" "$RC_FILE"; then
    echo "⚠️  Shortcuts already installed"; return 0
  fi
  
  cat >> "$RC_FILE" << 'ALIASES'

# PyStreamMCP dashboard shortcuts
alias dash-pystreammcp='pystreammcp dashboard --static'
alias dash-pystreammcp-live='pystreammcp dashboard'
alias dash-pystreammcp-export='pystreammcp dashboard --export /tmp/pystreammcp_metrics.json && echo ✓ Exported'
ALIASES
  
  echo "✅ Shortcuts added to $RC_FILE"
  echo "   Run: source $RC_FILE"
}

remove_shortcuts() {
  sed -i '' '/# PyStreamMCP dashboard shortcuts/,/alias dash-pystreammcp-export=/d' ~/.zshrc 2>/dev/null
  sed -i '' '/# PyStreamMCP dashboard shortcuts/,/alias dash-pystreammcp-export=/d' ~/.bashrc 2>/dev/null
  echo "✅ Shortcuts removed"
}

case "${1:-}" in --remove) remove_shortcuts ;; *) add_shortcuts ;; esac
