Title: PR-8 — Add Ruff linting, dependency review, and Gitleaks secret scanning CI
Date: 2026-02-21
Author: copilot
Status: merged
Summary: Documents why Ruff, dependency-review, and Gitleaks were chosen, configuration decisions, and lessons learned.

---

## Context

The repository had unit tests, CodeQL security scanning, Pyright type checking, and codespell spell checking, but no fast Python style/lint gate, no check for vulnerable dependencies introduced via PRs, and no secret-scanning to catch accidentally committed credentials. This PR adds all three.

## What changed

- **`.github/workflows/ruff.yml`** (new): Runs `ruff check .` on every push and pull request to `main`.
- **`.github/workflows/dependency-review.yml`** (new): Runs GitHub's dependency review action on every PR to `main` to block the introduction of known-vulnerable dependencies.
- **`.github/workflows/gitleaks.yml`** (new): Runs Gitleaks on every push and PR to `main` to detect accidentally committed secrets.
- **`.gitleaks.toml`** (new): Extends the default Gitleaks ruleset; allowlists lock files; documents per-line (`# gitleaks:allow`) and per-path suppression of false positives.
- **`pyproject.toml`**: Added `[tool.ruff]` and `[tool.ruff.lint]` sections (E/F/W rules, 120-char line length, Python 3.12 target).
- **`custom_components/ev_lb/coordinator.py`**: Removed unused import `UNAVAILABLE_BEHAVIOR_STOP` (pre-existing Ruff F401 violation).
- **`tests/test_load_balancer.py`**: Removed unused `import pytest` (pre-existing Ruff F401 violation); wrapped an overlong docstring line (pre-existing Ruff E501 violation).
- **`README.md`**: Added Ruff and Gitleaks CI badges; added local-run instructions for all three new checks.

## Design decisions

### 1. Ruff over flake8/pylint

Ruff is 10–100× faster than flake8 or pylint, written in Rust, and has zero transitive Python dependencies. It reads the same `pyproject.toml` that already contained the codespell config, keeping all tool config co-located. The E/F/W rule set was chosen as the minimal, widely-accepted baseline (PEP 8 style + pyflakes unused-import/undefined-name checks) without introducing opinionated rules that would require significant code changes.

### 2. Ruff not pinned in the initial version

Ruff follows semver and does not add new lint rules in patch versions. The `pip install ruff` step was kept unpinned intentionally to keep the workflow simple; a pinned version (similar to how Pyright is pinned) should be introduced in a follow-up maintenance commit once the project stabilises on a specific Ruff version.

### 3. `ruff format --check` not enabled

Running `ruff format --check` would have required reformatting 14 source files, which is a separate concern from linting. Format enforcement was intentionally deferred so that this PR remains focused on CI infrastructure rather than large-scale code reformatting.

### 4. Line length set to 120

The existing codebase had several lines (in particular multi-line docstrings) that exceeded the default 88-character Ruff line length. 120 was chosen as a pragmatic compromise that requires only the egregiously long lines to be wrapped without forcing a wholesale reformatting pass.

### 5. Dependency Review uses `actions/dependency-review-action@v4`

This is GitHub's official action, free for public repositories, and requires no configuration for basic use. It blocks PRs that introduce dependencies with known CVEs by comparing the dependency snapshot before and after the PR. It runs on `pull_request` only (not push) because it needs two snapshots to diff.

### 6. Gitleaks uses `gitleaks/gitleaks-action@v2` with `fetch-depth: 0`

Full history fetch (`fetch-depth: 0`) is required so that Gitleaks can scan all commits in a push, not just the tip. Without it, commits added before the current HEAD would not be scanned and a developer could sneak a secret in an early commit and then remove it in a later one. The `GITHUB_TOKEN` env var is passed so the action can post annotations on PRs.

### 7. `.gitleaks.toml` with `useDefault = true`

Extending the default ruleset rather than defining rules from scratch ensures Gitleaks stays current with the community's evolving secret patterns. The allowlist covers only lock files (`go.sum`, `package-lock.json`) which may contain opaque binary-safe strings that trigger false positives; no application paths are suppressed.

## Lessons learned

- Pre-existing lint violations must be fixed before adding a new lint gate, or the new CI check fails immediately on merge. Always run the new tool locally against the codebase before adding it to CI.
- The `isort` (`I`) Ruff rule category triggers import-order violations across almost every file in this project (imports are grouped by convention but not sorted within groups). It is better to add `I` rules as a separate targeted PR with an accompanying `ruff check --fix` pass rather than bundling it with the initial lint gate.
- Ruff's `E501` line-length check applies to docstrings as well as code; wrapping a docstring is preferable to raising the line limit.

## What's next

- Pin Ruff to a specific version in `ruff.yml` once the project settles on a version (similar to how Pyright is pinned in `type-check.yml`).
- Consider enabling `ruff format --check` in a dedicated formatting PR that applies `ruff format` to the whole codebase in one commit.
- Consider enabling the `I` (isort) rule category after a one-shot `ruff check --fix --select I` pass to fix all import ordering issues.
- Bump `actions/dependency-review-action` and `gitleaks/gitleaks-action` versions via Dependabot (already configured in `.github/dependabot.yml`).
