---
name: team-time-off
description: >-
  Arjun's conversational assistant for his team's time off and availability. Records ad-hoc
  time off, answers "who's off?" questions, flags coverage conflicts, and runs Slack
  conversations with teammates about their availability — folding replies back into the Notion
  Time off DB. It is the human front-end over the DB that the batch-sync `time-off` skill owns,
  and reuses that skill's write rules rather than reinventing them. Trigger when Arjun says
  "/team-time-off", "put/mark Marc off next Thursday", "add time off for…", "cancel Marc's
  Friday", "who's off / who's around next week", "is Marc free Tuesday", "any overlaps / is the
  team covered in August", "ask Marc about his availability", "message the team about time off",
  or "harvest the replies". For batch sync (mySilae / public holidays / Loadline push) use
  `time-off` instead — this skill never syncs.
---

# /team-time-off

Arjun's **conversational assistant** for recording, reading, planning, and coordinating his team's
availability. It is the human-facing front-end over the Notion **Time off** DB. It does **not** own
that domain: the ubiquitous language (Time off, Entry, Type, Person, Holiday) lives in
[`time-off/CONTEXT.md`](/Users/arjun/Mendo/playground/ProjectManagement/time-off/CONTEXT.md) and the
write discipline lives in
[`time-off/SKILL.md`](/Users/arjun/Mendo/playground/ProjectManagement/.claude/skills/time-off/SKILL.md).
This skill **reuses** those rules — it never reinvents them. The assistant-layer language (Coverage
planning, Ask/Harvest, Ledger, Identity resolution) is in
[`CONTEXT.md`](./CONTEXT.md); the boundary decision is
[ADR 0001](./docs/adr/0001-team-time-off-is-a-conversational-front-end-over-the-time-off-domain.md).

```
/team-time-off <action>

actions:
  add        Record one ad-hoc time off Entry ("put Marc off Thu–Fri"). Default.
  cancel     Edit or archive an existing Entry ("Marc's back Friday" / "cancel Marc's day off").
  check      Read the DB and answer availability questions ("who's off next week?", "is Marc free?").
  plan       Coverage view over a horizon — surface overlaps / thin squads for Arjun to judge.
  ask        Draft (via arj-comms) → confirm → send a Slack availability question; log it as outstanding.
  harvest    Read replies to outstanding requests, interpret, and propose Notion writes to confirm.
  help       Print this action list.
```

Pick the action from `$ARGUMENTS` / Arjun's words — but this is a **conversational** skill, so
natural language ("who's around the week of the 18th?") maps to an action directly; the slash form is
just for explicit calls:
- "put / mark … off", "add time off", "he's off / she's out" → **add**
- "actually back", "cancel", "shorten", "remove", "he's not off after all" → **cancel**
- "who's off / who's around", "is X free / available", empty query → **check**
- "any overlaps", "is the team covered", "who's thin in August", "coverage" → **plan**
- "ask X about availability", "message the team about time off", "check with X if…" → **ask**
- "did X reply", "harvest", "any answers on the pending requests" → **harvest**
- "sync", "mySilae", "public holidays", "push to Loadline" → **not this skill** → run `/time-off`.

## Preflight (every run)

1. **Anchor to the repo.** This skill hard-anchors to
   `/Users/arjun/Mendo/playground/ProjectManagement`. If it is absent, stop and say so — do not
   proceed with a guessed config. Read `time-off`'s **Config** table (bottom of its SKILL.md) for the
   live data-source IDs, match key, and Type list. **Never** hardcode a private copy of these here
   (see ADR 0001 — that is the drift this skill exists to avoid).
2. **Never use the paid Notion query tools** (`notion-query-data-sources` /
   `notion-query-database-view` — Business+ only). Read via `notion-fetch` on the People↔Time off
   relation, exactly as `time-off` does.

## `add` — record one Entry

1. **Resolve the Person.** Exact match on the People DB `Name` (or `mySilae name`). **Never guess** —
   first names collide (`PATTERSON Adrian` vs `JUMELET Adrian`). If ambiguous or unmatched, ask.
2. **Parse the window.** Resolve relative dates ("next Thursday and Friday") against today into a
   continuous `start → end` range, `YYYY-MM-DD`. **Whole days only** — no half-days (domain rule). A
   gap (off Thu, back Fri, off Mon) is **two** Entries, not one.
3. **Type.** Infer from Arjun's words — "sick" → `Sick`, "conference/offsite" → `Offsite/Conference`,
   "parental" → `Parental`; otherwise **default `Vacation`** and say so ("added as Vacation — say if
   it's something else"). Type is a human label, not the load math, so a wrong guess is cheap and
   reversible — unlike a wrong Person. Never use `Public holiday` here (owned by the holiday sync).
4. **Conflict check (proactive).** Before writing, read who else is off in that same window (and flag
   same-**Squad** thinning). Surface overlaps for Arjun to judge — don't block the write.
5. **Dedup then write.** Read current state for that Person, key on **`(Person, Start, End)`**: exact
   match → skip; same range, different Type/Notes → **update in place** (never a second row); new →
   **create**. Report what you did.

## `cancel` — edit or archive an Entry

Find the Entry by `(Person, window)`. A shortened/moved leave → **update in place**. A fully removed
leave → **archive**, but **only on Arjun's explicit confirm** (deletions stay manual — inherited hard
rule). Never touch `Public holiday` rows.

## `check` — answer availability questions

Read the Time off DB (via the relation walk) for the asked window/person and answer plainly —
"Marc is off Thu–Fri that week; everyone else is around." Include `Public holiday` rows as read-only
context (they make the whole team off) but never modify them.

## `plan` — coverage over a horizon

Read all Entries across a horizon (default: next 4–6 weeks) and surface **coverage problems** for
Arjun to judge: windows where several people overlap, a **Squad** dropping thin, or a key person out
during a window Arjun flags. No hardcoded minimum-coverage threshold — this is presence reasoning, not
Loadline capacity/load math (deferred, see ADR 0001). Output a compact week-by-week view.

## `ask` — send a Slack availability question (phase 1 of the loop)

1. **Resolve the Slack user.** Take the Person's `Email` → `slack_search_users`. On success, **offer
   to persist** the Slack user ID onto the People page (a `Slack` property) so next time is instant.
   **Confirm the human before the first message** ("Marc Dubois, @marc.d — right?"). Never message on
   a name-only guess.
2. **Draft via arj-comms.** Invoke the [`arj-comms`](/Users/arjun/.claude/skills/arj-comms) skill
   (internal register) to word the question in Arjun's voice. Show the draft.
3. **Never auto-send.** Send only after Arjun approves (a Slack DM is an outward message — explicit
   confirmation required every time).
4. **Log it as outstanding** in the ledger (below): `{person, personPageId, window, threadTs,
   channel, askedOn}`.

## `harvest` — read replies and propose writes (phase 2 of the loop)

Asynchronous — runs in a later session, on Arjun's prompt (**no polling, no scheduled/unattended
harvest**).

1. **List outstanding requests** from the ledger ("3 still waiting").
2. For each (or the one asked about): **re-open the Slack thread**, read the teammate's reply,
   **interpret** it into a concrete window + Type.
3. **Propose** the resulting `add`/`cancel` — run it through the full `add` discipline (person match,
   conflict check, `(Person, Start, End)` dedup) and **Arjun confirms before the write**.
4. On a written (or explicitly dropped) request, **clear it from the ledger**. The Slack thread is
   authoritative; the ledger is only a convenience cache.

## The ledger

A minimal JSON file at **`team-time-off/state/outstanding.json`** tracking open availability requests.
The `state/` dir is **git-ignored** (see `~/.agents/.gitignore`) — never committed. Create it lazily
on the first `ask`. Shape:

```json
{ "requests": [
  { "person": "Marc Dubois", "personPageId": "…", "window": "2026-08-18/2026-08-22",
    "channel": "D0…", "threadTs": "1723…", "askedOn": "2026-07-12" }
] }
```

## Hard rules

Inherited from `time-off` (non-negotiable — read its **Hard rules** for the full text):

- **Dedup/reconcile on `(Person, Start, End)`.** Exact match → skip/update; **never a second row**.
- **Read current state before writing.** Never blind-insert; re-running an add must be a no-op.
- **Disjoint by Type.** Never read-for-write, update, or archive `Public holiday` rows — they belong
  to the holiday sync. (They're fine to *show* in `check`/`plan` as team-wide context.)
- **Never guess a Person.** Exact match only; report unmatched for Arjun to confirm.
- **Deletions/archival stay manual.** Flag; remove only on Arjun's explicit confirm.
- **Never use the paid Notion query tools.**

New to this skill:

- **This skill never syncs.** No mySilae, no holidays API, no Loadline push. Point at `/time-off`.
- **Never auto-send Slack.** Every outbound message is drafted (via `arj-comms`) and approved by Arjun.
- **Confirm the Slack human before the first message.** Never message on a name-only guess.
- **Every Notion write from a harvested reply still passes Arjun's confirmation.**
- **Type may be inferred/defaulted; a Person may not be guessed.** The asymmetry is deliberate — Type
  is a cheap, reversible label; the wrong Person is not.

## Config

This skill deliberately holds **no private config** — it reads the live values from `time-off` at run
time (ADR 0001). The pointers:

| Key | Source |
|---|---|
| Repo anchor | `/Users/arjun/Mendo/playground/ProjectManagement` (fail loudly if absent) |
| Notion People / Time off data sources, match key, Type list | `time-off/SKILL.md` → **Config** table |
| Domain language | `time-off/CONTEXT.md` |
| Slack | MCP `slack_*` tools (`slack_search_users`, `slack_send_message`, `slack_read_thread`, …) |
| Voice for outbound messages | `arj-comms` skill (internal register) |
| Outstanding-request ledger | `team-time-off/state/outstanding.json` (git-ignored) |
