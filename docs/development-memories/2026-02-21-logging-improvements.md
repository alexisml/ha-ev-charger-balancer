# Logging Improvements

- **Date:** 2026-02-21
- **Author:** Copilot
- **Status:** Complete
- **Summary:** Structured logging across the integration to support runtime debugging without overloading Home Assistant logs.

## Problem

The integration had only 8 log calls, all in `coordinator.py` (3 debug, 1 info, 4 warning). There was no logging in `__init__.py` or `config_flow.py`, and the computation pipeline was invisible at debug level. The "ignore" unavailable mode logged at info on every meter event, which was too chatty for production use.

## Design Decisions

### Log level policy

| Level   | Purpose                                        | Cadence           |
|---------|------------------------------------------------|-------------------|
| DEBUG   | Full computation pipeline, state transitions, skips, cooldown holds | Every meter event |
| INFO    | Charging started / stopped transitions only    | Rare (state flip) |
| WARNING | Real problems: unparseable values, action failures, unavailable meter in stop/fallback modes | Occasional faults |

### Key changes

1. **coordinator.py — `_recompute`**: Added a single debug log that emits the full pipeline values (`house_power`, `available`, `raw_target`, `clamped`, `final`) plus the `reason` on every recompute. This is the most valuable log for runtime debugging.

2. **coordinator.py — ramp-up cooldown**: Added a debug log when the cooldown holds the current at the previous value instead of allowing an increase.

3. **coordinator.py — `_resolve_fallback`**: Demoted the "ignore" mode log from `info` to `debug`. In ignore mode, this fires on every unavailable meter event and was unnecessarily noisy.

4. **coordinator.py — `_update_and_notify`**: Added info-level logs for charging start/stop transitions only. These are the only info logs in the coordinator — they fire only on state flips (active ↔ stopped), keeping the info-level log cadence very low.

5. **coordinator.py — `manual_set_limit`**: Added debug log with requested and clamped values.

6. **coordinator.py — `_handle_power_change` and `async_recompute_from_current_state`**: Added debug logs for disabled-balancer skips and parameter-change recomputes.

7. **__init__.py**: Added debug logs for entry setup/unload and service calls.

8. **config_flow.py**: Added debug logs for config flow validation and entry creation.

### Principle: avoid log overload

- **No info logs on steady-state meter events.** The debug-level `_recompute` log covers this.
- **No info logs for "ignore" unavailable mode.** This was the main noise source; demoted to debug.
- **Info only on state transitions.** Charging start/stop are the only user-visible events worth info-level logging.
- **Warnings only for actionable problems.** Unparseable values, failed actions, and unavailable meter in stop/fallback modes are the only warning triggers.

## Tests

12 new tests in `tests/test_logging.py` covering:
- Debug logs for recompute pipeline, ramp-up holds, disabled skips, manual overrides
- Info logs only for start/stop transitions (and NOT during steady state)
- Warning logs for unparseable values, unavailable stop/fallback modes
- Ignore mode logs at debug (NOT warning)
