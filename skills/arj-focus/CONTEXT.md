# Arj Focus — Context

A twice-daily workflow that monitors Arjun's communication sources (Slack,
Outlook, Linear), turns genuine action items into tracked Linear tickets in his
personal ARJ workspace, and sends a focused Telegram recap of what needs his
attention. Its purpose is to stop important things being forgotten — without
becoming noise.

## Language

**Signal**:
A raw event from a source — a Slack mention/DM, an Outlook email, a Linear
notification. A Signal is *input*, not yet something to track. Most Signals
never become Commitments.
_Avoid_: notification, alert, ping (too generic)

**Commitment**:
Something Arjun must personally act on, with a real done-state (e.g. "reply to
Bérengère about Marcel Tessier next steps", "review Vincent's intent-extraction
plan"). A Commitment is the ONLY thing that earns a Linear ticket. If it's
noise, it is not a Commitment.
_Avoid_: task (overloaded — used by Robin for a different concept), todo, item

**Ticket**:
The Linear issue in the ARJ workspace that represents exactly one Commitment.
Created automatically by the workflow. Its body carries two things: the
**Delivery checklist** (the concrete steps to satisfy the Commitment, which may
span channels — e.g. "post in #fifty-talents, then email Bérengère") and the
**Source anchors** (every Signal that fed it, for dedup). It also carries
exactly one **Theme** sub-label (recruitment / team / management / client /
product / engineering / ops) for quick at-a-glance context on the board and in
the Recap. Arjun steers the workflow's judgment by leaving feedback as comments
on Tickets.
_Avoid_: issue, card

**Delivery checklist**:
The list of concrete actions inside a Ticket needed to fulfil the Commitment.
One Commitment can require several actions across different channels (post a
Slack message AND send an email). The checklist makes "what done looks like"
explicit.
_Avoid_: steps, subtasks

**Source anchor**:
A stable ID of an originating Signal (Slack permalink/message ts, Outlook
message-id, Linear issue id) recorded in the Ticket. Used to recognise on a
later Run that a Signal is already tracked, so the same ask is never
re-ticketed. Multiple anchors can attach to one Ticket when the same Commitment
arrives via several channels.
_Avoid_: dedup key, reference

**Recap**:
The Telegram message sent each run summarising what needs focus. Kept
deliberately low-noise — it highlights Commitments by urgency, it is not a dump
of every Signal.
_Avoid_: digest, summary, report

### Recap shape

- Only **Urgent + High** Tickets are listed by title, one line each:
  `ARJ-NN · [theme] one-line commitment`. No source detail or rationale in the
  Recap — those live in the Ticket.
- **Medium + Low** are counted, not enumerated, with a deep link to the full
  filtered Linear view.
- Footer shows what changed this Run: `N new since last run · N nudged · N open total`.
- **Empty Run** (no new Commitments, nothing Urgent open) sends a one-line
  heartbeat — e.g. "✅ All clear — 4 open, none urgent" — never silence, so a
  broken Run is distinguishable from a genuinely quiet one.

Example:

```
🎯 Focus — Wed 8am

🔴 Urgent (2)
• ARJ-42 · [recruitment] Reply to Bérengère re: Marcel Tessier next steps
• ARJ-45 · [ops] Send Q3 budget approval — finance blocked on you

🟠 High (3)
• ARJ-43 · [product] Review Vincent's intent-extraction plan
• ...

+7 Medium/Low → <linear filtered view link>
3 new since last run · 1 nudged · 12 open total
```

**Run**:
One scheduled execution of the workflow (currently 08:00 and 13:00). Pulls
Signals, reconciles them against existing Tickets, creates new Tickets for new
Commitments, and sends the Recap. Scans a rolling **7-day** window of each
source on every Run (Arjun's explicit choice — a 24h window missed slow-burn
threads). Dedup (via Source anchors) makes the heavy overlap between Runs and
any skipped/retried Run harmless.
_Avoid_: tick (that's Robin's term), job, cycle

## Source scope (v1 — deliberately narrow)

Kept small and accurate on purpose; widened only when Arjun's feedback shows a
real Signal was missed.

- **Slack**: DMs + group DMs + @-mentions in channels Arjun follows (via the
  `<@U0B71TMF690>` member-ID search — `to:me` only catches DMs, not channel
  mentions), **plus threads Arjun himself started/sent into** (`from:<@U0B71TMF690>`)
  that are left pending on the other person. Channel mentions matter because
  important asks land in followed channels, not only in direct messages; and a
  message he sent that no one has actioned is an open loop he needs to chase.
- **Outlook**: mail addressed directly to Arjun (to/cc), within the window,
  **read and unread**. His replies on threads are read too, to verify the loop
  is closed with no pending task — a Ticket auto-closes only once he has
  responded AND nothing is left outstanding (a reply that promises or awaits
  something keeps the Ticket open). Newsletters/bulk excluded.
- **Linear** (ARJ workspace): open issues assigned to Arjun or @-mentioning him.

## Urgency

Urgency lives in Linear's native **Priority** field (Urgent / High / Medium /
Low / None) — sortable, visible in the Linear UI, and read directly by the
Recap. Every Ticket description carries a one-line **"why this priority"**
rationale so Arjun can see what was weighed and correct it precisely via a
comment; the next Run adjusts Priority accordingly.

Urgency judgment — **urgency is a property of the task, not of who is asking.**
The primary driver is always what the task itself demands; the sender is only a
secondary modifier that can raise attention but cannot manufacture urgency from
a task that has none.

**Primary (what the task demands):**
- **Explicit deadlines / time words** — "by EOD", "before the call", "urgent".
- **Blocking others** — someone cannot proceed until Arjun acts.
- **Consequence of inaction** — something breaks, is missed, or harms if ignored.
- **Quick-but-critical** — small effort, large downside if dropped.
- **Repeated nudges** — a Scenario-B follow-up raises urgency.

**Secondary modifier (who is asking — raises attention, never creates urgency):**
- Clients / external parties (non-@mendo.cloud) warrant more attention.
- Mendo managers (Alex, Quentine, Camille, …) warrant more attention.
- A peer can still hand Arjun a genuinely Urgent task; a client can send a Low one.

**Hard filter (not a modifier — disqualifies entirely):**
- Bots/tools that only relay information (Linear, Revo, Notion Slack bots, etc.)
  are **never Commitments**. No task for Arjun to do → no Ticket, regardless of
  sender.

## Relationships

- A **Run** reads many **Signals** from Slack, Outlook, and Linear
- A **Signal** becomes a **Commitment** only if it requires Arjun's personal action
- A **Commitment** maps to exactly one **Ticket** in the ARJ Linear workspace
- A **Run** produces one **Recap** delivered to Telegram
- Arjun's feedback lives as comments on **Tickets**, tuning future urgency judgment

## Reconciliation rules (how a Run treats an already-seen Signal)

A Run matches each Signal's stable ID against **Source anchors** on ARJ Tickets
in **any state** (open, Done, Canceled) — not just open ones:

- **Anchor matches an OPEN Ticket, new activity on the thread** → add a short
  comment to that Ticket ("follow-up received <time>: <gist>") and let it raise
  urgency. Never create a second Ticket.
- **Anchor matches a CLOSED Ticket (Done/Canceled)** → the Signal is already
  handled. Stay silent; do NOT re-create. (This is why anchors must survive on
  closed Tickets.)
- **No anchor matches** → this is a new Commitment candidate; create a Ticket.

Anchor suppression is per-message/thread ID and lasts **forever** — a genuinely
new ask arrives with a new ID (new Ticket), while an old thread resurfacing in
the window stays suppressed.

## Flagged ambiguities

- "task" is deliberately NOT used here — Robin's context already binds "task"
  to a different concept (a bullet in an Obsidian inbox). This workflow uses
  **Commitment** to avoid the collision.

## Example dialogue

> **Arjun:** "I get pinged all day and things slip. I want the important ones tracked."
> **Agent:** "So a Slack ping is a **Signal**. It only becomes a **Ticket** if it's a
> **Commitment** — something *you* must do. A colleague FYI-ing a doc is a Signal,
> not a Commitment — it shows in the **Recap** but never becomes a Ticket."
> **Arjun:** "Right. And if you misjudge urgency?"
> **Agent:** "You comment on the **Ticket**; I use that to tune the next **Run**."
