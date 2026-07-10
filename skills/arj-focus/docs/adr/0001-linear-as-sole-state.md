# Linear is the sole source of truth for Run state

**Context.** The arj-focus workflow runs twice daily and must not re-create
Tickets it has already made (dedup via Source anchors). It needs to know, each
Run, which Signals are already tracked. Robin — the sibling scheduled workflow
in this repo — keeps a rich local `state.json` because its Obsidian inbox has no
queryable status. We considered the same here.

**Decision.** arj-focus keeps **no meaningful local state**. Each Run queries
the ARJ Linear workspace for Tickets in all states, reads the Source anchors out
of their descriptions, and dedups against that live. The only thing persisted
locally is a trivial last-run timestamp (`last_run.txt`) used to compute the
"N new since last run" footer and to distinguish a first-ever Run; the scan
window is a fixed rolling 7 days on every Run (see SKILL.md → Step 1). Linear is
the single source of truth.

**Why.** At Arjun's ticket volume (dozens, not thousands) fetching open +
recently-closed ARJ Tickets each Run is cheap, and one source of truth
eliminates an entire class of drift bugs — e.g. Arjun closing a Ticket by hand
in Linear while a local cache still thinks it is open. This deliberately
diverges from Robin, whose inbox is not queryable and therefore *requires* a
local state mirror.

**Consequences.** Every Run pays a full-list Linear read (acceptable at this
volume; revisit if ARJ ever holds thousands of Tickets). Source anchors must be
written durably into Ticket descriptions and must survive on closed Tickets, so
that a resurfacing old thread stays suppressed. No cache to corrupt, no
reconciliation logic between two stores.
