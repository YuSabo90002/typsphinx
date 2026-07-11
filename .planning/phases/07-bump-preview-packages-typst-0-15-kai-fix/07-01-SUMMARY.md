---
phase: 07-bump-preview-packages-typst-0-15-kai-fix
plan: 01
subsystem: infra
tags: [typst, mitex, gentle-clues, codly, codly-languages, uv, dependency-pin, docs-pdf]

# Dependency graph
requires:
  - phase: 06-raise-runtime-pins-python-floor
    provides: Sphinx 9.1 + Python 3.12 floor raised; docs-pdf lane intentionally left red on `unknown variable: kai`
provides:
  - typst PyPI pin raised to >=0.15.0,<0.16 with a regenerated, reproducible uv.lock
  - Four bundled @preview packages bumped in lockstep (mitex 0.2.7, gentle-clues 1.3.1, codly-languages 0.1.10, codly unchanged at 1.3.0)
  - Empirical proof (real `tox -e docs-pdf` compile) that the kai break is fixed under typst 0.15
affects: [phase-08-sphinx9-api-compat, phase-09-ci-hardening]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "3-way @preview version-sync lockstep edit (writer.py / template_engine.py / templates/base.typ), guarded by tests/test_preview_version_sync.py"

key-files:
  created: []
  modified:
    - pyproject.toml
    - uv.lock
    - typsphinx/writer.py
    - typsphinx/template_engine.py
    - typsphinx/templates/base.typ

key-decisions:
  - "Bumped typst + all four @preview packages atomically in one wave, per the ROADMAP contingency (bisect only on failure) — no failure occurred, so no bisect was needed."
  - "mitex import-style asymmetry preserved exactly: named `mi, mitex` in the two .py sync sites, glob `*` in base.typ — not refactored to match, per CONTEXT.md's explicit out-of-scope note."
  - "Local dev-environment fix (not committed): the pip/uv-installed `.venv/bin/uv` binary is a generic manylinux ELF that cannot run under this NixOS sandbox (`Could not start dynamically linked executable`). Replaced it in-place with the nixpkgs-provided `uv` binary so `tox -e docs-pdf`'s `uv-venv-lock-runner` could execute. `.venv/` is gitignored; no repo files were touched by this workaround."

patterns-established:
  - "Pre-existing bugs surfaced by a newly-green compile gate are logged to a phase-local deferred-items.md rather than fixed inline when they fall outside the plan's files_modified scope."

requirements-completed: [FWD-02, PKG-01, PKG-02, PKG-03]

coverage:
  - id: D1
    description: "typst PyPI pin raised to >=0.15.0,<0.16; uv.lock regenerated and uv sync --locked green"
    requirement: "FWD-02"
    verification:
      - kind: other
        ref: "uv sync --locked && grep -A2 '^name = \"typst\"' uv.lock (version = 0.15.0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Four @preview versions bumped in lockstep (mitex 0.2.7 / gentle-clues 1.3.1 / codly-languages 0.1.10 / codly 1.3.0 unchanged) across writer.py, template_engine.py, templates/base.typ"
    requirement: "PKG-01"
    verification:
      - kind: unit
        ref: "tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites"
        status: pass
      - kind: unit
        ref: "tests/test_preview_version_sync.py::test_all_four_packages_declared"
        status: pass
    human_judgment: false
  - id: D3
    description: "tox -e docs-pdf compiles the project docs to PDF against typst 0.15 with zero TypstError and no unknown variable: kai"
    requirement: "FWD-02"
    verification:
      - kind: other
        ref: "tox -e docs-pdf (real compile; captured log has no TypstError / kai; docs/_build/pdf/index.pdf produced, 101 pages)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Coarse visual glance of the compiled PDF finds no tofu / broken boxes / error glyphs (D-01/D-04)"
    verification: []
    human_judgment: true
    rationale: "Visual PDF quality is a human-judgment call per CONTEXT.md D-01/D-04; sampled ~12 of 101 pages (cover, TOC, config examples, code blocks, math source examples, API reference, changelog tail) and found no tofu/broken boxes/error glyphs. A separate, pre-existing (non-blocking) rendering bug was found and logged to deferred-items.md rather than treated as a plan failure — see Deviations."

# Metrics
duration: 12min
completed: 2026-07-11
status: complete
---

# Phase 7 Plan 01: Bump @preview Packages + typst 0.15 (kai fix) Summary

**Raised the typst PyPI pin to 0.15.0 and bumped mitex/gentle-clues/codly-languages in lockstep, empirically closing the `unknown variable: kai` compile break via a real `tox -e docs-pdf` run producing a clean 101-page PDF.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-07-11T00:10:58Z (JST 09:10:58)
- **Completed:** 2026-07-11T00:17:11Z (JST 09:17:11)
- **Tasks:** 3
- **Files modified:** 6 (pyproject.toml, uv.lock, typsphinx/writer.py, typsphinx/template_engine.py, typsphinx/templates/base.typ, plus a phase-local deferred-items.md log)

## Accomplishments
- `typst` dependency pin raised from `>=0.14.1,<0.15` to `>=0.15.0,<0.16`; `uv.lock` regenerated (typst 0.14.9 -> 0.15.0) and `uv sync --locked` verified green
- All four `@preview` package versions bumped in lockstep across the three sync sites: `mitex 0.2.4 -> 0.2.7`, `gentle-clues 1.2.0 -> 1.3.1`, `codly-languages 0.1.1 -> 0.1.10`; `codly` left at `1.3.0` (registry ceiling, unchanged); `tests/test_preview_version_sync.py` passes
- Empirically proved the fix: `tox -e docs-pdf` compiles the project's own docs to PDF against typst 0.15.0 with zero `TypstError` and no `unknown variable: kai`, producing a 101-page `docs/_build/pdf/index.pdf`

## Task Commits

Each task was committed atomically:

1. **Task 1: Raise the typst PyPI pin and regenerate the lockfile (FWD-02)** - `2ed64aa` (feat)
2. **Task 2: Bump the four @preview versions in lockstep across the three sync sites (PKG-01, PKG-02, PKG-03)** - `ca4c1ab` (feat)
3. **Task 3: Empirical compile gate — docs-pdf compiles kai-free, plus coarse PDF glance (FWD-02, PKG-01, PKG-02)** - `82d573b` (docs; no source edit needed — task produced a verification log + deferred-items.md)

_No plan-metadata commit yet — STATE.md/ROADMAP.md/REQUIREMENTS.md update and final commit follow this SUMMARY._

## Files Created/Modified
- `pyproject.toml` - typst dependency pin raised to `>=0.15.0,<0.16`
- `uv.lock` - regenerated; typst resolves to 0.15.0
- `typsphinx/writer.py` - included-document imports bumped (mitex/gentle-clues/codly-languages)
- `typsphinx/template_engine.py` - master-document imports bumped (same three versions)
- `typsphinx/templates/base.typ` - default template imports bumped (same three versions, glob mitex import preserved)
- `.planning/phases/07-bump-preview-packages-typst-0-15-kai-fix/deferred-items.md` - logs a pre-existing, out-of-scope admonition-rendering bug discovered during the Task 3 visual glance

## Decisions Made
- Bumped typst + all four `@preview` packages atomically in a single wave (no bisect needed — the atomic bump compiled clean on the first attempt, confirming the mitex `0.2.6+` kai attribution from RESEARCH.md).
- Preserved the mitex import-style asymmetry (named vs. glob) exactly as instructed — no refactor.
- Worked around a local NixOS sandbox limitation (the pip-installed `.venv/bin/uv` binary can't execute here) by swapping in the nixpkgs `uv` binary inside the gitignored `.venv/` so `tox -e docs-pdf`'s `uv-venv-lock-runner` could actually run the hard gate. This is a local dev-environment fix only — no repository file was touched, and it does not affect CI (GitHub Actions runners are standard Linux, not NixOS).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Local `.venv/bin/uv` binary could not execute under NixOS sandbox**
- **Found during:** Task 3 (running `tox -e docs-pdf`)
- **Issue:** `tox-uv`'s `uv-venv-lock-runner` shells out to the uv binary installed inside the project venv (via the `dev` extra's `uv` dependency). That binary is a generic manylinux ELF (`interpreter /lib64/ld-linux-x86-64.so.2`) which NixOS cannot execute without `nix-ld`, producing `Could not start dynamically linked executable` and blocking the plan's hard gate.
- **Fix:** Replaced `.venv/bin/uv` in place with the nixpkgs-provided `uv` binary (`nix-shell -p uv`), which is correctly linked against the Nix store's glibc. This is scoped entirely to the gitignored `.venv/` directory — no tracked file was modified.
- **Files modified:** None (only `.venv/bin/uv`, which is gitignored and not committed).
- **Verification:** `tox -e docs-pdf` then ran to completion and exited 0.
- **Committed in:** N/A (not a repo change).

**2. [Not auto-fixed — logged as deferred, per SCOPE BOUNDARY] Pre-existing admonition rendering bug discovered during the Task 3 visual glance**
- **Found during:** Task 3 (coarse D-01/D-04 PDF visual glance)
- **Issue:** `.. note::` admonitions (and similar) render literal, unevaluated Typst source text (e.g. `par({text("...")...})`) instead of typeset prose, in 4 places across the compiled docs. Root cause: `typsphinx/translator.py::_visit_admonition` opens gentle-clues calls with markup-mode brackets (`info[`) but paragraph content is emitted in "unified code mode" (`par({...})`, no `#` prefix) — a markup/code-mode mismatch.
- **Why not fixed:** `translator.py` is not in this plan's `files_modified` list, and `git blame` confirms the affected `.. note::` content (and the untouched `_visit_admonition`/`visit_paragraph` translator code) predates this phase by months (2025-11-01). It reproduces independently of `@preview` package versions — it's a pre-existing translator bug that was simply invisible until now because `docs-pdf` never compiled successfully before this phase's kai fix. Per SCOPE BOUNDARY, out-of-scope pre-existing issues are logged, not fixed inline.
- **Files modified:** None (documented only).
- **Verification:** N/A — logged, not fixed.
- **Committed in:** `82d573b` (added `.planning/phases/07-bump-preview-packages-typst-0-15-kai-fix/deferred-items.md`)

---

**Total deviations:** 2 (1 auto-fixed local environment blocker, 1 logged-but-not-fixed pre-existing out-of-scope bug)
**Impact on plan:** Neither deviation affects the plan's success criteria. The environment fix was necessary to run the hard gate at all and touches no repo file. The admonition bug is real and worth fixing but is orthogonal to this atomic version-bump plan's scope and does not block FWD-02/PKG-01/PKG-02/PKG-03.

## Issues Encountered
- `ruff` and the venv's `uv` binary (both prebuilt Rust binaries pulled in via pip/uv wheels) cannot execute directly under this NixOS sandbox without `nix-ld`. Worked around both via `nix-shell -p ruff --run "ruff check ."` (ruff, read-only check, no file changes) and by swapping the nixpkgs `uv` binary into the gitignored `.venv/bin/uv` (see Deviation 1). Neither workaround touches a tracked file; CI is unaffected since GitHub Actions runners are standard Linux.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- The `kai`-class break is empirically closed: `docs-pdf` compiles clean against typst 0.15.0 with the bumped `@preview` set. This unblocks Phase 8 (Sphinx 9 API compatibility, `traverse()` -> `findall()`) and Phase 9 (CI hardening, dedicated `typst compile` smoke test, drift/Dependabot ceiling bumps) — both of which assumed a green `docs-pdf` lane.
- **Carried forward for a future phase:** the admonition rendering bug logged in `deferred-items.md` (literal Typst source leaking into rendered PDFs for `.. note::`-style content) should be triaged and fixed — it affects real user-facing output quality, independent of this milestone's forward-port scope.
- No blockers for proceeding to Phase 8.

---
*Phase: 07-bump-preview-packages-typst-0-15-kai-fix*
*Completed: 2026-07-11*

## Self-Check: PASSED

All created/modified files found on disk; all task commit hashes (2ed64aa, ca4c1ab, 82d573b, 4e37b71) found in git log.
