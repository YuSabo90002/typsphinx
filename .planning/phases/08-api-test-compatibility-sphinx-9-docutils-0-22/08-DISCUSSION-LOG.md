# Phase 8: API & Test Compatibility (Sphinx 9 / docutils 0.22) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-11
**Phase:** 8-api-test-compatibility-sphinx-9-docutils-0-22
**Areas discussed:** admonition-bug handling, deprecated-API sweep breadth, deprecation-warning strictness

---

## Gray-area selection

Presented four phase-specific gray areas (multi-select). Locked/mechanical items (traverse()→findall()
swap, full-suite green, black/ruff/mypy clean) excluded from discussion per ROADMAP/REQUIREMENTS.

| Area | Selected |
|------|----------|
| admonition bug handling | ✓ |
| test-failure fix bias | (not selected → routed to Claude's Discretion) |
| deprecated-API sweep breadth | ✓ |
| deprecation-warning strictness | ✓ |

---

## admonition-bug handling

| Option | Description | Selected |
|--------|-------------|----------|
| Fix in Phase 8 now | translator.py is touched by Phase 8; avoid shipping v0.5.0 with literal-source admonitions | |
| Defer to a dedicated follow-up phase (within v0.5.0) | Keep Phase 8 crisply API-focused; fix admonition as its own phase | ✓ |
| Defer to backlog (v0.5.1+) | Prioritize release; leave as tech-debt | |

**User's choice:** Defer to a dedicated follow-up phase — fix within v0.5.0, but NOT folded into Phase 8.
**Notes:** The admonition bug is a rendering bug (markup/code-mode mismatch), orthogonal to the
Sphinx-9/docutils-0.22 API compat that defines Phase 8. Keeping them separate preserves a clean phase
boundary. CONTEXT `<deferred>` records the action: add the phase via `/gsd-phase`, recommended before
Phase 9 so the CI-green run + release ship the fixed rendering.

---

## deprecated-API sweep breadth

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal / reactive | Only the known traverse() + whatever the suite actually surfaces | |
| Mid: light grep audit | Grep obvious deprecated patterns beyond traverse(), no full audit | |
| Thorough audit | Proactively enumerate & modernize ALL soft-deprecated docutils/Sphinx API | ✓ |

**User's choice:** Thorough audit — expands Phase 8 beyond API-01's single call to a full soft-deprecation sweep.
**Notes:** Prior Sphinx-9 changelog audit found no load-bearing breaks; this converts that into a
clean-posture proactive sweep to reduce future forward-port (Sphinx 10 / docutils 0.23+) debt. Captured
as D-01.

---

## deprecation-warning strictness

| Option | Description | Selected |
|--------|-------------|----------|
| Lightweight | Verify zero own-code deprecation warnings by hand; no permanent gate | |
| Permanent guard | Add filterwarnings=error::DeprecationWarning to pytest config; ignore-list third-party | ✓ |

**User's choice:** Permanent guard.
**Notes:** Structurally enforces the D-01 thorough sweep — any future DeprecationWarning fails the suite.
Third-party (Sphinx/docutils/typst-py) unfixable warnings excluded via targeted module-scoped
`ignore::DeprecationWarning:<module>` entries, determined empirically from the first suite run. Captured
as D-02.

## Claude's Discretion

- **Test-failure fix bias** (area surfaced but not selected): default locked in CONTEXT — prefer fixing
  source to preserve existing `.typ` output over loosening test assertions, UNLESS the red reflects a
  genuine docutils 0.22 output/structure change (then adapt translator + update fixture to the new
  correct output).
- **docutils 0.22 multi-`<term>` edge case** — implementation-level; planner/researcher verify the
  single-term buffering in `translator.py` against the resolved docutils 0.22 node shape.
- **Sweep mechanics** — how to enumerate deprecated calls (changelog cross-ref + grep + running the
  suite under the new guard) and the exact findall replacement form.

## Deferred Ideas

- **Admonition rendering bug** → dedicated follow-up phase within v0.5.0 (see CONTEXT `<deferred>` +
  `07-.../deferred-items.md`). Add via `/gsd-phase`, recommended before Phase 9.
- **CFG-01** (configurable `@preview` versions), **XOS-01** (cross-OS docs-PDF CI) — already tracked in
  REQUIREMENTS.md v2; not this milestone.
