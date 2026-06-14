# Upload Runbook (Notion)

Publishing to Notion is how R&D becomes shared and trackable at a company level.

**Hard rules**
- **Only ever on the user's explicit request.** Never auto-upload; never make it the default next step.
- **Full content, not links.** Publish the actual problem statement and plan *into* Notion as pages. The Obsidian vault is private — its paths/links must never appear in Notion. Every link and asset in the Notion entry must be Notion-internal.
- **Confirm before writing**, and report the resulting Notion URL(s) back to the user.

## Target

Dedicated R&D page (workspace `mendo-ai`):
`https://app.notion.com/p/mendo-ai/RnD-37f5ce63a40b80d2beb0cadac9f99ff1`
(page id `37f5ce63a40b80d2beb0cadac9f99ff1`)

All R&D tracking lives under this page.

## Step 1 — Find or create the tracking database

The tracking database **may not exist yet** (it's created on first upload, then reused).

1. Use `Notion:notion-search` (and/or `notion-fetch` on the R&D page) to look for an existing R&D tracking database under that page.
2. If found, reuse it. If not, create it with `Notion:notion-create-database` as a child of the R&D page, with this schema:

| Property | Type | Values |
|---|---|---|
| **Name** | Title | project name |
| **Status** | Select | Idea · Documenting · Planning · In Progress · Validated · Parked · Done |
| **Phase** | Select | current phase (free/short) |
| **Profiles needed** | Multi-select | Engineering · AI Specialist · Product · Client |
| **Business value** | Text (or Select) | the business outcome / impact |
| **Priority** | Select | High · Medium · Low |
| **Mendo integration area** | Multi-select / Text | which app/channel/stack it touches (Excel, ChatGPT, Copilot, API, Client Hub…) |

> Do not add a vault/Obsidian link property — sharing is Notion-only.

## Step 2 — Create / update the project entry

1. Create (or update, if it already exists) a **database row** for the project and set all properties above from the problem statement and plan.
2. Publish the **content** as the page body and/or child pages under that row:
   - Problem statement → a page (e.g. "Problem Statement") with the full §1–§10 content.
   - Plan → a page (e.g. "Plan") with the full content.
   - Use `Notion:notion-create-pages` / `notion-update-page`. Convert markdown to Notion blocks; tables and headings should survive.
3. Internal references (problem statement ↔ plan, links to other R&D entries) must point to Notion pages, not files.

## Step 3 — Report back

Give the user the Notion URL(s) created/updated and a one-line summary of what was published and the property values set. If anything in the schema was ambiguous (e.g. Priority not yet decided), ask rather than guessing.
