# Robin — Context

Robin is Arjun's autonomous coding agent: a scheduled pipeline that turns
phone-captured bullets in an Obsidian note into implemented, verified code
changes, negotiating everything ambiguous through Slack and keeping the
reviewable record in Notion.

## Glossary

**Inbox** — the single Obsidian file `A2 - TODO Apps.md` in the iCloud vault.
Write-mostly from Arjun's side (phone or desktop). Robin's edits are limited
to Markers and one-time `| path |` tables.

**App** — a `## <name>` section of the Inbox. Maps to one repo via its
`| path |` table (or the cached mapping in state). `## Robin` is itself an
App whose repo is Robin's own skill directory.

**Task** — one top-level bullet under an App, plus everything below it (any
indentation, bulleted or plain lines) until the next top-level bullet,
heading, table, or horizontal rule. Content under an **Ideas** block is
never a Task.

**Marker** — the `🤖 R-<n> <stage>` suffix Robin appends to a Task's bullet.
Serves as dedup key (a marked bullet is never re-ingested) and as at-a-glance
status inside Obsidian.

**Stage** — a Task's position in the pipeline: ingested → grilling →
planning → review → implementing → done, with blocked and dropped as exits.
Stage is mirrored on three surfaces: Marker (glance), state.json (runner
truth), Notion (review record).

**Tick** — one scheduled run, every 30 minutes. Begins with the Gate; a tick
with nothing to do costs near-zero tokens.

**Gate** — the deterministic `precheck.py` script. Verdict NOOP ends the tick
immediately; verdict WORK enumerates exactly what needs attention.

**Round** — one batched Slack message of grilling questions and its reply.
Budgeted by Complexity: simple 3, complex 5, very-complex 10.

**Complexity** — Robin's classification of a Task (simple / complex /
very-complex). Sets the Round budget. Self-modification Tasks are at least
complex.

**Board** — the Robin Tasks database in Notion, under the Robin home page.
One page per Task holding the Q&A transcript, versioned plan, and
implementation report.

**Self-modification** — a Task from the `## Robin` App. Runs the same
pipeline but with mandatory plan AND diff approval; never auto-merged.
