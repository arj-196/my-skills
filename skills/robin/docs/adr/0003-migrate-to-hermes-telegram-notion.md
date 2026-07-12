# 0003 — Migrate to Hermes: Telegram capture, Notion conversation, no Obsidian/Slack

Date: 2026-07-12
Status: accepted

## Context

Robin was built for the Claude-routines runtime, where it captured tasks from an
Obsidian vault inbox (`🤖 R-n` markers) and negotiated every ambiguity in a
Slack thread per task, with Notion as the write-only record. Arjun moved the
runner to Hermes and asked for three behaviour changes at the same time:

1. Stop reading Obsidian. Feedback now arrives on Telegram.
2. Stop all Slack communication. Move the entire conversation (questions,
   answers, plan approval) onto each task's Notion page.
3. Treat what he drops as *feedback, not tasks* — Robin must group related
   feedback into tasks and may cover multiple feedbacks in one task.

Under Hermes, Robin has no direct Slack/Notion tools; the only integration path
is headless `claude -p --allowedTools "mcp__claude_ai_<Server>__<tool>"`, the
same bridge the sibling `arj-focus` skill uses.

## Decision

- **Capture** is a Telegram message whose text starts with `Feedback`. A cheap
  capture turn appends it to `~/.hermes/robin/feedback.jsonl` (`add_feedback.py`)
  and acks; no work happens until the next tick, so batches group together.
- **Grouping** is the new front of the Ingest stage: Robin analyzes all
  unprocessed feedback as a batch and derives Tasks, recording `source_feedbacks`
  per Task. Feedback ≠ Task.
- **Conversation** lives entirely on the Notion page via a `❓ Robin needs input`
  block: numbered questions, lettered options with a recommendation, an `A:`
  line per question, and a `Done — Robin, proceed` checkbox. The checkbox is
  Arjun's deterministic "finished answering" signal — Robin reads answers only
  when it is ticked, then decides if it is satisfied enough to advance the stage
  (or posts follow-ups and unticks). Same mechanism serves grilling and review.
- **Change detection stays token-free.** `precheck.py` no longer parses a vault;
  it polls each `awaiting_answer` task's Notion `last_edited_time` via a plain
  REST call (`NOTION_API_KEY` from `~/.hermes/.env`) and compares it to the
  `notion_last_edit` Robin recorded. Newer ⇒ Arjun edited ⇒ wake that task.
  Unchanged pages are never read, so idle waiting costs no model tokens.
- **State** drops from three surfaces to two (ADR 0001 amended): state.json +
  Notion. Telegram is capture + notify only and holds no state.
- **Notion read/write** goes through the `mcp__claude_ai_Notion__notion` bridge;
  the cheap poll uses the REST API directly. Two paths, two jobs.

## Consequences

- No Obsidian dependency; `precheck.py` no longer parses Markdown or edits any
  vault file. The old `parse_vault`, marker regexes, and `sections_missing_path`
  logic are gone.
- No Slack dependency; the Slack tool grants and thread bookkeeping are gone.
- Robin must refresh `notion_last_edit` after every read AND every write, or its
  own edits would re-trigger the gate (self-wake loop). This is a load-bearing
  invariant called out in SKILL.md safety rails.
- A new secret is required: `NOTION_API_KEY` (Notion internal integration shared
  with the Robin home page). Without it the gate degrades safe — it wakes every
  waiting task each tick and warns — but wastes tokens until set.
- Grouping introduces judgement at ingest (which feedbacks belong together). The
  `source_feedbacks` array keeps the provenance auditable and lets Arjun see, on
  the Notion page, exactly which of his messages a task came from.
- Delivery caveat: a cron scheduled from a CLI session is local-only; Telegram
  pings require the job's `deliver` to target `telegram:8628776494` through the
  Hermes gateway.
