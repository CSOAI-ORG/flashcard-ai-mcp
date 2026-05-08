<div align="center">

# Flashcard Ai MCP

**MCP server for flashcard ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-flashcard-ai-mcp)](https://pypi.org/project/meok-flashcard-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Flashcard Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `create_deck` | Create a new flashcard deck. Optionally provide initial cards as JSON array of { |
| `add_card` | Add a flashcard to an existing deck. Creates the deck if it doesn't exist. |
| `quiz_session` | Start a quiz session from a deck. Modes: standard (front->back), reverse (back-> |
| `get_stats` | Get deck statistics and optionally record quiz results. Results format: JSON arr |

## Installation

```bash
pip install meok-flashcard-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "flashcard-ai": {
      "command": "python",
      "args": ["-m", "meok_flashcard_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 4 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
