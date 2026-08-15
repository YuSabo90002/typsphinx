---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
verified: 2026-08-12T00:00:00Z
status: passed
score: 11/11 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 10/11
  gaps_closed:
    - "BLD-03 (plan 47-11 must-have, superset of the roadmap wording): _is_usable_typst_documents_entry() is the single source of truth for entry usability, consulted everywhere a typst_documents entry's usability matters — the fifth site, TypstBuilder._compute_master_included_docnames(), is now routed through the predicate instead of a bare `if entry` truthiness test."
  gaps_remaining: []
  regressions: []
---

# Phase 47: Two-Layer Output — Content/Wrapper Split, Target-as-Path, Collision Detection Verification Report (Re-verification after gap-closure plans 47-13/47-14)

**Phase Goal:** The unit of output stops being "one `.typ` per docname whose shape depends on
whether that docname is a master." Every document gets a docname-named, template-less **content**
file; every `typst_documents` entry gets a **wrapper** file carrying the template and the include
of its master's content. B-1 and B-2 close, and any two logical files wanting one physical path
are reported instead of silently overwritten.

**Verified:** 2026-08-12T00:00:00Z
**Status:** passed
**Re-verification:** Yes — after gap-closure plans 47-13 (BLD-03 gap 9b / CR-01) and 47-14 (WR-01
deletion + BLD-02 bookkeeping)

## Summary

The single BLOCKER that kept the prior verification pass at `gaps_found` (score 10/11) —
`TypstBuilder._compute_master_included_docnames()` bypassing the shared entry-usability predicate
— is genuinely closed. This pass independently reproduced the fix with real `sphinx-build`
subprocess runs against both new fixtures (`bld03_ghost_entry_xref_gate`,
`bld03_unhashable_docname_gate`) on both builders, not taken on the SUMMARYs', the REVIEW's, or
the prior VERIFICATION's word. Every previously-verified truth was re-measured (not merely
assumed to survive) because `_resolve_output_stem()` — a function three of the ten requirement
IDs' evidence trail touched — no longer exists after plan 47-14's deletion; its 22 surviving
semantics were confirmed retargeted onto the live resolver with expected values verbatim, and the
three deleted assertions carry recorded rationale. No regression was found anywhere in the full
suite (1039 passed, 5 skipped, matching both plans' own closing measurements exactly).

Two informational items are recorded below (a stale test-module docstring, and REQUIREMENTS.md's
BLD-03 checkbox lagging this report by construction) — neither is a truth failure, an artifact
defect, or a broken link, so neither blocks `passed`.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | COMP-01: every document written as a docname-named content `.typ` with no template applied | ✓ VERIFIED | Regression: full suite (1039 passed, 5 skipped) re-run in this pass; neither 47-13 nor 47-14 touched `translator.py` or content-writing code (confirmed by `git diff --stat 80043b3^..HEAD`, which shows only `typsphinx/builder.py` under `typsphinx/`). |
| 2 | COMP-02: each `typst_documents` entry produces a wrapper `.typ` at its resolved target path, carrying template + include | ✓ VERIFIED | Regression, as above; independently re-confirmed live in this pass via the two new fixture builds below (`manual.typ` / `real.typ` wrappers written correctly alongside content). |
| 3 | COMP-03: a document that is also another master's toctree child builds/compiles without `file not found` (B-1) | ✓ VERIFIED | Regression: `test_two_layer_output_gate.py` (12 passed) re-run in this pass; not touched by 47-13/47-14. |
| 4 | COMP-04: an included master no longer re-expands its title page/`#outline()` into the parent's body (B-2) | ✓ VERIFIED | Regression: same as #3; `render_wrapper()` untouched by both gap-closure plans (confirmed by the diff-stat above showing no `writer.py` change). |
| 5 | OUT-01: a target is a path relative to the output directory (bare name → outdir root, explicit path → written where asked) | ✓ VERIFIED | Re-anchored, not merely regressed: `_resolve_target_stem()`'s AST body is byte-identical (`git diff -U0 -- typsphinx/builder.py` shows only prose/docstring changes in this function); `tests/test_builder_output_stem.py` (25 tests, retargeted from 28 by 47-14) passes; independently spot-checked `test_resolve_target_stem_preserves_period_in_stem`/`_with_suffix`/`_preserves_non_ascii_target` exist by name and `test_two_layer_output_gate.py`'s build-level placement assertions pass. |
| 6 | OUT-02: an escaping target (`..`, absolute, drive-qualified) is still refused with a warning + safe fallback | ✓ VERIFIED | Re-anchored: the three escape-shape unit tests (`test_resolve_target_stem_guards_parent_traversal`/`_absolute_target`/`_drive_qualified_target`) confirmed present by name and passing; `tests/test_out02_escape_target_gate.py` passes with `git diff --stat` empty against this diff range; `_escapes_outdir()`/`_is_drive_qualified()` bodies untouched. |
| 7 | OUT-03: content files stay docname-derived regardless of where their master's wrapper is written | ✓ VERIFIED | Regression: `test_wrapper_path_ignores_docname_directory_but_content_path_does_not` (unchanged body, per plan) and `tests/test_two_layer_output_gate.py`'s OUT-03 assertions pass; `_content_output_path()` untouched. |
| 8 | BLD-02: two `typst_documents` entries resolving to the same target path are detected and reported instead of silently dropping one master's body | ✓ VERIFIED | Regression: `tests/test_collision_predicate_completeness_gate.py` (11 passed) and `tests/test_collision_validator_gate.py` (7 passed) re-run in this pass; `_collision_key()`/`_validate_output_path_collisions()` untouched by 47-13/47-14. |
| 9 | BLD-03 (roadmap wording): a wrapper target that collides with a content file's own path is detected | ✓ VERIFIED | Regression: `tests/test_collision_predicate_completeness_gate.py::TestBld03UnderLengthEntryGate` unaffected. |
| 9b | BLD-03 (plan 47-11 must-have, superset): `_is_usable_typst_documents_entry()` is the single predicate for entry usability, consulted everywhere the question matters — including the previously-missed fifth site | ✓ VERIFIED (gap closed) | Independently reproduced by this verification pass (not taken on 47-13-SUMMARY.md's, 47-14's, or 47-REVIEW.md's word) — see "Behavioral Spot-Checks" below for the full transcripts. `typsphinx/builder.py:308` now reads `if _is_usable_typst_documents_entry(entry)` (confirmed by direct read); the predicate's own docstring now enumerates all FIVE consumers by name (confirmed by direct read, lines 106–164); `grep -n "_is_usable_typst_documents_entry(" typsphinx/builder.py` shows exactly 5 call sites (308, 614, 792, 1008, 1440), up from the prior pass's 4. |
| 10 | BLD-04: collision detection behaves identically on case-insensitive filesystems | ✓ VERIFIED | Regression: `_collision_key()`'s case-folding line untouched (confirmed via the scoped diff); `test_collision_key_folds_case_but_not_unicode_normalization` passes. |
| 11 | WR-01 (plan 47-12 must-have): the superseded docname-first-match entry resolver is deleted, not merely annotated | ✓ VERIFIED | Unchanged from prior pass: `grep -rn '_resolve_entry_element' typsphinx/` returns zero hits. |
| 12 | WR-01 (new, from 47-REVIEW.md): the builder-side sibling dead resolver (`_resolve_output_stem()`) is deleted, not merely annotated | ✓ VERIFIED (new closure) | Independently reproduced: `git grep -c '_resolve_output_stem' -- 'typsphinx/'` returns zero matches; `python -c "from typsphinx.builder import TypstBuilder; print(hasattr(TypstBuilder, '_resolve_output_stem'))"` prints `False`. Nine remaining hits project-wide are all in `tests/`/`tests/fixtures/`, each explicitly framed as history naming plan 47-14 as the removal point (confirmed by direct read of every hit). |

**Score:** 12/12 truths verified (11 must-haves per the phase's own frontmatter accounting, plus the
new WR-01(builder-side) closure truth surfaced by 47-REVIEW.md; 0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/builder.py::_compute_master_included_docnames` | Fifth predicate consumer, filters via `_is_usable_typst_documents_entry(entry)` | ✓ VERIFIED | Confirmed by direct read (lines 304–309): `masters = [entry[0] for entry in typst_documents if _is_usable_typst_documents_entry(entry)]`. |
| `typsphinx/builder.py::_is_usable_typst_documents_entry` | Single predicate, docstring names all five consumers | ✓ VERIFIED | Confirmed by direct read (lines 106–164): opening sentence says "all FIVE sites," enumerates the collision validator, `write()`'s D-07 report, `_write_typst_files()`'s wrapper loop, `TypstPDFBuilder.finish()`, and `_compute_master_included_docnames()`, with the cross-reference-safety reasoning stated as a contract. |
| `tests/test_master_include_set_predicate_gate.py` | 8-test regression gate pinning the fifth-site fix (6 real-build/unit tests + 2 invariance guards) | ✓ VERIFIED | `uv run pytest tests/test_master_include_set_predicate_gate.py -v` → 8/8 passed, zero xfail/xpass remaining (re-run directly in this verification pass). |
| `typsphinx/builder.py` (no `_resolve_output_stem`) | Dead resolver deleted | ✓ VERIFIED | Zero hits anywhere under `typsphinx/`; `hasattr()` check confirms absence at import time. |
| `tests/test_builder_output_stem.py` | 22 surviving semantics retargeted onto `_resolve_target_stem()`/`_wrapper_output_relpath()`, 3 deleted with recorded rationale | ✓ VERIFIED | `--collect-only` reports exactly 25 tests (28 − 3); `grep -c 'def test_resolve_target_stem'` = 21 named functions plus 1 `_wrapper_output_relpath` test = 22 retargeted; all 25 pass. |
| `.planning/REQUIREMENTS.md` | Checkbox state matches genuinely-satisfied requirement IDs | ⚠️ STALE (bookkeeping, not a truth failure) | COMP-01..04, OUT-01..03, BLD-02, BLD-04 all `[x]`/`Complete` (9/10). BLD-03 is still `[ ]`/`Pending` as of this report's writing — correctly so per plan 47-14's own explicit instruction not to flip it ahead of this re-verification's measurement. This report is that measurement: BLD-03 is now genuinely satisfied (see truth #9b) and its checkbox/table row should flip to `[x]`/`Complete` as this report's direct consequence. Not counted as a phase-goal defect. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `typst_documents` (config) | `_compute_master_included_docnames()` | `_is_usable_typst_documents_entry()` predicate (was: bare `if entry`) | ✓ WIRED (gap closed) | Confirmed by direct read and by two independent live `sphinx-build` reproductions (see below) — the prior pass's `✗ NOT_WIRED` finding is resolved. |
| `_is_usable_typst_documents_entry()` | all five consumer sites | Single predicate, five consumers, docstring enumeration matches wired reality | ✓ WIRED | `grep -n "_is_usable_typst_documents_entry(" typsphinx/builder.py` → exactly 5 call sites (308, 614, 792, 1008, 1440), matching the corrected docstring's own enumeration. |
| `_compute_master_included_docnames()` | `translator.py:3073-3075`'s degrade decision | `TypstBuilder.master_included_docnames` attribute | ✓ WIRED, and now correctly populated | The consumption path was always real; the upstream defect (wrong entries admitted to the set) is what's fixed. Live-reproduced: an under-length entry's phantom subtree no longer reaches the set, so the translator correctly degrades the cross-reference to plain text instead of emitting a dangling label. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|---------------------|--------|
| `_compute_master_included_docnames()` | `master_included_docnames` | `self.config.typst_documents` filtered by `_is_usable_typst_documents_entry()` | Yes, and now correctly excludes unusable entries | ✓ FLOWING — the set now excludes an under-length entry's docname and its whole toctree closure, and never reaches an unguarded `set` operation on a non-hashable `entry[0]`. Independently confirmed by both fixture builds below. |

### Behavioral Spot-Checks (independently run against this checkout, this pass)

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Gap 9b / CR-01 fix, silent dangling-label mode, `-b typst` | `uv run python -m sphinx -b typst tests/fixtures/bld03_ghost_entry_xref_gate /tmp/verify47-d` | Exit 0. `grep -c 'link(<ghost_child:' index.typ` → `0` (was ≥1 pre-fix). `grep -c 'Ghost Child Target Section' index.typ` → `1` (reference degraded to plain text, not dropped). Build log now also carries an explicit warning: `cross-reference to non-included document 'ghost_child' rendered as plain text` — a diagnostic that did not exist at the time of the prior verification's reproduction. | ✓ PASS — gap closed, with an added diagnostic |
| Gap 9b / CR-01 fix, hard compile fatal mode, `-b typstpdf` | `uv run python -m sphinx -b typstpdf tests/fixtures/bld03_ghost_entry_xref_gate /tmp/verify47-d-pdf` | `ExtensionError: typstpdf: 1 master document(s) failed: ghost: typst_documents entry ('ghost',) has no target element ...` — the existing graceful diagnostic, NOT `TypstError: label ... does not exist in the document`. `manual.pdf` (the well-formed sibling master) exists and was generated. | ✓ PASS — gap closed |
| Gap 9b / CR-01 fix, uncaught-crash mode, `-b typst` | `uv run python -m sphinx -b typst tests/fixtures/bld03_unhashable_docname_gate /tmp/verify47-e` | Exit 0. Output contains `produces no wrapper file`, contains neither `TypeError` nor `unhashable`. Both `index.typ` and `real.typ` (the well-formed sibling's wrapper) exist on disk. | ✓ PASS — gap closed |
| Gap 9b / CR-01 fix, uncaught-crash mode, `-b typstpdf` | `uv run python -m sphinx -b typstpdf tests/fixtures/bld03_unhashable_docname_gate /tmp/verify47-e-pdf` | `ExtensionError: typstpdf: 1 master document(s) failed: ['weird']: typst_documents entry has a non-str docname: ['weird'] ...` — graceful, no `TypeError`. `real.pdf` exists and was generated. | ✓ PASS — gap closed |
| New regression gate | `uv run pytest tests/test_master_include_set_predicate_gate.py -v` | 8/8 passed, zero xfail/xpass | ✓ PASS |
| Four previously-wired sites, zero source diff | `uv run pytest tests/test_collision_predicate_completeness_gate.py tests/test_missing_and_malformed_master_gate.py tests/test_non_str_docname_gate.py tests/test_xref_orphan_degrade_render_gate.py -q` | 25 passed (0 failures) | ✓ PASS |
| WR-01 (builder-side) closure | `git grep -c '_resolve_output_stem' -- 'typsphinx/'` and `hasattr()` | Zero hits; `hasattr` → `False` | ✓ PASS |
| Retargeted OUT-01/OUT-02 unit coverage | `uv run pytest tests/test_builder_output_stem.py --collect-only -q` / `-q` | 25 collected, 25 passed | ✓ PASS |
| Scope of functional diff | `git diff 80043b3^..HEAD -- typsphinx/builder.py \| grep -vE docstring/comment lines` | Only the `masters = [...]` filter expression and the `_resolve_output_stem()` deletion are functional; everything else in the diff is prose | ✓ PASS |
| Full existing suite | `uv run pytest -q` | `1039 passed, 5 skipped` in 202.5s | ✓ PASS |
| Lint/type gates | `uv run black --check .` / `uv run mypy typsphinx/` | Both clean (`ruff` unrunnable in this NixOS sandbox per environment note; CI is authoritative for it, and 47-CI-EVIDENCE.md records a prior green CI run including the lint lane) | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|----------------|--------------|--------|----------|
| COMP-01 | 47-01, 47-02, 47-04..09 | Docname-named content file, no template | ✓ SATISFIED | See truth #1 |
| COMP-02 | 47-01, 47-02, 47-04..09 | Wrapper at resolved target path, template + include | ✓ SATISFIED | See truth #2 |
| COMP-03 | 47-01, 47-02 | Nested master builds without `file not found` (B-1) | ✓ SATISFIED | See truth #3 |
| COMP-04 | 47-01, 47-02 | No mid-body template re-expansion (B-2) | ✓ SATISFIED | See truth #4 |
| OUT-01 | 47-02, 47-03, 47-14 | Target as path relative to outdir | ✓ SATISFIED | See truth #5 — re-anchored by 47-14 onto the live resolver |
| OUT-02 | 47-02, 47-03, 47-10, 47-14 | Escaping target refused, safe fallback | ✓ SATISFIED | See truth #6 — re-anchored by 47-14 |
| OUT-03 | 47-01, 47-02, 47-08 | Content files docname-derived regardless of wrapper placement | ✓ SATISFIED | See truth #7 |
| BLD-02 | 47-01, 47-08, 47-09, 47-11 | Duplicate target collision detected and reported | ✓ SATISFIED | See truth #8 |
| BLD-03 | 47-01, 47-04..07, 47-08, 47-09, 47-11, 47-13 | Wrapper/content self-collision detected; single-predicate ownership across all consumers | ✓ SATISFIED (was ⚠️ PARTIALLY, closed this pass) | See truths #9 and #9b — the fifth site is now wired and independently reproduced end-to-end on both builders. |
| BLD-04 | 47-01, 47-09, 47-10 | Case-insensitive collision detection | ✓ SATISFIED | See truth #10 |

**No orphaned requirements** — REQUIREMENTS.md's phase-mapping table assigns exactly these 10 IDs
to Phase 47, matching the union of every plan's `requirements:` frontmatter field, including
47-13's `[BLD-03]` and 47-14's `[OUT-01, OUT-02, BLD-02]`.

**Bookkeeping note:** `.planning/REQUIREMENTS.md` currently shows BLD-03 as `[ ]`/`Pending`,
correctly so at the time plan 47-14 wrote it (BLD-03's fix had not yet been measured). This report
is that measurement, and finds BLD-03 genuinely satisfied — its checkbox and phase-mapping row
should flip to `[x]`/`Complete` as this report's direct consequence, bringing Phase 47 to 10/10.
This is bookkeeping, not a phase-goal defect, and does not affect the `passed` status below.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `tests/test_master_include_set_predicate_gate.py` | 27-31, ~161-162, ~256-257 | Module docstring and two class docstrings still describe the pre-fix RED as being "recorded ... as `xfail(strict=True)`" and describe the in-body `TypstBuilder` import as landing "as an xfail" on a signature change — but the fix commit (`e422bfb`) removed all six `xfail` markers from the file, and `grep -n xfail tests/test_master_include_set_predicate_gate.py` confirms zero `@pytest.mark.xfail` decorators remain (only prose references). Independently confirmed real, matching `47-REVIEW.md`'s WR-02 finding exactly. | ⚠️ Warning | Purely a documentation-staleness issue — all 8 tests pass unconditionally today and the underlying fix is correct. A future maintainer searching for the described `xfail` markers while triaging a failure would not find them; the verbatim pre-fix transcripts remain accurate in `47-GAP2-RED-EVIDENCE.md`, which the same docstring correctly points at. Not blocking; no debt-marker (TBD/FIXME/XXX) present, so the debt-marker gate does not fire. |

No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` debt markers found in any file this
verification pass inspected (`typsphinx/builder.py`, the two new gap-closure test modules, the four
new fixture `conf.py` files, `tests/test_two_layer_output_gate.py`, `tests/test_corpus_gate.py`,
`tests/fixtures/entry_title_author_render_gate/conf.py`). The two `TODO-01`/`todo_node` hits in
`tests/test_corpus_gate.py` are a requirement-ID reference and a docutils node-type name, not debt
markers. No debt-marker gate violation.

### Human Verification Required

None. All gap-closure claims (the fifth-site predicate wiring, both CR-01 failure modes, the
builder-side WR-01 deletion) are deterministic and were reproduced directly by this verification
pass with real `sphinx-build` subprocess runs and direct source reads — not inferred from
`47-REVIEW.md`'s, the SUMMARYs', or the prior `47-VERIFICATION.md`'s narrative.

### Gaps Summary

No gaps remain. The one BLOCKER carried forward from the prior verification pass — gap 9b /
`47-REVIEW.md` CR-01, `_compute_master_included_docnames()`'s bare `if entry` filter bypassing the
shared entry-usability predicate — is genuinely closed by plan `47-13`, independently reproduced in
this pass with four live `sphinx-build` subprocess runs (two fixtures × two builders) plus a direct
read of the changed filter expression and the corrected five-consumer docstring. Plan `47-14`'s
non-blocking obligations (the builder-side `_resolve_output_stem()` dead-code deletion, mirroring
47-12's writer-side WR-01 closure, and the `BLD-02` requirement-checkbox correction) were also
independently confirmed: zero references to the deleted resolver remain anywhere under `typsphinx/`,
its 22 surviving test semantics are retargeted onto the live resolvers with expected values
verbatim (spot-checked), and its 3 deletions carry recorded rationale in the module docstring.

Every truth verified in the prior passes was re-measured rather than assumed to survive, because
the deletion of `_resolve_output_stem()` touched the evidence trail for OUT-01/OUT-02 directly; no
regression was found. The full suite (1039 passed, 5 skipped) exactly matches both closure plans'
own closing measurements, and `black`/`mypy` are clean.

Two informational, non-blocking items are recorded for future cleanup, neither a phase-goal defect:
`47-REVIEW.md`'s new WR-02 finding (a stale `xfail`-describing docstring in the new gate module,
confirmed still present) and `.planning/REQUIREMENTS.md`'s BLD-03 checkbox, which this report's own
measurement now makes ready to flip to `[x]`/`Complete`.

**Phase 47's goal is achieved: `_is_master_document()` is gone (confirmed absent from
`typsphinx/writer.py`/`typsphinx/builder.py`/`typsphinx/translator.py` by grep in this and prior
passes), B-1 and B-2 are closed, every "two logical files want one physical path" case is detected
and reported rather than silently overwritten — including, as of this pass, at the fifth site that
had bypassed that guarantee — and all 10 Phase 47 requirement IDs are genuinely satisfied.**

---

_Verified: 2026-08-12T00:00:00Z_
_Verifier: Claude (gsd-verifier)_
