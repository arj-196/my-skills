# 0001 — Task state lives on two surfaces, each with one job

Date: 2026-07-04 (revised 2026-07-12, see ADR 0003)
Status: accepted (amended — three surfaces reduced to two)

## Context

Robin needs (a) a friction-free capture point on Arjun's phone, (b) a status +
conversation view he can reach from anywhere, and (c) machine-readable state a
30-minute cron can consult for near-zero tokens. Single-source designs all fail
a leg: full state in one human-facing doc bloats it and risks sync conflicts;
state only in Notion makes every tick pay API/model cost just to learn "nothing
changed"; state only locally makes status invisible from the phone.

## Decision

Split by job, not by data. Under Hermes (ADR 0003) this is **two** surfaces plus
a notify channel:
- **state.json (local)** — the runner's source of truth. Read by the
  deterministic gate so a no-op tick never spends model tokens.
- **Notion board** — the human record AND the conversation surface: grouped
  feedback, Q&A blocks, versioned plans, implementation reports, stage property.
  Body is read on the hot path ONLY when the cheap gate says the page changed.
- **Telegram** — capture (inbound `Feedback …`) + notification (pings). Holds no
  state and no conversation.

The original design had a third surface — an Obsidian vault inbox with `🤖 R-n`
markers — as the capture point and glanceable status. ADR 0003 removed it:
capture moved to Telegram, glanceable status lives on the Notion board.

## Consequences

- A no-op tick costs one script run (local log read + a `last_edited_time` REST
  poll per waiting task) — no model tokens. 30-minute cadence stays affordable.
- The same fact lives in two places; transitions must update both, state first
  then Notion. state.json is authoritative on disagreement; the Notion board
  allows reconstruction if state is lost.
- Notion outage degrades: the gate fails safe (wakes waiting tasks) and warns.
