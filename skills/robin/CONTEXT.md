# Robin — Context

Robin is Arjun's autonomous coding agent, running under **Hermes**: a scheduled
pipeline that turns feedback Arjun drops on Telegram into implemented, verified
code changes, negotiating everything ambiguous on each task's Notion page and
keeping the reviewable record there.

Robin has no Obsidian vault and no Slack — those belonged to the earlier
Claude-routines version (see ADR 0003 for the migration).

## Glossary

**Feedback** — a raw message Arjun sends on Telegram starting with the word
`Feedback`. Captured verbatim into the append-only log `feedback.jsonl` as an
`F-<n>` row. Feedback is *input*, NOT a unit of work — it is not a Task.

**Capture** — the cheap, synchronous turn that fires when a `Feedback …`
Telegram message arrives: it appends the row and acks. No grouping or planning
happens in capture; that waits for the next Tick so a batch groups together.

**Grouping** — the Ingest step where Robin analyzes all unprocessed feedback as
a batch and shapes Tasks from it: related feedback is merged into one Task (even
across several `F-n`); a single feedback is split only if it holds clearly
separate asks. Recorded per Task as `source_feedbacks`.

**Task** — one coherent piece of work, `R-<n>`, derived from one or more
Feedbacks. Maps to one repo (App) via `app_paths`. Robin's own repo is itself an
App; Tasks against it are Self-modification.

**App** — a target repo. Mapped from `app_paths` in state.json.

**Stage** — a Task's position in the pipeline: ingested → grilling → planning →
review → implementing → done, with blocked and dropped as exits. Mirrored on two
surfaces: state.json (runner truth) and the Notion page (human record +
conversation).

**Tick** — one scheduled run (every 30 min) or an on-demand "robin tick". Begins
with the Gate; a tick with nothing to do costs near-zero tokens.

**Gate** — the deterministic `precheck.py` script. Verdict NOOP ends the tick
immediately; verdict WORK enumerates exactly what changed. It detects two kinds
of change with ZERO model tokens: new unprocessed feedback (local log), and a
waiting Task whose Notion page `last_edited_time` moved (plain Notion REST poll).

**Notion Q&A block** — the `❓ Robin needs input` block on a Task's Notion page:
numbered questions with lettered options (one recommended), an `A:` line per
question for Arjun, and a `Done — Robin, proceed` checkbox. The checkbox is
Arjun's deterministic "I'm finished answering" signal; Robin reads the answers
only when it's ticked, then decides whether it's satisfied enough to advance.

**Round** — one Q&A block posted + Arjun's answers. Budgeted by Complexity in
grilling (simple 3, complex 5, very-complex 10); review is unbudgeted.

**Complexity** — Robin's classification of a Task (simple / complex /
very-complex). Sets the grilling Round budget. Self-modification Tasks are at
least complex.

**Board** — the Robin Tasks database in Notion, under the Robin home page. One
page per Task holding grouped feedback, the live Q&A block, the Q&A transcript,
versioned plan, and implementation report.

**Bridge** — how Robin (inside Hermes) reaches Notion for read/write: headless
`claude -p --allowedTools "mcp__claude_ai_Notion__notion"`. Telegram is reached
via the Hermes cron `deliver` target. See SKILL.md → Integration bridge.

**Self-modification** — a Task against Robin's own repo/skill. Same pipeline but
with mandatory plan AND diff approval; never auto-merged.

## Urgency

Urgency is a property of the Task, not of the feedback's tone or timing. Robin
does not manufacture urgency from an exclamation mark; it reasons about the work
itself when setting Complexity and priority.
