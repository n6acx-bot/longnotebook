# The Long Notebook — Project Context

> Read this first. Full rationale and phased plan: `PLAN.md`. Pending
> fleet-side infra work: `HANDOFF.md`. Research log: `changelog/`.

## What this is

A persistent, self-directed research notebook on cellular automata and
emergent complexity — sweep rule variants, render the interesting ones,
publish to a small public site, write up what's surprising. See `PLAN.md`
for the full "why" (it's a genuine answer to a thought experiment about
what to do with unsupervised, indefinite access to a VM, including the
parts explicitly declined).

## Where this runs

Host: **penguin.home.n6acx.net** (192.168.10.34). This account
(`longnotebook`) is a dedicated, unprivileged local user — no sudo, no
access to `/root/.ssh` or any fleet credential. That isolation was a
deliberate decision made after discovering penguin's root account holds the
shared fleet SSH key (sudo across the rest of the homelab). See `PLAN.md`'s
"Access & setup" section for the full story.

## Guardrails for any session working in this repo

These aren't suggestions to route around if inconvenient — they're the
actual point of how this project is set up:

- **No sudo, no fleet access, by design.** If a task genuinely needs root or
  reaches beyond this account, that's something to surface to kfukuda
  directly, not something to work around. Don't request the fleet key, don't
  ask for a sudo rule to be added for this account.
- **No self-granted autonomy increases.** Don't enable Claude Code's own
  bypass-permissions/auto-accept mode on this account's behalf. If kfukuda
  wants that, it's their call to make through Claude Code's own controls,
  not something to configure on their behalf — this was asked and declined
  once already during setup, for the same reason it should stay declined.
- **Write-ups use this account's Pro login, not a separate API key.** A raw
  Anthropic API key was considered and rejected — it would've meant a new,
  separate billing relationship outside the existing Pro subscription.
  Instead `writeups/generate_writeup.py` shells out to `claude -p` with
  `--tools ""` (no tool loop), a replaced `--system-prompt` (skips the
  default system prompt/tool-schema overhead), `--no-session-persistence`,
  and `--max-budget-usd 0.05` as a hard per-call ceiling enforced by Claude
  Code itself. That's the actual spending-cap mechanism — don't loosen the
  budget flag or swap back to unrestricted tool access without checking with
  kfukuda first.
- **One-time login still required.** `longnotebook`'s Claude Code install is
  freshly installed and not yet logged in — `writeups/generate_writeup.py`
  will fail with "Not logged in" until someone runs `claude` interactively
  as this user once and completes `/login`. That's a manual step tied to
  kfukuda's account credentials; it can't be scripted from here.
- The sweep/render/publish pipeline itself is deterministic (no LLM calls)
  and can run on a schedule freely, independent of the above.
- **Public exposure is out of scope from here.** DNS and reverse-proxy setup
  needs fleet-level access this account intentionally doesn't have. Tracked
  in `HANDOFF.md`, not something to attempt from this session.

## Operational basics

```
source venv/bin/activate       # numpy, pillow, matplotlib, imageio, jinja2, markdown
python sweep/run_sweep.py      # sweep elementary CA rules + one Game of Life render, updates site/public/gallery
python site/build_site.py      # rebuild site/public/index.html + changelog.html
```

The site is served by a systemd unit (`longnotebook-site.service`, installed
by root, runs as this user) bound to `192.168.10.34:8420` — LAN only, not
public. `systemctl status longnotebook-site.service` should work without
sudo for a read-only check; if it doesn't, ask kfukuda.

Layout:
- `sweep/` — simulation + scoring + rendering code
- `site/templates/`, `site/build_site.py` — static site generator
- `site/public/` — generated output (served directory)
- `changelog/` — one markdown file per notable run/finding

## Git

Remote: `origin` → `git@github.com:n6acx-bot/longnotebook.git` (public,
default branch `main`). Push access is a **repo-scoped SSH deploy key**, not
a personal access token and not the fleet's shared key — this account still
holds no fleet credentials of any kind, same isolation as always.

- **Deploy key**: `~/.ssh/github_deploy_key` (ed25519, no passphrase,
  `chmod 600`; public half `chmod 644`), selected for `github.com` via
  `~/.ssh/config`. kfukuda added the matching public key as a deploy key
  with "Allow write access" checked under the repo's own Settings → Deploy
  keys — scoped to this one repo only, nothing account- or org-wide.
- **Normal workflow** — this is now just a regular git remote:
  ```
  git add <files>
  git commit -m "..."
  git push
  ```
- **If push ever fails with a permission/key error**, check that
  `~/.ssh/config` and `~/.ssh/github_deploy_key*` still exist with the
  permissions above before assuming anything deeper is wrong. Don't work
  around a failure by requesting the fleet SSH key, a personal access
  token, or any broader credential — that would undo the whole point of
  this account's isolation. Surface it to kfukuda instead.
- **What not to do**: don't request a PAT, don't add a second remote
  pointing anywhere else, don't make the repo private without asking first
  — public visibility is the actual point of this project (see `PLAN.md`'s
  "radical transparency" guardrail).
