# 0002 — Deterministic pre-check gate + one implementation at a time

Date: 2026-07-04
Status: accepted

## Context

Arjun wants a 30-minute cadence (≈48 ticks/day) but most ticks find nothing:
no new feedback, no new Notion answers. Paying model tokens to discover
"nothing" 48 times a day is waste. Separately, the first thing Arjun ever wrote
about Robin was a bug report: "the runner is picking up multiple tasks and I
don't think any of them is running" — unbounded parallel implementation
produced zero finished work.

## Decision

1. Every tick starts with `scripts/precheck.py`, a pure-Python, read-only,
   ZERO-model-token gate that prints NOOP or WORK. On NOOP the model stops
   immediately — no bridge call, no Notion body read, no exploration. It
   detects change from two cheap sources only: unprocessed rows in the local
   feedback log, and — for tasks marked `awaiting_answer` — a Notion page whose
   `last_edited_time` moved since Robin last read it (a plain Notion REST poll,
   not the LLM bridge, and never a page-body read). A Notion page body is read
   (via the bridge) ONLY after the gate confirms that page changed. (Revised
   from the original vault-parsing gate — see ADR 0003.)
2. Cheap stages (ingest, grilling, planning, review) advance for ALL tasks
   every tick, but at most ONE task is in `implementing` at a time
   (`implementing_now` lock); approved tasks queue behind it.

Alternatives rejected: lower frequency (2–4×/day) conflicts with the desired
Slack-reply latency; fully parallel implementation reproduces the observed
failure; per-project locks add complexity without evidence they're needed yet.

## Consequences

- The 30-minute loop is economically viable; latency for a Slack answer to
  be picked up is ≤30 min.
- The gate's NOOP contract is load-bearing: `precheck.py` must stay
  deterministic and read-only, and self-modification tasks may not weaken it
  without an approved plan explicitly saying so.
- A very long implementation delays queued tasks; acceptable for a
  single-user pipeline, revisit with per-project locks if it hurts.
