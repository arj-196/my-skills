---
name: handoff
description: Write a handoff document for a fresh session to pick up — the current state, what's next, and what's already been ruled out.
argument-hint: "What should the next session focus on?"
disable-model-invocation: true
---

Write a handoff document so a fresh Claude session can pick up this work. Unlike `/claude-handoff`, this launches nothing — it leaves a file on disk and prints the command the user runs when they are ready.

If the conversation has nothing substantive to hand off, say so and stop. Do not manufacture a doc.

If the user passed arguments, treat them as what the next session should focus on and tailor the doc accordingly.

## Where it goes

`HANDOFF-<slug>.md` at the repo root — `git rev-parse --show-toplevel`, or the current directory when there is no repo.

- `<slug>` is kebab-case, four words max: from the arguments when given, otherwise inferred from the work.
- Never overwrite an existing file. If the name is taken, append `-2`, `-3`, and so on.
- If another `HANDOFF-*.md` already exists at the root, add a `Previous handoff: <path>` line under the metadata line.

The file is meant to be committed, but **do not run any git command that writes**. Print `git add HANDOFF-<slug>.md` as a suggestion and let the user commit it.

## Writing rules

- Address the next session in second person.
- Omit any section with nothing true to say. Do not pad.
- Reference specs, ADRs, issues, plans, commits, and diffs by path or URL. Never restate their content.
- Redact secrets, keys, and PII — this file gets committed.
- Keep it to a page. Longer means you are duplicating something that should be a reference.
- **Dead ends** is the highest-value section. A fresh session cannot reconstruct what was tried and will burn hours re-deriving it.
- **Decisions already made** stops the next session relitigating settled choices. Record the decision and its reason, not the debate.

## Template

```markdown
# Handoff: <Task name>

<YYYY-MM-DD> · branch `<branch>`

## Task

<One or two sentences.> **Done when:** <observable condition>

## Context

<Why this matters and anything you need to know that the steps below do not cover.>

## Next steps

1. <Concrete, ordered.>

## Key files

- `path/to/file.ts` — <why it matters>

## Decisions already made

- <Decision> — <reason.> Do not reopen this.

## Dead ends

- <What was tried> — <why it failed.>

## Suggested skills

- `/skill-name` — <when to reach for it>

## Open questions for the human

- <Anything you must not guess at.>

---

Delete this file once the work is finished. If you hand off again before then, leave it in place — the new handoff points back to it.
```

## Then print

Three lines of gist — the task, how many next steps, and whether there are open questions awaiting the human — followed by the file path and the launch line:

```
claude -n "<Task name>" "Read HANDOFF-<slug>.md and continue the work described there."
```

Say that it should be run from the repo root, and suggest `git add HANDOFF-<slug>.md`.
