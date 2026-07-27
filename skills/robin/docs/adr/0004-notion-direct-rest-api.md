# 0004 — Reach Notion via the direct REST API, retire the Claude CLI bridge

Date: 2026-07-26
Status: accepted

## Context

ADR 0003 established that, under Hermes, Robin reached Notion through the only
integration path then available: headless `claude -p --allowedTools
"mcp__claude_ai_Notion__notion-*"`, i.e. driving the Claude Code CLI's Notion
MCP connector with a natural-language instruction.

That bridge had one persistent operational failure: it depended on the `claude`
CLI being logged in to an interactive claude.ai OAuth session, whose token kept
expiring. When it lapsed, every agentic Notion read/write silently failed
("Not logged in" / permission not granted), which is indistinguishable at a
glance from "the page didn't change" — exactly the ambiguity the gate is
designed to avoid. Refreshing it required a manual interactive `/login`.

Separately, the cheap change-poll in `precheck.py` and the token lifecycle in
`notion_token.py` had *already* been talking to the Notion REST API directly
with a `NOTION_API_KEY` workspace-integration token (with OAuth auto-refresh on
401/403). So Robin was already carrying a working, non-interactive Notion
credential — only the read/write bridge still went through the CLI.

## Decision

Route ALL Notion access through the direct Notion REST API. Add
`scripts/notion_api.py`: a small urllib client that reuses `notion_token.py`
for auth and one-shot auto-refresh, exposing read (`render`, `fetch`,
`fetch-deep`, `page`), write (`append`, `update-block`, `delete-block`,
`create-page`, `create-database`), query (`query-ds`), and a generic `call`
escape hatch — usable both as a Python import and as a CLI subcommand.

The `render` command reproduces the one job the bridge did for the Q&A loop:
return the "Robin needs input" block text verbatim plus the `to_do` Done
checkbox state, in one call (`<block_id>\t<type>\t[x]/[ ]\t<text>` lines).

Retire the `claude -p --allowedTools mcp__claude_ai_Notion__*` bridge entirely.
No Claude Code CLI, no MCP connector, and no interactive OAuth login are part of
Robin's Notion path anymore.

## Consequences

- **No more expiring interactive login.** The single `NOTION_API_KEY` token
  (auto-refreshing) now serves both the cheap poll and read/write — one
  credential, one refresh path, no `/login`.
- **Auth failures are now unambiguous.** `notion_api.py` returns `{"error": …}`
  on a real auth failure after its refresh attempt; that is never confusable
  with "no change".
- **Faster + cheaper writes.** A direct REST call replaces spawning a whole
  Claude CLI agent turn per Notion operation.
- **Robin now constructs Notion block JSON itself** rather than describing edits
  in natural language. Slightly more verbose at the call site, but exact and
  deterministic — no interpretation layer between intent and API.
- Amends ADR 0003's "Integration bridge" mechanism; the Telegram capture/notify
  design and the two-surface state split (0001) are unchanged.
