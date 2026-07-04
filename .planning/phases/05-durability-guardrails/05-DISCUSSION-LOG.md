# Phase 5: Durability Guardrails - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-05
**Phase:** 5-durability-guardrails
**Areas discussed:** Lockfile verification (DUR-01), Weekly drift detection (DUR-02), Dependabot grouping (DUR-03), Additional hardening scope

---

## Lockfile verification method & scope (DUR-01)

| Option | Description | Selected |
|--------|-------------|----------|
| Add `--locked` to all `uv sync` sites | ci/docs/release all 9 sites; no extra job; every job enforces lock integrity; matches uv.lock-single-source-of-truth | ✓ |
| Dedicated `uv lock --check` gate job | Clear separation but +1 job; other jobs stay unguarded | |
| ci.yml only | Minimal change; leaves release/docs re-resolution path uncovered | |

**User's choice:** Add `--locked` to all `uv sync` sites (recommended)
**Notes:** Enforcing lock integrity across every workflow is milestone-consistent; closes the release/docs re-resolution gap with zero extra jobs.

---

## Weekly drift-detection job shape & reporting (DUR-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Standalone `drift.yml` + auto-file Issue | Weekly schedule; `uv lock --upgrade` + test/build; auto-files/updates a dedup'd GitHub Issue on breakage; non-blocking | ✓ |
| Standalone `drift.yml` + red-X only | Same resolve, failure is only a red X on Actions — easy to miss | |
| `schedule:` added to ci.yml | No new file but bloats ci.yml; mixes per-PR and scheduled concerns | |

**User's choice:** Standalone `drift.yml` + auto-file Issue (recommended)
**Notes:** "Early reporting" needs a visible, persistent signal; single-issue-update pattern avoids weekly duplicate-issue spam. Must stay out of `main` required checks.

---

## Dependabot grouping granularity (DUR-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated sphinx/docutils/typst group | Append `groups:` to existing pip ecosystem; one PR for the 3; verbatim DUR-03 | ✓ |
| Whole-runtime single group | Fewer PRs but too broad; loses per-cluster review; obscures kai-cluster intent | |
| Group both dev + runtime separately | More comprehensive but exceeds DUR-03's required scope | |

**User's choice:** Dedicated sphinx/docutils/typst group (recommended)
**Notes:** Exactly DUR-03 — one grouped PR prevents a lone `typst` bump from reintroducing the `kai` break.

---

## Additional hardening scope

| Option | Description | Selected |
|--------|-------------|----------|
| softprops@v2→v3 only | node20 removed from hosted runners 2026-09-16 (dated risk); Phase-4 tracked carry-over; SHA-pin deferred | ✓ |
| softprops + SHA-pinning both | Full supply-chain hardening but rewrites every action + hash-maintenance burden; inflates maintenance scope | |
| Defer both | Phase 5 = DUR-01..04 only; leaves the Sep-2026 node20 deadline unaddressed | |

**User's choice:** softprops@v2→v3 only (recommended)
**Notes:** The node20 straggler is a dated hosted-runner-compat risk explicitly carried into Phase 5 by Phase 4. SHA-pinning is a new category, deferred to a future milestone.

---

## Claude's Discretion

- DUR-04 CI status badge (single CI-workflow badge in the existing README badge row) — pre-decided as clear-cut; user did not need to weigh in.
- Exact Issue-dedup mechanism/action for DUR-02.
- Exact Dependabot `patterns` glob strings and group name.
- Badge markdown placement within the badge row.
- Whether `drift.yml` also runs the docs-pdf build vs a cheaper test subset.

## Deferred Ideas

- SHA-pin GitHub Actions to commit hashes (supply-chain hardening) → future milestone (new category, high maintenance surface, outside DUR-01..04).
- Broader Dependabot grouping (dev tools / whole runtime) → not needed; DUR-03 scoped to the risk cluster.
