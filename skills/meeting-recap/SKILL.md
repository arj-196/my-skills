---
name: meeting-recap
description: >-
  Turn a Fireflies meeting into Arj's readout and post it to Slack. Trigger whenever Arj says "recap Thursday's session", "summarise the meeting and post it", "find the meeting in Fireflies", "fireflies to slack", "write up the walkthrough", "what did we decide in X", or names a meeting and a channel. Reads the FULL transcript (not the summary field), warns when Fireflies mis-attributed speakers, splits actionables into now / before-the-next-forcing-function / standing principles, filters anything that shouldn't be in a public channel, turns the filtered items into proposed DMs instead of dropping them, and adds its own technical observations. Always drafts first — never posts or sends without Arj's explicit go.
---

# Meeting recap → Slack

Arj sits in a lot of meetings that Fireflies records. He wants the useful ones turned into a **readout**: decisions, actionables split by horizon, and things worth flagging that nobody raised. Then posted to the right Slack channel.

This is his readout, in his voice. It is **not** a neutral minutes document and it is **not** the team's own progress recap — if a team owns a recurring bilan for that meeting, say so in the post and hand it back to them.

## Hard rules (read first)

- **Draft first, always.** Show him the full text before anything is sent. He approves, then you post or schedule. Never auto-send, never send "while you're at it". Each DM is a separate go.
- **Read the whole transcript.** The `summary` field on a Fireflies meeting is not enough — it routinely misses the most important technical finding in the session. See Step 2.
- **English.** Arj only messages in English, even when the meeting was in French and everyone in it is francophone.
- **Nothing gets silently dropped.** Anything the sensitivity pass cuts becomes a proposed side-action (Step 5), not a deletion.
- **Weekends.** If it's Saturday or Sunday, offer to schedule for Monday 09:00 CEST rather than sending. Scheduled Slack messages **cannot be edited via API** afterwards — he has to use "Drafts and sent" in the Slack UI — so get the draft right before scheduling.

## Step 1 — Find the meeting

Tools are deferred; load them with ToolSearch first (`fireflies_get_transcripts`, `fireflies_get_transcript`, `slack_search_channels`, `slack_search_users`, `slack_send_message`, `slack_schedule_message`).

When Arj names a day ("Thursday"), resolve it to a date and list that day's meetings — don't guess which one he means from the title alone:

```
fireflies_get_transcripts(fromDate: "YYYY-MM-DD", toDate: "YYYY-MM-DD", limit: 25, format: "text")
```

That returns titles, times, attendees, and Fireflies' own summary + action items. If several could match, name them and confirm which one before reading a 100k-character transcript.

## Step 2 — Read the full transcript (and check attribution)

```
fireflies_get_transcript(transcriptId: "01K...")
```

A ~1h meeting exceeds the tool's token limit. It gets written to a file and the error gives you the path — **read that file in chunks of ~300 lines until you have read 100% of it.** State explicitly which portion you read. Do not summarise from a partial read.

**Then check attribution before naming anyone.** Compare the transcript's `Speakers:` list against `Meeting Attendees:`. If Fireflies logged fewer speakers than attendees, it has collapsed people together — typically attributing everyone to the host. This is common and it will make you assign the wrong person's commitment to someone else.

When counts disagree:
- Attribute from **content**, not labels — who narrates a piece of work, who says "I tested…", who someone else credits by name ("X found this bug, I verified it after").
- Where content doesn't settle it, **write the item unattributed** rather than guessing.
- Add a one-line footer to the post: recap came from the Fireflies transcript, it caught N of M speakers, correct your own line if it's wrong. This also sets the expectation that these posts are machine-assisted.

## Step 3 — Build the recap

Four sections, in this order:

**🔒 Decisions locked.** What was actually decided, with the number or the reason that makes it defensible. A decision without its trade-off gets silently re-opened three months later.

**▶️ Now.** Unblocked, someone can move it this week. Name an owner only where the transcript demonstrably supports it — that's a restatement of their own commitment, not a new assignment. Mark genuinely unowned items **"needs an owner"** rather than leaving them floating; in a channel with leads in it, that's the cheapest way to surface work without assigning someone else's backlog.

**⏳ Before [the next forcing function].** The bucket that earns its place. Find the real upcoming event that changes the team's context — a project kickoff that pulls people off this work, a release, someone's leave — and put here the items that are cheap now and expensive after it. Name the forcing function in the header.

**🧭 Principles.** Standing frames, not tasks. Arj braindumps these in walkthroughs and they're often the most valuable part of the meeting. Keeping them separate stops them reading as unassigned work nobody picks up.

**➕ Worth adding.** Your own observations — things nobody in the room raised. This is what makes it a readout instead of a transcript. Look for: decisions resting on an unvalidated measurement, silent failure paths with no telemetry, "not a priority but keep it in mind" items that need a number to survive, single points of failure. Split them: technical ones go in the post, governance/commercial/personnel ones go to Arj in chat only (Step 5).

Then close warm, and add the attribution footer.

## Step 4 — Length and format

Follow the **arj-comms** skill's *internal* register: 📢 header, emoji anchoring each bullet, bold lead then the point, warm close.

- **Bold titles must carry the point on their own.** Arj's default is a short post — one line per item, no explanatory sentences. Only add context where the title genuinely can't stand alone.
- **No tables.** Recap items don't fit cells.
- **One message, not a thread.** A thread hides half the content.
- Use real Slack mention syntax `<@U…>` so people are actually notified — not `@Name` as plain text.

## Step 5 — Sensitivity pass, and the side-actions it generates

Most target channels are **public**. Before showing him the draft, pull these out:

| Cut | Keep instead |
|---|---|
| Characterisations of a named person ("not happy", "looking for reasons to say no") | The scenario, anonymised — it usually makes the point better |
| An individual's hardware, performance, workload or pay | Nothing. It's a DM. |
| Non-technical reasoning behind a technical call (vendor stigma, internal politics) | The decision, with a neutral rationale |
| Euro figures, subscriptions, spend approvals | At most "compute/storage constraints resolved", if it explains why something is now unblocked |
| A ruling with legal/privacy/compliance weight made in passing | Leave it open ("separate call, getting it confirmed") rather than asserting it's settled |

**Every cut becomes a proposed side-action.** List them for Arj as concrete DMs — recipient, what it asks, why it can't go in the channel — and let him pick. He will usually take fewer than you propose; don't re-raise the ones he drops.

Draft the chosen DMs in his voice too, and send them one at a time on his explicit go.

Finally, give him the **governance items in chat only** — the ones that need a lead, compliance, or just his own decision. Surface them and stop. Don't turn them into actions unless he asks.

## Step 6 — Post or schedule

- **He named a channel** → post directly on his go with `slack_send_message`, return the link.
- **Weekend or out of hours** → `slack_schedule_message` with a Unix timestamp. Compute it, don't estimate:
  ```bash
  TZ=Europe/Paris date -j -f "%Y-%m-%d %H:%M:%S" "2026-07-27 09:00:00" "+%s"
  ```
  Put the channel post first and stagger DMs 1–2 minutes behind it, so a DM that references the post doesn't land before it.
- **No destination named** → show the draft and ask where.

## Channel notes

> This skill is global (`~/.agents/skills`), so these channel notes are the only Mendo-specific state it carries. Everything above works for any Fireflies meeting and any Slack channel.

**#42-rnd** — `C0BJ3BEU734`, public, created July 2026 by Arj for R&D topics that cut across squads.
- Working language is **English** (Arj set the precedent) and **Heather is a member and works in English** — she owns several product-side specs the R&D pair depends on, so a French post would structurally cut her out.
- **The recurring progress bilans belong to Vincent and Jad.** Arj's posts here are his own readouts; say so, so the two don't get confused.
- Members: Arj `U0B71TMF690` · Vincent Durey `U0BFPUWN33L` · Jad `U06JAG9E75Z` · Heather `U0B6LDW48CF` · Camille `U09DB6YHMKK` · Alexandre Pinon-Jacques `U03AK0P94TD`.
- Other IDs that come up: Jean-Charles Eray `U03AXJRFESD` (hardware/IT).

**#42-dev** — `C03ARRV5THS`. **#99-arj-test** — `C0BJG5L83CN`, use to preview formatting.

> Only one `Jad` exists in Slack (`U06JAG9E75Z`, `jad@mendo.ai`) even though calendar invites use `jad@mendo.cloud`. Same person.

## Related

- **arj-comms** — his voice. Global, always available. Load it before drafting.
- **ritual-priorities** — the other Slack-posting ritual; same draft-vs-post convention. Project-scoped to `ProjectManagement`.
- **tech-debt** / **tech-decision** — where a decision or a debt item found in a meeting should end up if Arj wants it recorded rather than just posted. Also `ProjectManagement`-scoped, so only reachable from that repo.
