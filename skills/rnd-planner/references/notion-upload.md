# Upload Runbook (Notion)

Publishing to Notion is how R&D becomes shared and trackable at a company level.

**Hard rules**
- **Only ever on the user's explicit request.** Never auto-upload; never make it the default next step.
- **Full content, not links.** Publish the actual problem statement and plan *into* Notion as pages. The Obsidian vault is private — its paths/links must never appear in Notion. Every link and asset in the Notion entry must be Notion-internal.
- **Confirm before writing**, and report the resulting Notion URL(s) back to the user.

---

## The canonical structure is LOCKED — follow it exactly

The R&D Notion structure below already exists (built 2026-06-15). It is the **single source of truth** for how we document R&D in Notion. Every session must follow it **strictly**:

- **Reuse, never recreate.** Use the IDs below. Do **not** create a new database, new property set, new view set, or a different parent location.
- **Do not change the structure on your own initiative** — do not add, remove, rename, or retype properties/views/sub-page types, and do not move the parent.
- **If a requested task doesn't fit the structure:** stop and **propose a specific change for the user to review** (see *Proposing a structure change* at the bottom). Only apply it after explicit approval, then update this file so it stays accurate.

---

## Live structure (IDs — reuse these)

- **R&D page** (parent): `37f5ce63a40b80d2beb0cadac9f99ff1` — `🔬 RnD`, under *Mendo Internal → Tech*.
- **Database `R&D Topics`**: `62ddbe588dd249bfa0dc98a739b307d0`
- **Data source** (for page creation / schema reads): `collection://6498700f-33eb-474f-a799-9a88db877bf3`

**Model:** one database, **one row = one R&D topic = one page**. Each topic page holds **three child sub-pages** so documentation never bleeds between topics or doc types. Notion is the *macro / documentation* layer; **Linear holds executable tasks** (linked via the `Linear` property) — never track tasks in Notion.

### Database properties (exact names & types)

| Property | Type | Values |
|---|---|---|
| **Name** | Title | topic name |
| **Status** | Status (grouped) | groups map to backlog/ongoing/done — see note below |
| **Owner** | Person | who drives it |
| **Priority** | Select | `High` · `Medium` · `Low` |
| **Profiles needed** | Multi-select | `Engineering` · `AI Specialist` · `Product` · `Client` |
| **Theme** | Multi-select | `Security` · `RAG` · `Agents` · `Voice` · `Infra` (extend by adding options, not new properties) |
| **Mendo integration area** | Multi-select | `Excel` · `ChatGPT` · `Copilot` · `Desktop` · `API` · `Client Hub` |
| **Business value** | Text | the business outcome / impact |
| **Related Topics** | Relation (self) | non-directional "these are connected" |
| **Depends on** / **Blocks** | Relation (self, two-way pair) | directional sequencing between topics |
| **Linear** | URL | link to the Linear project/issues for execution |
| **Last updated** | Last edited time | auto |

> Do not add a vault/Obsidian link property — sharing is Notion-only.

**Status semantics:** the dedicated Status type's three groups are the backlog/ongoing/done picture — **To-do = backlog, In progress = ongoing, Complete = done**. The intended lifecycle options are: To-do → `Idea`, `Documenting`, `Planning`, `Parked`; In progress → `In Progress`; Complete → `Validated`, `Done`. The Notion API **cannot create or edit Status options/groups**, so any missing options are added once in the UI; when setting a row's Status, use an option that already exists (don't error on a missing one).

### Views (already created)

`Board — by Status` (the backlog/ongoing/done picture) · `Ongoing` (table) · `By Theme` (board) · `By Integration area` (board) · the default table. Reuse them; don't spawn parallel views.

### Per-topic sub-pages (exactly these three, always)

Every topic page contains three child sub-pages, stubbed from the templates:
- **📄 Problem Statement** — full §1–§10 from [problem-statement-template.md](problem-statement-template.md).
- **📄 Plan** — full content from [plan-template.md](plan-template.md).
- **📄 Research Log** — reverse-chronological dated entries.

A database template named **"R&D Topic"** pre-builds these on each new row (set in the UI via `•••` → *Save as template*). If it isn't applied to a row, create the three sub-pages yourself with `Notion:notion-create-pages` — same three names, same order.

---

## Step 1 — Locate the database (don't recreate)

`Notion:notion-fetch` the database id `62ddbe588dd249bfa0dc98a739b307d0` to confirm it exists and read the current schema/data-source id. Only if it has genuinely been deleted do you rebuild it — and then to **this exact schema**.

## Step 2 — Create / update the project entry

1. Create (or update, if it already exists) a **database row** for the project under data source `collection://6498700f-33eb-474f-a799-9a88db877bf3`, and set the properties above from the problem statement and plan. Set relations (`Related Topics`, `Depends on`/`Blocks`) to other R&D rows where they apply.
2. Publish the **content** as the three sub-pages under that row:
   - Problem statement → the **Problem Statement** sub-page (full §1–§10).
   - Plan → the **Plan** sub-page (full content).
   - Ongoing notes → the **Research Log** sub-page.
   - Use `Notion:notion-create-pages` / `notion-update-page`. Convert markdown to Notion blocks; tables and headings should survive.
3. Internal references (problem statement ↔ plan, links to other R&D entries) must point to Notion pages, not files.

## Step 3 — Report back

Give the user the Notion URL(s) created/updated and a one-line summary of what was published and the property values set. Flag anything that needed a manual UI step (e.g. a not-yet-created Status option). If anything in the schema was ambiguous (e.g. Priority not yet decided), ask rather than guessing.

---

## Proposing a structure change (when the structure doesn't fit)

The structure is deliberately fixed so documentation stays consistent and traversable across sessions. When a task genuinely cannot be served by it, **do not silently adapt** — surface it:

1. **State the gap:** what the task needs that the current structure can't express.
2. **Propose a precise change:** the exact property/view/sub-page/relation to add or alter, its type and values, and which of the five goals (backlog/ongoing picture · rich docs · unmixed docs · topic linking · easy traversal) it serves — and any cost (clutter, migration, maintenance).
3. **Wait for explicit user approval.** Prefer extending an existing multi-select (add an option) over adding a new property; prefer a new view over a new property; treat new properties and new sub-page types as the highest-bar changes.
4. **On approval, apply it and update this file** in the same session, so this runbook always reflects the live structure.

Known API limitations to account for (not reasons to change the structure): Status options/groups can't be created via API (UI only); the view DSL won't apply `status`-property filters (set those in the UI).
