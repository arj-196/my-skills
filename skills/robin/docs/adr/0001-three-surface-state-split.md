# 0001 — Task state lives on three surfaces, each with one job

Date: 2026-07-04
Status: accepted

## Context

Robin needs (a) a friction-free capture point on Arjun's phone, (b) a status
view he can check from anywhere, and (c) machine-readable state a 30-minute
cron can consult for near-zero tokens. The obvious single-source designs all
fail one leg: keeping full state in the Obsidian file risks iCloud sync
conflicts (the file is edited from the phone while Robin runs on the Mac) and
bloats the inbox; keeping it only in Notion makes every tick pay API calls
and model tokens just to learn "nothing changed"; keeping it only locally
makes status invisible from the phone.

## Decision

Split by job, not by data:
- **Obsidian inbox** — capture only. Robin's write surface is one appended
  marker per bullet (`🤖 R-n <stage>`) plus a one-time `| path |` table per
  section. The marker doubles as dedup key and glanceable status.
- **state.json (local)** — the runner's source of truth. Read by the
  deterministic pre-check gate so a no-op tick never queries Slack or Notion.
- **Notion board** — the human record: Q&A transcripts, versioned plans,
  implementation reports, stage property. Never read on the hot path.

Slack threads are the interaction log but hold no state; Robin re-reads them
only when state.json says a task is waiting on Arjun.

## Consequences

- A no-op tick costs one script run — 30-minute cadence is affordable.
- iCloud conflict surface is one line per task; a phone edit at worst delays
  a marker update by one tick (Robin re-reads before every edit and skips on
  mismatch).
- The same fact lives in three places; transitions must update all three, in
  the order vault → state → Notion → Slack. state.json is authoritative on
  disagreement; markers + Notion allow reconstruction if it's lost.
- Notion outage degrades gracefully (notion_sync_pending) without stopping
  the pipeline.
