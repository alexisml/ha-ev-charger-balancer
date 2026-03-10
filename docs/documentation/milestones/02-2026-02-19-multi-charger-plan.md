Title: Multi-Charger Support Plan
Date: 2026-02-19
Author: alexisml
Status: in-review
Summary: Phase 2 plan for adding multi-charger support with per-charger priority-based current distribution. Refined 2026-03-10 to fix the priority model, input/output contract, and tie-breaking rules.

---

This document covers Phase 2 of the integration — multi-charger support. Phase 2 begins after the MVP (Phase 1) is released and stable. See the MVP plan: [`01-2026-02-19-mvp-plan.md`](01-2026-02-19-mvp-plan.md).

## Goal

Extend the single-charger integration to support N EV chargers sharing the same service connection. Available current is distributed across all configured chargers in **priority order**, always maximising the total current delivered. Each charger is configured independently with its own scripts, limits, and priority.

---

## Inputs and outputs

### Per-power-meter inputs (shared across all chargers on the same meter)

| Input | Description |
|---|---|
| `power_meter_entity` | HA sensor that reports the **total** service power draw in Watts |
| `voltage` | Nominal supply voltage in Volts |
| `max_service_current` | Service breaker / fuse rating in Amps — hard ceiling for the entire site |
| `unavailable_behavior` | What to do when the power meter is unavailable (`stop`, `ignore`, `set_current`) |
| `unavailable_fallback_current` | Fallback current (Amps) used when behavior is `set_current` |

### Per-charger inputs (configured per charger)

| Input | Description |
|---|---|
| `action_set_current` | HA script entity called to command the charger current (receives `current_a` variable) |
| `action_start_charging` | HA script entity called to start a charging session |
| `action_stop_charging` | HA script entity called to stop a charging session |
| `charger_status_entity` | Optional HA sensor that reports the charger state (e.g. `"Charging"`) |
| `max_charger_current` | Per-charger hard ceiling in Amps — the charger will never be commanded above this |
| `min_ev_current` | Minimum usable current in Amps — below this the charger is stopped rather than throttled |
| `priority` | Integer from 0 to 100 (multiples of 5). Higher value = higher preference when headroom is scarce. |
| `charger_index` | Zero-based position order in which the charger was added — used as a tie-breaker |

### Per-charger outputs (computed per cycle, exposed as HA entities)

| Output | Description |
|---|---|
| `current_set_a` | Current most recently commanded to this charger in Amps |
| `current_set_w` | Same, converted to Watts |
| `available_current_a` | Headroom allocated to this charger before charger-limit clamping |
| `balancer_state` | Operational state string: `stopped`, `active`, `adjusting`, `ramp_up_hold`, `disabled` |
| `ev_charging` | Boolean — whether the charger reports that an EV is actively charging |
| `last_action_reason` | Why the last command was issued |
| `last_action_error` | Error message from the most recent failed action script call |
| `last_action_timestamp` | UTC timestamp of the most recent action script call |
| `last_action_status` | `ok` or `error` |
| `action_latency_ms` | Round-trip time for the most recent action call in milliseconds |

---

## Priority model

### Priority field

- Configurable per charger as an integer from **0 to 100**, in **steps of 5**.
- Default: `50` (neutral — equal footing with other default-priority chargers).
- Higher value = higher preference when headroom is scarce.

### Distribution algorithm

The balancer runs once per power-meter update cycle. The algorithm is:

1. **Compute site headroom** — same formula as the single-charger MVP:
   ```
   total_ev_a    = sum of current_set_a for all chargers
   non_ev_a      = max(0, service_current_a − total_ev_a)
   available_a   = max_service_a − non_ev_a
   ```

2. **Sort chargers** by priority descending; ties broken by `charger_index` ascending (lowest index = first configured = highest tie-break preference).

3. **Greedy pass** — iterate chargers in sorted order and allocate current:
   - Give the charger `min(remaining_headroom, max_charger_a)`.
   - If the allocation is below `min_ev_a` for that charger, set its allocation to `0` (stop charging) and do **not** consume headroom.
   - Subtract the granted allocation from `remaining_headroom` before moving to the next charger.

4. **Surplus redistribution** — if a charger was capped at `max_charger_a` and there is still remaining headroom, that headroom flows forward to the next lower-priority charger. This ensures charging is **always maximised** — no headroom is left on the table when another charger can use it.

5. **Ramp-up cooldown and idle clamp** — applied per charger independently, exactly as in the MVP single-charger logic.

### Tie-breaking rule

When two or more chargers share the same priority **and available headroom is insufficient to bring more than one charger up to `min_ev_a`**, only the charger with the **lowest `charger_index`** (i.e. the first charger added during configuration) receives current. All other same-priority chargers are stopped.

### Maximise charging principle

The algorithm never withholds current from a lower-priority charger when the higher-priority charger has already reached its `max_charger_a` cap. Any surplus after satisfying a higher-priority charger is always offered to the next charger in priority order. Headroom is only left unused when no remaining charger can accept even `min_ev_a`.

---

## Milestones

| PR milestone | Scope | Exit criteria |
|---|---|---|
| PR-1-ph2: Multi-charger data model | Extend config/options flow to support N chargers. Each charger gets its own script, limit, and priority fields. | N chargers can be configured; each has a stable unique ID; per-charger entities are linked to per-charger HA devices; options flow supports adding/removing/editing chargers without restart. |
| PR-2-ph2: Priority distribution engine | Implement the priority-based greedy distribution algorithm in `load_balancer.py`. Replace the single-charger `compute_target_current` path in the coordinator with the multi-charger path. | Available current is allocated in priority order; surplus is redistributed; tie-breaking by index is correct; all edge cases covered by unit tests. |
| PR-3-ph2: Runtime charger management | Options flow for adding/removing chargers and updating priority at runtime. | Chargers can be added/removed and priorities changed at runtime; entities/device links remain consistent; options-flow integration tests pass. |
| PR-4-ph2: Test stabilization + release | Full integration tests for multi-charger scenarios; documentation updated. | CI green; multi-charger configuration documented in user manual and how-it-works; release notes updated. |

## Global quality gates

- Add/update unit tests for every behavior introduced in each milestone.
- Keep the CI workflow green on every PR before merge.
- Include a short "how to test" section in each PR description.

## Next steps, timeline, deliverables

| Step | PR | Owner | ETA | Deliverable | Status |
|------|-----|-------|-----|-------------|--------|
| Multi-charger data model | PR-1-ph2 | alexisml | post-MVP | Config/options flow for N chargers + priority field | |
| Priority distribution engine | PR-2-ph2 | alexisml | post-MVP | Priority-based greedy allocation algorithm + unit tests | |
| Runtime charger management | PR-3-ph2 | alexisml | post-MVP | Options flow for add/remove chargers + priority update | |
| Test stabilization + release | PR-4-ph2 | alexisml | post-MVP | Full integration tests, updated docs | |
