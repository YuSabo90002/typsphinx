# Phase 9: Green CI Matrix + Smoke Test + Guardrails - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-11
**Phase:** 9-green-ci-matrix-smoke-test-guardrails
**Areas discussed:** CI-01 observed green-run method

---

## Gray areas presented (user selected which to discuss)

| Gray area | Selected for discussion |
|-----------|-------------------------|
| Smoke test form & placement (CI-02) | |
| Smoke test coverage scope (CI-02) | |
| CI-03 concrete scope | |
| Observed green-run method (CI-01) | ✓ |

Only the CI-01 observation method was chosen; CI-02/CI-03 left to Claude's discretion (defaults approved by user, see below).

---

## CI-01 — Observed green-run method

The user pushed back on the initial framing twice, clarifying the operating model rather than picking a pre-set option. Key exchange:

- Q: How to observe an all-green run when ci.yml/docs.yml don't fire on `release/v0.5.0`?
- User: reasoned that at milestone completion → push release branch → open PR → **PR checks run** → therefore observation happens on the PR. (Correct.)
- Claude confirmed: PR to main is the one path firing both ci.yml + docs.yml on release-branch content; PR checks run pre-merge (safety gate) vs. the post-merge push run; branch protection requires them green anyway.
- Claude flagged an over-complication it had introduced (early "draft PR") as unnecessary; retracted.

| Option | Description | Selected |
|--------|-------------|----------|
| (a) Open PR at end of Phase 9, observe green → close CI-01 in Phase 9; Phase 10 adds version-bump commit to same PR then merges | CI-01 closed within its own phase | ✓ |
| (b) Do Phase 9 work on branch; open PR + observe only at start of Phase 10, then merge/release in one go | Observation slips to Phase 10 boundary | |

**User's choice:** (a)
**Notes:** No workflow trigger change (no `release/**`, no `docs.yml workflow_dispatch`). Merge/version-fix/release all deferred to Phase 10 on the same PR.

---

## Claude's Discretion (areas not selected, defaults approved by user)

- **CI-02 (smoke test):** Default approved — the smoke fixture must exercise **all four** `@preview` packages (codly, codly-languages, mitex, gentle-clues), because the existing `test_pdf_render_gate.py` fixture only touches admonitions/gentle-clues and would miss a mitex `kai` regression (mitex was the actual `kai` culprit). Form/placement left to researcher/planner.
- **CI-03 (guardrail ceilings):** Default approved — treat as primarily verification; pyproject ceilings already reflect the new majors (set in Phases 6/7), drift.yml hardcodes no ceilings, Dependabot group has no version constraints. Researcher confirms whether any concrete change is truly required.

## Deferred Ideas

- XOS-01 cross-OS docs-PDF CI (macOS/Windows) — deferred to v2.
- FWD-03 → CFG-01 user-configurable `@preview` versions — deferred to v2.
- Making `drift.yml` a required check — kept advisory-only.
