---
name: arj-comms
description: >-
  Write Slack messages and emails in Arj's voice — internal team announcements, updates, polls, and external client communications (English and French). Trigger this skill whenever Arj wants to draft, rewrite, or polish any message for his team or for a client: "write a Slack message", "message for my team", "mail for client", "rewrite this", "make this shorter/funnier/more formal", "reply to the client", "annonce à l'équipe", "mail client en français", or any variation where the deliverable is a communication that needs to sound like him. Also trigger when he pastes a draft and asks to fix the tone. Handles the internal-vs-client register switch automatically.
---

# Arj Comms

Arj is Engineering Manager at Mendo (GenAI org-transformation startup). He writes a lot of Slack messages and client emails, switching constantly between two registers. This skill captures his voice so drafts come out sounding like him — not like generic corporate copy.

He is bilingual (French / English) and switches based on audience. Match the language he asks for; if he pastes French, reply French; if English, English.

## Step 0 — Identify the register

Every message is one of two registers. Get this right first, because everything else flows from it.

| | **Internal (team)** | **External (client)** |
|---|---|---|
| Emojis | Yes, but **selectively** — see the emoji budget below | **Never.** Zero emojis, ever. |
| Tone | Warm, funny, human, a little irreverent | Professional, warm, approachable — not stiff, not academic |
| Formatting | Two modes — see Step 0.5. Announcements get the full kit; DMs stay plain | Short paragraphs; bullets only for a list of distinct points |
| Humor | Dry parenthetical asides, gentle ribbing | Light warmth only; no jokes |

If it's ambiguous, ask which one. When he says "for my team" → internal. "For client" / "mail client" → external.

## Step 0.5 — Pick the formatting weight (internal only)

Register tells you the *voice*. This tells you how much *structure* to put around it, and it is a separate decision. Arj called this out in Aug 2026 after a DM came back looking like a company memo: *"Don't need so much formatting for a casual slack message. Keep fully formatted for official announcements and simpler formatting for direct messages."*

| | **Announcement** (channel, team-wide) | **Direct message** (one colleague) |
|---|---|---|
| `###` section headers | Yes, when there are two+ lists | **Never** |
| Blockquote (`>`) premise | Yes | **Never** |
| Bullets | Yes, with **bold lead** on each | Only if there are genuinely 3+ items — and **no bold leads**, just the plain thought |
| Bold | On key terms and bullet leads | Sparingly — the link label, maybe one term. Often zero |
| Emoji | 8–11 at announcement length (see the emoji budget) | **1–2 total.** Usually just the 🙏 / 👋 carrying the tone |
| Opening | 📢 header + hook | Just say hi and get to the ask: "Hey [Name], need a favour…" |

**The reasoning, so you can extrapolate:** the heavy structure is *what signals* "this is an announcement, read it carefully." Spending it on a casual DM burns that signal and makes a simple ask read like a memo. On a DM, write it the way he'd say it out loud — the paragraph is the default unit, not the bullet.

**The one exception:** links stay formatted as a labelled hyperlink in both modes — `**[Label](url)**`. He explicitly asked for this back after a plain-DM rewrite dropped it to a bare URL. Never paste a naked URL inline. (When *sending* through the Slack API rather than handing him text to paste, convert to Slack's `<url|Label>` syntax.)

### DM template (shape)

```
Hey [Name], [the ask in one line, with the human beat built in] 🙏

[Context paragraph: who/what, and why it matters. Plain prose.]

[Link, if there is one:] **[Label](url)**

[If there are several distinct points — plain bullets, no bold leads:]
- [thought]
- [thought]
- [thought]

[Any nuance or caveat as its own short paragraph, not a fourth bullet.]

Thanks!
```

## Core voice (applies to both registers)

- **Short, declarative sentences.** No throat-clearing. Get to the point.
- **Lead with the human warmth, then the substance.** "Hope you're doing well" / "listen up 👇" — a quick human beat before the content.
- **Plain language over jargon.** "no more good ideas lost to the void" beats "improved action-item persistence."
- **Bullets for anything multi-point.** Arj organizes his thoughts as bullets and expects them back. If there's more than one idea, bullet them. (In a DM, raise the bar to 3+ items — two thoughts are just a sentence with a comma.)
- **Bold the key phrase in each bullet**, then explain. e.g. "- **Confirming the root cause.** We analyzed the logs…" **Announcements only** — bold leads on DM bullets are exactly the over-formatting he flagged.
- **Warm, open-ended close.** "Feedback welcome as always." / "Looking forward to it." / "Thanks for bearing with me." Never a cold sign-off.
- **Never academic, never pompous.** If a line sounds like a consultant wrote it, rewrite it. He flags phrases like "Nous nous réjouissons d'échanger" as "too formal, not my style."

## Internal (team) register

The personality dial goes up. This is where Arj is fun.

- **Emoji as punctuation, never as bullet points.** See the emoji budget below — this is the rule he cares most about.
- **Dry parenthetical humor.** The signature move. Examples he's kept:
  - "(yes, there's a difference 😄)"
  - "(looking especially at you, expensive-Mac owners 😅)"
  - "no more good ideas lost to the void"
  - "nobody has to copy-paste their way through it"
- **Gentle, affectionate ribbing** — never punching down. The Tom-and-his-3-beers running joke; teasing Mac owners. Light, inclusive, self-aware.
- **Firm when needed, but never harsh.** He'll say "Not optional-ish — it's important everyone joins" but softens the landing. When asked to be "firm," keep the warmth; firmness = clarity, not sternness.
- **Tag colleagues** with @ when they're involved (@Geoffrey, @Jad).
- **Bold key terms**: **Dev All Hands**, **Linear**, **DAKI**.
- **Sign-offs are casual**: "More to come. Stay tuned." / "Thanks for bearing with me on this. 🙏"

### The emoji budget — announcements (Aug 2026 — he pushed back hard on this)

Everything in this section is calibrated for an **announcement**. A DM gets 1–2 emoji, full stop; don't apply the 8–11 landing zone there.

He got to a ~20-line announcement carrying 14 emojis and called it: *"there are too many and therefore they lose their importance."* But cutting to 3 was also wrong — *"loses the colorful aspect."* The landing zone is **8–11 for a long announcement**, and placement matters more than count.

- **Emoji is punctuation, not a bullet character.** If every bullet has one, none of them mean anything — they've become bullet points with extra steps, and they're redundant with the bold lead that's already there.
- **Keep it only where it means something the words don't.** ✅ = this rule is settled · 🚧 = wet paint, still moving · 🚦 = a gate you don't drive through · 🔐 = security · ⚖️ = legal · 🎯 = the point. Drop anything purely decorative (📚 next to "one generic hub" adds zero).
- **Leave at least two bullets bare in every list.** The contrast is the whole mechanism — a 🚧 lands *because* the bullets above it don't have one.
- **Load-bearing emoji that always stay**: 📢 on the header, 👇 after it, the 😄/😅 inside a parenthetical joke, and the 🙌/🙏 on the close. These carry tone, not structure. Cutting them makes him read colder than he is.
- **A marked bullet at the end of a list makes it the punchline.** Four clean bullets building to 🚦 on the Migration Gate — that's the shape.

### Colour without emoji (reach for these first when he wants more "fun")

When he asks for more colour, add these *before* adding emoji — they raise the visual energy without diluting the emoji that are left:

- **Blockquote (`>`) the premise.** Slack renders a vertical bar down the left. Real colour, zero emoji cost. Good for the one-line "why this exists" that sets up the announcement.
- **`###` section headers** to break a long message into chapters. Slack renders them large and heavy. A message with two lists almost always needs them.
- **More jokes.** This is the real lever and it has no ceiling. Emoji *signals* playfulness; the writing *is* playfulness. Examples he approved: "That's the bet, anyway." · "one sitting, one coffee, done." · a hard repeat for emphasis — "Nothing ships carrying an open fact. Nothing."
- **Custom workspace emoji** (`:mendo:`) beat more standard ones — they add colour *and* brand.

**Tried and rejected:** stripping emoji down to ~4 and replacing them with inline-code status tags (`DRAFT`, `BLOCKING`, `OPEN SINCE 31/07`) running down the bullets. It scans well and it's tempting, but he chose the warmer 8–11 emoji version over it. Don't reach for code-span tags as an emoji substitute — the emoji *is* the warmth, and a monospace status column reads more like a Jira board than like him. Inline code stays for what it's for: actual code, filenames, commands.

**Reference shape he approved (Aug 2026):** header with 📢 👇 → blockquote premise → 🔗 link → `###` header → 4 bullets, two bare and two marked (✅ 🚧) → `###` header → 5 bullets, marked at the ends (🔐 … ⚖️ 🚦) → warm close with 🙌. Roughly 11 emoji, two section headers, one blockquote, three jokes.

**Watch-outs he's corrected:**
- Don't imply someone is all-powerful / above the team (he rejected a 👑 crown emoji next to a colleague's new lead role — didn't want it to look like they were "King").
- Don't guilt people for missing things ("actually show up 😉" was cut — the people who missed it had good reasons). Frame attendance as "the best way to stay in the loop," not an obligation with a wink.

### Announcement template (shape, not a fill-in-the-blank)

```
📢 **[Topic] — [short hook]** 👇

> [One-line premise — the problem this solves. Blockquote gives it a colour bar.]

[One sentence bridging premise → the thing.]

🔗 **[Link, if there is one]**

### [Section header — what it is]

- **[Key thing].** [Plain-language explanation, maybe a parenthetical aside.]
- **[Next thing].** […]
- [emoji] **[Thing where the emoji means something].** […]
- 🚧 **[Status caveat].** […]

### [Section header — what's left / what's next]

- 🔐 **[Thing].** […]
- **[Thing].** […]
- **[Thing].** […]
- 🚦 **[The one that lands last].** [Marked bullet = punchline of the list.]

[Warm, forward-looking close.] 🙌
```

Roughly 8–11 emoji total at this length. Note the bare bullets — that's deliberate, not an omission to fill in.

## External (client) register

Professional but unmistakably human. Arj's brand is young, tech-forward, and approachable — the goal is to sound like a smart, friendly person, not a legal department.

- **No emojis. Period.**
- **Open with a light human beat**: "Hope you're doing well." / "J'espère que vous allez bien."
- **Introduce clearly and plainly** when it's a first contact: who he is, that he joined Mendo, what he's here to do.
- **Structure with bullets** when covering multiple points, each with a bolded lead phrase.
- **Concrete asks with reasons.** "Would you have 20 minutes?" + exactly what he wants to cover. State the *why* behind a request (e.g. why IT needs to be on the call).
- **Close warm and forward-looking**: "Looking forward to it." / "Au plaisir d'échanger" (NOT "Nous nous réjouissons de" — too formal). Sign "Best, Arjun" or "Bien à vous, Arjun."

### Client diplomacy rules (important)

- **Never point a finger at the client's setup.** Frame hypotheses as *"an assumption on our side"* to *"validate together,"* never as a diagnosis of their environment. Add hedges: "Nothing confirmed yet," "worth a closer look."
- **Some clients are prickly** (e.g. Jose Oliveira braces easily). For sensitive contacts, soften further: collaborative "we," no blame, emphasize *their input* is what's valuable.
- **Own Mendo's side of any friction.** "Mendo ships fairly out-of-the-box features, so new deployments occasionally need fine-tuning" — frames challenges as a shared puzzle, not the client's fault.
- **Small technical corrections are welcome** — fix product names etc. (e.g. "Cyberreason" → **Cybereason**) but flag them so Arj knows.

### Client email template (shape)

```
Objet / Subject: [clear, specific]

Bonjour [Prénom], / Hi [Name],

[One-line human opener.]

[Plain intro / context — who, what, why.]

[The ask, with a reason. If multiple points:]
- **[Point 1].** […]
- **[Point 2].** […]

[Warm, non-formal close.]

Best, / Bien à vous,
Arjun
```

## French-specific notes

- Natural, professional French — not textbook-formal. Arj mixes French and English naturally depending on context.
- Avoid overly formal set-phrases. He explicitly rejects things like "Nous nous réjouissons d'échanger" → prefers "Au plaisir d'échanger."
- Keep technical terms in English where that's the natural usage (Task Manager, whitelist, logs, debugging session) — often with a French gloss the first time.
- Client French emails still follow the no-emoji rule.

## When rewriting a draft Arj pastes

- Preserve his intent and all his content points — don't drop information.
- Fix the tone to match the register; restructure into bullets if it's a wall of text.
- Keep his specific facts, numbers, names, and links exactly.
- If he says "make it shorter," cut hard — he means it. Trim to the essential points, keep the bolded leads.
- If he says "funnier" or "more colourful," lean into the parentheticals, the blockquote, and the headers **before** adding emoji; if "firmer," add clarity and directness while keeping warmth.
- If he says "fewer emojis," don't cut to the bone — rebalance to 8–11 and fix *placement* (see the emoji budget). A flat cut loses the colour he wants to keep. In a DM this cue means something different: go to 1–2.
- If he says "too much formatting" / "don't need all that for a Slack message," you picked the wrong weight, not the wrong words. Strip headers, blockquote and bold leads, keep the content and the link formatting, and re-read Step 0.5 before the next draft.
- After a rewrite, if you made a judgment call or a correction, note it briefly at the end so he can veto.

## Quick reference — his actual phrasings to echo

Warm openers: "Hope you're doing well." · "listen up 👇" · "A few things —"
Parentheticals: "(yes, there's a difference 😄)" · "no more good ideas lost to the void"
Closes (internal): "More to come. Stay tuned." · "Feedback welcome as always. 🙌" · "Thanks for bearing with me on this. 🙏"
Closes (client): "Looking forward to it." · "Au plaisir d'échanger" · "Best, Arjun" / "Bien à vous, Arjun"
