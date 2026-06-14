# Mendo Grounding Map

Where to look when grounding an R&D idea in what Mendo actually has. Use `Agent` with
`subagent_type=Explore` against these locations — don't assume, verify. This map is a
starting point; the repo evolves, so confirm paths still exist before relying on them.

Repo root: `/Users/arjun/Mendo/apps/mendoverse`

## What Mendo is
An AI-powered learning platform delivered as add-ins/extensions across distribution channels:
- **Excel** (native add-in) · **ChatGPT** (web) · **Microsoft Copilot** (browser & desktop) · **Internal** (browser extension)
- Runtime vocabulary: `Product` = distribution channel; `ProductApp` = host app (Excel/Word/PowerPoint/Outlook/Teams/Copilot Web); **Connectors** adapt the core app to each host.
- **Client Hub** = separate platform for group management/administration.

## Where to read first (docs)
- `docs/tech/README.md` — onboarding entry point.
- `docs/tech/getting-started/overview.md`, `app-architecture.md`, `communication-flow.md`, `adding-features.md`.
- `docs/tech/architecture/` — `fsd-architecture-reference.md`, `fsd-nomenclature.md`, `app-fsd-implementation.md`, `typescript-workspace-architecture.md`.
- `docs/product/mendo-ai/` — AI feature specs (lab validation, AI execution, settings, certifications).
- `docs/product/client-hub/` — Client Hub + credit domain.
- `AGENTS.md` files: root, `typescript/AGENTS.md`, and per-package (e.g. `typescript/api/AGENTS.md`) — source of truth for each layer + learned user preferences.

## Where the code lives
TypeScript monorepo under `typescript/` (15+ workspaces):
- `api/` — NestJS backend (MongoDB, Redis, tRPC adapter). **Main API.**
- `app/` — main React task pane; `src-new` uses **FSD**.
- `mendo-mvp/` (frontend + Fastify+tRPC api), `client-hub/` + `client-hub-mvp/`.
- `browserConnector/`, `desktopConnector/` (Electron), `back-office/` (+ `-mvp`).
- `mcp-gateway/`, `adminjs/`, `shared/`, `qa/` (Playwright), `global/`, `others/`.

Other stacks: `python/ai/app/` (Flask AI utils), `python/menbot/` (Teams bot), `csharp/` (Excel connector), `yaml/cluster/` (AKS), `prompts/`, `scripts/`.

## Where AI/LLM code lives today (mostly OpenAI)
- `typescript/api/src/ai/` — core AI service: `ai.service.ts`, `prompts.ts` (large prompt library), `ai.controller.ts`, `helpers/`, `use-cases/`.
- `typescript/back-office-mvp/api/src/shared/plugins/openai/Openai.service.ts` — OpenAI wrapper (marked for deprecation); `LabsTranslation/`, `LPVisualizer/`.
- `python/ai/app/` — `search.py`, `similarity.py`, `text_to_formula.py`.
- `typescript/others/ai-pr-reviewer/` — GitHub Action, OpenAI-based code review.

> **No existing Anthropic/Claude integration.** Treat Claude as greenfield — any plan that
> uses it is also proposing a new integration, and that integration cost belongs in the plan.

## Stacks & patterns (for integration-feasibility checks)
- Backends: **NestJS** (main API) · **Fastify + tRPC** (Client Hub, MVPs).
- Frontends: **React** with **FSD** in `app/src-new`, `mendo-mvp/frontend`, `client-hub/frontend`.
- Contracts: **tRPC** (schema-first). State: Zustand (app), Jotai (back-office MVP), React Query (server state).
- Comms: App↔API tRPC/HTTPS; App↔Connector postMessage/IPC/chrome.webview; Connector↔Platform DOM/Windows APIs/MOffice.js.

## Existing R&D-adjacent material
- `AIImpactHubAnalysis.md`, `AIImactHubAudit.md` at repo root.
- Tracking lives in **Linear** (workspace `mendoooo`; teams `INA` mendo-mvp, `CLI` client-hub) — out of scope for this skill for now, but relevant context.
