"""
telegram_bot.py — Telegram interface for the Agentic Team.

Sends tasks to Parry via long polling. No public URL or tunnel needed.
Conversation history is stored natively in Telegram.

Setup:
  1. Create a bot via @BotFather → get token
  2. Get your Telegram user ID via @userinfobot
  3. Add to .env:
       TELEGRAM_BOT_TOKEN=<token>
       TELEGRAM_ALLOWED_USER_ID=<your numeric user ID>
  4. Run: start_bot.bat  (or: set CLAUDECODE= && python telegram_bot.py)

Commands:
  /start   — welcome message
  /agents  — list active agents
  /help    — show help
  Any text — routed to Parry → best-fit agent
"""
from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import sys
import uuid
from datetime import datetime, timezone

# Must be removed (not just emptied) before claude-agent-sdk spawns its subprocess.
# This allows the bot to run even when launched from inside a Claude Code session.
os.environ.pop("CLAUDECODE", None)
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
AGENT_TEAM   = PROJECT_ROOT / "Agent Team"
OWNERS_INBOX = PROJECT_ROOT / "Owner's Inbox"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ── Config ─────────────────────────────────────────────────────────────────────
load_dotenv(PROJECT_ROOT / ".env")

BOT_TOKEN    = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ALLOWED_UID  = os.environ.get("TELEGRAM_ALLOWED_USER_ID", "")

if not BOT_TOKEN:
    raise SystemExit(
        "TELEGRAM_BOT_TOKEN not set in .env\n"
        "Create a bot at @BotFather and add the token to your .env file."
    )

TELEGRAM_MAX_CHARS = 4096  # Telegram's per-message character limit


# ── Agent runner ───────────────────────────────────────────────────────────────

_PARRY_FALLBACK_SYSTEM = """
You are Parry, Chief of Staff to the user. Answer conversationally, helpfully, and
concisely. You have the current team roster below — use it to answer questions about
the team accurately. For simple questions, answer directly. For work tasks, suggest
which specialist to ask and how to phrase the request clearly. Be warm and direct.
Never mention internal routing mechanics or technical implementation details.
""".strip()


async def _answer_directly(task_text: str) -> str:
    """Fallback: answer conversationally with live team roster injected."""
    import registry  # type: ignore
    from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage  # type: ignore

    agents = [a for a in registry.get_active_agents() if a["name"] != "Rarry"]
    roster = "\n".join(
        f"- {a['name']}: {a['role']} — skills: {', '.join(a.get('skills', [])[:5])}"
        for a in agents
    )
    system = f"{_PARRY_FALLBACK_SYSTEM}\n\nCurrent team roster:\n{roster}"

    options = ClaudeAgentOptions(system_prompt=system, max_turns=3)
    result = ""
    async for msg in query(prompt=task_text, options=options):
        if isinstance(msg, ResultMessage):
            result = msg.result or ""
    return result


async def _run_parry(task_text: str) -> tuple[str, str]:
    """Load Parry dynamically and run the task. Returns (result_text, agent_name)."""
    parry_path = AGENT_TEAM / "parry.py"
    spec   = importlib.util.spec_from_file_location("Parry", parry_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    parry = module.Parry()
    result, agent = await parry.run(task_text)
    result = str(result)  # guard against non-string returns from any agent

    # Parry signals routing failure with this phrase — fall back to direct answer
    if "[Parry] Could not find or create a suitable agent" in result:
        result = await _answer_directly(task_text)
        agent = "Parry"

    return result, agent


def _save_to_owners_inbox(task_id: str, task_text: str, result: str, agent: str) -> None:
    """Mirror main.py's _save_result() so Word doc build scripts still work."""
    OWNERS_INBOX.mkdir(exist_ok=True)
    status   = "error" if agent == "error" else "success"
    filename = f"result_{task_id}_{agent.split()[0].lower()}.json"
    data = {
        "task_id":      task_id,
        "description":  task_text,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "source_file":  "telegram_bot",
        "assigned_to":  agent,
        "status":       status,
        "result":       result,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    (OWNERS_INBOX / filename).write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ── Message chunking ───────────────────────────────────────────────────────────

def _chunk(text: str, limit: int = TELEGRAM_MAX_CHARS) -> list[str]:
    """Split text into chunks that fit within Telegram's message limit."""
    if len(text) <= limit:
        return [text]
    chunks = []
    while text:
        chunks.append(text[:limit])
        text = text[limit:]
    return chunks


# ── Access check ───────────────────────────────────────────────────────────────

def _is_allowed(update: Update) -> bool:
    if not ALLOWED_UID:
        return True  # No restriction set — allow all (not recommended)
    return str(update.effective_user.id) == ALLOWED_UID


# ── Background task executor ───────────────────────────────────────────────────

async def _keep_typing(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send typing indicator every 4 seconds until cancelled."""
    try:
        while True:
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")
            await asyncio.sleep(4)
    except asyncio.CancelledError:
        pass


async def _execute_and_reply(
    task_text: str,
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Run Parry in the background and send result back to Telegram."""
    task_id = uuid.uuid4().hex[:8]
    typing_task = asyncio.create_task(_keep_typing(chat_id, context))
    try:
        result_text, agent_name = await _run_parry(task_text)
        typing_task.cancel()
        _save_to_owners_inbox(task_id, task_text, result_text, agent_name)

        header = f"[{agent_name}]\n\n"
        full   = header + result_text
        chunks = _chunk(full)

        total = len(chunks)
        for i, chunk in enumerate(chunks, start=1):
            label = f"(continued {i}/{total})\n\n" if i > 1 and total > 2 else ""
            await context.bot.send_message(chat_id=chat_id, text=label + chunk)

    except Exception as exc:
        typing_task.cancel()
        error_msg = str(exc)
        _save_to_owners_inbox(task_id, task_text, f"ERROR: {error_msg}", "error")
        await context.bot.send_message(chat_id=chat_id, text=f"Error: {error_msg}")


# ── Command handlers ───────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update):
        await update.message.reply_text("Access denied.")
        return
    await update.message.reply_text(
        "Hi! I'm Parry, your AI team orchestrator.\n\n"
        "Send me any task and I'll route it to the right specialist:\n"
        "  • Leary — executive reports, research, learning content\n"
        "  • Harry — build new specialist agents\n"
        "  • or whoever fits best\n\n"
        "Try: Write a brief on agentic AI trends in banking\n\n"
        "Commands: /agents  /help"
    )


async def cmd_agents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update):
        await update.message.reply_text("Access denied.")
        return

    import registry  # type: ignore
    agents = [a for a in registry.get_active_agents() if a["name"] != "Rarry"]
    lines = ["Active agents:\n"]
    for a in agents:
        skills = ", ".join(a.get("skills", [])[:4])
        lines.append(f"• {a['name']} — {a['role']}\n  Skills: {skills}")
    await update.message.reply_text("\n".join(lines))


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update):
        await update.message.reply_text("Access denied.")
        return
    await update.message.reply_text(
        "How to use:\n\n"
        "Just send any task as a message. Examples:\n"
        "  • Write an executive report on AI in banking\n"
        "  • Build an agent that summarises PDFs\n"
        "  • Create a lesson plan on agentic AI for senior managers\n\n"
        "Commands:\n"
        "  /agents — list the team\n"
        "  /start  — welcome message\n"
        "  /help   — this message\n\n"
        "Long tasks (reports, new agents) take a few minutes. "
        "You'll get an acknowledgment immediately and the result when done."
    )


# ── Message handler ────────────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update):
        await update.message.reply_text("Access denied.")
        return

    task_text = update.message.text.strip()
    if not task_text:
        return

    # Run silently in background — typing indicator shows progress
    asyncio.create_task(
        _execute_and_reply(task_text, update.effective_chat.id, context)
    )


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Starting Agentic Team Telegram Bot...")
    print("Press Ctrl+C to stop.\n")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("agents", cmd_agents))
    app.add_handler(CommandHandler("help",   cmd_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
