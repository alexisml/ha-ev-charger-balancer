Title: Multi-Charger Plan Refinement
Date: 2026-03-10
Author: alexisml
Status: approved
Summary: Documents the design decisions made when refining the Phase 2 multi-charger plan. Replaces the vague "weight/ratio TBD" placeholder with a concrete priority model (0–100, steps of 5), a greedy-with-redistribution distribution algorithm, a well-defined tie-breaking rule, and explicit per-charger vs per-power-meter input/output contracts.

---

## Context

The original multi-charger plan (`02-2026-02-19-multi-charger-plan.md`) left the priority mechanism undecided ("weight as a ratio, integer priority tier, or percentage — not yet decided"). This document captures the decisions made to resolve that open question and align the plan with the actual requirements.

## Decisions made

### 1. Priority field: integer 0–100 in steps of 5

**Decision:** Each charger has a configurable `priority` field — an integer from 0 to 100 in multiples of 5. Default is 50 (neutral).

**Rationale:**
- Steps of 5 give 21 distinct levels, which is expressive enough for real-world use without overwhelming users with micro-distinctions.
- An integer scale is easier to reason about than a floating-point weight ratio (e.g. "priority 80 beats priority 60" is more intuitive than "weight 0.6 vs weight 0.4").
- The 0–100 range is a familiar UX pattern (like volume controls).

### 2. Distribution algorithm: greedy pass with surplus redistribution

**Decision:** The balancer uses a greedy priority-ordered pass rather than proportional allocation.

**Algorithm:**
1. Compute total site headroom from the power meter (same formula as MVP).
2. Sort chargers by priority descending; ties broken by `charger_index` ascending.
3. Allocate `min(remaining_headroom, max_charger_a)` to each charger in order.
4. If allocation < `min_ev_a`, set that charger's allocation to 0 and skip consuming headroom.
5. Pass any remaining headroom to the next charger in priority order.

**Rationale:**
- Greedy priority order matches user mental models: "charger A has priority over charger B" simply means A is filled first.
- Surplus redistribution ensures we always maximise total charging delivered — no headroom is wasted.
- This is simpler to implement and test than a proportional/water-filling approach and avoids the oscillation risk that comes with fractional allocations.

### 3. Tie-breaking: lowest charger_index wins

**Decision:** When two or more chargers share the same priority and there is only enough headroom to bring one of them up to `min_ev_a`, the charger with the lowest `charger_index` (i.e. first configured) receives current. All other same-priority chargers in that tie group are stopped.

**Rationale:**
- Deterministic and predictable — the user controls the outcome by adjusting either priority or configuration order.
- Avoids arbitrary or random outcomes, which would be confusing and hard to debug.

### 4. Maximise charging principle

**Decision:** The algorithm never withholds current from a lower-priority charger when the higher-priority charger is already capped at its `max_charger_a`. Surplus always flows forward.

**Rationale:** The goal is to maximise total energy delivered to vehicles, not to reserve headroom for higher-priority chargers that are already full.

### 5. Input/output contract: per-power-meter vs per-charger

**Decision:** The plan now explicitly distinguishes which inputs/outputs belong to the power meter (shared) vs to each charger (independent).

**Per-power-meter inputs:** `power_meter_entity`, `voltage`, `max_service_current`, `unavailable_behavior`, `unavailable_fallback_current`.

**Per-charger inputs:** `action_set_current`, `action_start_charging`, `action_stop_charging`, `charger_status_entity`, `max_charger_current`, `min_ev_current`, `priority`, `charger_index`.

**Per-charger outputs:** `current_set_a/w`, `available_current_a`, `balancer_state`, `ev_charging`, `last_action_*`, `action_latency_ms`.

**Rationale:** This separation clarifies the data model for PR-1-ph2 (multi-charger data model) and ensures that per-charger entities are linked to per-charger HA devices rather than a single shared device.

## What was not changed

- The single-charger MVP behavior (Phase 1) is unchanged — this refinement only applies to Phase 2.
- The four-milestone structure (PR-1 through PR-4-ph2) is preserved.
- Ramp-up cooldown and idle-clamp behavior remain per-charger, using the same logic as the MVP.

## References

- Updated plan: [`docs/documentation/milestones/02-2026-02-19-multi-charger-plan.md`](../documentation/milestones/02-2026-02-19-multi-charger-plan.md)
- Original plan (pre-refinement): see git history for the file above
- MVP plan: [`docs/documentation/milestones/01-2026-02-19-mvp-plan.md`](../documentation/milestones/01-2026-02-19-mvp-plan.md)
