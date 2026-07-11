# Milestones: typsphinx

A historical record of shipped versions. Full detail per milestone lives in `.planning/milestones/`.

---

## v0.5.0 — forward-ecosystem

**Shipped:** 2026-07-11
**Closeout:** verified_closeout (pre-close artifact audit clear; all 6 phases verified; milestone audit passed — 14/14 requirements, 5/5 integration seams, E2E release flow ready)
**Phases:** 6 (6–10 + 8.1) · **Plans:** 13 · **Tasks:** 29
**Requirements:** 14/14 v1 requirements complete · **Known gaps:** none
**Git:** milestone work on `release/v0.5.0`, merged to `main` via PR #112; tagged `v0.5.0` (on `main`)
**Released:** PyPI `typsphinx 0.5.0` (wheel + sdist) + GitHub Release, via `release.yml` (green end-to-end)
**Code delta (milestone scope, excl. `.planning/`):** 29 source/config files, +1025 / −467 lines

**Delivered:** Ported typsphinx forward from the v0.4.4 known-good pins to the current ecosystem — Sphinx 9.1, docutils 0.22, typst 0.15, Python 3.12–3.13 — bumping the four bundled `@preview` packages in lockstep to compile cleanly (empirically closing the `unknown variable: kai` break), modernizing the soft-deprecated docutils/Sphinx API surface, fixing a long-latent admonition markup/code-mode render bug (discovered once `docs-pdf` first compiled post-`kai`-fix), adding a `typst compile` smoke gate that guards all four packages, and releasing v0.5.0 to PyPI with the full 3-OS × Python 3.12–3.13 CI matrix observed green. Latest-only, no compatibility range.

**Key accomplishments:**

1. **Raised runtime pins + Python floor (Phase 6):** Re-pinned `sphinx>=9.1,<10` / `docutils>=0.21,<0.23` and raised the Python floor to 3.12–3.13 across all 21 declaration sites (pyproject `requires-python`/classifiers, regenerated `uv.lock`, `tox.ini`, and the four GitHub Actions workflows) as one atomic pin-raise — both builders confirmed registering and a live `-b typst` build passing under Sphinx 9.1.
2. **Bumped `@preview` packages + typst 0.15 — the `kai` fix (Phase 7):** Raised `typst>=0.15.0,<0.16` and bumped mitex `0.2.4`→`0.2.7` (the actual fix, mitex PR #201), gentle-clues `1.2.0`→`1.3.1`, codly-languages `0.1.1`→`0.1.10` (codly `1.3.0` unchanged, registry ceiling), in lockstep across the 3-way version-sync — empirically closing the `unknown variable: kai` compile break via a real `tox -e docs-pdf` run producing a clean 101-page PDF.
3. **API & test compatibility (Phase 8):** Landed `traverse()`→`findall()` and modernized all soft-deprecated docutils/Sphinx call sites (`OptionParser`→`get_default_settings`, `builder.app`→`_app`, `writer_name`→`writer=get_writer_class(...)()`), then installed a permanent pytest `filterwarnings` guard escalating both `DeprecationWarning` and `PendingDeprecationWarning` — full suite green, zero `traverse()` remaining.
4. **Admonition rendering fix (Phase 8.1, inserted):** Rewrote `_visit_admonition`/`_depart_admonition` to emit gentle-clues code-mode content-blocks (`info({...})`) instead of markup-mode brackets (`info[...]`), preserved inline-markup titles via a buffer-swap (also fixing a latent title double-emission bug), added the five previously-unimplemented types (`hint`/`error`/`danger`/`attention`/generic `.. admonition::`), and proved it with a real `sphinx-build → typst.compile() → pypdf` PDF-text-extraction acceptance gate.
5. **Green CI matrix + smoke gate + guardrails (Phase 9):** Observed all 13 CI jobs green for the first time on Sphinx 9.1/docutils 0.22/typst 0.15 across all 3 OS runners (PR #112); added a `typst compile` smoke gate (`tests/test_preview_smoke_gate.py`) exercising all four `@preview` packages via real calls — closing the coverage gap the historical `kai` regression slipped through, proven with a negative control; reconciled stale `main` branch-protection required-checks; confirmed the dependency-ceiling guardrails (`sphinx<10`/`typst<0.16`/`docutils<0.23`).
6. **Version single-source + v0.5.0 release (Phase 10 + milestone close):** `typsphinx.__version__` now derives from `importlib.metadata` (retiring the stale `0.4.3`) with `pyproject.toml` the sole `0.5.0` literal, `uv.lock` regenerated, plus an independent `tomllib` drift-guard test; curated `CHANGELOG.md` `## [0.5.0]` entry as the Release-body source; publish half (merge PR #112 → tag `v0.5.0` → `release.yml` → PyPI + GitHub Release) executed at milestone close, mirroring the v0.4.4 precedent.

**Deferred:** CFG-01 (was FWD-03 — user-configurable `@preview` versions) and XOS-01 (cross-OS docs-PDF CI on macOS/Windows) → v2. Phase 8's multi-`<term>` definition-list hardening deferred as forward-looking (no current docutils 0.22.4 rST syntax emits a multi-`<term>` node).

**Archives:** `milestones/v0.5.0-ROADMAP.md`, `milestones/v0.5.0-REQUIREMENTS.md`, `milestones/v0.5.0-MILESTONE-AUDIT.md`

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
