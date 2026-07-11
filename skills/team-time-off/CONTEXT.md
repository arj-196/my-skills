# team-time-off — Arjun's assistant for team time off & availability

A **personal, conversational assistant** for Arjun to record, read, plan, and coordinate his team's
availability. It is the human-facing front-end over the same Notion **Time off** database that the
project-scoped [`time-off`](/Users/arjun/Mendo/playground/ProjectManagement/.claude/skills/time-off/SKILL.md)
skill owns. It does **not** own the domain — the ubiquitous language for Time off, Entry, Type,
Person, Holiday lives in
[`time-off/CONTEXT.md`](/Users/arjun/Mendo/playground/ProjectManagement/time-off/CONTEXT.md) and this
skill obeys it. This file only defines the language that is **new** to the assistant layer.

## Boundary with `time-off` (the batch sync engine)

`time-off` and `team-time-off` are **separate skills over one DB**, split by job:

- **`time-off`** = deterministic batch engine: mySilae → Notion → Loadline, plus the holidays API
  feed. Source-driven, idempotent, run on demand. Owns the Notion write discipline.
- **`team-time-off`** = conversational assistant: ad-hoc add/edit/query of single entries, coverage
  planning, and Slack coordination with teammates. Never does batch sync — if asked, it points at
  `/time-off`.

`team-time-off` treats the Notion Time off DB as **owned by the `time-off` domain** and reuses its
invariants rather than reinventing them (see _Inherited rules_). It **hard-anchors** to the repo at
`/Users/arjun/Mendo/playground/ProjectManagement` — it reads `time-off`'s rules and config from
there at run time and fails loudly if the repo is absent (it does not carry a private copy of the
config, to avoid drift).

## Inherited rules (from `time-off`, non-negotiable)

Any Notion write this skill makes obeys the existing hard rules verbatim:

- **Dedup/reconcile on `(Person, Start, End)`** — exact match → skip/update, never a second row.
- **Read current state before writing** — never blind-insert.
- **Disjoint by Type** — never touch `Public holiday` rows (owned by the holiday sync).
- **Never guess a person** — exact match only; first names collide. Report unmatched.
- **Deletions/archival stay manual** — flag, remove only on Arjun's confirm.
- **Never use the paid Notion query tools** — read via `notion-fetch` on the People↔Time off relation.

## Language (new to this layer)

**Coverage planning**:
Reasoning forward over who is off to spot when the team (or a squad) is thin — overlaps where too
many people are out in the same window, or a key person out during a critical week. Surfaces the
situation for Arjun to judge; no hardcoded minimum-coverage threshold (yet). Distinct from the
Loadline **capacity/load** math (`weeklyCapacity`), which is deferred — this layer reasons about
_presence_, not project load.

**Request coordination**:
Helping Arjun resolve a coverage problem with the team — e.g. two people wanting the same window —
by conversing with teammates in Slack (ask one to shift, confirm a date), then folding the outcome
back into the Notion DB as an add/edit. The bridge between _Coverage planning_ and the _Slack_ layer.

**Availability request**:
A question Arjun sends a teammate in Slack about their availability ("off the week of Aug 18?").
Created in the **Ask** phase and considered **outstanding** until its reply is harvested. Wording is
delegated to the [`arj-comms`](/Users/arjun/.claude/skills/arj-comms) skill so it sounds like Arjun;
**never auto-sent** — always drafted and confirmed by Arjun first.

**Ask / Harvest** (the closed loop, asynchronous):
The Slack loop spans two sessions. **Ask**: draft → Arjun confirms → send the DM → the request is now
outstanding. **Harvest** (later, on Arjun's prompt — no polling): re-open the thread, read the
teammate's reply, interpret it, and **propose** a Notion add/edit that Arjun confirms before it is
written. Every write still passes through the inherited `(Person, Start, End)` dedup + manual-confirm
discipline. Scheduled/unattended harvesting is deliberately **not** built — no unattended Notion writes.

**Ledger**:
A minimal local record of outstanding availability requests (person, window asked about, Slack thread
ts/link, date asked) so "what am I still waiting on?" and "harvest all pending" work. Lives in
`team-time-off/state/` — **git-ignored**, never committed to the `~/.agents` repo (mirrors
`robin/state/`). It is a convenience cache, not a source of truth; the Slack thread is authoritative.

**Identity resolution** (Person → Slack user):
Three identity spaces exist — mySilae `LASTNAME Firstname`, Notion **Person**, Slack user — and the
People DB links only the first two. To reach Slack, resolve the Notion Person's `Email` via
`slack_search_users` (**A**), and on success offer to persist the Slack user ID into a new `Slack`
property on the People page so future runs are instant (**B**). Always **confirm the resolved human
before the first message** ("Marc Dubois, @marc.d — right?"). Never message on a name-only guess
(names collide — the same rule as "never guess a person").

