# 0002 — Deterministic pre-check gate + one implementation at a time

Date: 2026-07-04
Status: accepted

## Context

Arjun wants a 30-minute cadence (≈48 ticks/day) but most ticks find nothing:
no new bullets, no Slack replies. Paying model tokens to discover "nothing"
48 times a day is waste. Separately, the first thing Arjun ever wrote about
Robin was a bug report: "the runner is picking up multiple tasks and I don't
think any of them is running" — unbounded parallel implementation produced
zero finished work.

## Decision

1. Every tick starts with `scripts/precheck.py`, a pure-Python, read-only
   gate that parses the inbox and state.json and prints NOOP or WORK. On
   NOOP the model stops immediately — no Slack, no Notion, no exploration.
   Slack is only queried when state says a task is actually awaiting a reply.
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
