# ARJ Linear access uses a personal API key, not Claude Code's Linear MCP

**Context.** The original plan (grilling Q10) routed ALL Linear access — read
and write — through Claude Code's connected Linear MCP, on the reasoning that it
was a single OAuth-managed integration and the pasted personal API key could be
discarded. The first dry-run disproved this: Claude Code's Linear MCP is
authenticated to the **Mendo** organization and returns nothing for the personal
**ARJ** workspace. Zero tickets were created because ARJ was simply unreachable
that way.

**Decision.** Slack and Outlook Signals are gathered via headless `claude -p`
(their MCPs work). ARJ Linear read/write goes through `scripts/linear_arj.py`,
which calls the Linear GraphQL API directly using `LINEAR_ARJ_API_KEY`. The key
is stored in `~/.hermes/.env` (chmod 600, outside the git repo).

**Why.** The personal API key is the only credential that can see the ARJ
workspace. Claude's Linear MCP, being org-scoped to Mendo, is structurally
incapable of it — no amount of tool-granting fixes that. Splitting the
integration (comms via MCP, ARJ via key) is therefore not a preference but a
requirement.

**Consequences.** There are now two integration paths and one secret to manage.
The key must be rotated after the setup session (it was pasted in chat) and kept
only in `.env`. This supersedes the Q10 decision to discard the key; ADR 0001
(Linear as sole state) is unaffected — the source of truth is still Linear, only
the access mechanism changed.
