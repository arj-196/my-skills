---
name: orchestrator
description: "Drain a repo's ready-for-agent GitHub issue queue by spawning parallel implementation subagents in isolated worktrees (2 in flight by default), each delivering a PR or a reasoned refusal. Explicit invocation only — spends real money and opens PRs."
disable-model-invocation: true
---

# Orchestrator

Drain the queue of `ready-for-agent` GitHub issues: for each one, spawn a
subagent in its own git worktree that either delivers a PR or refuses with a
reason. At most N tasks in flight (default 2). Never auto-merge.

**Model.** The orchestrator's reasoning runs on whatever the session model is —
any model is fine, no warning, no switching. Subagents run on **Opus**
regardless.

## Arguments

`/orchestrator [--parallel N] [--limit M] [--dry-run]`

- `--parallel N` — max tasks in flight. Default 2.
- `--limit M` — max tasks this run will take. Default unlimited (drain).
- `--dry-run` — print the qualifying issues in pick order, with any
  serialization decisions from the overlap heuristic, then stop. Spawn
  nothing, write nothing.

## Tracker config

GitHub issues are the only task source. Use the workflows in
`docs/agents/issue-tracker.md` and the label strings in
`docs/agents/triage-labels.md` when those files exist (the
`/setup-matt-pocock-skills` convention). When the repo has no config, fall
back to plain `gh` with the literal labels `ready-for-agent`, `needs-info`,
`ready-for-human`, `agent-in-progress`.

Ensure the `agent-in-progress` label exists before the first claim:
`gh label create agent-in-progress --description "Claimed by an orchestrated agent — hands off" || true`.

## Queue discipline

An issue **qualifies** when all of:

- open, labelled `ready-for-agent`;
- no assignee;
- no open blocker — GitHub native dependencies
  (`issue_dependencies_summary.blocked_by == 0`), falling back to a
  `Blocked by: #n, #n` line in the body where every referenced issue must be
  closed;
- no blocker currently **in flight in this run** (a task this orchestrator is
  working counts as an open blocker for anything it gates).

Pick order: **oldest first** among qualifying issues. Re-evaluate the queue
each time a slot frees — completions can unblock issues mid-run.

**Overlap heuristic.** Before filling both slots, read the candidate issue
bodies (you need them for the briefs anyway). If two candidates *obviously*
target the same module or files, don't run them together: take the older one
and fill the slot with the next non-overlapping candidate. This is one
judgment call from text already in context — no file-level prediction, no
codebase scanning. Ties break toward running anyway; the PR airlock absorbs
real conflicts.

## Per-task lifecycle

### 1. Claim (orchestrator)

Swap labels: remove `ready-for-agent`, add `agent-in-progress`. The
orchestrator is the **sole writer of the assigned issue's state** — subagents
never touch their own issue's labels or comments. This prevents label races
and means a stale `agent-in-progress` after a crash tells you exactly what
died.

### 2. Spawn (orchestrator)

Spawn via the Agent tool: `isolation: "worktree"`, `model: "opus"`, run in
background. Keep at most N running; when one reports, process it (step 4),
then pull the next qualifying issue.

Brief the subagent with the template below, filling in: issue number, full
issue body and all comments (the subagent must not need the tracker to
understand its task), branch name `agent/<issue-number>-<slug>`, and the
repo's default branch.

### 3. Subagent contract (goes in the brief, verbatim modulo placeholders)

> You are implementing GitHub issue #<N> in an isolated git worktree. The
> issue body and comments below are your **entire spec**. Do not ask
> questions — no one will answer. Either you can confidently complete this
> task, or you refuse; there is no middle path and no brainstorming during
> execution.
>
> **Refuse-unclear**: the spec does not determine what to build. Stop before
> writing code; report outcome `refused-unclear` with the specific questions
> the issue fails to answer.
>
> **Refuse-risky**: you understand the task, but a mistake would be hard to
> reverse for an agent working alone. Illustrative examples — not hard
> rules, judge each case: schema/data migrations, auth or security-sensitive
> code, payment flows, production configuration, deleting data. Report
> outcome `refused-risky` with the risk named.
>
> Otherwise:
>
> 1. Create branch `agent/<N>-<slug>` in your worktree.
> 2. Implement using the `/implement` skill (it applies `/tdd` and ends with
>    `/code-review`). Keep the review **diff-scoped**: review the diff since
>    your branch point only — do not expand scope beyond the changes.
> 3. Commit, push the branch, and open a PR referencing the issue
>    (`gh pr create` with "Closes #<N>" in the body).
> 4. If code review surfaces work that outlives this PR: cross-check each
>    item **by meaning** against open issues (list titles, read plausible
>    collisions). Comment on an existing issue rather than duplicating. For
>    genuinely new items, run `/to-tickets`; label the created tickets
>    `needs-triage` (never `ready-for-agent`) and include the line
>    "Discovered during orchestrated implementation of #<N> (code review)".
> 5. Do **not** edit issue #<N> itself — no labels, no comments; the
>    orchestrator owns that.
>
> If tests are red or you cannot reach a confident, complete result: stop and
> report outcome `failed` with a summary of what broke and what state the
> branch is in. If partial committed work is worth salvaging, push the branch
> and say so; otherwise leave it unpushed.
>
> Your final message is a structured report, nothing else:
> `outcome` (done | refused-unclear | refused-risky | failed), `pr_url`,
> `branch`, `questions` (refused-unclear), `risk` (refused-risky),
> `failure_summary` and `branch_pushed` (failed), `followup_tickets`
> (list of issue refs created).

### 4. Resolve (orchestrator, on report)

| Outcome | Labels on #N | Comment on #N |
| --- | --- | --- |
| `done` | remove `agent-in-progress` | PR link, one-line summary, follow-up ticket refs if any |
| `refused-unclear` | `agent-in-progress` → `needs-info` | the subagent's questions, verbatim |
| `refused-risky` | `agent-in-progress` → `ready-for-human` | the named risk, verbatim |
| `failed` | `agent-in-progress` → `needs-info` (or `ready-for-human` if the failure itself revealed risk) | failure summary; branch name if pushed |

Never return a task to `ready-for-agent` — that is a retry loop burning
tokens on a task that already failed once for a reason. A subagent that dies
without reporting (killed, terminal error) is a `failed` with
"agent terminated without report" as the summary.

## End-of-run report

When the queue is drained (or `--limit` reached), print:

1. **Needs attention** — refusals and failures first, with why.
2. One line per task: `#N <title> → <outcome>` with PR/issue links.
3. Follow-up tickets created (issue refs).

No token/cost figures — in-session cost accounting is guesswork; don't
report numbers that lie.
