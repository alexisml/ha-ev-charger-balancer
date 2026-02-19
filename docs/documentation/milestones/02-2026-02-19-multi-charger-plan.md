Title: Multi-Charger Support Plan
Date: 2026-02-19
Author: alexisml
Status: draft
Summary: Phase 2 plan for adding multi-charger support with per-charger prioritization and weighted current distribution.

---

This document covers Phase 2 of the integration — multi-charger support. Phase 2 begins after the MVP (Phase 1) is released and stable. See the MVP plan: [`01-2026-02-19-mvp-plan.md`](01-2026-02-19-mvp-plan.md).

## Goal

Extend the single-charger integration to support multiple EV chargers sharing the same service connection, with configurable per-charger priority or weight to control how available current is distributed between them.

## Design intent

- Each charger has a user-configurable **weight** (or priority percentage) that determines its relative share of the available current pool.
- A charger with a higher weight receives proportionally more current when headroom is constrained.
- When a charger is inactive, capped at its maximum, or stopped (below `min_ev_a`), its unused headroom is redistributed to the remaining active chargers according to their relative weights.
- The algorithm must still respect per-charger min/max limits and the global service current limit.

> ⚠️ The exact mechanism (weight as a ratio, integer priority tier, or percentage) is not yet decided. This plan will be updated before implementation begins.

## Milestones

| PR milestone | Scope | Exit criteria |
|---|---|---|
| PR-1-ph2: Multi-charger data model | Extend config/options flow to support multiple chargers; add per-charger weight/priority field. | Multiple chargers can be configured; each has a stable unique ID and a configurable weight; entity/device links are correct. |
| PR-2-ph2: Weighted current distribution engine | Implement weighted distribution algorithm replacing the single-charger computation; port or replace existing `distribute_current` logic. | Available current is allocated proportionally to charger weights; capped and stopped chargers correctly redistribute surplus; all edge cases covered by unit tests. |
| PR-3-ph2: Runtime charger management | Add options flow for adding/removing chargers and updating weights at runtime without HA restart. | Chargers can be added/removed and weights changed at runtime; entities/device links remain consistent; options-flow integration tests pass. |
| PR-4-ph2: Test stabilization + release | Complete integration tests for multi-charger scenarios; update docs. | CI green, multi-charger configuration documented, release notes updated. |

## Global quality gates

- Add/update unit tests for every behavior introduced in each milestone.
- Keep the CI workflow green on every PR before merge.
- Include a short "how to test" section in each PR description.

## Next steps, timeline, deliverables

| Step | PR | Owner | ETA | Deliverable | Status |
|------|-----|-------|-----|-------------|--------|
| Multi-charger data model | PR-1-ph2 | alexisml | post-MVP | Config/options flow for multiple chargers + weight field | |
| Weighted distribution engine | PR-2-ph2 | alexisml | post-MVP | Weighted current allocation algorithm + unit tests | |
| Runtime charger management | PR-3-ph2 | alexisml | post-MVP | Options flow for add/remove chargers + weight update | |
| Test stabilization + release | PR-4-ph2 | alexisml | post-MVP | Full integration tests, updated docs | |
