# Plan Template (`01-plan.md`)

The plan turns the problem statement into a set of smaller, individually-solvable challenges — sequenced where they must be, parallelised where they can be — and names who is needed to solve each. Thoroughness and method are the goal; parallelism is a bonus.

Every challenge must have an **exit criterion**: the concrete signal that tells us it's solved and we can move on. A challenge without one is a wish, not a plan.

---

```markdown
# <Project Name> — Plan

> Status: …  ·  Last updated: <date>  ·  Owner: <name>
> Based on: 00-problem-statement.md

## 1. Approach overview
2–4 sentences: the overall strategy, and why this sequencing. What's the critical path?

## 2. Challenge breakdown
One block per challenge. Number them (C1, C2, …) so the dependency map can reference them.

### C1 — <name>
- **Description & hypothesis:** what this challenge is, and the belief we're testing.
- **Approach / spike:** how we'd attack it; the smallest experiment that de-risks it.
- **Profiles needed:** Engineering | AI Specialist | Product | Client (one or more, with why).
- **Effort & uncertainty:** rough size + how unknown it is (low/med/high).
- **Exit / success criterion:** the concrete signal that it's done.

### C2 — <name>
…

## 3. Dependency map (sequence vs parallel)
Which challenges block which; what can run in parallel. A short list or ASCII graph:

    C1 ──▶ C2 ──▶ C4
       └──▶ C3 (parallel with C2)

## 4. Profiles & roles needed (overall)
Aggregate staffing across all challenges. Engineering, AI Specialist, Product, Client —
roughly how much of each, and at which points they're load-bearing.

## 5. Milestones / phases
The few checkpoints that mark real progress, with what's true at each.

## 6. Validation checkpoints
Where Product and/or Client teams must engage — to clarify questions, confirm hypotheses,
or review results against the market need. Tie each to a specific milestone/challenge,
not "sometime later".

## 7. Risks & mitigations
The things that could derail or harm us, each with a mitigation or a trigger to revisit.
Pull anything unresolved from the blind-spots checklist up into here.
```
