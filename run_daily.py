#!/usr/bin/env python3
"""Daily orchestrator: sweep -> write-up -> build site -> commit/push.

Run once a day by longnotebook-daily.service (systemd timer). Each step is
best-effort — a failure in one doesn't skip the others, so a broken write-up
step still lets that day's sweep results get built and published. Always
appends one status line to status/runs.jsonl and commits/pushes it, even on
a fully failed day, so the weekly digest (which reads this file straight off
the public GitHub repo, no credentials needed) has an honest record.

Any failure pages kfukuda via notify-notebook.sh.
"""
from __future__ import annotations

import datetime
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
VENV_PYTHON = ROOT / "venv" / "bin" / "python3"
NOTIFY = Path.home() / "bin" / "notify-notebook.sh"
STATUS_FILE = ROOT / "status" / "runs.jsonl"


def run_step(args: list[str], timeout: int) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            args, cwd=ROOT, capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            return False, result.stderr.strip()[-2000:]
        return True, ""
    except subprocess.TimeoutExpired:
        return False, f"timed out after {timeout}s"
    except Exception as e:
        return False, str(e)


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def notify(message: str) -> None:
    try:
        subprocess.run([str(NOTIFY), message], timeout=30)
    except Exception:
        pass  # a failing page shouldn't crash the run itself


def main() -> None:
    today = datetime.date.today().isoformat()
    status = {
        "date": today,
        "sweep_ok": False,
        "writeup_ok": False,
        "build_ok": False,
        "errors": [],
    }

    ok, err = run_step([str(VENV_PYTHON), "sweep/run_sweep.py"], timeout=1800)
    status["sweep_ok"] = ok
    if not ok:
        status["errors"].append(f"sweep: {err}")

    # Runs before build_site so that today's write-up (if it succeeds) is
    # already on disk when the changelog page is generated - otherwise it
    # only shows up starting the *next* day's build.
    ok, err = run_step([str(VENV_PYTHON), "writeups/generate_writeup.py"], timeout=180)
    status["writeup_ok"] = ok
    if not ok:
        status["errors"].append(f"writeup: {err}")

    ok, err = run_step([str(VENV_PYTHON), "site/build_site.py"], timeout=300)
    status["build_ok"] = ok
    if not ok:
        status["errors"].append(f"build_site: {err}")

    STATUS_FILE.parent.mkdir(exist_ok=True)
    with open(STATUS_FILE, "a") as f:
        f.write(json.dumps(status) + "\n")

    git("add", "-A")
    commit = git("commit", "-m", f"Daily update: {today}")
    status["committed"] = commit.returncode == 0
    if commit.returncode == 0:
        push = git("push")
        status["pushed"] = push.returncode == 0
        if push.returncode != 0:
            status["errors"].append(f"push: {push.stderr.strip()[-500:]}")
    else:
        status["pushed"] = False

    if status["errors"]:
        summary = "; ".join(status["errors"])[:800]
        notify(f"Daily run {today} had problems: {summary}")
        sys.exit(1)


if __name__ == "__main__":
    main()
