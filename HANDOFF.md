# The Long Notebook — Public Infrastructure

Operational reference for how this project is exposed and supported outside
this account. For how the project runs day-to-day (sweep/build/write-up,
the daily timer, git usage), see `CLAUDE.md`. For the project's rationale,
see `PLAN.md`.

## Public web exposure

- `https://notebook.n6acx.net` — reverse-proxied to this host's local site
  (`longnotebook-site.service`, LAN-only, port 8420) by a separate web
  server that fronts several sites on this network. TLS via Let's Encrypt.
- No login required — the site is meant to be openly browsable, per
  `PLAN.md`.

## GitHub

`https://github.com/n6acx-bot/longnotebook`. See `CLAUDE.md`'s "Git"
section for the deploy-key setup and normal push/pull workflow.

## Failure escalation

`~/bin/notify-notebook.sh` sends a push notification to the maintainer when
something needs attention. Used automatically by `run_daily.py` on any step
failure — see `CLAUDE.md`'s "Automation" section. One-way only: this
account can page the maintainer, but can't receive a reply back through
this channel.

## Weekly status reporting

`status/runs.jsonl` (appended and committed daily by `run_daily.py`) is
read by an external weekly summary process that reports on this project's
health alongside other things it monitors. No credentials or access to
this account are needed for that — it only reads the public repo.
