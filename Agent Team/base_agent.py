"""
base_agent.py — Foundation class for every agent on the team.

All agents inherit from BaseAgent and use _call_claude() to interact with
the LLM via claude-agent-sdk. Agents communicate with each other via direct
Python await calls; file I/O is handled by Python, not the LLM.
"""
from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Ensure project root is importable from any agent file
AGENT_TEAM_DIR = Path(__file__).parent
PROJECT_ROOT = Path(__file__).parent.parent
for _p in (str(AGENT_TEAM_DIR), str(PROJECT_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage  # type: ignore


@dataclass
class AgentConfig:
    name: str
    role: str
    persona: str               # One-sentence character description
    system_prompt: str         # Full system prompt passed to ClaudeAgentOptions
    skills: list[str] = field(default_factory=list)
    allowed_tools: list[str] = field(default_factory=list)  # [] = text-only


class BaseAgent(ABC):
    """
    Abstract base for all team agents.

    Subclasses implement run(task_description) and may call
    _call_claude() or other agents directly (await agent.run(...)).
    """

    def __init__(self, config: AgentConfig) -> None:
        self.config = config

    @abstractmethod
    async def run(self, task_description: str, **kwargs: Any) -> str:
        """Execute the agent's task. Returns a plain-text result string."""
        ...

    async def _call_claude(
        self,
        prompt: str,
        extra_system: str = "",
        allowed_tools: list[str] | None = None,
        max_turns: int | None = None,
    ) -> str:
        """
        Thin async wrapper around claude_agent_sdk.query().

        Returns the final result text from the last ResultMessage.
        Raises RuntimeError if the SDK signals an error.
        """
        system = self.config.system_prompt
        if extra_system:
            system = f"{system}\n\n{extra_system}"

        tools = allowed_tools if allowed_tools is not None else self.config.allowed_tools

        kwargs: dict[str, Any] = dict(
            system_prompt=system,
            allowed_tools=tools,
        )
        if max_turns is not None:
            kwargs["max_turns"] = max_turns

        options = ClaudeAgentOptions(**kwargs)

        result_text: str = ""
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, ResultMessage):
                if getattr(message, "is_error", False):
                    raise RuntimeError(
                        f"[{self.config.name}] Claude returned an error: {message.result}"
                    )
                result_text = message.result or ""

        return result_text

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.config.name!r} role={self.config.role!r}>"
