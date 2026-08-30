# Project Research Summary: typsphinx v0.9.2

**Project:** typsphinx v0.9.2 — Inline image blocker fix + PyPI release  
**Domain:** Sphinx→Typst translator bugfix (code-mode expression separator defect)  
**Researched:** 2026-08-30  
**Confidence:** HIGH (all major claims independently measured via real `typst.compile()`, file:line code reads, and live workflow API)

## Executive Summary

typsphinx v0.9.2 is a **narrow, two-aim patch release**: fix ONE blocker in `visit_image()` that prevents `-b typstpdf` from generating any PDF when an image node appears anywhere but at the start of its container (currently emits `expected semicolon or line break` syntax error), and publish the result together with v0.9.1's already-completed but never-released work as version 0.9.2 on PyPI.

The blocker is structurally identical to a defect v0.6.5 fixed for `visit_math`: the image emitter fails to participate in the shared separator discipline (`_add_paragraph_separator()` / `_emit_inline_concat_separator()` / `in_list_item` + `list_item_needs_separator`) that every other inline code-mode emitter (text, literal, math, footnote reference, reference) already uses. The fix is a 10–15 line addition mirroring the established triad, proven to close all 16 measured failing shapes (mid-sentence images, consecutive images, images in list items, tables, definitions, admonitions, footnotes, figures' legends, field-list bodies, and section titles) while leaving 9+ passing shapes byte-identical — confirmed by measured sampling, not assertion alone.

Release mechanics are straightforward but require exact execution: three version-literal files (`pyproject.toml`, `uv.lock`, `README.md`) must move in lockstep; the existing `uv.lock` regeneration must not be skipped (already blocking dependabot in this repo); and the CHANGELOG's "Planned for Future Releases" scratch block must be relocated before its heading becomes `## [0.9.2]` (to avoid the extraction algorithm capturing it as release notes). The release-prep phase inherits a proven guard procedure (SHA-256 baseline + re-verification) to prevent the checkbox auto-flip defect that fired five consecutive times at prior closes. No new runtime or test dependencies are required — the fix uses existing `typst-py` and regression tests reuse the existing parallel-gate idiom from three precedent modules.

## Key Findings

### Recommended Approach

**Add nothing to the stack.** All runtime and test dependencies (typst-py, sphinx, docutils, the four @preview Typst Universe packages) are already at their current released versions as of 2026-08-30, verified live against PyPI/Typst Universe APIs. No version bump, no new test framework, no new package import is needed. The "stack" work is entirely version-literal management and regression-gate implementation using tooling already proven in the repo.

**The mechanism is singular and precedent-bound.** FEATURES.md's measurement of 16 failing shapes all stem from one root cause: `visit_image()` never calls the three-part separator protocol that `visit_Text`, `visit_literal`, `visit_math`, `visit_footnote_reference`, and `visit_reference` all use. The fix reuses this exact protocol in the non-`in_figure` branch.

### Trigger Matrix: 16 Measured Failures

All emit `par({text("...")image(...)` with zero separator, all answer `expected semicolon or line break`:

- 1–3: Mid-sentence substitution image, two adjacent images, image in list item (from original todo, reproduced)
- 4–8: Image as 2nd list-item element, in table cell, definition-list body, admonition, footnote (MEASURED new)
- 9–10: Image(s) in figure legend, mid-text (MEASURED new, shows `in_figure` not complete guard)
- 11–13: Image after inline literal, emphasis, external link (MEASURED new)
- 14: Image in field-list body (MEASURED new, also concat-context)
- 15: Image in section title (MEASURED new)
- 16: Image with width/height attributes, mid-sentence (MEASURED new)

### Regression Surface: 9+ Shapes Must Stay Byte-Identical

Standalone block-level image, figure, image first in paragraph, images with attributes (standalone/first), image with target ID, figure with plain-text legend, figure nested in list, figure as first list-item element, bare block image as first list-item element.

Zero pre-existing test edits achievable — 144 existing `image(` matches are substring assertions, never exact-byte checks.

### Release Mechanics: Three Version Literals in Lockstep

| File | Line | Current | Target | Critical Note |
|------|------|---------|--------|---------|
| `pyproject.toml` | 7 | `"0.9.0"` | `"0.9.2"` | Hand-edited source of truth |
| `uv.lock` | 1467 | `"0.9.0"` | (regenerated) | **NOT hand-edited** — run `uv lock` after pyproject.toml; omitting breaks eleven `--locked` CI steps |
| `README.md` | 347 | `v0.9.0` | `v0.9.2` | Only version literal (badges are dynamic) |
| `CHANGELOG.md` | new | (none) | `## [0.9.2] - <date>` | Must relocate "Planned for Future Releases" first to avoid extraction capture |

**CHANGELOG structure:** Relocate "Planned for Future Releases" to new empty `## [Unreleased]` at top; rename old `## [Unreleased]` to `## [0.9.2]`. No `## [0.9.1]` heading ever created — v0.9.1 was never released.

### Gate Idiom to Copy

**Precedent:** `tests/test_paragraph_concat_render_gate.py` + `test_abbr_pep_separator_render_gate.py`

- TYPST_AVAILABLE guard + pytest.mark.skipif
- `_run_sphinx_build_typstpdf()` helper (subprocess with `sys.executable -m sphinx`, not binary on PATH)
- Multi-shape fixture pairing FAIL + PASS control shapes
- Assertions: returncode == 0; "Typst compilation failed" not in stderr; structural string check; PDF magic bytes

### Critical Pitfalls (Ranked by Likelihood in This Milestone)

1. **String-only gate cannot see parser defects** — Existing nine image tests assert only on string. New gate must call `typst.compile()` explicitly; RED-first TDD proves teeth.

2. **Gate never proven RED** — Fixture written after fix is only ever passing. Must restore unfixed translator, capture error, restore fix, verify empty `git status`.

3. **Fixing tests instead of proving byte-identical** — Zero pre-existing test edits is the standard. Any change signals need for justification.

4. **`ruff` unrunnable in fresh worktree (NixOS)** — `black --check .` + `mypy` pass locally, hiding findings. Run `nix run nixpkgs#ruff -- check .` or dispatch CI.

5. **Release-checkbox auto-flip** — Five consecutive flips, then one hold via guard. `<phase>-CLOSEOUT-GUARD.md` with SHA-256 baseline + re-verification. Every plan declares `requirements-completed: []`.

6. **`uv.lock` regeneration omitted** — Bumping `pyproject.toml` without regenerating causes `--locked` failures (exact error blocking dependabot #123, #128). One commit touching all four files required.

7. **Windows-only encoding failures** — New tests must use explicit `encoding="utf-8"`.

## Implications for Roadmap

Three sequential phases:

### Phase A: Fix + Regression Gate

**Rationale:** Fix and acceptance test land together. Gate proves fix works (string assertion alone insufficient).

**Delivers:**
- `visit_image()`/`depart_image()` separator triad (10–15 lines)
- New regression-gate module + fixture covering all 16 FAIL + 9 PASS shapes via real `typst.compile()`
- Closure of pending todo with extended matrix

**Prevents:** Pitfalls 1, 2, 3

**Research flags:** None — measured end-to-end, gate idiom precedent-bound

**Observable success:**
- New test imports `typst`/`TYPST_AVAILABLE`
- All 16 FAIL shapes produce exact error on unfixed tree (Evidence file with error + successful restore)
- All 16 + 9 shapes pass after fix
- Pre-existing nine image tests unchanged
- Diff shows only new test files

---

### Phase B: Release Preparation

**Rationale:** Version bump, CHANGELOG curation, checkbox guard are release-prep bookkeeping (after fix, before publish).

**Delivers:**
- CHANGELOG: "Planned for Future Releases" relocated; `## [Unreleased]` → `## [0.9.2]` with v0.9.1 bullets + image fix; tail links updated
- `pyproject.toml`: version `0.9.0` → `0.9.2`
- `uv.lock`: regenerated
- `README.md`: Status line updated
- `<phase>-CLOSEOUT-GUARD.md`: SHA-256 baseline + re-verification

**Prevents:** Pitfalls 4, 5, 6, 7, 9

**Observable success:**
- One commit touching all four files
- `## [0.9.2]` heading non-empty
- "Planned for Future Releases" under new empty `## [Unreleased]`
- CLOSEOUT-GUARD baseline + MATCH re-verification
- All plans declare `requirements-completed: []` for release requirement
- Lint clean

---

### Phase C: Publish

**Rationale:** Tag push, PyPI publish, GitHub Release, post-publish RTD/translations checks — strictly last.

**Delivers:**
- Git tag `v0.9.2` pushed
- `release.yml` runs: validate, build, publish-pypi, create-release
- Manual dispatch of translations repo `update-pin.yml`
- RTD `en`/`ja` `stable` verify `0.9.2`

**Observable success:**
- All `release.yml` jobs show `success`/`skipped`
- Translations repo `update-pin.yml` run and `v0.9.2` tag created
- RTD APIs show `0.9.2` on both projects with `"active": true, "built": true`

---

### Phase Ordering Rationale

Fix → Release-Prep → Publish aligns with code/test completion → metadata finalization → immutable release. Matches v0.6.x → v0.9.1 precedent (fix phases never touch version files; prep phases curate and guard; publish is mechanical).

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | **HIGH** | All elements verified live vs. PyPI/Typst Universe (2026-08-30); no bump needed |
| Features (Defect Surface) | **HIGH** | 16 FAIL independently compiled with real `typst.compile()`; 9 PASS measured byte-identical; 14-construct survey confirms single-site |
| Architecture (Fix Mechanism) | **HIGH** | Triad extracted from five working visitors (line-number citations); three candidates eliminated via measured proof |
| Pitfalls | **HIGH** | Every major pitfall backed by RETROSPECTIVE.md incidents with line citations; currently live or recently live in repo |

**Overall:** **HIGH** — defect measured, fix precedent-bound, release mechanical, every major pitfall has documented tested workaround.

### Gaps to Address

1. **Fixture shape details** — Phase A adapts probe code from FEATURES.md into polished `.rst` (~50 lines, low complexity)
2. **Evidence capture** — Adapts Phase 59's template (~30 min execution, 5 min writeup)
3. **README scope check** — Spot-check for other version strings (1 grep, seconds)

None are unknown-unknowns; all have precedent from v0.9.0/v0.9.1.

## Sources

**Primary (HIGH confidence):**
- `.planning/PROJECT.md` (`## Current Milestone: v0.9.2` binding constraints)
- `.planning/todos/pending/2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md`
- `typsphinx/translator.py` (HEAD) — all file:line citations
- Live measurements: probe project + `typst.compile()` of all 16 FAIL + 9 PASS (2026-08-30)
- PyPI JSON APIs + Typst Universe (live 2026-08-30)
- `tests/test_paragraph_concat_render_gate.py`, `test_abbr_pep_separator_render_gate.py`
- `.github/workflows/release.yml`, `scripts/extract_changelog_section.py`
- `.planning/RETROSPECTIVE.md` (v0.4.4–v0.9.1), `v0.9.1-phases/61-*/61-CLOSEOUT-GUARD.md`

**Secondary (MEDIUM confidence, within repo):**
- Phase 59/58 EVIDENCE/SUMMARY (RED-first procedure precedent)
- `.claude/CLAUDE.md`, project memory

---

**Research completed:** 2026-08-30  
**Ready for roadmap:** yes
