"""Generate the week's plain-language write-up using this account's own
Claude Code login (Pro subscription) via `claude -p`, instead of a separate
Anthropic API key. Deliberately stripped down to a single bounded call:
no tools, no default system prompt, no session persistence, hard dollar
cap via --max-budget-usd — so this stays close to a plain text completion
rather than a full agentic session, while still riding the existing
subscription instead of opening a new billing relationship.

Requires: `longnotebook` has run `claude` once interactively and logged in
(one-time manual step, same as any Claude Code login — this script can't
do that part).

Usage:
    python writeups/generate_writeup.py
"""
from __future__ import annotations

import datetime
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
GALLERY = ROOT / "site" / "public" / "gallery"
CHANGELOG = ROOT / "changelog"

MODEL = "claude-haiku-4-5-20251001"  # cheap, fast, appropriate for a bounded summarization task
MAX_BUDGET_USD = "0.05"  # hard per-call ceiling enforced by Claude Code itself

SYSTEM_PROMPT = (
    "You maintain a small public research notebook about cellular automata "
    "and emergent complexity. You will be given this week's sweep results "
    "and recent prior entries. Write ONLY the new entry: plain prose, "
    "roughly 250-400 words, no headers, no preamble, no closing remarks. "
    "Be honest and specific rather than hyped — if nothing this week is "
    "especially surprising, say so plainly instead of overselling it."
)


def latest_manifest() -> dict:
    path = GALLERY / "manifest.json"
    if not path.exists():
        print(f"No manifest at {path} — run sweep/run_sweep.py first.", file=sys.stderr)
        sys.exit(1)
    return json.loads(path.read_text())


def recent_changelog_text(n: int = 2) -> str:
    entries = sorted(CHANGELOG.glob("*.md"), reverse=True)[:n]
    return "\n\n---\n\n".join(p.read_text() for p in entries)


def build_prompt(manifest: dict, prior: str) -> str:
    return f"""This week's sweep results (rule, complexity score, image file):
{json.dumps(manifest, indent=2)}

Recent prior entries, for tone and continuity (do not repeat their content):
{prior or "(none yet — this is the first entry)"}
"""


def main() -> None:
    manifest = latest_manifest()
    prior = recent_changelog_text()
    prompt = build_prompt(manifest, prior)

    result = subprocess.run(
        [
            "claude", "-p",
            "--system-prompt", SYSTEM_PROMPT,
            "--tools", "",
            "--no-session-persistence",
            "--output-format", "text",
            "--max-budget-usd", MAX_BUDGET_USD,
            "--model", MODEL,
            prompt,
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        print(f"claude -p failed (exit {result.returncode}):\n{result.stderr}", file=sys.stderr)
        if "not logged in" in result.stderr.lower() or "login" in result.stderr.lower():
            print(
                "\nThis account's Claude Code install may not be logged in yet. "
                "Run `claude` interactively once as longnotebook to log in, then retry.",
                file=sys.stderr,
            )
        sys.exit(1)

    text = result.stdout.strip()
    today = datetime.date.today().isoformat()
    out_path = CHANGELOG / f"{today}-writeup.md"
    out_path.write_text(f"# {today}\n\n{text}\n")

    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
