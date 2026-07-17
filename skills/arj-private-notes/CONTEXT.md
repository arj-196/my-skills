# Context — arj-private-notes

The domain language for the `arj-private-notes` skill and the Notion store it feeds.

## Glossary

### Protected Conversation Log
The canonical name of the Notion database this skill writes to (title: `🗣️ Protected Conversation Log`, under the `Protected` parent page). Called "private notes" / "private conversations" informally and labelled `🗣️ 1:1 & Conversation Log` on one ancestor — **all refer to this same DB**. Use "Protected Conversation Log" everywhere in the skill; never invent a fourth name.

- DB URL: `https://app.notion.com/p/2e63b19a91724505a96c6760d4a3ce9c`
- Data source: `collection://1fa09a9f-83b9-408b-996a-4bbcc798519c`

### Protected conversation
A single entry (page) in the Protected Conversation Log. One consequential conversation Arj had, distilled to a Context narrative plus topic sections — not a transcript.

## Boundaries

### arj-private-notes vs one-on-one
`arj-private-notes` owns the Protected Conversation Log as the catch-all for any **ad-hoc** consequential conversation (feedback given/received, corrections, conflicts, career chats, sensitive peer/cross-team talks). The biweekly 1:1 ritual stays with the `one-on-one` skill, which logs to member Person Pages — NOT to this DB. The `Type: 1:1` option here exists only for the rare case where a 1:1 surfaces something protected worth logging separately. This resolves the `one-on-one` skill's own note that ad-hoc conversations "go to the Private Conversation Log by hand" — this skill automates that gap.
