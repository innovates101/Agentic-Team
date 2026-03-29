"""
registry.py — Helpers for reading and writing agent_registry.json.

The registry is the single source of truth for which agents exist,
what they can do, and where their code lives.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REGISTRY_PATH = Path(__file__).parent / "agent_registry.json"


def load_registry() -> dict[str, Any]:
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_registry(data: dict[str, Any]) -> None:
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_active_agents() -> list[dict[str, Any]]:
    """Return all agents with active=true."""
    return [a for a in load_registry()["agents"] if a.get("active", True)]


def register_agent(entry: dict[str, Any]) -> None:
    """
    Add a new agent entry to the registry.
    Silently skips if an agent with the same name already exists.
    """
    data = load_registry()
    existing_names = {a["name"] for a in data["agents"]}
    if entry["name"] not in existing_names:
        data["agents"].append(entry)
        save_registry(data)


def get_agent_by_name(name: str) -> dict[str, Any] | None:
    """Return the registry entry for the given agent name, or None."""
    return next(
        (a for a in load_registry()["agents"] if a["name"] == name),
        None,
    )
