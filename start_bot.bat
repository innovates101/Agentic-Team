@echo off
REM CLAUDECODE must be unset — claude-agent-sdk refuses to run nested inside a Claude Code session
set CLAUDECODE=

cd /d "c:\Users\celes\.claude\Experiments\Agentic Team"
echo Starting Agentic Team Telegram Bot...
echo Press Ctrl+C to stop.
echo.
python telegram_bot.py
