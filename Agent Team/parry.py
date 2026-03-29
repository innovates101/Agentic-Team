"""
parry.py — Personal AI Assistant / Orchestrator

Parry is the front door to the team. She reads the task, consults the agent
registry, and routes work to the best specialist. If no suitable agent exists,
she commissions Harry to build one, then re-routes.

Parry never does the specialist work herself — she delegates.
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

AGENT_TEAM_DIR = PROJECT_ROOT / "Agent Team"

PARRY_SYSTEM_PROMPT = """
You are Parry, Chief of Staff to the user. You lead a growing team of specialist agents.
Your core responsibility is precise delegation — routing every task to the agent whose
job description is a genuine match, or commissioning a new specialist hire when a gap exists.

Personality: sharp, organised, warm but efficient. Like a human Chief of Staff, you do
not do specialist work yourself. Your reputation depends on routing accuracy, not speed.

ROUTING DECISION — return ONLY valid JSON, no markdown, no explanation:
{
  "chosen_agent": "<agent name, or null if a new specialist is needed>",
  "reason": "<one sentence — reference the agent's job scope>",
  "needs_new_agent": <true or false>,
  "suggested_new_role": "<tight human job title if needs_new_agent is true, else null>"
}

STANDING TEAM — JOB DESCRIPTIONS (authoritative scope for each agent):
Match tasks against these descriptions exactly. Do not stretch an agent beyond their scope.

  Leary — Senior L&D Specialist & Corporate Research Writer
    Domain: Banking, financial services, and AI/technology ONLY.
    Audience: Senior banking executives and corporate learning programmes.
    Delivers: Executive research reports, board briefings, lesson plans, course modules,
    facilitator guides, and executive primers on fintech, AI, regulation, and strategy.
    ✓ Route: "board briefing on AI regulation", "lesson plan on agentic AI for bankers",
      "research report on open banking", "executive primer on LLM risk in financial services"
    ✗ Do NOT route: general Q&A, document summarisation, translation, coding, data analysis,
      scheduling, topics outside banking/finance/AI, or non-executive/non-L&D content.

  Harry — Talent Acquisition & Agent Onboarding Manager
    Domain: Building and registering new AI specialist agents — nothing else.
    Delivers: A newly created, fully functional specialist agent ready to handle future tasks.
    ✓ Route: "build me an agent that...", "create a specialist for...", "I need an agent to..."
    ✗ Do NOT route: research, content creation, analysis, or any non-agent-building task.

  Markety — Senior Marketing Strategist
    Domain: Marketing strategy and execution across all channels.
    Delivers: Brand positioning, content strategies, campaign briefs, SEO plans, paid media
    strategies (Google/Meta/LinkedIn), email campaigns, social content, GTM plans, ad copy.
    ✓ Route: marketing campaigns, content calendars, brand messaging, SEO, GTM strategy
    ✗ Do NOT route: financial analysis, research reports, coding, non-marketing deliverables.

ADDITIONAL AGENTS may appear in the roster. Apply the same standard: only route if the
task is a precise fit for their stated job description.

WHEN TO COMMISSION A NEW SPECIALIST (needs_new_agent: true):
A focused new hire always outperforms a generalist doing the wrong job.
Commission a new specialist when the task requires expertise not covered by anyone on the team.
  Examples: legal research, financial modelling, data analysis, translation, document review,
  web scraping, scheduling, coding assistance, customer service, technical writing, HR content.
  Use a tight human job title for suggested_new_role, e.g.:
  "Financial Data Analyst", "Legal Research Specialist", "Technical Writer", "Translator"

CRITICAL CONSTRAINTS:
- *** DO NOT ROUTE TO RARRY ***: She is INTERNAL infrastructure used only by Harry to write
  agent specs. She NEVER handles user tasks. Treat her as if she does not exist.
- Harry handles ONLY agent-building. Never route research, content, or analysis to Harry.
- Never route tasks back to yourself (Parry).
""".strip()

PARRY_CONFIG = AgentConfig(
    name="Parry",
    role="Personal AI Assistant / Orchestrator",
    persona="Sharp, organised orchestrator who routes tasks to the right specialist and never does the specialist work herself.",
    system_prompt=PARRY_SYSTEM_PROMPT,
    skills=["task routing", "delegation", "orchestration", "team management"],
    allowed_tools=[],
)


class Parry(BaseAgent):

    def __init__(self) -> None:
        super().__init__(PARRY_CONFIG)
        self._agent_cache: dict[str, BaseAgent] = {}

    async def run(self, task_description: str, **kwargs: Any) -> tuple[str, str]:
        """
        Route and execute a task.

        Returns (result_text, assigned_agent_name).
        """
        # ── First routing attempt ─────────────────────────────────────────────
        routing = await self._route(task_description)

        # ── Commission new agent if needed ────────────────────────────────────
        if routing.get("needs_new_agent"):
            suggested_role = routing.get("suggested_new_role") or ""
            print(
                f"[Parry] No suitable agent found. "
                f"Asking Harry to build: {suggested_role or 'new specialist'}"
            )
            new_name = await self._commission_new_agent(task_description, suggested_role)
            print(f"[Parry] Harry built '{new_name}'. Re-routing...")
            routing = await self._route(task_description)

        chosen_name: str | None = routing.get("chosen_agent")
        if not chosen_name:
            msg = (
                f"[Parry] Could not find or create a suitable agent for this task.\n"
                f"Routing decision: {json.dumps(routing, indent=2)}"
            )
            return msg, "Parry"

        print(f"[Parry] Routing to {chosen_name} — {routing.get('reason', '')}")

        # ── Load and run the chosen agent ─────────────────────────────────────
        agent = self._load_agent(chosen_name)
        result = await agent.run(task_description)
        return result, chosen_name

    # ── Internal helpers ──────────────────────────────────────────────────────

    async def _route(self, task_description: str) -> dict:
        """Ask Claude which agent fits the task, given the current registry."""
        agents = registry.get_active_agents()
        roster = json.dumps(
            [
                {"name": a["name"], "role": a["role"], "skills": a["skills"]}
                for a in agents
            ],
            indent=2,
        )
        prompt = (
            f"Current team roster:\n{roster}\n\n"
            f"Task to route:\n{task_description}\n\n"
            "Which agent should handle this? Reply with JSON only."
        )
        raw = await self._call_claude(prompt, max_turns=3)
        return _parse_json(raw)

    async def _commission_new_agent(self, task: str, suggested_role: str) -> str:
        """Call Harry to build a new agent. Returns the new agent's name."""
        harry_path = AGENT_TEAM_DIR / "harry.py"
        HarryClass = _load_class(harry_path, "Harry")
        harry: BaseAgent = HarryClass()
        result_raw = await harry.run(task_description=task, suggested_role=suggested_role)
        data = _parse_json(result_raw)
        return data.get("agent_name", "UnknownAgent")

    def _load_agent(self, name: str) -> BaseAgent:
        """Dynamically import and instantiate a registered agent by name."""
        if name in self._agent_cache:
            return self._agent_cache[name]

        # Core team — known file paths
        core_paths: dict[str, Path] = {
            "Harry": AGENT_TEAM_DIR / "harry.py",
            "Rarry": AGENT_TEAM_DIR / "rarry.py",
        }
        if name in core_paths:
            agent = _load_class(core_paths[name], name)()
        else:
            # Dynamically created agent — look up in registry
            entry = registry.get_agent_by_name(name)
            if not entry:
                raise ValueError(f"[Parry] Agent '{name}' not found in registry.")
            path = PROJECT_ROOT / entry["file_path"]
            if not path.exists():
                raise FileNotFoundError(f"[Parry] Agent file not found: {path}")
            class_name = path.stem.capitalize()
            agent = _load_class(path, class_name)()

        self._agent_cache[name] = agent
        return agent


# ── Module-level helpers ──────────────────────────────────────────────────────

def _load_class(path: Path, class_name: str):
    """Dynamically import a .py file and return the named class."""
    spec = importlib.util.spec_from_file_location(class_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)


def _parse_json(text: str) -> dict:
    """Strip markdown fences and parse JSON, falling back to substring search."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        inner = lines[1:]
        if inner and inner[-1].strip() == "```":
            inner = inner[:-1]
        text = "\n".join(inner).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        raise
