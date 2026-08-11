---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
verified: 2026-08-11T23:33:12Z
status: gaps_found
score: 10/11 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 8/10
  gaps_closed:
    - "BLD-02: two typst_documents entries resolving to the same target path (via unnormalized path SHAPE, e.g. `./manual.typ` vs `manual.typ`) are detected and reported instead of silently dropping one master's body"
    - "BLD-03: a wrapper target that collides with a content file's own path (an under-length typst_documents entry) is detected instead of silently destroying the docname's own content"
  gaps_remaining: []
  regressions: []
gaps:
  - truth: "BLD-03 (plan 47-11 must-have, superset of the roadmap wording): _is_usable_typst_documents_entry() is the single source of truth for entry usability, consulted everywhere a typst_documents entry's usability matters -- not just at the four wrapper-path-resolving sites the plan enumerated"
    status: failed
    reason: >
      TypstBuilder._compute_master_included_docnames() (typsphinx/builder.py line 269) is a FIFTH
      site that reads typst_documents to decide which docnames are "part of a compiled master" --
      the set translator.py's cross-reference degrade-to-text decision consults at
      translator.py:3073-3075 to decide whether a :doc:/:ref: target gets a real Typst link(<label>)
      or degrades to plain text. It filters entries with a bare `if entry` truthiness check, never
      _is_usable_typst_documents_entry(). This is exactly the drift class BLD-03 exists to eliminate,
      at a site 47-11's own docstring claim ("the SINGLE source of truth ... consulted by all FOUR
      sites") did not reach. Independently reproduced against this checkout with two real
      `sphinx-build` subprocess runs (not taken on 47-REVIEW.md's word):

      (a) Silent correctness bug, escalating to a hard compile fatal. Fixture:
      `typst_documents = [("index", "manual.typ", "T", "A"), ("ghost",)]`, `ghost.rst` (orphan) has a
      toctree pulling in `ghost_child`, and `index.rst` (the real master) references
      `:ref:\`ghost-child-label\`` (a label defined in `ghost_child.rst`). Under `-b typst`: exit 0,
      only an unrelated "produces no wrapper file" warning for the `ghost` entry, and `index.typ` on
      disk silently contains `link(<ghost_child:ghost-child-label>, ...)` -- a label that will never
      exist in any compiled document, because the `ghost` entry produces no wrapper (per the correct,
      already-fixed BLD-03 behavior) so `ghost_child.typ` is never `#include()`d anywhere. Under
      `-b typstpdf`, the identical input crashes `typst.compile()`:
      `TypstError: label \`<ghost_child:ghost-child-label>\` does not exist in the document` -- a hard
      fatal, not the graceful degrade-to-plain-text this mechanism exists to provide (which DOES fire
      correctly for a genuinely orphaned/excluded docname -- this failure is specific to the
      under-length-entry class BLD-03 governs).

      (b) Uncaught crash. Fixture: `typst_documents = [(["weird"], "manual.typ", "T", "A")]` (a
      non-hashable `entry[0]`, e.g. from a `conf.py` typo -- config values are user-authored and not
      type-checked by Sphinx). Under `-b typst`: the build crashes with an uncaught
      `TypeError: unhashable type: 'list'` at `builder.py:276` (`if docname in included`), instead of
      the graceful `logger.warning`-and-skip every other `_is_usable_typst_documents_entry()`-guarded
      site in this file now guarantees for exactly this malformed-entry shape.
    artifacts:
      - path: typsphinx/builder.py
        issue: >
          `_compute_master_included_docnames()` (~line 246-282) filters `typst_documents` entries with
          `if entry` alone (line 269) instead of `_is_usable_typst_documents_entry()`, so an
          under-length or non-str-docname entry is silently treated as contributing a real docname (and
          its whole toctree closure) to `master_included_docnames`, and a non-hashable `entry[0]`
          reaches an unguarded `docname in included` / `included.add(docname)` set operation with no
          type check ahead of it.
    missing:
      - "Filter typst_documents through _is_usable_typst_documents_entry() inside _compute_master_included_docnames(), per 47-REVIEW.md CR-01's suggested fix."
      - "A regression fixture/gate exercising a valid master plus an under-length entry whose toctree pulls in a document a real master's content cross-references via :ref:, asserting the build either degrades the reference to plain text or excludes the under-length entry's subtree from master_included_docnames -- never both silently link it AND never include it."
      - "A regression fixture/gate exercising a non-hashable entry[0] (e.g. a list), asserting a graceful logger.warning-and-skip rather than an uncaught TypeError."
human_verification: []
---

# Phase 47: Two-Layer Output — Content/Wrapper Split, Target-as-Path, Collision Detection Verification Report (Re-verification after gap closure)

**Phase Goal:** The unit of output stops being "one `.typ` per docname whose shape depends on
whether that docname is a master." Every document gets a docname-named, template-less **content**
file; every `typst_documents` entry gets a **wrapper** file carrying the template and the include
of its master's content. B-1 and B-2 close, and any two logical files wanting one physical path
are reported instead of silently overwritten.

**Verified:** 2026-08-11T23:33:12Z
**Status:** gaps_found
**Re-verification:** Yes — after gap-closure plans 47-11 and 47-12

## Summary

Plans 47-11 and 47-12 closed both gaps the prior `47-VERIFICATION.md` (score 8/10) found: BLD-02's
unnormalized-path-shape false negative and BLD-03's under-length-entry write-time destruction. Both
closures were independently reproduced against this checkout with real `sphinx-build` subprocess
runs, not taken on the SUMMARYs' word — see "Gaps Closed" evidence below. `47-12` additionally
deleted the WR-01 dead-code finding (`_resolve_entry_element()`) and corrected six stale
`REQUIREMENTS.md` checkboxes, both independently confirmed.

However, a code review that ran after both closure plans landed (`47-REVIEW.md`, CR-01) found a
**new BLOCKER**: `TypstBuilder._compute_master_included_docnames()` is a fifth site consuming
`typst_documents` that 47-11's single-source-of-truth predicate did not reach. This verification
independently reproduced both of CR-01's claimed failure modes end-to-end with real `sphinx-build`
subprocess runs (not inferred from the review's narrative) — see the Gaps section. The finding is
confirmed real and does bear directly on the BLD-03 must-have as 47-11's own plan frontmatter
stated it ("exactly ONE predicate ... and all FOUR sites ... consult it" — there are actually five
relevant sites, and the fifth was missed). Overall status is **gaps_found**, not `passed`.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | COMP-01: every document written as a docname-named content `.typ` with no template applied | ✓ VERIFIED | Regression: full suite (1034 passed, 5 skipped, incl. `test_two_layer_output_gate.py`) unaffected by 47-11/47-12's changes (neither plan touched `translator.py`/content-writing code); unchanged since prior verification's independent reproduction. |
| 2 | COMP-02: each `typst_documents` entry produces a wrapper `.typ` at its resolved target path, carrying template + include | ✓ VERIFIED | Regression, as above; independently reproduced live in this pass via the BLD-02/BLD-03 fixture builds below (`manual.typ` carries `#show: project.with(...)` + `#include(...)`). |
| 3 | COMP-03: a document that is also another master's toctree child builds/compiles without `file not found` (B-1) | ✓ VERIFIED | Regression: `test_two_layer_output_gate.py` (12 passed) and `test_pdf_generation.py` unaffected; not touched by 47-11/47-12. |
| 4 | COMP-04: an included master no longer re-expands its title page/`#outline()` into the parent's body (B-2) | ✓ VERIFIED | Regression: same as #3; `render_wrapper()` (the mechanism) untouched by both gap-closure plans. |
| 5 | OUT-01: a target is a path relative to the output directory (bare name → outdir root, explicit path → written where asked) | ✓ VERIFIED | Regression: `_resolve_target_stem()` byte-identical per 47-11 Task 2's own acceptance criteria (`git diff` scoped to `_collision_key` only); `test_builder_output_stem.py` passes unmodified. |
| 6 | OUT-02: an escaping target (`..`, absolute, drive-qualified) is still refused with a warning + safe fallback | ✓ VERIFIED | Regression: `tests/test_out02_escape_target_gate.py` passes with the module byte-identical (`git diff --stat` empty, confirmed by 47-11's own acceptance criteria and re-run here); `_escapes_outdir()`/`_is_drive_qualified()` untouched. |
| 7 | OUT-03: content files stay docname-derived regardless of where their master's wrapper is written | ✓ VERIFIED | Regression: `test_out03_content_files_stay_docname_derived` (part of the still-green suite) and `_content_output_path()` untouched by both plans. |
| 8 | BLD-02: two `typst_documents` entries resolving to the same target path are detected and reported instead of silently dropping one master's body | ✓ VERIFIED (gap closed) | Independently reproduced live: `typst_documents = [("index", "./manual.typ", "T1", "A1"), ("other", "manual.typ", "T2", "A2")]` with `-b typst` now exits non-zero with `ExtensionError: typst: 1 output path collision(s): 'manual.typ': typst_documents entry 0 (docname 'index', target './manual.typ') and typst_documents entry 1 (docname 'other', target 'manual.typ') both resolve to the same output path 'manual.typ'`, and zero `.typ` files are written. Also reproduced the `./_template.typ` reserved-file-clobber shape: `ExtensionError: typst: 1 output path collision(s): './_template.typ': the reserved _template.typ infrastructure file and typst_documents entry 0 ... both resolve to the same output path './_template.typ'`. `posixpath.normpath()` confirmed present inside `_collision_key()`. |
| 9 | BLD-03 (roadmap wording): a wrapper target that collides with a content file's own path is detected | ✓ VERIFIED (gap closed) | Independently reproduced live against `tests/fixtures/bld03_under_length_entry_gate/` (`typst_documents = [("index",), ("other", "manual.typ", ...)]`) with `-b typst`: exit 0, `grep -c 'UNDERLENGTH-CONTENT-SENTINEL-CCC' index.typ` returns `1` (content survives) and `grep -c '#show: project.with(' index.typ` returns `0` (no template applied — no self-including wrapper overwrote it), plus a `produces no wrapper file` warning naming the skipped entry. |
| 9b | BLD-03 (plan 47-11 must-have, superset): `_is_usable_typst_documents_entry()` is the single predicate for entry usability, consulted everywhere the question matters | ✗ FAILED (new gap) | Independently reproduced (see Gaps): `_compute_master_included_docnames()` is a fifth, unguarded site — reproduced both a silent dangling-label defect (fatal under `-b typstpdf`, silent under `-b typst`) and an uncaught `TypeError` crash. |
| 10 | BLD-04: collision detection behaves identically on case-insensitive filesystems | ✓ VERIFIED | Regression: `_collision_key()`'s case-folding line untouched by 47-11 (only `posixpath.normpath()` was added, confirmed by reading the function and by `test_collision_key_still_folds_case_and_ignores_unicode_normalization` passing, unmarked/non-xfail from the start). |
| 11 | WR-01 (plan 47-12 must-have): the superseded docname-first-match entry resolver is deleted, not merely annotated | ✓ VERIFIED | Independently reproduced: `grep -rn '_resolve_entry_element' typsphinx/` returns zero hits; `python -c "import typsphinx.writer as w; hasattr(w, '_resolve_entry_element')"` prints `False`. Only historical/comment references remain in test docstrings, correctly framed as history naming 47-12-PLAN.md as the removal point. |

**Score:** 10/11 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/builder.py::_collision_key` | Comparison-only normalization folding case, separator style, AND path shape | ✓ VERIFIED | `posixpath.normpath()` confirmed present between separator-folding and `casefold()`; the BLD-02 gap fixtures (path-shape duplicate, template clobber) both now correctly collide, independently reproduced live. |
| `typsphinx/builder.py::_is_usable_typst_documents_entry` | Single predicate for "can this entry produce a wrapper file", consulted at every site that needs the answer | ⚠️ PARTIAL (new gap) | Exists, substantive, and wired at exactly 4 of the sites its own docstring claims to cover (`grep -n _is_usable_typst_documents_entry typsphinx/builder.py` shows the definition plus call sites at lines 617, 794, 1011, 1442). `_compute_master_included_docnames()` at line 269 is a fifth site that needs the same answer (entry usability) and does not consult it — confirmed by direct reading and by two independent live `sphinx-build` reproductions. |
| `typsphinx/builder.py::_write_typst_files` | Single shared write path for content + wrapper files, guarded by the shared predicate | ✓ VERIFIED | Wrapper-matching loop's guard now includes `_is_usable_typst_documents_entry()` (line 1011); independently reproduced live — the under-length entry produces no wrapper and the docname's own content survives. |
| `typsphinx/writer.py::_entry_element_value` | Sole entry-element resolution route (post-WR-01 deletion) | ✓ VERIFIED | `render_wrapper()`'s only call is to `_entry_element_value()`; `_resolve_entry_element()` confirmed absent from the module. |
| `.planning/REQUIREMENTS.md` | Checkbox state matches genuinely-satisfied requirement IDs; BLD-02/BLD-03 open pending this re-verification | ⚠️ STALE (as of the moment this report is written) | Currently shows COMP-01..04, OUT-01..03 as `[x]` (correct, matches plan 47-12's edit) and BLD-02/BLD-03 as `[ ]` (was correct pending this re-verification; BLD-02 is now genuinely satisfied per this report but BLD-03 is NOT — see gap 9b — so BLD-02 alone should flip to `[x]` and BLD-03 should stay `[ ]` once this report is acted on). This is bookkeeping, not a phase-goal defect; not counted as a truth failure. |
| `tests/test_collision_predicate_completeness_gate.py` | 11-test regression gate pinning both closed gaps | ✓ VERIFIED | `uv run pytest tests/test_collision_predicate_completeness_gate.py -q` → `11 passed`, re-run directly in this verification pass, zero xfail/xpass remaining. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `_collision_key()` | `_validate_output_path_collisions()` | Single normalization function, now folding shape too | ✓ WIRED | Confirmed; path-shape and reserved-file-clobber collisions both now correctly raise `ExtensionError` with zero `.typ` written. |
| `_is_usable_typst_documents_entry()` | the four wrapper-path-resolving sites | Single predicate, four consumers | ✓ WIRED (as scoped) / ⚠️ INCOMPLETE (as claimed) | The four sites the plan named are correctly wired. The plan's own must-have text claims broader coverage ("consulted everywhere") that a fifth site (`_compute_master_included_docnames()`) does not receive — see gap 9b. |
| `TypstPDFBuilder.finish()` | `_is_usable_typst_documents_entry()` | New "has no target element" failure branch | ✓ WIRED | Independently reproduced: `-b typstpdf` on the under-length-entry fixture reports `has no target element` in the aggregate `ExtensionError`, while the well-formed sibling master's PDF is still produced. |
| `typst_documents` (config) | `_compute_master_included_docnames()` | Bare `if entry` filter (NOT the shared predicate) | ✗ NOT_WIRED (new gap) | Confirmed by direct reading (`typsphinx/builder.py:269`) and by two independent live reproductions — see gap 9b. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|---------------------|--------|
| `_compute_master_included_docnames()` | `master_included_docnames` | `self.config.typst_documents` filtered by `if entry` | Yes, but the filter admits entries that should be excluded (under-length, non-str docname) | ⚠️ STATIC-adjacent — the SET is computed from real config, but the filter logic is wrong for the malformed-entry class, so the set can contain a docname whose subtree is never physically compiled in, or crash before the set is ever produced. |
| `translator.py`'s `degrade_xref_to_text` decision | `master_included_docnames` | `self.builder.master_included_docnames` | Yes | Confirmed downstream consumption is real (not mocked) — `translator.py:3073-3075` reads the live builder attribute set at the top of `write()`; the defect is upstream in what populates that set, not in how it's consumed. |

### Behavioral Spot-Checks (independently run against this checkout)

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| BLD-02 gap closure, path-shape duplicate (`./manual.typ` vs `manual.typ`) | Real `sphinx-build -b typst` in a throwaway fixture | Exit non-zero, `ExtensionError: ... 1 output path collision(s) ...`, zero `.typ` files written | ✓ PASS — gap closed |
| BLD-02 gap closure, `./_template.typ` reserved-file clobber | Real `sphinx-build -b typst` in a throwaway fixture | Exit non-zero, `ExtensionError: ... reserved _template.typ infrastructure file ...` | ✓ PASS — gap closed |
| BLD-03 gap closure, under-length entry (`("index",)`) | Real `sphinx-build -b typst` against `tests/fixtures/bld03_under_length_entry_gate/` | Exit 0; `index.typ` content sentinel count = 1, template-marker count = 0; `produces no wrapper file` warning present | ✓ PASS — gap closed |
| WR-01 closure, dead resolver removal | `grep -rn '_resolve_entry_element' typsphinx/` and `hasattr()` check | Zero hits in `typsphinx/`; `hasattr` → `False` | ✓ PASS — closed |
| **CR-01 (new), silent dangling-label / hard compile fatal** | Real `sphinx-build -b typst` then `-b typstpdf` in a throwaway fixture (`("index", "manual.typ", ...)` + `("ghost",)`, `index.rst` has `:ref:` into `ghost`'s toctree child) | `-b typst`: exit 0, only an unrelated warning, `index.typ` silently contains `link(<ghost_child:ghost-child-label>, ...)` to a label that will never exist anywhere. `-b typstpdf`: `typst.compile()` fails with `TypstError: label \`<ghost_child:ghost-child-label>\` does not exist in the document`, then `ExtensionError: typstpdf: 2 master document(s) failed`. | ✗ FAIL — new gap, confirmed real |
| **CR-01 (new), uncaught crash on non-hashable entry[0]** | Real `sphinx-build -b typst` in a throwaway fixture (`typst_documents = [(["weird"], "manual.typ", "T", "A")]`) | Uncaught `TypeError: unhashable type: 'list'` at `builder.py:276`, full sphinx traceback dumped, build aborts ungracefully | ✗ FAIL — new gap, confirmed real |
| Full existing suite | `uv run pytest -q` | `1034 passed, 5 skipped` in 211s | ✓ PASS |
| Lint/type gates | `uv run black --check .` / `uv run mypy typsphinx/` | Both clean (`ruff` unrunnable in this NixOS sandbox per environment note; CI is authoritative for it) | ✓ PASS |
| `_is_usable_typst_documents_entry` call-site count | `grep -n "_is_usable_typst_documents_entry(" typsphinx/builder.py` | Definition + 4 call sites (617, 794, 1011, 1442) — matches the plan's claim of "four sites," confirming the fifth (`_compute_master_included_docnames`) genuinely was never wired | ✓ PASS (confirms the gap's precise shape) |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|----------------|--------------|--------|----------|
| COMP-01 | 47-01, 47-02, 47-04..09 | Docname-named content file, no template | ✓ SATISFIED | See truth #1 |
| COMP-02 | 47-01, 47-02, 47-04..09 | Wrapper at resolved target path, template + include | ✓ SATISFIED | See truth #2 |
| COMP-03 | 47-01, 47-02 | Nested master builds without `file not found` (B-1) | ✓ SATISFIED | See truth #3 |
| COMP-04 | 47-01, 47-02 | No mid-body template re-expansion (B-2) | ✓ SATISFIED | See truth #4 |
| OUT-01 | 47-02, 47-03 | Target as path relative to outdir | ✓ SATISFIED | See truth #5 |
| OUT-02 | 47-02, 47-03, 47-10 | Escaping target refused, safe fallback | ✓ SATISFIED | See truth #6 |
| OUT-03 | 47-01, 47-02, 47-08 | Content files docname-derived regardless of wrapper placement | ✓ SATISFIED | See truth #7 |
| BLD-02 | 47-01, 47-08, 47-09, 47-11 | Duplicate target collision detected and reported | ✓ SATISFIED | See truth #8 — gap closed and independently reproduced |
| BLD-03 | 47-01, 47-04..07, 47-08, 47-09, 47-11 | Wrapper/content self-collision detected | ⚠️ PARTIALLY SATISFIED | Roadmap-wording self-collision (truth #9) is genuinely fixed. The broader single-predicate-ownership promise 47-11's own plan frontmatter made for BLD-03 (truth #9b) is FALSE — a fifth site bypasses the predicate with reproducible crash and silent-corruption consequences. Marked BLOCKED for this requirement ID pending the fix. |
| BLD-04 | 47-01, 47-09, 47-10 | Case-insensitive collision detection | ✓ SATISFIED | See truth #10 |

**No orphaned requirements** — REQUIREMENTS.md's phase-mapping table assigns exactly these 10 IDs to Phase 47, matching the union of every plan's `requirements:` frontmatter field.

**Bookkeeping note:** `.planning/REQUIREMENTS.md` currently (correctly, as of before this report) shows BLD-02 and BLD-03 both `[ ]`. This report finds BLD-02 genuinely satisfied — its checkbox should flip to `[x]` — but BLD-03 should stay `[ ]` because of the new gap 9b/CR-01, not because the original roadmap-wording scenario is unfixed.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `typsphinx/builder.py` | 284-324 | `_resolve_output_stem()` (docname-based first-match lookup) has zero production call sites anywhere in `typsphinx/` — confirmed by `grep -rn "_resolve_output_stem" typsphinx/`, which returns only the method's own definition plus docstring cross-references, no call. Reachable only via `tests/test_builder_output_stem.py`'s ~25 direct unit-test invocations. | ⚠️ Warning | Same dead-code pattern as the already-fixed WR-01 (`_resolve_entry_element()`); a green test suite over this function reports false confidence in a code path no real build reaches. Flagged by `47-REVIEW.md` as its own WR-01 finding; not blocking (does not affect any requirement's correctness), but should be deleted, mirroring how 47-12 handled `_resolve_entry_element()`. |
| `typsphinx/builder.py` | 33-40 | `_is_drive_qualified()`'s docstring names `_resolve_output_stem()` as a caller; the actual second caller is `_resolve_target_stem()` (confirmed: `grep -n "_is_drive_qualified(" typsphinx/builder.py` shows only lines 103 and 388 as call sites, neither inside `_resolve_output_stem()`). | ℹ️ Info | Stale docstring, symptom of the same drift as the warning above. No functional impact. |

No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` markers found in `typsphinx/builder.py`, `typsphinx/writer.py`, or `tests/test_collision_predicate_completeness_gate.py`. No debt-marker gate violation.

### Human Verification Required

None. Both the two closed gaps and the one new gap are deterministic, reproduced with real `sphinx-build` subprocess runs directly by this verification (not inferred from `47-REVIEW.md`'s or the SUMMARYs' narrative), and require no runtime/visual/UX judgment to confirm.

### Gaps Summary

**Gaps closed (2 of 2 from the prior verification pass):** BLD-02's path-shape false negative
(`./manual.typ` vs `manual.typ`, and the `./_template.typ` reserved-infrastructure-file clobber
variant) and BLD-03's under-length-entry write-time content destruction are both genuinely fixed.
`posixpath.normpath()` now runs inside `_collision_key()`, and a single
`_is_usable_typst_documents_entry()` predicate now guards the four wrapper-path-resolving sites the
gap-closure plan set out to fix. Both fixes were independently reproduced against this exact
checkout with real `sphinx-build` subprocess runs producing the expected `ExtensionError` /
content-preservation outcomes — not taken on the SUMMARYs' word. Plan 47-12's WR-01 dead-code
deletion (`_resolve_entry_element()`) and its six `REQUIREMENTS.md` checkbox corrections were also
independently confirmed accurate.

**One new gap found and confirmed (not present in the prior verification pass, surfaced by a
code review that ran after both closure plans landed):** `TypstBuilder._compute_master_included_docnames()`
is a fifth site that reads `typst_documents` and needs the same "is this entry usable" answer the
new predicate was built to centralize, but it was never wired to it — it still uses a bare `if
entry` truthiness check. This verification independently reproduced, with real end-to-end
`sphinx-build` runs (not mocked, not taken on the review's word):

- A silent correctness bug under `-b typst` (a real master's `:ref:` into an under-length entry's
  toctree child silently emits a Typst label reference that will never exist in any compiled
  document — no warning names this specific consequence) that escalates to a hard `typst.compile()`
  fatal (`TypstError: label ... does not exist in the document`) under `-b typstpdf`, instead of the
  graceful degrade-to-plain-text this exact mechanism exists to provide for excluded documents.
- An uncaught `TypeError: unhashable type: 'list'` crash for a non-hashable `entry[0]` (a plausible
  `conf.py` typo), instead of the graceful `logger.warning`-and-skip every other
  `_is_usable_typst_documents_entry()`-guarded site in this file now guarantees for malformed
  entries.

This bears directly on the BLD-03 must-have as plan `47-11`'s own frontmatter stated it: "exactly
ONE predicate decides whether a `typst_documents` entry is usable ... and all FOUR sites that
resolve a wrapper path consult it." There are, in fact, at least five relevant sites once
`_compute_master_included_docnames()` (which resolves a *cross-reference safety* decision fed by
the same config, not literally a wrapper *output path*) is counted, and the fifth was missed. The
roadmap's own narrower BLD-03 wording ("a wrapper target that collides with a content file's own
path is detected") is satisfied — the self-collision defect itself is fixed — but the single-
predicate-ownership guarantee the phase's own gap-closure plan promised as the mechanism that would
prevent this exact class of defect from recurring elsewhere is not fully realized. Per this
verification's brief, this is reported plainly as a genuine, confirmed BLOCKER rather than deferred
or softened: **overall status is `gaps_found`, not `passed`.**

The fix identified by `47-REVIEW.md` (CR-01) is narrow and precisely located
(`_compute_master_included_docnames()`'s one-line filter, `typsphinx/builder.py:269`); this is a
closure-plan-sized gap, not a phase redesign. `47-REVIEW.md`'s WR-01 (new) finding
(`_resolve_output_stem()` dead code) is real but non-blocking — flagged above as a Warning-severity
anti-pattern, not a gap.

---

_Verified: 2026-08-11T23:33:12Z_
_Verifier: Claude (gsd-verifier)_
