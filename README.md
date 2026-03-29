# Agentic Team

A self-expanding multi-agent AI team. Submit a task and **Parry** (the orchestrator) routes it to the best specialist. If no suitable agent exists, **Harry** (HR) builds one on-the-fly using a research brief from **Rarry** (researcher).

All LLM calls run via the Claude Agent SDK — no API key required.

---

## The Team

| Agent | Role |
|-------|------|
| **Parry** | Orchestrator — routes tasks, never does specialist work herself |
| **Harry** | HR Agent — builds new specialist agents on demand |
| **Rarry** | Internal researcher — writes agent specs for Harry (never handles user tasks) |
| **Leary** | Executive Content Agent — board-quality reports, lesson plans, and briefings (banking/fintech/AI) |
| **Markety** | Marketing Strategist — brand, content, SEO, GTM, paid media, and copywriting |

New agents built by Harry are saved to `Agent Team/` and registered in `agent_registry.json` automatically.

---

## Project Structure

```
.
├── main.py                    # Entry point (CLI, inbox pickup, interactive)
├── registry.py                # Agent registry helpers
├── agent_registry.json        # Live roster of all agents
├── telegram_bot.py            # Telegram interface (long polling, no tunnel needed)
├── Agent Team/
│   ├── base_agent.py          # BaseAgent ABC + AgentConfig dataclass
│   ├── parry.py               # Orchestrator
│   ├── harry.py               # HR / agent builder
│   ├── rarry.py               # Internal spec researcher
│   ├── leary.py               # Executive content agent
│   └── markety.py             # Marketing strategist
├── Team Inbox/                # Drop .txt task files here for inbox-pickup mode
├── Owner's Inbox/             # Results saved as JSON; Word docs saved here too
├── regen_figures_v2.py        # Regenerates matplotlib report diagrams
└── build_enhanced_report.py   # Builds formatted Word document from Leary's output
```

---

## Prerequisites

- Python 3.13+
- [Claude Code CLI](https://claude.ai/code) installed and authenticated (OAuth — no API key needed)
- `pip install claude-agent-sdk python-telegram-bot python-dotenv python-docx matplotlib`

---

## Running

> **Important:** Always unset `CLAUDECODE` when running from inside a Claude Code session — the Agent SDK refuses to spawn a nested session otherwise.

```bash
# Task via CLI argument
env -u CLAUDECODE python main.py "Write a market analysis for X"

# Task via inbox — drop a .txt file in Team Inbox/, then:
env -u CLAUDECODE python main.py

# Interactive prompt
env -u CLAUDECODE python main.py
```

Results are saved to `Owner's Inbox/` as `result_<id>_<agent>.json`.

---

## Telegram Bot

Send tasks to the team from your phone — no public URL or tunnel required.

**Setup:**
1. Create a bot via [@BotFather](https://t.me/BotFather) and copy the token
2. Get your user ID via [@userinfobot](https://t.me/userinfobot)
3. Create a `.env` file:
   ```
   TELEGRAM_BOT_TOKEN=<your_token>
   TELEGRAM_ALLOWED_USER_ID=<your_numeric_user_id>
   ```
4. Start the bot:
   ```bash
   # Windows
   start_bot.bat

   # or manually
   set CLAUDECODE= && python telegram_bot.py
   ```

**Bot commands:**
| Command | Action |
|---------|--------|
| `/start` | Welcome message |
| `/agents` | List active agents |
| `/help` | Show help |
| Any text | Routes to Parry → best-fit agent |

---

## Word Document Report Pipeline

When Leary produces a research report, run the build pipeline to get a formatted `.docx` with ToC, diagrams, citations, and references.

**Step 1 — Run Leary directly:**
```bash
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
```

**Step 2 — Regenerate diagrams:**
```bash
python regen_figures_v2.py
```

**Step 3 — Build the Word document:**
```bash
python build_enhanced_report.py
```

Output: versioned `.docx` in `Owner's Inbox/`.

---

## Adding Agents Manually

1. Add an entry to `agent_registry.json`
2. Place the `.py` file in `Agent Team/`
3. Class name must match the file stem, capitalised (e.g. `strategerry.py` → `class Strategerry`)
4. Every agent must inherit `BaseAgent` and implement:
   ```python
   async def run(self, task_description: str, **kwargs) -> str:
   ```

---

## How It Works

```
User task
    └─▶ Parry (orchestrator)
            ├─▶ [match found] → Specialist agent → result saved to Owner's Inbox/
            └─▶ [no match] → Harry (HR)
                                └─▶ Rarry (internal researcher) → agent spec brief
                                └─▶ Harry generates code, saves to Agent Team/, registers agent
                                └─▶ Parry re-routes task to new agent
```

---

## Deliverable Standards

All executive-facing content follows these standards:

- Board/executive quality — each section complete enough to stand alone
- Plain English — no jargon without explanation
- Real named institutions and specific, cited statistics
- Inline citations `[n]` throughout; numbered references list at end
- Minimum 6 named case studies for banking reports
- Banking analogies for all technical concepts

**Standard report sections:**
```
1. Executive Summary
2. What Is It
3. How It Differs / Context
4. Types / Taxonomy
5. Technology & Mechanics
6. Banking Case Studies (min 6 named institutions)
7. Risks and Governance
8. Future Outlook
9. Recommendations for Banking Leaders
   References
   Further Reading and Resources
```

---

## License

MIT
