# Copilot Instructions

## Repository context

This repository contains a custom Home Assistant (HACS) integration for dynamic EV charger load balancing. The integration is under `custom_components/ev_lb/`.

## Rules for the coding agent

### Always read all markdown files first

Before making any changes, **always** read and review all `.md` files in the repository to understand the current project state, plans, and decisions. Key files:

- `README.md` — project overview, status, and quick-start actions
- `docs/development-memories/README.md` — rules for development documentation
- `docs/development-memories/2026-02-19-research-plan.md` — original research and design decisions
- `docs/documentation/milestones/01-2026-02-19-mvp-plan.md` — MVP plan: Phase 1 implementation roadmap and PR milestones
- `docs/documentation/milestones/02-2026-02-19-multi-charger-plan.md` — multi-charger plan: Phase 2 design and milestones (post-MVP)
- `docs/development-memories/2026-02-19-lessons-learned.md` — design decisions and rationale
- `docs/development-memories/2026-02-19-testing-guide.md` — how to test the integration

When new `.md` files are added under `docs/development-memories/` or `docs/documentation/milestones/`, read those as well.

### Development documentation rule

All research plans, design notes, and development artifacts MUST be placed under `docs/development-memories/` with an ISO-date prefix: `docs/development-memories/YYYY-MM-DD-short-name.md`. Milestone documents (e.g. MVP plan) go under `docs/documentation/milestones/` with a numeric prefix.

### Testing

- Run `python -m pytest tests/ -v` to execute all tests.
- Existing pure-logic tests are in `tests/test_load_balancer.py` (39 tests).
- Config flow and integration tests use `pytest-homeassistant-custom-component`.
- All tests must pass before committing changes.

### Integration structure

The integration lives in `custom_components/ev_lb/` and follows the standard Home Assistant custom component layout:
- `manifest.json` — HA/HACS metadata
- `__init__.py` — entry setup/unload
- `config_flow.py` — Config Flow UI
- `const.py` — constants and defaults
- `strings.json` + `translations/` — UI strings (English + Spanish)

### Current limitations and future plans

- **Single charger only:** The integration currently supports exactly one charger. Multi-charger support with per-charger prioritization is planned for Phase 2 (post-MVP) — see [`docs/documentation/milestones/02-2026-02-19-multi-charger-plan.md`](../docs/documentation/milestones/02-2026-02-19-multi-charger-plan.md).
- **Single instance only:** Only one config entry can be created (enforced by `async_set_unique_id`). Multiple instances are not supported.
- **Future multi-charger approach:** Phase 2 will add weighted/prioritized current distribution across chargers. Design is tracked in the multi-charger plan. Do not implement multi-charger logic or remove the single-instance guard without an explicit PR milestone that scopes it.
