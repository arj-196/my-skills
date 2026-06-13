---
name: linkedin-post-builder
description: Turn a rough post idea into a finished, high-reach LinkedIn post written in the user's own voice. Use this skill whenever the user says they want to write, draft, build, or improve a LinkedIn post — including phrasings like "I have an idea for a post", "help me post this on LinkedIn", "turn this into a LinkedIn post", "make this catchier for LinkedIn", or when they paste a raw thought/observation and mention LinkedIn. The skill interviews the user to fill gaps in their idea, then produces a finished post plus hook variations and a visual/format suggestion. Trigger it even when the user just dumps a half-formed idea and says "LinkedIn" — that's the core use case.
---

# LinkedIn Post Builder

Take a seed idea and shape it into a finished LinkedIn post that sounds like the user, lands emotionally, and is built to earn reach and comments. The user supplies the idea; this skill supplies the questions, the structure, and the writing.

## The voice (non-negotiable)

The post must read as a mix of **humour, humbleness, creativity, and genius** — playful but not goofy, sharp but never arrogant, insightful without lecturing. The user is funny and self-aware, drops a genuinely smart insight, and wears it lightly. Avoid: corporate LinkedIn-speak, "I'm humbled to announce", hustle-bro motivation, fake vulnerability, emoji-bullet walls, and "Agree?" engagement-bait closers.

### Calibrating the voice each session
**Always read `references/voice.md` first** — it holds the user's confirmed voice profile plus two annotated sample posts. It is the source of truth for tone, rhythm, humour, emoji use, and how they tag people. Match it closely; imitate the *rhythm and structure* of the samples, not their topics.

If over time the user's style seems to evolve, offer to update `references/voice.md` with a fresh sample.

## Workflow

### Step 1 — Capture the seed
Take whatever the user gave you (a sentence, a story, an opinion, a screenshot, a win). Restate it back in one line to confirm you understood the core idea, then move to interviewing. Don't draft yet.

### Step 2 — Interview thoroughly
Ask as many questions as needed to fill the gaps — but ask in small batches (2-4 at a time), conversationally, so it doesn't feel like a form. Use the checklist in `references/interview.md` to decide what's missing. Prioritise the questions that change the post most:
- **The point**: what does the reader walk away thinking or feeling? What's the one idea?
- **The angle/tension**: what's surprising, contrarian, or honest here? Posts travel on tension, not information.
- **The story**: is there a concrete moment, scene, or specific detail? Specifics > abstractions.
- **The audience**: who is this for, and what do they already believe that this challenges or confirms?
- **The stakes / why now**: why should anyone care today?
- **The ask**: what do you want — comments, DMs, reshares, just visibility?
Stop interviewing once you have enough to write something genuinely good. Don't interrogate for its own sake.

### Step 3 — Draft
Read `references/structure.md` for hook patterns, post anatomy, and formatting rules, then write the post. Default to a strong one-line hook, generous white space, short lines, one clear idea, and an ending that invites a response without begging for it. Keep it in the user's voice (Step "The voice" above).

### Step 4 — Deliver the package
Hand back, in this order:
1. **The post** — finished, ready to paste, properly spaced for LinkedIn (blank lines between short paragraphs).
2. **3 alternative hooks** — different angles on the opening line, since the first line decides reach.
3. **Visual / format suggestion** — one concrete idea: a single image, a carousel outline, a "text-only for intimacy" call, a document post, etc., with a one-line why.

Then ask if they want to tweak tone, length, or hook. Iterate until they're happy.

### Step 5 — Save versions to file
When the user is happy with a draft (or asks to save), persist it to a markdown file in their LinkedIn folder, one file per post topic. Naming: `LinkedIn posts - <Topic>.md`.

- Each finished draft is saved as a version: `# V1`, `# V2`, etc.
- Version headers stay short — a header plus a 2-4 word change note: `# V2 — more concise`, `# V3 — punchier hook`.
- Newest version goes FIRST. Order top-to-bottom: latest version → older versions → the original source idea last.
- Separate each section with a `---` horizontal rule.
- Never overwrite or edit an existing version when asked for a new one — append a new version block. Only touch an existing version if the user explicitly says to edit/revert it.
- Keep the raw source idea at the bottom under `# Idea` so the original thinking is never lost.

## Notes
- Length: most high-reach posts run 120–250 words. Go shorter for a punchy take, longer only if there's a real story.
- Never invent facts, metrics, or quotes about the user. If a number would strengthen the post, ask for it.
- One idea per post. If the user gave you three, suggest splitting into a series.
- File structure for saved posts (newest first):

  # V{n} — short change note
  <post text>

  ---

  # V{n-1} — short change note
  <post text>

  ---

  # Idea
  <original source notes>
