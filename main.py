"""
main.py — Entry point for the AI team.

Three ways to submit a task:
  1. CLI argument:   python main.py "Write a strategy memo about X"
  2. Inbox file:     drop a .txt file into Team Inbox/, then run: python main.py
  3. Interactive:    run python main.py with no args and no inbox files

Results are saved to Owner's Inbox/ as JSON files.
"""
from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
TEAM_INBOX    = PROJECT_ROOT / "Team Inbox"
OWNERS_INBOX  = PROJECT_ROOT / "Owner's Inbox"
AGENT_TEAM    = PROJECT_ROOT / "Agent Team"

# Make project root importable (needed by Parry and friends)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ── Task helpers ──────────────────────────────────────────────────────────────

def _next_inbox_task() -> tuple[str, str] | None:
    """
    Return (task_text, filename) for the first .txt file in Team Inbox/.
    Returns None if the inbox is empty.
    """
    for f in sorted(TEAM_INBOX.glob("*.txt")):
        text = f.read_text(encoding="utf-8").strip()
        if text:
            return text, f.name
    return None


def _save_result(result_data: dict) -> Path:
    """Write the result dict to Owner's Inbox/ as a JSON file."""
    filename = (
        f"result_{result_data['task_id']}"
        f"_{result_data['assigned_to'].split()[0].lower()}.json"
    )
    out_path = OWNERS_INBOX / filename
    out_path.write_text(
        json.dumps(result_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return out_path


# ── Core runner ───────────────────────────────────────────────────────────────

async def run_task(task_text: str, source_file: str) -> None:
    # Deferred import — Parry pulls in the SDK which needs the event loop running
    parry_path = AGENT_TEAM / "parry.py"
    spec = importlib.util.spec_from_file_location("Parry", parry_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    ParryClass = module.Parry

    task_id = uuid.uuid4().hex[:8]
    submitted_at = datetime.now(timezone.utc).isoformat()

    print(f"\n{'=' * 62}")
    print(f"  Task ID  : {task_id}")
    print(f"  Source   : {source_file}")
    print(f"  Task     : {task_text[:100]}{'...' if len(task_text) > 100 else ''}")
    print(f"{'=' * 62}\n")

    parry = ParryClass()
    assigned_to = "Parry (routed)"

    try:
        result_text, assigned_to = await parry.run(task_text)
        status = "success"
    except Exception as exc:
        result_text = f"ERROR: {exc}"
        status = "error"
        print(f"\n[main] Error: {exc}")

    result_data = {
        "task_id": task_id,
        "description": task_text,
        "submitted_at": submitted_at,
        "source_file": source_file,
        "assigned_to": assigned_to,
        "status": status,
        "result": result_text,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    out_path = _save_result(result_data)

    print(f"\n{'=' * 62}")
    print(f"  Status   : {status.upper()}")
    print(f"  Agent    : {assigned_to}")
    print(f"  Saved to : {out_path.relative_to(PROJECT_ROOT)}")
    print(f"{'=' * 62}\n")

    # Print a preview of the result
    preview = result_text[:500]
    if len(result_text) > 500:
        preview += f"\n... [{len(result_text) - 500} more characters — see result file]"
    print(preview)


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    # Mode 1: task from CLI argument(s)
    if len(sys.argv) > 1:
        task_text = " ".join(sys.argv[1:])
        asyncio.run(run_task(task_text, "cli_input"))
        return

    # Mode 2: pick up from Team Inbox/
    item = _next_inbox_task()
    if item:
        task_text, source_file = item
        asyncio.run(run_task(task_text, source_file))
        return

    # Mode 3: interactive prompt
    print("Parry's Team — ready.\n")
    print("No task in Team Inbox/ and no CLI argument found.")
    print("Type your task below (or Ctrl+C to quit):\n")
    try:
        task_text = input("  > ").strip()
        if task_text:
            asyncio.run(run_task(task_text, "interactive_input"))
        else:
            print("No task entered. Exiting.")
    except KeyboardInterrupt:
        print("\nExiting.")


if __name__ == "__main__":
    main()
