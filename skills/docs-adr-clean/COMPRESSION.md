# What survives compression, and what does not

Read this before rewriting any ADR. The cut list is safe to apply
mechanically. The keep list is not negotiable — losing any of it turns an ADR
into a summary, and a summary does not stop anyone re-litigating the decision.

## Keep — always, verbatim where possible

**The decision itself**, stated as a rule in one bolded sentence. If a reader
skims one line per section, that line must be the rule.

**Rationale that is not recoverable from the code.** The test: could an agent
reading the implementation work this out? If yes, cut it. If it is a *why* that
lives nowhere else, keep it.

**Every measurement and empirical figure.** These are what make a claim
checkable instead of assertable, and they can never be recovered — the
measurement was taken once, against data that has since moved.

> 7 seconds vs 6740 · 315 of 838 lines · ~248 phantom rows · $80 vs $202 ·
> 20 projects, zero collisions · 300 MB, 0.58 s

They also pre-empt the most expensive failure: an agent "improving" a tuned
constant that was tuned against evidence.

**Rejected alternatives, each with its reason.** Compress to one line —
`**Name** — why rejected.` — but never drop one. An undocumented rejection gets
proposed again, and the second rejection costs a full investigation.

**Accepted costs.** "Committed work in such a repo is unreviewable after the
window closes." These are the things a reader would otherwise report as bugs.
They appear nowhere else in the repo, by definition — a known cost is not in a
tracker and not in the code.

**Retracted rules** — anything shipped and then reversed. See the *Tried and
retracted* section in `SKILL.md`.

**Named constants with their calibration.** Keep `ACT_FLOOR (1s)` and *why* 1s.
Drop the mechanism that reads it.

**Exact glossary terms.** If the repo has a `CONTEXT.md`, its vocabulary is
load-bearing; never paraphrase a defined term into a synonym.

**Marked claims.** If the project distinguishes claims from facts (a `~` mark, a
"notional vs real" split), the ADR's own hedging is part of the content.

## Cut — aggressively

**Narrative build-up.** "Three tensions shaped the design", "The insight that
unblocks this", "It also sits badly beside…". State the tension, skip announcing
that you are about to.

**Restatement.** Merged ADRs restate their shared model once per file. Hoist it
to one table or list at the top and delete the repetitions. This is usually the
single largest win in a merge.

**Prose duplicating a docstring or the manual.** Exact file formats, YAML
frontmatter schemas, install mechanics, function signatures, flag lists that
`-h` already prints. The ADR keeps the *why*; the code keeps the *what*. This
also removes a rot surface — duplicated mechanics go stale when the code moves.

**Implementation mechanics.** `_sign_row` taking `width` as a required argument;
which function threads a parameter through. Keep the design intent, drop the
call graph.

**Scene-setting context that the decision restates.** A three-paragraph problem
statement whose content is fully implied by the one-sentence rule.

**Hedged meta-commentary.** "This is worth stating rather than leaving to be
inferred", "It is worth noting that". Just state it.

**Repeated framing of the same principle.** If a corpus-wide principle (honesty,
determinism, claims-vs-facts) is invoked in five sections, invoke it once and
let the others reference the rule by name.

## Structural moves that cut words at no cost

| Move | Typical saving |
|---|---|
| Enumerable properties → a two-column table | 60–70% on that block |
| `## Considered Options` prose blocks → one-line bullets | 50%+ |
| Shared model hoisted out of N merged files | the largest single win |
| `Status:`/`## Context`/`## Decision` scaffolding where a paragraph suffices | small but free |
| Bounds/rules → a numbered list | 20–30%, and it makes them countable |

Prefer a table whenever the content is *N things with the same shape*. Agents
parse tables reliably and they remove every connective word.

## Calibration

A well-compressed ADR of a single decision runs 300–600 words. A merged
multi-decision ADR runs 1,500–2,500. Past ~4,000 words, check whether it should
have stayed two files.

If a section survives at under 40 words, consider whether it is a decision at
all or just a fact that belongs in the code.

## The stop test

Before finishing a file, ask of the compressed version:

1. Could someone reverse this decision by accident, believing it was arbitrary?
2. Could someone re-propose a rejected alternative?
3. Could someone "fix" a deliberate behaviour, or retune a calibrated constant?
4. Could someone read a retracted rule in the code and treat it as current?

Any yes means something essential was cut. Put it back.
