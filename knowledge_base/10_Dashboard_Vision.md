# Dashboard Vision — The North Star

**Status:** Recreated July 15, 2026 (original file was never completed/uploaded).
**Owner:** Founder, quarterbacked by Claude.
**Purpose:** This is the single document every other build decision should be checked against. If a feature, integration, or architectural choice doesn't serve this vision, it doesn't get built yet — regardless of which AI proposed it.

---

## 1. The Ultimate Vision

Atlas is an **AI Companion to the CEO**.

Every small business generates dozens of data points daily — cash, sales, ops status, customer signals, marketing performance, team output — that a real CEO would use to make decisions. Most solo founders and small teams don't have the staff to collect, structure, and analyze that data. Atlas is the layer that does it for them: it collects the data points, turns them into daily answers to the questions that matter, and becomes the founder's best source for decision-making.

Dolce Mondo is not the product. Dolce Mondo is customer #1 and the proof that the system works on real, messy, small-business data. The long-term goal is a SaaS platform — vertical first (food/CPG, since that's what we're proving on), then horizontal (any small business) — where Atlas becomes "the AI Operating System for small businesses."

## 2. What Atlas Must Never Stop Doing (Non-Negotiable Core)

Regardless of how far the platform grows, Atlas always:

- Answers the 10 Core Questions daily (see `Claude_System_Design_Brief_Project_Atlas.md`).
- Produces the Morning Brief in the exact specified format.
- Never hallucinates facts about the business — grounded only in real data provided.
- Maintains Executive Memory: every significant decision logged with Why / Who / Expected Outcome / Actual Outcome, and reviewed later against what actually happened.
- Defaults to brutal honesty and execution focus over polish or flattery.
- Escalates high-stakes decisions (finance, regulatory, customer, hiring) for human review rather than acting autonomously.

## 3. The Roadmap (Shortest Path, Nothing Skipped That Shouldn't Be)

### Phase 1 — Prove it on Dolce Mondo (now → ~3 months)
Stable daily-use dashboard. Finance + Square data collection (manual/CSV first). Morning Brief and 10 Questions running reliably. Decisions Log in real use. Basic polish and mobile-friendliness. This phase is done when the founder is actually opening Atlas every day and it's changing what he does — not when the code is "feature complete."
**Explicitly deferred:** multi-user/auth, predictive analytics, bank integration, any multi-tenant code.

### Phase 2 — Remove manual data entry
Square API integration (real-time, not CSV). Possibly bank read-only (Plaid) if Square alone doesn't cover it. This is the one piece of "medium-term" pulled forward, because it's the actual daily friction the founder pays right now — and it's infrastructure a second business would need too, so the effort isn't wasted later.

### Phase 3 — Generalize the data model
The real unlock for SaaS. Today "cash," "burn," "Square revenue" are hardcoded to Dolce Mondo's shape. This phase redesigns the data model so "business type → relevant metrics" is configurable. Done deliberately, once Phase 1 is stable — not guessed at in advance.

### Phase 4 — Second customer
Found by hand, not through a signup flow. The goal is to learn what breaks with a different business's real data before building self-serve anything. This is also where multi-tenant auth and real security become non-optional.

### Phase 5 — Platform
Self-serve signup, billing, predictive/agent features, franchise/multi-location playbooks. This is the payoff phase, not the foundation — no architectural decisions should be made for this phase until Phase 4 has taught us what customer #2 actually needs.

## 4. Objectives by Horizon

**Short-Term**
- Stable, daily-use dashboard answering the 10 core questions
- Automatic or low-friction Morning Brief with real finance and Square data
- Persistent data input for cash, burn, revenue, key metrics
- Executive Memory (Decisions Log) tracking decisions and outcomes
- Basic polish: colors, mobile-friendliness, clean layout
  - Planned upgrade: Decisions Log should capture structured fields (Why / Who / Expected Outcome / Actual Outcome / Status), not just freeform text — needed for Executive Memory to actually close the loop on decisions
  - Planned upgrade (hold until after first week of daily use): CEO Intelligence Score broken into 7 domains (Financial, Operations, Marketing, Customer, People, Growth, Risk) plus Overall, replacing the current single overall score — only build if daily use shows the single score isn't enough
- Reliable enough for daily operation
- The beginning of an AI Operating System for Dolce Mondo

**Medium-Term**
- Full Square API (and possibly bank) integration for automatic sales/cash data
- Additional modules: full Operations status, Marketing performance
- Voice capability: voice-in (speak a prompt to Atlas instead of typing) and voice-out (Atlas reads responses aloud). Voice-in is the lower-effort add (browser speech-to-text feeding the existing text pipeline); voice-out is a separate layer on top. Sequenced here deliberately — added once Phase 1 is stable, not mid-build.
- Risk and Opportunity prediction based on real historical data (not before there's real historical data to learn from)
- Exportable reports for accountant/investor raise
- Multi-user support for future hires (COO, baking chef, sales director)
- Validated ROI — time saved, better decisions, faster reopening. **Measurement starts in Phase 1, not medium-term** — there's no baseline to compare against otherwise.

**Long-Term**
- Full SaaS version for other small businesses (vertical first, then horizontal)
- Advanced predictive analytics and AI agents per department
- Franchise / multi-location playbook automation
- Become "the AI Operating System" for small businesses
- Sell the platform to other businesses

## 5. Design Principles That Protect the Path

- **Dogfood first.** Nothing gets built for a hypothetical second customer before it's proven on Dolce Mondo.
- **Low-code / non-coder friendly.** The founder is not a programmer and is relying on Claude plus non-coding platforms (Streamlit Cloud, GitHub's web UI, Google Drive). Every build decision should minimize the founder's need to touch raw code directly, and every instruction should assume zero prior coding knowledge.
- **Boring before clever.** Reliability and daily use beat predictive analytics, agents, or franchise automation — all of which remain explicitly out of scope until their phase arrives.
- **Single source of truth.** This document, plus the 00–09 knowledge base files, are what Atlas is grounded in. Any AI working on this project (Claude, Grok, ChatGPT) should check proposals against this file before building.
- **Human-in-the-loop always.** High-stakes decisions get surfaced for founder approval, never auto-executed.

## 6. Interaction Preference

Simple, clean web dashboard (Streamlit for now). Daily/weekly briefings, decision synthesis, content ideas, unit economics tracking — all in one place the founder can check each morning without needing to interpret raw data himself.
