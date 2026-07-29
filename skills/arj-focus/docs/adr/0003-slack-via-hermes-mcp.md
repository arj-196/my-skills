# 0003 — Slack via the Hermes `slack` MCP server, not the Claude CLI

Date: 2026-07-28
Status: accepted

## Context

ADR 0002 recorded that Slack and Outlook Signals were gathered through headless
`claude -p`, driving the claude.ai Slack/Microsoft 365 connectors. That path had
one chronic failure: it depends on the `claude` CLI holding a live claude.ai
OAuth login, whose token kept expiring. A lapsed login made every Slack pull
silently return nothing — indistinguishable from "no Signals" — and recovery
required an interactive `/login` (or the Keychain-surgery workaround in the
pitfalls). Arjun asked that anything accessing Slack stop using the Claude CLI.

Hermes already ships a first-class Slack integration: the `slack` MCP server
(korotovsky `slack-mcp-server`), configured in `config.yaml` with Arjun's `xoxp`
user token. A user token can search and read *his* messages via Slack's Web API
— exactly what arj-focus needs — with no interactive login and no expiry drama.

## Decision

Gather all Slack Signals through the Hermes `slack` MCP tools, called directly
in the arj-focus session (they are loaded into the agent's toolset). Retire the
`claude -p` Slack path entirely. Tool mapping from the old connector:

| Purpose | Old (claude CLI connector) | New (Hermes `slack` MCP) |
|---|---|---|
| search messages | `slack_search_public_and_private` | `slack:conversations_search_messages` |
| read channel/DM | `slack_read_channel` | `slack:conversations_history` |
| read thread | `slack_read_thread` | `slack:conversations_replies` |
| resolve user | `slack_read_user_profile` | `slack:users_search` |

**Outlook stays on `claude -p`** — the Microsoft 365 connector still lives only
on the Claude CLI, and Arjun's instruction was Slack-specific. So arj-focus now
uses two integration paths: Slack (Hermes MCP) + Outlook (`claude -p`).

## Operational notes

- The `slack` MCP server MUST launch with `-no-cache`. Without it the server
  fatally crashes at startup caching the users collection, because the `xoxp`
  token lacks the `users:read` scope (`missing_scope`). Set once in
  `config.yaml` (`mcp_servers.slack.args`).
- A stale `--connect-timeout 60` arg was present in the original config; this
  Go binary rejects it (`flag provided but not defined`). Removed.
- Enabling the server (`mcp_servers.slack.enabled: true`) requires a gateway
  restart to load the tools into running sessions.

## Consequences

- **No more expiring interactive login for Slack.** The `xoxp` token is a
  long-lived workspace credential; Slack Signals no longer break when the
  `claude` CLI login lapses.
- **Failures are unambiguous.** A Slack MCP error is a real error, not a silent
  empty result masquerading as "no Signals."
- **The `claude` CLI dependency shrinks to Outlook only.** When the Microsoft
  365 side is likewise moved off the CLI, arj-focus can drop `claude -p`
  entirely.
- Amends ADR 0002's integration mechanism; the Linear-as-sole-state design
  (0001) and the personal-key Linear path (0002) are unchanged.
