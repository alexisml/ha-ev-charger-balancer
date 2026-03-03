# Watt-O-Balancer — User Documentation

Welcome to the documentation for the **Watt-O-Balancer** integration for Home Assistant.

This integration dynamically adjusts your EV charger's charging current based on real-time household power consumption, ensuring you never exceed your electrical service limit.

---

## Documentation sections

| # | Guide | Description |
|---|---|---|
| 01 | [**Installation & Setup**](01-installation-and-setup.md) | How to install the integration, configure it step-by-step, and get your first charger running. |
| 02 | [**How It Works**](02-how-it-works.md) | What the integration does, what to expect, what NOT to expect, entities reference, and the balancing algorithm in detail. |
| 03 | [**Multi-Charger Load Balancing**](03-multi-charger-guide.md) | Running 1–N chargers on one circuit with weighted priority distribution, worked examples, and runtime priority adjustment. |
| 04 | [**Action Scripts Guide**](04-action-scripts-guide.md) | Full reference for configuring charger action scripts (set current, stop, start) with examples for OCPP, REST, Modbus, and switch-based chargers. |
| 05 | [**Event Notifications Guide**](05-event-notifications-guide.md) | All event types, payloads, persistent notifications, and automation examples for mobile alerts. |
| 06 | [**Logging Guide**](06-logging-guide.md) | Debug log setup, log level policy, example output, and the logging wrapper architecture. |
| 07 | [**Troubleshooting & Debugging**](07-troubleshooting-and-debugging.md) | Common problems and their solutions, how to read logs, diagnostic sensors, and how to report issues. |
| 08 | [**Development Guide**](08-development-guide.md) | Architecture overview, running CI checks locally, contributing guidelines, and project roadmap. |

## Quick reference

| Guide | Description |
|---|---|
| [Starter Script Templates](../examples/) | Ready-to-use YAML templates — copy, adjust, and use. |

---

## Quick links

- [GitHub repository](https://github.com/alexisml/ha-ev-charger-balancer)
- [Issue tracker](https://github.com/alexisml/ha-ev-charger-balancer/issues)
- [MVP roadmap](milestones/01-2026-02-19-mvp-plan.md)
- [Multi-charger plan (Phase 2)](milestones/02-2026-02-19-multi-charger-plan.md)
