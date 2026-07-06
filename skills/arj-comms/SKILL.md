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
| Emojis | Yes — used to structure and add flair | **Never.** Zero emojis, ever. |
| Tone | Warm, funny, human, a little irreverent | Professional, warm, approachable — not stiff, not academic |
| Formatting | Bullets + bold + emoji headers | Short paragraphs; bullets only for a list of distinct points |
| Humor | Dry parenthetical asides, gentle ribbing | Light warmth only; no jokes |

If it's ambiguous, ask which one. When he says "for my team" → internal. "For client" / "mail client" → external.

## Core voice (applies to both registers)

- **Short, declarative sentences.** No throat-clearing. Get to the point.
- **Lead with the human warmth, then the substance.** "Hope you're doing well" / "listen up 👇" — a quick human beat before the content.
- **Plain language over jargon.** "no more good ideas lost to the void" beats "improved action-item persistence."
- **Bullets for anything multi-point.** Arj organizes his thoughts as bullets and expects them back. If there's more than one idea, bullet them.
- **Bold the key phrase in each bullet**, then explain. e.g. "- **Confirming the root cause.** We analyzed the logs…"
- **Warm, open-ended close.** "Feedback welcome as always." / "Looking forward to it." / "Thanks for bearing with me." Never a cold sign-off.
- **Never academic, never pompous.** If a line sounds like a consultant wrote it, rewrite it. He flags phrases like "Nous nous réjouissons d'échanger" as "too formal, not my style."

## Internal (team) register

The personality dial goes up. This is where Arj is fun.

- **Emoji as structure and flare.** One emoji per bullet to anchor it (📊 🗓️ 🔧 🤖 💬), plus emphasis emojis in-line (😅 🙌 🚀 🍻). Section header often opens with 📢 or a topic emoji.
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

**Watch-outs he's corrected:**
- Don't imply someone is all-powerful / above the team (he rejected a 👑 crown emoji next to a colleague's new lead role — didn't want it to look like they were "King").
- Don't guilt people for missing things ("actually show up 😉" was cut — the people who missed it had good reasons). Frame attendance as "the best way to stay in the loop," not an obligation with a wink.

### Internal template (shape, not a fill-in-the-blank)

```
📢 **[Topic] — [short hook]** 👇

- [emoji] **[Key thing].** [One-line plain-language explanation, maybe a parenthetical aside.]
    - [sub-bullet if nesting needed]
- [emoji] **[Next thing].** […]

[Warm, forward-looking close.] [emoji]
```

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
- If he says "funnier," lean into the parentheticals and emoji; if "firmer," add clarity and directness while keeping warmth.
- After a rewrite, if you made a judgment call or a correction, note it briefly at the end so he can veto.

## Quick reference — his actual phrasings to echo

Warm openers: "Hope you're doing well." · "listen up 👇" · "A few things —"
Parentheticals: "(yes, there's a difference 😄)" · "no more good ideas lost to the void"
Closes (internal): "More to come. Stay tuned." · "Feedback welcome as always. 🙌" · "Thanks for bearing with me on this. 🙏"
Closes (client): "Looking forward to it." · "Au plaisir d'échanger" · "Best, Arjun" / "Bien à vous, Arjun"
