#!/usr/bin/env python3
"""Create study flashcards, run quiz sessions, and track learning with spaced repetition. — MEOK AI Labs."""

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json, re, hashlib, math, random
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 30
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now - t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT:
        return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day. Upgrade: meok.ai"})
    _usage[c].append(now)
    return None

mcp = FastMCP("flashcard-ai", instructions="Create study flashcards, run quiz sessions, and track learning progress. By MEOK AI Labs.")

_decks = {}  # deck_id -> {name, cards, created_at, stats}


def _deck_id(name: str) -> str:
    return hashlib.md5(name.lower().strip().encode()).hexdigest()[:12]


def _card_id(front: str) -> str:
    return hashlib.md5(front.encode()).hexdigest()[:10]


@mcp.tool()
def create_deck(name: str, description: str = "", cards_json: str = "", api_key: str = "") -> str:
    """Create a new flashcard deck. Optionally provide initial cards as JSON array of {front, back} objects."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl():
        return err

    did = _deck_id(name)
    if did in _decks:
        return json.dumps({"error": f"Deck '{name}' already exists", "deck_id": did})

    cards = []
    if cards_json:
        try:
            raw = json.loads(cards_json)
            if isinstance(raw, list):
                for item in raw:
                    if isinstance(item, dict) and "front" in item and "back" in item:
                        cid = _card_id(item["front"])
                        cards.append({
                            "id": cid,
                            "front": item["front"],
                            "back": item["back"],
                            "tags": item.get("tags", []),
                            "ease": 2.5,
                            "interval": 1,
                            "repetitions": 0,
                            "next_review": datetime.now(timezone.utc).isoformat(),
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        })
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid cards_json. Provide a JSON array of {front, back} objects."})

    _decks[did] = {
        "name": name,
        "description": description,
        "cards": cards,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total_reviews": 0,
        "correct_reviews": 0,
    }

    return json.dumps({
        "status": "created",
        "deck_id": did,
        "name": name,
        "card_count": len(cards),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@mcp.tool()
def add_card(deck_name: str, front: str, back: str, tags: str = "", hint: str = "", api_key: str = "") -> str:
    """Add a flashcard to an existing deck. Creates the deck if it doesn't exist."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl():
        return err

    did = _deck_id(deck_name)
    if did not in _decks:
        _decks[did] = {
            "name": deck_name,
            "description": "",
            "cards": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "total_reviews": 0,
            "correct_reviews": 0,
        }

    deck = _decks[did]
    cid = _card_id(front)

    for card in deck["cards"]:
        if card["id"] == cid:
            return json.dumps({"error": "Card with this front text already exists", "card_id": cid})

    tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else []
    card = {
        "id": cid,
        "front": front,
        "back": back,
        "hint": hint,
        "tags": tag_list,
        "ease": 2.5,
        "interval": 1,
        "repetitions": 0,
        "next_review": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    deck["cards"].append(card)

    return json.dumps({
        "status": "added",
        "card_id": cid,
        "deck_id": did,
        "deck_name": deck_name,
        "total_cards": len(deck["cards"]),
        "front_preview": front[:60],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@mcp.tool()
def quiz_session(deck_name: str, count: int = 5, mode: str = "standard", api_key: str = "") -> str:
    """Start a quiz session from a deck. Modes: standard (front->back), reverse (back->front), mixed. Returns cards due for review with SM-2 scheduling."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl():
        return err

    did = _deck_id(deck_name)
    if did not in _decks:
        return json.dumps({"error": f"Deck '{deck_name}' not found. Create it first."})

    deck = _decks[did]
    if not deck["cards"]:
        return json.dumps({"error": "Deck is empty. Add cards first."})

    count = max(1, min(count, 50))
    now = datetime.now(timezone.utc)

    due_cards = []
    for card in deck["cards"]:
        review_time = datetime.fromisoformat(card["next_review"])
        if review_time <= now:
            due_cards.append(card)

    if not due_cards:
        due_cards = list(deck["cards"])

    random.shuffle(due_cards)
    session_cards = due_cards[:count]

    mode = mode.lower().strip()
    quiz_items = []
    for i, card in enumerate(session_cards):
        if mode == "reverse":
            prompt = card["back"]
            answer = card["front"]
        elif mode == "mixed" and random.random() > 0.5:
            prompt = card["back"]
            answer = card["front"]
        else:
            prompt = card["front"]
            answer = card["back"]

        quiz_items.append({
            "question_number": i + 1,
            "card_id": card["id"],
            "prompt": prompt,
            "answer": answer,
            "hint": card.get("hint", ""),
            "tags": card.get("tags", []),
            "repetitions": card["repetitions"],
            "ease": card["ease"],
        })

    session_id = hashlib.md5(f"{did}{now.isoformat()}".encode()).hexdigest()[:10]

    return json.dumps({
        "session_id": session_id,
        "deck_id": did,
        "deck_name": deck_name,
        "mode": mode,
        "total_due": len(due_cards),
        "quiz_count": len(quiz_items),
        "quiz": quiz_items,
        "instructions": "After answering, use get_stats to record results. Rate each card: 0 (forgot), 3 (hard), 4 (good), 5 (easy).",
        "timestamp": now.isoformat(),
    })


@mcp.tool()
def get_stats(deck_name: str, record_results: str = "", api_key: str = "") -> str:
    """Get deck statistics and optionally record quiz results. Results format: JSON array of {card_id, rating} where rating is 0-5 (SM-2 scale)."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl():
        return err

    did = _deck_id(deck_name)
    if did not in _decks:
        return json.dumps({"error": f"Deck '{deck_name}' not found."})

    deck = _decks[did]
    now = datetime.now(timezone.utc)

    if record_results:
        try:
            results = json.loads(record_results)
            if isinstance(results, list):
                card_map = {c["id"]: c for c in deck["cards"]}
                for r in results:
                    cid = r.get("card_id", "")
                    rating = int(r.get("rating", 0))
                    rating = max(0, min(5, rating))
                    if cid in card_map:
                        card = card_map[cid]
                        deck["total_reviews"] += 1
                        if rating >= 3:
                            deck["correct_reviews"] += 1

                        # SM-2 algorithm
                        if rating >= 3:
                            if card["repetitions"] == 0:
                                card["interval"] = 1
                            elif card["repetitions"] == 1:
                                card["interval"] = 6
                            else:
                                card["interval"] = round(card["interval"] * card["ease"])
                            card["repetitions"] += 1
                        else:
                            card["repetitions"] = 0
                            card["interval"] = 1

                        card["ease"] = max(1.3, card["ease"] + (0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02)))
                        card["next_review"] = (now + timedelta(days=card["interval"])).isoformat()
        except (json.JSONDecodeError, ValueError, TypeError):
            pass

    total_cards = len(deck["cards"])
    due_now = sum(1 for c in deck["cards"] if datetime.fromisoformat(c["next_review"]) <= now)
    mastered = sum(1 for c in deck["cards"] if c["repetitions"] >= 5)
    learning = sum(1 for c in deck["cards"] if 0 < c["repetitions"] < 5)
    new_cards = sum(1 for c in deck["cards"] if c["repetitions"] == 0)
    avg_ease = sum(c["ease"] for c in deck["cards"]) / total_cards if total_cards else 0

    accuracy = (deck["correct_reviews"] / deck["total_reviews"] * 100) if deck["total_reviews"] > 0 else 0

    return json.dumps({
        "deck_id": did,
        "deck_name": deck_name,
        "total_cards": total_cards,
        "due_now": due_now,
        "mastered": mastered,
        "learning": learning,
        "new_cards": new_cards,
        "total_reviews": deck["total_reviews"],
        "correct_reviews": deck["correct_reviews"],
        "accuracy_percent": round(accuracy, 1),
        "average_ease": round(avg_ease, 2),
        "created_at": deck["created_at"],
        "timestamp": now.isoformat(),
    })


if __name__ == "__main__":
    mcp.run()
