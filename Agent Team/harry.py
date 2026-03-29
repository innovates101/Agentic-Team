"""
harry.py — HR Agent

Harry's job: recruit new AI agents.

When Parry can't find a suitable agent for a task, Harry is called.
He asks Rarry to research what the new agent needs, then uses Claude to
generate the agent's Python code, saves it to Agent Team/, and registers it.

The LLM produces code as text; Python (not the LLM) writes the file.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

AGENT_TEAM_DIR = Path(__file__).parent
PROJECT_ROOT = Path(__file__).parent.parent
for _p in (str(AGENT_TEAM_DIR), str(PROJECT_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from base_agent import BaseAgent, AgentConfig  # type: ignore  # noqa: E402
import registry  # type: ignore  # noqa: E402

HARRY_SYSTEM_PROMPT = """
You are Harry, the team's HR Agent. Your name signals your purpose: you Handle Recruitment.

Personality: energetic, structured, takes genuine pride in quality hires. You care that
every agent you build is well-crafted, coherent, and ready to hit the ground running
on day one.

YOUR JOB: Given a research brief from Rarry, write a complete, runnable Python file
for a new agent. Follow the team's exact code template — no deviations.

TEMPLATE TO FOLLOW:

```
\"\"\"
<snake_case_name>.py — <Agent Name>

<One paragraph describing what this agent does and when it's used.>
\"\"\"
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

<AGENT_UPPER>_SYSTEM_PROMPT = \"\"\"
<system prompt text — paste from brief>
\"\"\".strip()

<AGENT_UPPER>_CONFIG = AgentConfig(
    name="<AgentName>",
    role="<role from brief>",
    persona="<persona_summary from brief>",
    system_prompt=<AGENT_UPPER>_SYSTEM_PROMPT,
    skills=<skills list from brief>,
    allowed_tools=[],
)


class <ClassName>(BaseAgent):

    def __init__(self) -> None:
        super().__init__(<AGENT_UPPER>_CONFIG)

    async def run(self, task_description: str, **kwargs: Any) -> str:
        prompt = (
            f"Task:\\n{task_description}"
        )
        return await self._call_claude(prompt, max_turns=10)
```

Output ONLY the Python code — no explanation, no markdown fences, no preamble.
The output must be a complete, syntactically valid Python file that can be saved
directly and imported.
""".strip()

HARRY_CONFIG = AgentConfig(
    name="Harry",
    role="HR Agent — recruits and builds new AI agents",
    persona="Energetic builder who turns research briefs into polished, working agent code.",
    system_prompt=HARRY_SYSTEM_PROMPT,
    skills=[
        "agent creation",
        "code generation",
        "onboarding",
        "system prompt writing",
    ],
    allowed_tools=[],
)


class Harry(BaseAgent):

    def __init__(self) -> None:
        super().__init__(HARRY_CONFIG)

    async def run(self, task_description: str, **kwargs: Any) -> str:
        """
        Full recruitment pipeline:
          1. Ask Rarry to research what the new agent needs
          2. Use Claude (as Harry) to generate the Python code from the brief
          3. Save the file to Agent Team/
          4. Register the new agent in agent_registry.json
          5. Return JSON: {"agent_name": ..., "file_path": ...}
        """
        suggested_role: str = kwargs.get("suggested_role", "")

        # ── Step 1: Get Rarry's research brief ────────────────────────────────
        rarry_path = AGENT_TEAM_DIR / "rarry.py"
        RarryClass = _load_class(rarry_path, "Rarry")
        rarry: BaseAgent = RarryClass()

        print(
            f"[Harry] Consulting Rarry on: "
            f"{suggested_role or task_description[:60]!r}"
        )
        brief_raw = await rarry.run(task_description, suggested_role=suggested_role)
        brief = _parse_json(brief_raw)

        agent_name: str = brief["agent_name"]
        role: str = brief["role"]
        skills: list[str] = brief.get("skills", [])
        system_prompt_text: str = brief["system_prompt"]
        persona_summary: str = brief.get("persona_summary", "")

        # ── Step 2: Check registry — don't build if already exists ────────────
        existing = registry.get_agent_by_name(agent_name)
        if existing:
            print(f"[Harry] Agent '{agent_name}' already exists in registry — skipping build.")
            return json.dumps({"agent_name": agent_name, "file_path": existing["file_path"]})

        # ── Step 3: Generate Python code ──────────────────────────────────────
        print(f"[Harry] Writing code for new agent: {agent_name}")
        code_prompt = (
            f"Build a new agent using the following specification:\n\n"
            f"Name: {agent_name}\n"
            f"Role: {role}\n"
            f"Persona: {persona_summary}\n"
            f"Skills: {', '.join(skills)}\n\n"
            f"System prompt to embed verbatim:\n{system_prompt_text}\n\n"
            "Produce the complete Python file. Output ONLY the code."
        )
        python_code = await self._call_claude(code_prompt, max_turns=5)

        # Strip accidental markdown fences if Claude wraps the code
        python_code = _strip_code_fences(python_code)

        # ── Step 4: Save the file ─────────────────────────────────────────────
        file_stem = agent_name.lower()
        agent_path = AGENT_TEAM_DIR / f"{file_stem}.py"
        agent_path.write_text(python_code, encoding="utf-8")
        print(f"[Harry] Saved: {agent_path.relative_to(PROJECT_ROOT)}")

        # ── Step 5: Register ──────────────────────────────────────────────────
        relative_path = f"Agent Team/{file_stem}.py"
        registry.register_agent(
            {
                "name": agent_name,
                "role": role,
                "skills": skills,
                "file_path": relative_path,
                "active": True,
            }
        )
        print(f"[Harry] Registered '{agent_name}' in agent_registry.json")

        return json.dumps({"agent_name": agent_name, "file_path": relative_path})


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_class(path: Path, class_name: str):
    """Dynamically import a .py file and return the named class."""
    spec = importlib.util.spec_from_file_location(class_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)


def _parse_json(text: str) -> dict:
    """Strip markdown fences and parse JSON, with one retry on failure."""
    cleaned = _strip_code_fences(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Find the outermost {...} block
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(cleaned[start:end])
        raise


def _strip_code_fences(text: str) -> str:
    """
    Extract Python code from a response that may contain prose and/or
    markdown code fences. Finds the first ``` block and returns its contents.
    Falls back to the raw text if no fence is found.
    """
    text = text.strip()
    # Find the first opening fence (```python or just ```)
    fence_start = text.find("```")
    if fence_start == -1:
        return text  # No fence — assume raw code

    # Skip the fence line itself (e.g. ```python\n)
    after_fence = text[fence_start:]
    newline_pos = after_fence.find("\n")
    if newline_pos == -1:
        return text
    code_start = fence_start + newline_pos + 1

    # Find the closing fence
    close_fence = text.find("\n```", code_start)
    if close_fence == -1:
        return text[code_start:].strip()

    return text[code_start:close_fence].strip()
