Title: Available-current wording update and max-current offset sensor
Date: 2026-05-15
Author: copilot
Status: in-review
Summary: Renamed the available-current sensor label for clarity, added an explicit non-EV-load description, and introduced a new sensor for current offset versus max charger current.

---

## Context

This change set addresses two user-facing observability requests:

1. Clarify that `sensor.*_available_current` is the **available current to charge** and that it is computed from **non-EV load only**.
2. Add a new sensor showing the **offset to max charger current** (`max_charger_current - current_set_a`).

## What changed

- `custom_components/ev_lb/sensor.py`
  - Added `EvLbCurrentOffsetToMaxSensor` with translation key `current_offset_to_max`.
  - Added a description attribute on `EvLbAvailableCurrentSensor`:
    - `"Available current to charge based on non-EV load only."`
- `custom_components/ev_lb/coordinator.py`
  - Added `current_offset_to_max_a` property to expose the computed offset.
- `custom_components/ev_lb/strings.json`
  - Renamed sensor label:
    - `available_current` → `"Available current to charge"`
  - Added sensor label:
    - `current_offset_to_max` → `"Current offset to max charger current"`
- `custom_components/ev_lb/translations/en.json`
  - Same updates as `strings.json`.
- `custom_components/ev_lb/translations/es.json`
  - Updated label:
    - `available_current` → `"Corriente disponible para cargar"`
  - Added label:
    - `current_offset_to_max` → `"Diferencia de corriente respecto al máximo del cargador"`
- Documentation updates:
  - `docs/documentation/02-installation-and-setup.md`
  - `docs/documentation/03-how-it-works.md`
  - `docs/documentation/07-troubleshooting-and-debugging.md`

## Tests updated

- `tests/test_entities.py`
  - Updated total entity count (24 → 25).
  - Added expected unique-id suffix for `current_offset_to_max`.
  - Added sensor behavior tests for initial and updated offset values.
- `tests/test_entity_initialization.py`
  - Updated reload entity count assertion (24 → 25).
- `tests/balancing_engine/test_target_computation.py`
  - Added assertion for available-current description attribute.
  - Added coverage for `current_offset_to_max` sensor value updates.

## Notes

- No balancing algorithm behavior was changed; this is observability/UI clarification plus one new derived sensor.
- The new offset value is clamped at `0` as a defensive measure.

## Follow-up review fixes

After PR review, two compatibility clarifications were added:

- Overrode the `suggested_object_id` property on both sensors to keep default entity IDs stable and aligned with docs:
  - `available_current`
  - `current_offset_to_max`
- Updated `how-it-works.md` to clarify the healthy-meter guarantee:
  - During normal meter operation, charging current is `<= available_current`.
  - In meter-unavailable `set_current` fallback mode, charging can be positive while `available_current` remains `0 A`.
