---
name: arj-focus
description: Arj's twice-daily focus workflow. Monitors Slack, Outlook, and Linear for genuine action items (Commitments), tracks each as a ticket in the personal ARJ Linear workspace, and sends a low-noise Telegram Recap of what needs attention. Trigger on scheduled arj-focus runs, "/arj-focus", "run arj-focus", or "focus run".
---

# Arj Focus

Turns Arjun's incoming Signals (Slack mentions/DMs, Outlook mail, Linear
notifications) into tracked **Commitments** — one Linear Ticket each, in the
personal **ARJ** workspace — and sends a focused **Recap** to Telegram twice a
day.

Read `CONTEXT.md` (same directory) for the full glossary and reconciliation
rules, and `docs/adr/0001-linear-as-sole-state.md` for why there is no local
state store. The definitions there are binding — do not silently change them.

## Fixed facts

| What | Value |
|---|---|
| Linear workspace | "Arjun Chatterjee" (urlKey `arjun-chatterjee`), team **ARJ**, id `9cfe0eac-3600-4f74-a20a-8dcc2415ee2c` |
| Arjun / viewer | Arj — arjun@mendo.cloud |
| Telegram target | chat id `8628776494` (deliver via the cron job's `deliver='telegram:8628776494'`) |
| Last-run stamp | `~/.hermes/arj-focus/last_run.txt` (ISO timestamp; the ONLY local state) |
| Integration layer | headless `claude -p` — the single path to Slack, Outlook, Linear |

## Core rule

A **Ticket exists only for a Commitment** — something Arjun must personally act
on with a real done-state. If it is noise, it is not a Commitment and earns no
Ticket. **Urgency is a property of the task, not of who is asking** (see
CONTEXT.md → Urgency). Bots/tools that only relay information (Linear, Revo,
Notion Slack bots) are never Commitments.

## A Run, step by step

### Step 1 — Window

Read `~/.hermes/arj-focus/last_run.txt`.
- **Missing** (first Run ever) → window = last **7 days** (seed the backlog).
- **Present** → window = last **24 hours** (deliberate overlap; dedup handles it).

Do NOT update the stamp yet — only after a successful Run (Step 6).

### Step 2 — Pull Signals (one headless call)

Invoke Claude Code headlessly to gather Signals from all three sources in the
narrow v1 scope (CONTEXT.md → Source scope). Grant the exact tools:

```
claude -p "<signal-gathering prompt>" \
  --permission-mode acceptEdits \
  --allowedTools \
    "mcp__claude_ai_Slack__slack_search_public_and_private" \
    "mcp__claude_ai_Slack__slack_search_public" \
    "mcp__claude_ai_Slack__slack_read_thread" \
    "mcp__claude_ai_Slack__slack_read_user_profile" \
    "mcp__claude_ai_Microsoft_365__outlook_email_search" \
    "mcp__claude_ai_Linear__list_issues" \
    "mcp__claude_ai_Linear__get_issue" \
    "mcp__claude_ai_Linear__list_comments"
```

The prompt must ask for, within the window:
- **Slack**: DMs + group DMs + channel @-mentions (`to:me` search). Exclude
  pure bot/tool relay messages. For each: sender, channel/DM, permalink or
  message ts, ISO time, one-line gist.
- **Outlook**: unread inbox mail addressed directly to Arjun (to/cc). Exclude
  newsletters/bulk. For each: sender, message-id, ISO time, subject + gist.
- **Linear (ARJ)**: open issues assigned to Arjun or @-mentioning him. For
  each: identifier, id, title, gist.

Require structured output (one Signal per line with its **stable ID**) so the
IDs can be used as Source anchors.

### Step 3 — Fetch current Tickets (dedup basis)

`list_issues` for team ARJ in **all** states (open + recently closed). For each,
read the **Source anchors** recorded in its description. Linear is the sole
source of truth (ADR 0001) — trust it over any assumption.

### Step 4 — Reconcile (CONTEXT.md → Reconciliation rules)

For each Signal, match its stable ID against the anchors:
- **Anchor → OPEN Ticket, new thread activity** → `save_comment` on that Ticket
  ("follow-up received <time>: <gist>") and raise Priority if warranted. **Never
  create a second Ticket.**
- **Anchor → CLOSED Ticket** (Done/Canceled) → already handled. Stay silent.
- **No anchor match** → candidate new Commitment. Judge: is there a real action
  Arjun must take? If yes → Step 5. If it's noise/FYI → drop it (no Ticket).

Anchor suppression is per-message/thread ID and lasts forever.

### Step 5 — Create Tickets for new Commitments

For each new Commitment, `save_issue` in team ARJ with:
- **Title** — the commitment as an action ("Reply to Bérengère re: Marcel Tessier").
- **Priority** — set per CONTEXT.md → Urgency (task-first; sender is a modifier).
- **Description** — must contain:
  - **Delivery checklist** — concrete steps, possibly multi-channel
    (e.g. "- [ ] post in #fifty-talents\n- [ ] email Bérengère").
  - **why this priority:** one line of rationale (so Arjun can correct it).
  - **Source anchors:** every originating stable ID, one per line
    (`source: slack:<permalink>` / `source: outlook:<message-id>` / `source: linear:<id>`).

Writes go through Claude Code's Linear MCP (`save_issue`, `save_comment`) — same
`claude -p` mechanism, add those two tools to `--allowedTools`. No raw API key.

### Step 6 — Recap + stamp

Compose the **Recap** (CONTEXT.md → Recap shape) and make it this job's final
message so the cron delivers it to Telegram:
- Urgent + High listed by title (`ARJ-NN · commitment`); Medium/Low counted with
  a deep link to the filtered ARJ view.
- Footer: `N new since last run · N nudged · N open total`.
- **Empty Run** → one-line heartbeat ("✅ All clear — N open, none urgent"),
  never silence.

Only after the Recap is composed, write the current ISO timestamp to
`~/.hermes/arj-focus/last_run.txt`. If any earlier step failed hard, do NOT
update the stamp (so the next Run re-covers the window) and say so in the Recap.

## Pitfalls

- **Permission gate**: headless `claude -p` silently refuses MCP calls unless the
  exact tool names are in `--allowedTools`. If a source returns nothing,
  suspect a missing/renamed tool grant before concluding "no Signals".
- **Slack has no true mentions endpoint** — the `to:me` search is a proxy; an
  oddly-phrased channel @-mention can be missed. Arjun feeds back real misses;
  do not widen scope preemptively.
- **Never re-ticket a closed thread** — always check anchors across ALL Ticket
  states, not just open ones.
- **Bots are never Commitments** — Linear/Revo/Notion Slack relays get dropped
  even though they appear as DMs.
- **Rotate the key**: the raw Linear API key Arjun once pasted is unused by this
  workflow (all Linear access is via Claude Code MCP). It should be rotated and
  discarded; never persist it anywhere.
