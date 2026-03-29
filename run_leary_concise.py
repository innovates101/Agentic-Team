"""Re-run Leary with conciseness requirement for the Agentic AI report."""
import asyncio
import sys
import json
from pathlib import Path
import importlib.util

AGENT_TEAM = Path(__file__).parent / "Agent Team"
PROJECT_ROOT = Path(__file__).parent

for _p in (str(AGENT_TEAM), str(PROJECT_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

TASK = """
Produce a CONCISE deep-dive research report on Agentic AI for senior banking executives.

CONCISENESS RULES (strictly enforced):
- Total report length: 4,000–5,500 words (body text, excluding references/further reading)
- Executive Summary: 150–200 words
- Each of Sections 2–5: 250–350 words
- Section 6 (Case Studies): 6 named institutions, ~80 words each = ~500 words total
- Section 7 (Risks): 250–300 words
- Section 8 (Future Outlook): 200–250 words
- Section 9 (Recommendations): 150–200 words as a tight bullet list
- No repetition across sections — each section makes its own unique points
- Eliminate all filler phrases ("it is worth noting", "as we have seen", etc.)
- Lead with the key point in every paragraph; cut anything that doesn't add new information
- Use bullet points and short paragraphs throughout

REPORT TOPIC: Agentic AI — what it is, how it differs from Generative AI, types of agentic systems
(agentic workflows vs autonomous AI), tech stack, banking case studies (real examples and measurable
outcomes), risks and governance, future developments, and recommendations for banking leaders.

AUDIENCE: Senior banking executives with no technical background.

FORMAT: Follow the standard 9-section report template. Use citations [n] throughout.
Include a References section (15–20 sources) and Further Reading (3 readings + 2 videos with URLs).
"""

async def main():
    spec = importlib.util.spec_from_file_location("Leary", AGENT_TEAM / "leary.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    leary = mod.Leary()
    print("Running Leary (concise report)...")
    result = await leary.run(TASK)
    out = PROJECT_ROOT / "Owner's Inbox" / "result_agenticai_report_leary.json"
    out.write_text(json.dumps({"result": result}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved to {out}")
    print(f"Approximate word count: {len(result.split()):,}")

asyncio.run(main())
