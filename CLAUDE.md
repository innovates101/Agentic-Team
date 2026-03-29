# Agentic Team

A self-expanding multi-agent AI team. The user submits a task; Parry (the orchestrator)
routes it to the best specialist. If no suitable agent exists, Harry (HR) builds one
on-the-fly using a research brief from Rarry (researcher).

## Project Structure

| File | Purpose |
|------|---------|
| `main.py` | Entry point — CLI, inbox pickup, or interactive prompt |
| `registry.py` | `load_registry()`, `get_active_agents()`, `register_agent()`, `get_agent_by_name()` |
| `agent_registry.json` | Live roster of all agents (name, role, skills, file path) |
| `Agent Team/base_agent.py` | `BaseAgent(ABC)` + `AgentConfig` dataclass; `_call_claude()` helper |
| `Agent Team/parry.py` | Orchestrator — routes tasks, commissions new agents via Harry |
| `Agent Team/harry.py` | HR agent — asks Rarry for a brief, generates agent code, saves + registers |
| `Agent Team/rarry.py` | Research agent — produces JSON spec briefs for new agents (INTERNAL ONLY) |
| `Agent Team/leary.py` | Executive content agent — research reports, lesson plans, executive briefings |
| `regen_figures_v2.py` | Regenerates all 6 matplotlib report diagrams (min 11pt fonts) |
| `build_enhanced_report.py` | Builds the enhanced Word document from Leary's JSON output |
| `Team Inbox/` | Drop `.txt` task files here for inbox-pickup mode |
| `Owner's Inbox/` | Results saved as `result_<id>_<agent>.json`; Word docs saved here too |

## The Team

| Agent | Role | Personality |
|-------|------|-------------|
| **Parry** | Personal AI Assistant / Orchestrator | Sharp, organised; routes tasks, never does specialist work herself |
| **Harry** | HR Agent -- builds new AI agents | Energetic builder; turns research briefs into working agent code |
| **Rarry** | Senior Research Agent (INTERNAL ONLY) | Methodical; researches what a new agent needs to look like. Never handles user tasks. |
| **Leary** | Executive Content & Learning Agent | Board-quality research reports, lesson plans, executive briefings -- banking domain specialist |

Dynamically created agents (built by Harry) are saved to `Agent Team/` and appear in
`agent_registry.json`.

## Running

```bash
# IMPORTANT: Must use env -u CLAUDECODE when running from within a Claude Code session.
# claude-agent-sdk refuses to spawn a nested session if the CLAUDECODE env var is set.

# Task via CLI argument
env -u CLAUDECODE python main.py "Your task here"

# Task via inbox -- drop a .txt file in Team Inbox/, then run with no args
env -u CLAUDECODE python main.py

# Interactive prompt
env -u CLAUDECODE python main.py
```

## Pipeline

1. `main.py` hands the task to **Parry**
2. Parry consults `agent_registry.json` and asks Claude which agent fits best
3. **If a match exists** -- that agent runs the task -- result saved to `Owner's Inbox/`
4. **If no match** -- Parry asks Harry to build a new agent:
   - Harry asks **Rarry** to research skills, persona, and system prompt
   - Harry generates a Python file from the brief, saves it to `Agent Team/`, registers it
   - Parry re-routes the original task to the new agent

## Word Document Report Pipeline

When Leary produces a research report, a separate build step converts it to a formatted
Word document with embedded diagrams, inline citations, table of contents, and references.

```bash
# Step 1: Run the task through Leary directly (more reliable than routing via Parry)
env -u CLAUDECODE python -c "
import asyncio, sys, json
from pathlib import Path
sys.path.insert(0, str(Path('Agent Team')))
sys.path.insert(0, '.')
async def main():
    spec = __import__('importlib').util.spec_from_file_location('Leary', Path('Agent Team/leary.py'))
    mod = __import__('importlib').util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    leary = mod.Leary()
    result = await leary.run('YOUR TASK HERE')
    out = Path(\"Owner's Inbox/result_report.json\")
    out.write_text(__import__('json').dumps({'result': result}, ensure_ascii=False, indent=2))
asyncio.run(main())
"

# Step 2: Regenerate matplotlib diagrams (once, or after font/content changes)
python regen_figures_v2.py

# Step 3: Build the Word document
python build_enhanced_report.py
```

Output: versioned `.docx` file in `Owner's Inbox/`

## Deliverable Standards (User Preferences)

These standards apply to all executive-facing content produced by the team:

**Content quality:**
- Board/executive quality -- each section complete enough to stand alone
- Plain executive English -- no jargon without explanation
- Real named institutions and specific statistics (not generic claims)
- All statistics attributed with source and year
- Inline citations [n] throughout body text; numbered references list at end
- Minimum 6 named case studies for banking reports
- Banking analogies to explain all technical concepts

**Document formatting (Word output):**
- Cover page, clickable ToC with deep links, navy/blue heading hierarchy
- Key Statistics at a Glance panel after Executive Summary
- Diagrams embedded at relevant sections (min 11pt font in all figures)
- Further Reading section: 3 authoritative readings + 2 videos with live hyperlinks
- References section with 15-20 cited sources
- 1.15" left/right margins; 11pt body font

**Standard report section template:**
```
SECTION 1: EXECUTIVE SUMMARY
SECTION 2: [WHAT IS IT]
SECTION 3: [HOW IT DIFFERS / CONTEXT]
SECTION 4: [TYPES / TAXONOMY]
SECTION 5: [TECH / MECHANICS]
SECTION 6: BANKING CASE STUDIES (min 6 named institutions)
SECTION 7: RISKS AND GOVERNANCE
SECTION 8: FUTURE OUTLOOK (near/medium/long horizon)
SECTION 9: RECOMMENDATIONS FOR BANKING LEADERS
REFERENCES
FURTHER READING AND RESOURCES
```

## Adding New Agents Manually

Add an entry to `agent_registry.json` and place the corresponding `.py` file in
`Agent Team/`. The class name must match the file stem, capitalised
(e.g. `strategerry.py` -> class `Strategerry`). Every agent must inherit from `BaseAgent`
and implement `async def run(self, task_description: str, **kwargs) -> str`.

## Routing Rules (Parry)

Parry's routing prompt enforces these rules -- do not weaken them when editing:
- **Rarry is INTERNAL ONLY** -- she researches agent specs for Harry, never user tasks.
  Parry's prompt uses `*** CRITICAL -- DO NOT ROUTE TO RARRY ***` language to enforce this.
- **Harry** is only for agent-building tasks.
- If no agent fits, Parry sets `needs_new_agent: true` and Harry+Rarry build a new one.
- For deep research/content/report tasks -- route to **Leary**.

## Rules

**Claude SDK -- never use API key.** All LLM calls must use `claude-agent-sdk`:
```python
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
```
Never use `ANTHROPIC_API_KEY`. The `query()` function authenticates via Claude CLI OAuth.

**`Agent Team/` has a space -- never use dotted imports.** Always use:
```python
importlib.util.spec_from_file_location(name, absolute_path)
```

**sys.path must include both directories in every agent file:**
```python
AGENT_TEAM_DIR = Path(__file__).parent
PROJECT_ROOT = Path(__file__).parent.parent
for _p in (str(AGENT_TEAM_DIR), str(PROJECT_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
```

**LLMs produce text only; Python handles all file I/O.** Agents use `allowed_tools=[]`.

**`agent_registry.json` is the source of truth.** Every active agent must have an entry.

## Python Path

`c:\Users\celes\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe`
