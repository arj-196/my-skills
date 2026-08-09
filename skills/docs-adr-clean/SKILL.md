---
name: docs-adr-clean
description: Aggressively consolidate and compress a repo's ADRs (docs/adr/) without losing decision-critical information. Merges ADRs that have become one design, cuts prose an agent doesn't need, renumbers contiguously, and rewrites every citation in code and docs. Use when the user says there are too many ADRs, that the ADRs are verbose or bloated, that they want them merged/cleaned/consolidated/compressed, or when ADR numbers have gaps or dangling references.
---

# Clean and compress ADRs

Reduce an ADR corpus hard — typically 60–70% fewer files and 30–40% fewer words
— while keeping every fact a future agent needs to avoid re-litigating a settled
decision or "fixing" something deliberate.

**The audience is agents, not humans.** Optimise for information per token. That
does not license unreadable output: an agent reads prose, and compressed-to-cryptic
costs more than it saves. Cut *narrative*, keep *content*.

## The one non-negotiable

An ADR exists to stop someone redoing a decision or undoing it by accident.
Everything that serves that survives compression; everything else is fair game.
Load `COMPRESSION.md` before rewriting any file — it is the keep/cut taxonomy,
and guessing at it is how essential information gets lost.

## Phase 0 — Inventory before touching anything

```bash
wc -lw docs/adr/*.md | sort -n
grep -rhozE --exclude-dir=__pycache__ "ADR[[:space:]#]*[0-9]{4}" src/ lib/ *.md docs/ 2>/dev/null \
  | grep -aoE "[0-9]{4}" | sort | uniq -c | sort -rn
```

The two-stage shape is deliberate: the first grep matches citations even when
wrapped across a line break, the second extracts bare numbers from its output
— which is NUL-separated under GNU grep (`-z` = null-data) but newline-separated
under ugrep (where multiline matching is native and `-z` means decompression).
Post-processing the match text with `tr`/`sed` breaks on one or the other;
extracting numbers works on both.

Then establish four facts:

1. **How many citations exist, and where.** This sets the cost of renumbering.
   Include `README.md`, `CONTEXT.md`, `TODO.md`, `CLAUDE.md`, `docs/**` — not
   just source. Docs citing ADRs is the thing most often missed.
2. **Dangling references** — a cited number with no file. Common, and worth
   reporting; the decision was usually made and never written down, with its
   content sitting in a code comment.
3. **Cross-references between ADRs** — `grep -n "ADR [0-9]" docs/adr/*.md`.
   These are the merge map (Phase 2).
4. **Whether supersession is already happening in place** — one ADR editing or
   voiding another's rule. If so, the corpus is already being maintained as a
   reference, which is what makes merging legal.

> **Never conclude "no references here" from a `head`-truncated grep.** Count
> first (`| wc -l`), then read. A truncated grep once produced a confident
> wrong claim that the docs cited no ADRs, when they cited fourteen including
> ten file links the merge was about to break.

> **A citation can wrap.** Comments break at ~80 columns, so `ADR` lands at the
> end of one line and `0004` at the start of the next — sometimes behind a `#`
> comment prefix. A line-anchored grep is blind to the wrapped form, which is
> exactly how four stale citations once survived a full renumbering pass. Every
> grep over citations must be the `-z` form above. `--exclude-dir=__pycache__`
> is load-bearing too: `-I` is inert under `-z` (NUL-as-separator disables
> binary detection), so stale compiled docstrings resurrect old numbers.

## Phase 1 — Confirm the reading

Merging is only legal if ADRs are a **rationale reference** (current truth,
rewritten as decisions change) rather than an **immutable decision log**
(append-only, dated, never edited). Ask the user, unless they have already said.

Under the log reading, stop: the only cleanup available is an index, a Status
header, and writing the dangling ones. Say so rather than merging anyway.

Evidence the corpus is already a reference: in-place amendments, one ADR voiding
another's bound, `Status:` fields nobody updates.

## Phase 2 — Cluster by entanglement, not by topic

Two ADRs merge when **reading one alone misinforms you.** Concrete tests, in
descending strength:

| Test | Signal |
|---|---|
| A voids or amends a bound in B | strongest — B is already lying to a cold reader |
| A and B are implemented in the same function/module | one code seam, one doc |
| B's rationale is stated by reference to A ("mirrors X", "same reason as Y") | the shared half is written twice |
| They shipped in one commit | weak on its own — check the others |

**Topic similarity alone is not a reason to merge.** Two decisions about "the
CLI" that never reference each other and live in different files stay separate.

Put the clustering to the user with concrete depth options and a recommendation.
Name what each depth costs. The real risks of over-merging:

- **citation precision** — a bare `(ADR 0004)` in a module about that subsystem
  says nothing. Mitigated by section anchors (Phase 4), not by avoiding merges.
- **the dumping ground** — one file becomes the default home for every future
  decision in that area. Not mitigable; state it and let the user choose.
- **mixing altitudes** — a dependency choice buried on page 3 among hex values.

## Phase 3 — Merge and compress

Read `COMPRESSION.md` now.

Per merged file:

1. One `##` section per absorbed decision. **Section headings are the citation
   anchors** — keep them short and noun-shaped (`## The removed-row field`, not
   `## Removed code sits on a faint red field`), because every anchor is repeated
   in code comments that wrap at ~80 columns.
2. State each shared property **once**. If three ADRs all said "stored durably,
   pruned with the log, marked as a claim", that becomes one table at the top.
3. **`## Tried and retracted`** — rules that shipped and were reversed. This is
   the highest-value section and the easiest to lose in a merge. The code still
   carries a retracted rule's shape; without the record a future agent reads
   current behaviour as a bug and "fixes" it.
4. **`## Alternatives considered`** — options never shipped, each one line:
   `**Name** — why rejected.`
5. Drop `Status: accepted` (under the reference reading every file is current by
   definition, so the field asserts nothing). Keep one `Date:` meaning last
   substantive revision. Date individual sections only where the date is
   load-bearing (a "this turned out wrong once it met real data" note).

When an ADR contains an amendment contradicting its own earlier text, **the
corrected version becomes the text** and the wrong one moves to *Tried and
retracted*. Never carry both forward — that is the exact defect being fixed.

## Phase 4 — Renumber and rewrite citations

Renumber contiguously `0001..N` only if the user asks. It is safe **only**
because renumbering and citation rewriting happen in one change.

Preserve relative order unless the user wants a re-ordering; closing the gaps is
what they asked for.

### Rewrite rules

- **One regex pass. Never rescan replacements.** Build the whole substitution in
  a single `re.sub` with a function, including the markdown-link form via
  alternation. Two sequential passes will re-match the number you just inserted
  and produce `ADR 0009 § Project Handles § short option letters`.
- **Match the wrapped form.** The rewrite regex must tolerate a citation split
  across a line break — `ADR[\s#]*(\d{4})`, run over whole-file text, not line
  by line — and the rewrite should *unwrap* it: put `ADR NNNN` on one line
  while reflowing, so the corpus converges on the form any grep can see.
- **Anchor every citation into a multi-section ADR**:
  `(ADR 0004 § the removed-row field)`. A heading *prefix* is fine when the full
  heading is unwieldy, as long as it is unambiguous in that ADR.
- **Terminate anchors.** An anchor running into prose (`ADR 0005 § Project
  Handles is untouched`) cannot be validated and cannot be grepped. Put it in
  parentheses or end it with a comma.
- **Fix markdown links too** — `[ADR 0018](docs/adr/0018-old-name.md)` needs
  both label and path rewritten.

### Reflowing — where this goes wrong

Adding `§ the removed-row field` to a comment overflows the line. Reflowing is
necessary and is the single most dangerous step in this skill.

**Do not run a general-purpose reflow script over source files.** A blunt
paragraph-rewrapper will:

- merge a docstring's closing `"""` into the following statement;
- merge two adjacent statements into one line;
- rewrap a string literal, breaking the quote;
- flatten a bullet list's continuation indent.

Instead:

1. Reflow only **pure `#` comment runs** and **interior docstring prose** (lines
   with identical indent, no `"""`, no bullet marker, no `=`, not code).
2. Everything else — module-docstring first lines, one-line docstrings, bullets,
   inline comments on code, string literals — **by hand**.
3. For an inline comment on a code line, move the comment *above* the code
   rather than wrapping it.
4. **Verify with `ast.parse` per file after every batch.** `python -m compileall
   -q` can report success misleadingly; do not trust it.

If a script does damage: `git checkout -- <path>` and redo by hand. Use
**absolute paths** in every bash call — the working directory persists between
calls, and a `git checkout -- src/` issued from inside `src/` silently matches
nothing while the `&&` chain reports success.

## Phase 5 — Verify mechanically

```bash
python3 ~/.agents/skills/docs-adr-clean/verify.py .
```

It checks, and all must pass:

- every source file still parses;
- **the set of ADR numbers referenced anywhere == the set of ADR files present**
  (this is the check that catches a missed rename — including citations wrapped
  across a line break, which any hand grep must also tolerate);
- every `§` anchor resolves to a real `##` heading in the ADR it names;
- every markdown link into `docs/adr/` resolves;
- numbering is contiguous with no gaps.

Then smoke-test the tool itself — help output, and each primary view — because
comment reflowing touches real files and a broken docstring is a broken import.

## Phase 6 — Record the rules so it does not decay

- `docs/adr/README.md`: the index table, the citation convention (number **and**
  section), the numbering rule with its verification command, and the
  keep-retracted-rules rule. The recorded command must be the break-tolerant
  form from Phase 0 — pinning a line-anchored grep here is how wrapped
  citations survive the *next* pass.
- The repo's agent instructions (`CLAUDE.md` or equivalent): the same three
  rules in short form, since that is what an agent reads first.
- If you renumbered, state plainly in the index that commit messages naming old
  ADR numbers are now wrong and cannot be fixed. That is the accepted cost.

## Report honestly

Give before/after **words**, not just file counts — word count is the thing the
user asked to reduce. Report what you cut categorically ("narrative build-up,
restatement, prose duplicating docstrings") and what you kept verbatim
(measurements, rejected alternatives, accepted costs). Flag the largest
remaining file and any rule you inverted in `CLAUDE.md`.
