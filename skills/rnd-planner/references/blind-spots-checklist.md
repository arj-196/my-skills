# Blind-Spots Checklist

Run this before declaring a problem statement or plan "done". It's the quality gate — the
job is to catch what's been missed *before* it costs us. Don't just tick boxes: for each,
either point to where the doc/plan answers it, or raise it as an open question / risk.

Surface anything unresolved into §10 of the problem statement or §7 of the plan.

## Is the problem real and worth it?
- [ ] Is the **market/business need** concrete, or assumed? Who actually hurts?
- [ ] Is "why now" answered? What changes if we *don't* do this?
- [ ] Have we separated **business framing** from **technical framing** — and do they map?

## Can we tell if it worked?
- [ ] Is there a **measurable success criterion**? How exactly would we measure it?
- [ ] Is there an **eval strategy** for the AI/quality part (golden set, judge, human review)?
- [ ] Does each challenge have an **exit criterion** so we know when to stop or move on?

## Will it actually fit Mendo?
- [ ] **Integration feasibility** confirmed against real code — which app/channel/stack/seam?
- [ ] Are we proposing a **new integration** (e.g. Anthropic where it's OpenAI today)? Is that cost in the plan?
- [ ] Does the **data we need** exist, is it accessible, and do we have the **rights** to use it?

## What could bite us later?
- [ ] **Cost** at scale (tokens, infra,人-time) — within a sane budget?
- [ ] **Latency** acceptable for the host app/channel it lives in?
- [ ] **Security & privacy** — PII, client data, model data-handling.
- [ ] **Maintenance / long-run ownership** — who keeps this alive after the research ends?
- [ ] **Scope creep** — is the challenge sharply bounded, or quietly expanding?
- [ ] **Build vs buy** — is building justified vs an existing tool/model/API?

## Who do we need, and have we lined them up?
- [ ] Right **profiles** named per challenge (Eng / AI Specialist / Product / Client)?
- [ ] **Dependencies on Product/Client teams** identified as concrete checkpoints, not "later"?
- [ ] Any **external dependency** (vendor, API, another team) that could block us?

## Honesty pass
- [ ] What's the **single biggest unknown**, and does the plan de-risk it *first*?
- [ ] What assumption, if wrong, **kills the project** — and how cheaply can we test it?
