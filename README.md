# Flashcard Ai

> By [MEOK AI Labs](https://meok.ai) — Create study flashcards, run quiz sessions, and track learning progress. By MEOK AI Labs.

Create study flashcards, run quiz sessions, and track learning with spaced repetition. — MEOK AI Labs.

## Installation

```bash
pip install flashcard-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install flashcard-ai-mcp
```

## Tools

### `create_deck`
Create a new flashcard deck. Optionally provide initial cards as JSON array of {front, back} objects.

**Parameters:**
- `name` (str)
- `description` (str)
- `cards_json` (str)

### `add_card`
Add a flashcard to an existing deck. Creates the deck if it doesn't exist.

**Parameters:**
- `deck_name` (str)
- `front` (str)
- `back` (str)
- `tags` (str)
- `hint` (str)

### `quiz_session`
Start a quiz session from a deck. Modes: standard (front->back), reverse (back->front), mixed. Returns cards due for review with SM-2 scheduling.

**Parameters:**
- `deck_name` (str)
- `count` (int)
- `mode` (str)

### `get_stats`
Get deck statistics and optionally record quiz results. Results format: JSON array of {card_id, rating} where rating is 0-5 (SM-2 scale).

**Parameters:**
- `deck_name` (str)
- `record_results` (str)


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/flashcard-ai-mcp](https://github.com/CSOAI-ORG/flashcard-ai-mcp)
- **PyPI**: [pypi.org/project/flashcard-ai-mcp](https://pypi.org/project/flashcard-ai-mcp/)

## License

MIT — MEOK AI Labs
