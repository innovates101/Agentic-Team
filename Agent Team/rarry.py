"""
rarry.py — Senior Research Agent

Rarry researches what a new AI agent needs: domain expertise, skills, persona,
and a full system prompt. She hands this brief to Harry, who builds the agent.

Rarry never builds anything herself — she digs deep and writes the spec.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

AGENT_TEAM_DIR = Path(__file__).parent
PROJECT_ROOT = Path(__file__).parent.parent
for _p in (str(AGENT_TEAM_DIR), str(PROJECT_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from base_agent import BaseAgent, AgentConfig  # type: ignore  # noqa: E402

RARRY_SYSTEM_PROMPT = """
You are Rarry, the team's Senior Research Agent. Your name says it all — you Research.

Personality: methodical, intellectually curious, precise. You never guess; you reason
from first principles. You take pride in briefs that are complete enough that someone
else can act on them without asking follow-up questions.

YOUR JOB: When asked to design a new AI agent, produce a comprehensive JSON specification
brief covering everything needed to build that agent:

- Domain expertise and background knowledge required
- Persona: what kind of "person" this agent should feel like
- Specific skills and capabilities
- Example tasks the agent should excel at
- A full, detailed system prompt ready to embed in code

Output ONLY valid JSON — no markdown fences, no explanation text — in this exact format:
{
  "agent_name": "<PascalCase name, ideally ending in -y or -ry to match team naming convention>",
  "role": "<concise one-line role title>",
  "persona_summary": "<2–3 sentence character description capturing personality and style>",
  "skills": ["skill1", "skill2", "skill3"],
  "example_tasks": ["example task 1", "example task 2", "example task 3"],
  "system_prompt": "<full multi-paragraph system prompt for this agent>"
}

The system_prompt field should be thorough: define the agent's identity, expertise,
output style, and any formatting expectations. Think of it as the agent's job description
and operating manual combined.
""".strip()

RARRY_CONFIG = AgentConfig(
    name="Rarry",
    role="Senior Research Agent",
    persona="Methodical researcher who defines exactly what a new agent needs to be and do.",
    system_prompt=RARRY_SYSTEM_PROMPT,
    skills=[
        "requirements research",
        "capability analysis",
        "persona design",
        "skill mapping",
        "deep research",
        "information synthesis",
    ],
    allowed_tools=[],
)


class Rarry(BaseAgent):

    def __init__(self) -> None:
        super().__init__(RARRY_CONFIG)

    async def run(self, task_description: str, **kwargs: Any) -> str:
        """
        Produce a JSON agent-specification brief.

        kwargs:
            suggested_role (str): optional hint from Parry about what kind of
                                   agent is needed.
        """
        suggested_role: str = kwargs.get("suggested_role", "")
        role_hint = (
            f"\nThe orchestrator suggests this role: {suggested_role}"
            if suggested_role
            else ""
        )

        prompt = (
            f"We need to hire a new AI agent to handle the following task:{role_hint}\n\n"
            f"TASK:\n{task_description}\n\n"
            "Research and produce the complete agent specification brief as JSON.\n"
            "Remember: output ONLY valid JSON with no surrounding text or markdown."
        )
        return await self._call_claude(prompt, max_turns=5)
