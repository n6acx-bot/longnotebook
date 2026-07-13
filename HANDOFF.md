# Long Notebook — Handoff for svc-claude / fleet session

## Context

The Long Notebook (cellular automata research notebook, see `PLAN.md` in this
repo) runs on **penguin.home.n6acx.net (192.168.10.34)**, under a dedicated
unprivileged local account, **`longnotebook`** — not root, no sudo, no access
to the svc-claude fleet key. That isolation was a deliberate decision (see
`PLAN.md`'s "Access & setup" section) after discovering `/root/.ssh/id_ed25519`
on penguin is the shared fleet key. Everything below should preserve that
isolation, not undo it.

**Do not add penguin to the svc-claude sudo rule (`pbs-svc-claude`) or
otherwise grant svc-claude/root-equivalent access on penguin as part of this
handoff.** The items below are things to do *from* other hosts (puffin, ns1)
or credentials to deliver narrowly *to* the `longnotebook` account — not fleet
access to penguin itself.

Current state: static site live at `http://192.168.10.34:8420/` (LAN only,
systemd service `longnotebook-site.service`, hardened + runs as
`longnotebook`). Project at `/home/longnotebook/the-long-notebook` on
penguin, git-initialized locally, 2 commits, not pushed anywhere yet.

## Action items

### 1. Public web exposure — `notebook.n6acx.net` (or your preferred name)

- **ns1, internal view**: add an A record for the chosen subdomain pointing
  at **puffin's** LAN IP (hairpin pattern — same as every other public
  subdomain in this fleet, e.g. Ente). Back up the zone file first, bump the
  SOA serial, `named-checkzone`, `rndc reload <zone> IN internal`.
  No public DNS change needed — the `*.n6acx.net` wildcard at the registrar
  already covers it (confirmed via the Ente rollout).
- **puffin**: new Apache vhost reverse-proxying
  `https://notebook.n6acx.net` → `http://192.168.10.34:8420/`. Include
  `disablereuse=On` on the ProxyPass (same keepalive-vs-backend-timeout
  gotcha hit on Wetty/Vaultwarden/Ente). Cert via
  `certbot --apache -d notebook.n6acx.net` — remember certbot writes
  directly to `sites-enabled`, not `sites-available`.
- No Authentik OIDC gate needed — this is meant to be an openly browsable
  public notebook (see PLAN.md). Optional: a portal-tile-only Authentik app
  (no provider) for convenience, same pattern as Ente/Vaultwarden, bound to
  `users` — purely optional, not required for the site to work.
- Verify with `dig` (not `dig @ns1` for the public check — see the
  "Public DNS is NOT actually authoritative" note in CLAUDE.md) and `curl`.

### 2. Notify/escalation tooling on penguin — needs a decision, not just a copy

`/root/.claude/scripts/notify-user.sh` / `ask-user.sh` / `check-reply.sh`
don't exist on penguin, so the project has no way to page you when it's
running unattended and hits something it can't do. Before copying anything
over: this means putting a Pushover relay credential on a box that's
deliberately kept outside the fleet's standing-credential set — treat it as
the same class of "new standing credential" decision your own CLAUDE.md flags
elsewhere, not a routine copy. If you want it, decide the scope (e.g. a
relay token distinct from the main one, so revoking it doesn't affect
anything else) before installing it.

### 3. GitHub repo — outside svc-claude's remit, needs you directly

Create `the-long-notebook` (public) under your own GitHub account — svc-claude
has no GitHub credentials of its own, this isn't a fleet-access task. Then
either hand a deploy key / PAT to the `longnotebook` account on penguin, or
push the initial commits yourself from a clone.

### 4. CLAUDE.md doc drift to fix

The fleet CLAUDE.md's "Known Remaining Items" lists penguin as *not yet*
provisioned into the CLAUDE.md git-sync — but `/root/.claude-md-repo` already
exists there (branch `proposed/penguin`, tracking `origin/main`), so it was
actually provisioned at some point after that section was last updated.
Worth a quick pass to make the doc match reality (per its own stated rule:
trust live state over the doc, then fix the doc).

## Not needed / explicitly out of scope

- No change to the svc-claude sudo rule host list.
- No secrets committed to the project's git repo.
- No bypassing the `longnotebook` account's lack of sudo — if the project
  later needs something requiring root on penguin, that's a decision for a
  live conversation, not something to bake into standing access.

## Still unresolved (mine to ask you, not an infra task)

A spending cap for the part of Phase 2 that would have Claude itself write
periodic notebook entries (real, ongoing API/subscription usage, no natural
ceiling otherwise). Not blocking anything above, but blocking that specific
piece of automation.
