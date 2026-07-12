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
| Arjun / viewer | Arj — arjun@mendo.cloud (Linear user id `8576cf51-89d0-40e3-aee7-f82bcf3be6f5`; new Tickets auto-assigned to him so they show in "Assigned to me") |
| Telegram target | chat id `8628776494` (deliver via the cron job's `deliver='telegram:8628776494'`) |
| Last-run stamp | `~/.hermes/arj-focus/last_run.txt` (ISO timestamp; the ONLY local state) |
| Integration — Slack/Outlook | headless `claude -p` (MCP connected there) |
| Slack member ID | `U0B71TMF690` (handle `arjun`, display "Arj") — used to search channel @-mentions via `<@U0B71TMF690>` |
| Integration — Linear ARJ | `scripts/linear_arj.py` via GraphQL + `LINEAR_ARJ_API_KEY` (Claude's Linear MCP is scoped to Mendo and CANNOT reach ARJ — see ADR 0002) |
| API key | `LINEAR_ARJ_API_KEY` in `~/.hermes/.env` (chmod 600, never committed) |

## Core rule

A **Ticket exists only for a Commitment** — something Arjun must personally act
on with a real done-state. If it is noise, it is not a Commitment and earns no
Ticket. **Urgency is a property of the task, not of who is asking** (see
CONTEXT.md → Urgency). Bots/tools that only relay information (Linear, Revo,
Notion Slack bots) are never Commitments.

## A Run, step by step

### Step 1 — Window

Every Run scans a rolling **7-day** window of each source (Arjun's explicit
choice — 24h missed slow-burn threads). Read `~/.hermes/arj-focus/last_run.txt`
only to distinguish a first-ever Run (missing stamp) from a normal Run; the
window is 7 days either way. Dedup via Source anchors makes the heavy overlap
between Runs harmless.

Do NOT update the stamp yet — only after a successful Run (Step 6).

### Step 2 — Pull Signals (Slack + Outlook via one headless call)

Invoke Claude Code headlessly to gather Signals from Slack and Outlook in the
narrow v1 scope (CONTEXT.md → Source scope). **Linear signals are NOT gathered
here** — ARJ is read directly in Step 3 via the helper. Grant the exact tools:

```
claude -p "<signal-gathering prompt>" \
  --permission-mode acceptEdits \
  --allowedTools \
    "mcp__claude_ai_Slack__slack_search_public_and_private" \
    "mcp__claude_ai_Slack__slack_search_public" \
    "mcp__claude_ai_Slack__slack_search_channels" \
    "mcp__claude_ai_Slack__slack_read_channel" \
    "mcp__claude_ai_Slack__slack_read_thread" \
    "mcp__claude_ai_Slack__slack_read_user_profile" \
    "mcp__claude_ai_Microsoft_365__outlook_email_search" \
    "mcp__claude_ai_Microsoft_365__read_resource"
```

The prompt must ask for, within the window:
- **Slack (incoming)**: DMs + group DMs **+ @-mentions in channels Arjun follows**.
  Search channel mentions with the query `<@U0B71TMF690>` (his member ID) — this
  is the ONLY reliable mentions query; `to:me` matches DMs, not `@`-mentions, and
  returns nothing for channel mentions (verified). Paginate past the first 20
  results if a `next_cursor` is returned. Exclude pure bot/tool relay messages.
  For each: sender, channel/DM, permalink or message ts, ISO time, one-line gist.
- **Slack (outgoing — messages ARJUN sent others)**: search `from:<@U0B71TMF690>`
  across DMs and channels in the window. For each thread Arjun sent into, read
  the thread (`slack_read_thread`) and judge whether the conversation is left
  **pending on the OTHER person** — i.e. Arjun asked a question / made a request /
  is waiting on a reply or an action, and the counterpart has NOT yet responded
  or delivered. This is a Commitment for Arjun to **chase/follow-up**, not to
  reply. Report: counterpart, channel/DM, Arjun's message permalink+ts, ISO time,
  the ask, and whether a reply exists after it. Skip threads that are clearly
  resolved (counterpart answered, or it was social/FYI with no open ask).
- **Outlook**: mail addressed directly to Arjun (to/cc) within the window —
  **read AND unread** (not just unread). Exclude newsletters/bulk. For each:
  sender, message-id, **conversationId/thread-id**, ISO time, subject + gist,
  **and whether Arjun has already replied on that thread** (i.e. a message from
  arjun@mendo.cloud later than the incoming mail — read the conversation via
  `read_resource` to check). Also, for threads where Arjun HAS replied, judge
  whether his reply **closed the loop or left a pending task** (he promised to
  send something, asked the counterpart for something and awaits it, or the ask
  is only partially handled). Report the reply's ISO time, one-line gist, and a
  `pending: yes/no` flag with what remains if yes.

Require structured output (one Signal per line with its **stable ID**) so the
IDs can be used as Source anchors.

### Step 3 — Fetch current Tickets (ARJ read + Linear signals)

Run `python3 scripts/linear_arj.py list` (needs `LINEAR_ARJ_API_KEY` in env —
source `~/.hermes/.env` first). This returns every ARJ issue in all states with
its `description` (where Source anchors live) and `priority`/`state`. This
single call covers BOTH:
- the **dedup basis** (existing Tickets + their anchors), and
- **Linear as a Signal source** (an open issue assigned to / mentioning Arjun
  that has no arj-focus anchor is itself a Commitment already captured — do not
  duplicate it; treat pre-existing ARJ issues as already-tracked).

Linear is the sole source of truth (ADR 0001).

### Step 4 — Reconcile (CONTEXT.md → Reconciliation rules)

For each Slack/Outlook Signal, match its stable ID against the anchors found in
Step 3:
- **Anchor → OPEN Ticket, new thread activity** →
  `python3 scripts/linear_arj.py comment <issue-id> "follow-up received <time>: <gist>"`
  and raise Priority via `set_priority <issue-id> <0-4>` if warranted.
  **Never create a second Ticket.**
- **Anchor → CLOSED Ticket** (Done/Canceled) → already handled. Stay silent.
- **No anchor match** → candidate new Commitment. Judge: is there a real action
  Arjun must take? If yes → Step 5. If it's noise/FYI → drop it (no Ticket).
  This now includes **outgoing-thread Commitments**: a Slack/email thread Arjun
  started that is left **pending on someone else** becomes a "chase/follow-up"
  Ticket (checklist: "- [ ] nudge <person> re: <ask>"). Its done-state is the
  counterpart having replied/delivered.

Anchor suppression is per-message/thread ID and lasts forever.

### Step 4b — Done-detection (is the loop actually closed, with NO pending task?)

A Commitment is done ONLY when the loop is closed and nothing is left pending —
NOT merely because a reply exists or a mail was read. Using the reply/pending
signals from Step 2, for every OPEN Ticket:

- **Outlook "reply-to" Commitments** — close (`set_state <issue-id> Done`) ONLY
  when Arjun has replied AND that reply left **no pending task** (Step 2's
  `pending: no`). If he replied but promised something / asked for something and
  awaits it / handled it only partially (`pending: yes`) → keep the Ticket OPEN,
  `comment` the progress ("replied <time> but still owes: <what>"), and update
  the Delivery checklist to the remaining item. Reading-without-replying is never
  done.
- **Outgoing "chase" Commitments** (Slack or email threads Arjun is waiting on) —
  close when the counterpart has responded/delivered (loop closed). If still
  waiting → keep open; add a `comment` if a nudge is overdue and consider raising
  priority.
- **Multi-channel Commitments** — close only when EVERY checklist item has
  evidence. If the checklist needs a Slack post AND an email and only one is
  found, comment progress but keep it open.

Close with a one-line `comment` recording the evidence, e.g.
"auto-closed: reply detected <ISO time>, loop closed, no pending — <gist>".
This is the ONLY path that auto-closes a Ticket.

Be conservative: if it is ambiguous whether the loop is truly closed (a bare
"thanks", an out-of-office, a forward, a promise still outstanding), keep the
Ticket OPEN and note the uncertainty in a comment rather than closing it.

### Step 5 — Create Tickets for new Commitments

For each new Commitment:
`python3 scripts/linear_arj.py create '<json>'` where json is
`{"title": ..., "priority": <0-4>, "description": ..., "theme": "<theme>"}`.
Priority map: 0 none · 1 urgent · 2 high · 3 medium · 4 low. New Tickets default
to the **Todo** state (active), not Backlog, and are **auto-assigned to Arjun**
(assigneeId defaults to his user id) so they appear in his "Assigned to me"
Linear view — an unassigned Ticket is invisible in his normal filters.

**Always classify the Commitment with exactly one `theme`** (see "Theme labels"
below) so the Ticket carries quick at-a-glance context. Pick the single best-fit
theme from: `recruitment`, `team`, `management`, `client`, `product`,
`engineering`, `ops`. `create` applies it as a Theme sub-label. To (re)label an
existing Ticket use `python3 scripts/linear_arj.py label <issue-id> <theme>`.

The **description** must contain:
- **Delivery checklist** — concrete steps, possibly multi-channel
  (e.g. "- [ ] post in #fifty-talents\n- [ ] email Bérengère").
- **why this priority:** one line of rationale (so Arjun can correct it).
- **Source anchors:** every originating stable ID, one per line
  (`source: slack:<permalink>` / `source: outlook:<message-id>`).

All ARJ writes go through `scripts/linear_arj.py` (GraphQL + personal key), NOT
through Claude's Linear MCP, which cannot see the ARJ workspace (ADR 0002).

#### Theme labels (quick context)

Every Ticket gets exactly one **Theme** sub-label — a child of the `Theme`
parent label group in Linear — so the board and Recap read at a glance. The
taxonomy (create new sub-labels only on Arjun's request, keep it small):

| theme | use for |
|---|---|
| `recruitment` | candidates, interviews, job descs, hiring partners, recruitment tooling/skill |
| `team` | internal 1:1s / colleague coordination not about managing-the-org |
| `management` | leveling, comp grids, playbooks, standup/meeting scope, people-management decisions |
| `client` | anything client-facing (Forvia, Crédit Agricole, CNP, client onboarding) |
| `product` | product/PM feature specs, product feedback triage, roadmap decisions |
| `engineering` | bugs, debugging, repo/infra-in-code, technical investigations |
| `ops` | accounts, licences, equipment, contracts, invoices, internal logistics |

If a Commitment genuinely spans two, pick the one matching the **primary
action** Arjun must take. `linear_arj.py themes` prints the valid list; the
helper rejects any theme outside it. The Theme group + sub-labels already exist
in the ARJ workspace — do NOT recreate them each Run.

### Step 6 — Recap + stamp

Compose the **Recap** (CONTEXT.md → Recap shape) and make it this job's final
message so the cron delivers it to Telegram:
- Urgent + High listed by title with their theme tag
  (`ARJ-NN · [theme] commitment`); Medium/Low counted with
  a deep link to the filtered ARJ view.
- Footer: `N new since last run · N nudged · N auto-closed · N open total`.
- **Empty Run** → one-line heartbeat ("✅ All clear — N open, none urgent"),
  never silence.

Only after the Recap is composed, write the current ISO timestamp to
`~/.hermes/arj-focus/last_run.txt`. If any earlier step failed hard, do NOT
update the stamp (so the next Run re-covers the window) and say so in the Recap.

## Pitfalls

- **Permission gate**: headless `claude -p` silently refuses MCP calls unless the
  exact tool names are in `--allowedTools`. If a source returns nothing,
  suspect a missing/renamed tool grant before concluding "no Signals".
- **Slack has no true mentions endpoint** — for channel @-mentions use the
  `<@U0B71TMF690>` search query (Arjun's member ID), NOT `to:me` (which only
  matches DMs and returns zero for channel mentions). Paginate past 20 results.
  Arjun feeds back real misses; do not widen scope further preemptively.
- **Never re-ticket a closed thread** — always check anchors across ALL Ticket
  states, not just open ones.
- **Bots are never Commitments** — Linear/Revo/Notion Slack relays get dropped
  even though they appear as DMs.
- **Linear MCP ≠ ARJ**: Claude Code's connected Linear MCP is scoped to the
  Mendo org and returns nothing for team ARJ. ALL ARJ access must go through
  `scripts/linear_arj.py` (personal key). Do not try to read/write ARJ via
  `claude -p` MCP tools — that was the v1 bug (ADR 0002).
- **Key hygiene**: `LINEAR_ARJ_API_KEY` lives only in `~/.hermes/.env`
  (chmod 600, outside git). The key value pasted in chat during setup should be
  rotated in Linear and the fresh value written to `.env`; never commit it.
