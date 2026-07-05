# Milestones: typsphinx

A historical record of shipped versions. Full detail per milestone lives in `.planning/milestones/`.

---

## v0.4.4 — CI-repair + modernize

**Shipped:** 2026-07-05
**Closeout:** verified_closeout (pre-close artifact audit clear; all 5 phases verified)
**Phases:** 5 (1–5) · **Plans:** 15 · **Tasks:** ~35
**Requirements:** 23/23 v1 requirements complete · **Known gaps:** none
**Git:** milestone work merged to `main` via PRs #104 / #105 / #106; close + release-prep via #109; tagged `v0.4.4` (on `main` dae500a)
**Released:** PyPI `typsphinx 0.4.4` (wheel + sdist) + GitHub Release, via release run 28731646924 (green end-to-end)
**Code delta (milestone scope):** ~15 source/config files, +217 / −1202 lines (net, incl. `uv.lock` collapse)

> **Release note:** The first `v0.4.4` tag push failed at the `release.yml` Validate gate — the
> version-verify step imported stdlib-only `tomllib` on the 3.10 floor (a PYVER-02 side effect
> only exercised at tag time). Fixed with a `tomllib`/`tomli` fallback (PR #110), tag re-pointed,
> release re-run green. This also resolved D-11 (`softprops/action-gh-release@v3` ran green).

**Delivered:** Restored a fully green CI pipeline on `main` — lint, the 3-OS × Python 3.10–3.13 test matrix (19 jobs), coverage, and the docs PDF build — by pinning the runtime dependency graph back to a known-good, reproducible combination, then modernized the Python floor and dev tooling and installed durability guardrails so the drift can't silently recur.

**Key accomplishments:**

1. **Root-cause pin (Phase 1):** Pinned `typst>=0.14.1,<0.15` (with precautionary `sphinx<9` / `docutils<0.22` ceilings), regenerated `uv.lock`, mirrored tox ceilings, and removed the dead `sphinx-testing` dep — fixing the `typst.TypstError: unknown variable: kai` break from a bundled `@preview` package under typst 0.15.
2. **Verified green baseline (Phase 2):** Confirmed every previously-red CI job green across the full matrix (incl. the 7 PDF-integration tests and `docs.yml` multi-language PDF-copy), and guarded the 3-way `@preview` version sync with an automated desync test.
3. **Modernized Python floor (Phase 3):** Bumped the supported range to 3.10–3.13 across every config surface (pyproject, tox, CI/docs/release workflows, black/ruff/mypy target-versions) as one atomic, CI-verified batch.
4. **Refreshed dev tooling (Phase 4):** Conservative floor+ceiling bumps for pytest/mypy/black/ruff/tox; artifact actions to node24 ahead of GitHub's 2026-09-16 Node-20 removal; removed the stale `Test Python 3.9` required check.
5. **Durability guardrails (Phase 5):** `uv sync --locked` at all 9 sites (DUR-01), a standalone weekly + dispatch `drift.yml` forward-drift detector with deduplicated issue reporting (DUR-02), a scoped `sphinx-typst-stack` Dependabot group (DUR-03), and a README CI status badge (DUR-04).

**Deferred:** D-11 (`softprops/action-gh-release@v3` tag-gated runtime confirmation) — signed off to the next real release tag (this v0.4.4 release exercises it). v2 forward-ecosystem support (FWD-01/02/03: Sphinx 9, typst 0.15+, configurable `@preview` versions) remains out of scope.

**Archives:** `milestones/v0.4.4-ROADMAP.md`, `milestones/v0.4.4-REQUIREMENTS.md`

---
