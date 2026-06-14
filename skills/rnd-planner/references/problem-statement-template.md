# Problem Statement Template (`00-problem-statement.md`)

This is the shareable artifact. Anyone — engineer, AI specialist, product, client team — should read it and be up to speed on *what* we're addressing, *how* we mean to, and *what the challenges are*. Write in plain language; keep business framing and technical framing in separate sections so neither hides behind the other.

Fill sections from real signal: business/market framing from the user, the "What Mendo has today" / "Gaps" sections from actual code and docs (via Explore — see [mendo-map.md](mendo-map.md)). Mark anything unverified as `(unconfirmed)`.

---

```markdown
# <Project Name> — Problem Statement

> Status: Idea | Documenting | Planning | In Progress | Validated | Parked | Done
> Last updated: <date>  ·  Owner: <name>

## 1. One-liner & business outcome
One sentence on what this is. Then the business outcome we're chasing — in business terms
(revenue, retention, time saved, deals won), not technical ones.

## 2. Market need — who hurts, and why now
Who has this problem, how painful it is today, and why this is worth doing *now*.
What is the business trying to create here?

## 3. Problem statement (plain, shareable)
The problem in plain language a non-technical collaborator can fully grasp.
No jargon. No solution baked in.

## 4. Success criteria (measurable)
What does success look like, concretely? Prefer measurable targets
(metric, threshold, how we'd measure it). If we can't measure it yet, say so and note how we will.

## 5. Business ↔ Technical glossary
Two columns of language that map to each other. Keeps the two jargons honest and separate.

| Business term | What it means technically | Notes / aliases to avoid |
|---|---|---|
| e.g. "instant answers" | RAG over the lab corpus | not "search", not "the AI" |

## 6. What Mendo has today (from code)
Grounded in the actual repo (cite paths). What existing capability is relevant?
What already does part of this? Where does the relevant AI/data live today?

## 7. Gaps / new capabilities to crack
What does NOT exist yet and must be built or researched. The genuinely hard, novel parts.

## 8. Integration constraints (must fit Mendo)
How this would have to slot into Mendo to be real: which app/product/channel
(Excel / ChatGPT / Copilot / Desktop), which stack/seam, data and contract constraints.
If it can't integrate, that's a finding — surface it.

## 9. Hypotheses to validate
The beliefs this rests on, stated so they can be proven or killed. Each: the hypothesis,
how we'd test it cheaply, and who confirms it (Product / Client / data).

## 10. Open questions & risks
What's still unknown, and what could harm us later (cost, latency, data rights, scope,
team dependencies, maintenance). Pulled forward from the blind-spots checklist.
```
