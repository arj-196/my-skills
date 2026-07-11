# team-time-off is a conversational front-end over the time-off domain, not a standalone skill

The goal is a personal assistant for Arjun to **record, read, plan, and coordinate** his team's
availability conversationally — including Slack conversations with teammates. That data already lives
in the Notion **Time off** DB, whose write discipline (dedup/reconcile on `(Person, Start, End)`,
disjoint-by-Type, manual-confirm archival, never-guess-a-person) is owned by the project-scoped
[`time-off`](/Users/arjun/Mendo/playground/ProjectManagement/.claude/skills/time-off/SKILL.md) batch
sync skill. The question was how the new assistant should relate to that existing skill and DB.

## Decision

`team-time-off` is a **separate, global, conversational skill** that treats the Notion Time off DB as
**owned by the `time-off` domain** and reuses its invariants rather than reinventing them. It owns the
human-facing surface — ad-hoc add/edit/query, coverage planning, and Slack coordination — and defers
all domain rules and config to `time-off`.

- **Separate skill, split by job.** `time-off` = deterministic batch engine (mySilae → Notion →
  Loadline + holidays API), source-driven and idempotent. `team-time-off` = conversational assistant,
  single ad-hoc operations and Slack. Different shapes of tool over one DB; keeping them separate keeps
  each coherent. `team-time-off` **never does batch sync** — it points at `/time-off` for that.
- **Delegation, not duplication.** Every Notion write `team-time-off` makes obeys `time-off`'s hard
  rules verbatim, read from `time-off/SKILL.md` + `time-off/CONTEXT.md` at run time. No private copy of
  the dedup/reconcile logic or config (data-source IDs, Type list) — that is exactly the drift this
  decision avoids.
- **Hard-anchored to the repo.** `team-time-off` is global but hard-codes the path
  `/Users/arjun/Mendo/playground/ProjectManagement` and reads `time-off`'s rules/config from there,
  failing loudly if the repo is absent. Arjun has exactly one checkout and the `time-off` domain is the
  source of truth; a portable private-config copy would recreate the drift problem.
- **Trigger split on a single discriminator.** "sync" / mySilae / holidays / Loadline → `time-off`.
  Everything conversational (add/edit/query, "who's around", overlaps, Slack) → `team-time-off`. The
  overlapping "who's off" trigger was removed from `time-off`'s description.
- **Slack loop is assisted and asynchronous.** Ask (draft via `arj-comms` → Arjun confirms → send) and
  Harvest (later, on prompt: read reply → propose Notion write → Arjun confirms) are separate phases;
  **never auto-send**, **no scheduled/unattended harvest**, every write passes Arjun's confirmation. A
  git-ignored `state/` ledger tracks outstanding requests but the Slack thread is authoritative.
- **Scope of "plan and manage": coverage + coordination only.** Reason about *presence* (who's thin,
  who overlaps) — **not** Loadline's capacity/load math, which is deferred while Loadline is a prototype
  and `time-off` owns its push.

## Rejected alternatives

- **Standalone sibling** — `team-time-off` re-implements its own Notion write path, sharing only the
  DB and data-source IDs. Rejected: two write paths over one DB inevitably drift, and the `time-off`
  invariants were hard-won (stale-row reconciliation, disjoint-by-Type). A second, looser writer is the
  fastest way to reintroduce duplicates or delete holidays.
- **Merge into `time-off`** — add conversational + Slack actions to the existing skill. Rejected: a
  batch sync engine and a conversational assistant have opposite shapes (idempotent bulk vs. single
  interactive ops); merging bloats `time-off`'s description and trigger surface and couples a global
  personal tool to a project skill's lifecycle.
- **Portable skill carrying its own config copy.** Rejected for the same drift reason as standalone —
  a stale copy of the data-source IDs or Type list is worse than a loud failure when the repo is absent.
- **Closed-loop with scheduled/unattended harvesting.** Deferred: a cron that misinterprets a Slack
  reply and writes to Notion unattended is exactly the unattended write the domain avoids. Manual
  harvest first; automate only once the loop is proven. Not a one-way door.
