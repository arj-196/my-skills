---
name: workload-balancer
description: Compute each Mendo dev's current Linear workload (broken down by status, with summed estimates) and recommend how to distribute unassigned Urgent/High tickets. Trigger whenever the user says "dev workload", "who is available", "workload", "who can pick this up", "distribute the tickets", "unassigned tickets to assign", "balance the team", "who has bandwidth", "suggest assignees", "give me the load", "distribution", or any variation asking for a per-developer load view and/or assignment recommendations for unassigned high-priority Linear tickets. This skill reads Linear only — it never writes assignments unless the user explicitly asks afterwards.
---

# Workload Balancer

Produce a per-developer workload snapshot for Mendo's Linear workspace and recommend who should pick up the unassigned **Urgent** and **High** tickets, balancing by current load and domain fit.

## Scope

- **Mendo's Linear workspace only.** Knows Mendo's squads and ticket conventions.
- **Read-only by default.** This skill computes and recommends. It does **not** call `save_issue` to assign tickets unless the user explicitly says "apply" / "assign" / "go" *after* seeing the report.
- Output is **displayed in chat** as a Markdown report. Do **not** auto-post to Slack. Only draft a Slack message if the user explicitly asks ("make me a Slack message", "draft for the team", etc.).

## Definitions (locked conventions)

These were chosen by Alexandre — do not silently change them:

- **Active load** = tickets whose status type is `started` **or** `unstarted` (i.e. "In Progress / In Dev Review / In Product Review / Waiting for … / Todo / Assigned"). **Exclude `backlog`, `triage`, `completed`, `canceled`, `duplicate`.**
  - In Linear MCP terms: fetch `state=started` and `state=unstarted`. Do **not** include `state=backlog`.
- **Estimate default** = any ticket with **no `estimate` field gets counted as `2` points.** Always report how many tickets were defaulted so the number is honest.
- **Unassigned** = `assignee` is null.

## Workflow

### 1. Pull the data

Make these `Linear:list_issues` calls (high `limit`, e.g. 200):

1. **Active assigned load** — two calls, merged:
   - `list_issues(state="started", limit=200)`
   - `list_issues(state="unstarted", limit=200)`
   - From the merged set, keep only tickets **with** an assignee.
2. **Unassigned priority tickets** — two calls, merged:
   - `list_issues(assignee="null", priority=1, limit=100)`
   - `list_issues(assignee="null", priority=2, limit=100)`
   - From the merged set, **drop** anything whose status type is `completed`, `canceled`, or `duplicate` (these come back even when closed). Keep `triage`, `backlog`, `started`, `unstarted` — an unassigned Urgent in Backlog still needs an owner.

Deduplicate by ticket `id` across calls (a ticket can appear in more than one response).

### 2. Compute per-dev workload

Group the active assigned tickets by `assignee` (use the display name; some assignees show as an email like `hella@mendo.cloud` — keep them as-is, they're real people).

For each dev, compute:

- **Ticket count** total.
- **Breakdown by status** — group by the human `status` string (e.g. "In Progress Dev", "In Dev Review", "Waiting for Info", "Todo", "Blocked", "Paused"). Keep the real status labels; they're informative (a dev with 8 tickets all in "Waiting for Info" is less loaded than one with 8 "In Progress Dev").
- **Summed estimate** — sum of `estimate.value`, treating missing estimates as `2`. Track the count of defaulted tickets.
- **Primary squad** — the team that owns most of their tickets.

### 3. Render the workload table

A Markdown table, sorted by summed estimate descending:

| Dev | Squad | # tickets | Est. (pts) | Active breakdown |
|---|---|---|---|---|

In the breakdown column, give the status split compactly, e.g. `4 In Progress · 2 Dev Review · 1 Blocked`. Distinguish clearly between **"actively coding"** statuses (In Progress Dev, In Dev Review) and **"parked"** statuses (Waiting for Info, Blocked, Paused) — a dev parked on reviews has more bandwidth than the raw count suggests. Add a one-line note under the table flagging the most- and least-loaded devs, and the total number of estimate-defaulted tickets.

### 4. Recommend assignments

For each unassigned Urgent/High ticket, suggest **one** assignee. Decision logic, in order:

1. **Domain fit first.** Match the ticket's surface to the dev who already owns related work (same squad, same connector, same feature area). Look at the assignee's existing ticket titles to infer their current focus.
2. **Then balance by load.** Among domain-appropriate candidates, prefer the one with the **lower summed estimate**. Avoid piling onto the top-2 most-loaded devs unless the context fit is overwhelming.
3. **Respect exclusions** (see below) — never recommend someone who's off or out of role.
4. If no good owner exists (everyone fit is overloaded, or it needs a skill nobody has), mark the ticket **"needs arbitration"** rather than forcing a bad assignment.

Present recommendations grouped by priority (🔴 Urgent, then 🟠 High), each line: `TICKET-ID — short title → **Dev** (one-clause rationale)`.

### 5. Caveats footer

Always end with a short ⚠️ block stating the limits of the analysis:
- Load is measured by open-ticket volume + estimates only — **not** real seniority, velocity, or current sprint commitment.
- The skill doesn't know who's **on leave / off / out of role** unless told.
- Estimates are partly defaulted (give the count).

### 6. Offer to apply (do not auto-apply)

End with a single offered next step: "Do you want me to apply these assignments in Linear? I'll list the exact batch and you confirm before any write." Only if the user says yes, call `save_issue` per ticket with `assignee` set, after listing the exact batch.

## Exclusions & roster notes

Before recommending, **ask the user if anyone is off or out of scope** — unless they already said so in the conversation. Known roster facts to apply when relevant (the user may correct these):

- **Yasser** is **QA e2e**, not a feature dev — do not recommend him for dev tickets (DevOps/Datadog/test tickets are fine).
- Roster changes (leave, role) are volatile. If the user mentions "X est off" / "X is QA" / "X a quitté", honor it for the rest of the session and weight accordingly.

If exclusions are unknown and the result could be materially wrong, ask once via `ask_user_input_v0` (e.g. "Is anyone off / out of scope this week?") before producing recommendations. Don't ask if the user already told you.

## Mendo squads (for domain-fit reasoning)

| Team | Owns |
|---|---|
| `In-app Adoption` | Web app + content + back office. Labels: APP, BO, API, Infra. |
| `Out-app Adoption` | Connectors (Browser, Desktop, Web+Desktop), M365. Labels: BrowserConnector, DesktopConnector, etc. |
| `ClientHub` | Client Hub, AI Impact Center, Credit Manager, Usage Dashboard. Label: ClientHub. |
| `Support` | Inbound customer issues (L1/L2/L3). |
| `Consulting` | Client-advisory deliverables. |

Use the assignee's **existing ticket titles** as the strongest signal of their current focus — it beats the squad label when the two disagree.

## Edge cases

- **Assignee shown as email** (e.g. `martin@mendo.cloud`) vs display name (e.g. `Tom`) — treat both as people; don't merge or drop them.
- **Sub-issues / parents** — count each ticket once; don't double-count a parent and its children.
- **A ticket in status "Assigned" but with null assignee** — this is a real Mendo quirk; surface it in the unassigned list and flag it ("status Assigned but no assignee — needs fixing").
- **No unassigned priority tickets** — still produce the workload table; just note there's nothing to distribute.
- **`hasNextPage: true`** in any response — paginate with the `cursor` until exhausted before computing, or note the table is partial if you stop early.

## Example output shape

```
## Load per dev (active = started + todo)

| Dev | Squad | # | Est. | Breakdown |
|-----|-------|---|------|-----------|
| AdeleCloud | Out-app | 14 | 31 | 9 In Progress · 3 Dev Review · 2 Waiting |
| Tom | In-app | 10 | 26 | ... |
...
> Most loaded: AdeleCloud, Tom. Most bandwidth: Eray, martin. 18 tickets without estimate (counted as 2 pts).

## Assignment recommendations

🔴 Urgent
• SUP-597 — UI delay staging → **needs arbitration** (needs an available backend)
• OUA-293 — M365 Excel validation → **Raymonceau** (connectors)

🟠 High
• OUA-295 — John Doe CNP → **Raymonceau** (BrowserConnector)
...

⚠️ Load measured by volume + estimates only (not seniority or actual sprint). Roster off/out-of-role not known unless mentioned. Estimates partly defaulted (18).
```
