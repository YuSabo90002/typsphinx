---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
verified: 2026-08-11T13:14:48Z
status: gaps_found
score: 8/10 must-haves verified
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "BLD-02: Two typst_documents entries resolving to the same target path are detected and reported instead of silently dropping one master's body"
    status: failed
    reason: >
      `_collision_key()` (typsphinx/builder.py ~line 403) folds `\` to `/` and `casefold()`s the
      result, but never applies `posixpath.normpath()`. `_resolve_target_stem()` returns a
      path-bearing target AS-IS (OUT-01), so two textually-different-but-physically-identical
      targets (e.g. `"./manual.typ"` vs `"manual.typ"`) produce two DIFFERENT collision keys and
      the validator never raises. Independently reproduced against this checkout (not taken on
      faith from 47-REVIEW.md): `typst_documents = [("index", "./manual.typ", "T1", "A1"),
      ("other", "manual.typ", "T2", "A2")]` with `-b typst` builds exit 0, the log claims "wrote 2
      wrapper file(s) -- compile these: ./manual.typ, manual.typ", but only ONE physical
      `manual.typ` exists on disk (the `index` entry's wrapper was silently overwritten by
      `other`'s, with no error, no warning naming the collision). This is precisely the
      warn-or-not-and-silently-overwrite failure the phase's whole collision validator was built
      to eliminate.
    artifacts:
      - path: typsphinx/builder.py
        issue: >
          `_collision_key()` never normalizes path SHAPE (redundant `./`, doubled `//`, embedded
          `/./`) before comparing — only case and separator style. Its own docstring's claim ("a
          bare `==` on two raw path strings can never creep back in and silently miss a
          collision") is false for this shape class.
    missing:
      - "Normalize path shape with posixpath.normpath() inside _collision_key() before casefold()."
      - "Regression fixture/unit test for a './'-prefixed (and doubled-separator) collision shape, per 47-REVIEW.md CR-02's suggested fix."
  - truth: "BLD-03: A wrapper target that collides with a content file's own path is detected"
    status: failed
    reason: >
      `_validate_output_path_collisions()` treats any `typst_documents` entry with `len(entry) < 2`
      as malformed and skips it WITHOUT registering a claim — by stated design, deferring reporting
      to `TypstPDFBuilder.finish()`. But `_write_typst_files()` (the method that actually writes
      wrapper files, invoked from `write_doc()` for every docname, long before `finish()` ever
      runs) has NO equivalent length guard — its loop only checks `entry[0] != docname`.
      Independently reproduced against this checkout: `typst_documents = [("index",)]` with
      `-b typst` and one `index.rst` carrying a content sentinel builds successfully (exit 0, only
      an unrelated "empty typst_documents target name" WARNING — no collision error at all), and
      `index.typ` on disk ends up containing the wrapper (template + a self-referential
      `#include("index.typ")`) with the docname's real translated content — including the sentinel
      — completely and silently destroyed. The plain `typst` builder never surfaces this at all;
      `-b typstpdf` only surfaces it later as a `TypstError: cyclic import` at compile time, which
      does not help a user who never runs the PDF builder.
    artifacts:
      - path: typsphinx/builder.py
        issue: >
          `_write_typst_files()`'s wrapper-matching loop (~line 897-899) lacks the validator's
          `len(entry) < 2` malformed-entry tolerance, so a 1-element entry the validator silently
          skips is still treated as a real wrapper-producing entry at write time, landing at the
          bare docname stem — identical to that docname's own content path.
    missing:
      - "Give _write_typst_files()'s wrapper loop (and TypstPDFBuilder.finish()) the same malformed-entry guard the validator applies, or extract one shared _is_usable_typst_documents_entry() helper both call, per 47-REVIEW.md CR-01's suggested fix."
      - "Regression fixture/unit test for a 1-element (or otherwise under-length) typst_documents entry naming a real docname."
human_verification: []
---

# Phase 47: Two-Layer Output — Content/Wrapper Split, Target-as-Path, Collision Detection Verification Report

**Phase Goal:** The unit of output stops being "one `.typ` per docname whose shape depends on
whether that docname is a master." Every document gets a docname-named, template-less **content**
file; every `typst_documents` entry gets a **wrapper** file carrying the template and the include
of its master's content. B-1 and B-2 close, and any two logical files wanting one physical path
are reported instead of silently overwritten.

**Verified:** 2026-08-11T13:14:48Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | COMP-01: every document written as a docname-named content `.typ` with no template applied | ✓ VERIFIED | Independently reproduced (`-b typstpdf`, nested-master fixture): `index.typ`/`guide/index.typ` carry only the D-06 preamble, no `#show: project.with(`. Real subprocess test `test_comp01_content_file_has_no_template` passes. |
| 2 | COMP-02: each `typst_documents` entry produces a wrapper `.typ` at its resolved target path, carrying template + include | ✓ VERIFIED | Independently reproduced: `outer.typ` and `manuals/guide.typ` both written, both carry `#show: project.with(...)` + `#include(...)`. `test_comp02_wrapper_file_has_template_and_include` passes. |
| 3 | COMP-03: a document that is also another master's toctree child builds/compiles without `file not found` (B-1) | ✓ VERIFIED | Independently reproduced: `-b typstpdf` two-master nested fixture (index→outer.typ, guide/index→manuals/guide.typ) compiled to `outer.pdf` and `manuals/guide.pdf` with no `TypstError`, exit 0. `test_comp03_b1_nested_master_compiles` passes. |
| 4 | COMP-04: an included master no longer re-expands its title page/`#outline()` into the parent's body (B-2) | ✓ VERIFIED | `test_comp04_b2_no_mid_body_template_reexpansion` is a real `typst.compile()` + `pypdf` structural assertion (exactly one `"Contents"` occurrence, no second title-page string) — inspected the assertion body directly, not just its pass/fail; it is non-vacuous. Passes. |
| 5 | OUT-01: a target is a path relative to the output directory (bare name → outdir root, explicit path → written where asked) | ✓ VERIFIED | Independently reproduced: `"manuals/guide.typ"` target wrote to `outdir/manuals/guide.typ` exactly, `"outer.typ"` wrote to the outdir root. |
| 6 | OUT-02: an escaping target (`..`, absolute, drive-qualified) is still refused with a warning + safe fallback | ✓ VERIFIED | Already marked `[x]` in REQUIREMENTS.md. `tests/test_out02_escape_target_gate.py` (3 real-subprocess shapes) passes locally; CI evidence (`47-CI-EVIDENCE.md`) shows all three shapes, including drive-qualified, executing and passing on both `windows-latest` and `macos-latest`, after a genuine Windows-only `ntpath` vs `posixpath` defect was triaged and fixed (`be4c4d5`). |
| 7 | OUT-03: content files stay docname-derived regardless of where their master's wrapper is written | ✓ VERIFIED | Independently reproduced: `guide/index`'s content stayed at `outdir/guide/index.typ` even though its wrapper target was `manuals/guide.typ` — no relocation. `test_out03_content_files_stay_docname_derived` passes. |
| 8 | BLD-02: two `typst_documents` entries resolving to the same target path are detected and reported | ✗ FAILED | Independently reproduced (see Gaps). `./manual.typ` vs `manual.typ` silently collide; validator's own unit tests (`TestCollisionKeyUnit`) never exercise a path-shape variant, only case/separator-style. |
| 9 | BLD-03: a wrapper target colliding with a content file's own path is detected | ✗ FAILED | Independently reproduced (see Gaps). A 1-element `typst_documents` entry destroys the docname's own content silently; the existing gate fixtures (`bld03_self_collision_gate`) only exercise the ≥2-element self-collision shape (`("index", "index.typ", …)`), never the under-length shape. |
| 10 | BLD-04: collision detection behaves identically on case-insensitive filesystems | ✓ VERIFIED | `_collision_key()` casefolds correctly (confirmed by reading the code and by `TestCollisionKeyUnit`); CI evidence quotes `test_bld04_case_collision_rejected_typst`/`_typstpdf` and `test_collision_key_folds_case_but_not_unicode_normalization` PASSED (not skipped) on both `windows-latest` and `macos-latest` in run `31492380799`. |

**Score:** 8/10 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/builder.py::_validate_output_path_collisions` | Pre-write validator catching all four collision kinds | ⚠️ PARTIAL | Exists, substantive, wired at the top of `write()` — but has a structural blind spot: silently skips any `len(entry) < 2` entry without claiming it, so it cannot detect BLD-03's under-length-entry self-collision shape. |
| `typsphinx/builder.py::_collision_key` | Comparison-only normalization for collision keys | ⚠️ PARTIAL | Exists, substantive, wired into every claim/lookup — but only folds case and backslash-vs-forward-slash separator style, never path SHAPE (`posixpath.normpath`), so it cannot detect BLD-02's `./`-prefixed collision shape. |
| `typsphinx/builder.py::_write_typst_files` | Single shared write path for content + wrapper files | ✓ VERIFIED (content path) / ✗ GAP (wrapper-matching loop) | Content-file write is unconditional and correct. Wrapper-matching loop (`for entry in typst_documents: if not entry or entry[0] != docname: continue`) has no malformed-entry guard mirroring the validator's, so a validator-skipped entry is still written as a real wrapper — this is the write-time half of the BLD-03 gap. |
| `typsphinx/writer.py::render_wrapper` / `compute_content_include_path` / `_compute_template_import_path` | Wrapper body assembly (template + include, correct relative paths) | ✓ VERIFIED | Independently reproduced correct `../guide/index.typ` / `../_template.typ` computation for the nested fixture; matches `47-EXPECTED-STRUCTURE.md`'s hand-derived arithmetic exactly. |
| `tests/test_two_layer_output_gate.py`, `tests/test_collision_validator_gate.py`, `tests/test_typst_documents_collision_gate.py`, `tests/test_builder_output_stem.py`, `tests/test_out02_escape_target_gate.py` | Real-subprocess regression gates | ✓ VERIFIED (as far as they go) | All pass (24 + 31 tests re-run locally). None of them exercise the `./`-prefixed collision shape or the under-length-entry shape — this is exactly why 1031 green did not catch either CR-01 or CR-02. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `_validate_output_path_collisions()` | `write()` | Called once, before the write loop | ✓ WIRED (but incomplete coverage) | Confirmed at `builder.py:641`. Structurally sound for the shapes it does cover; does not cover the two shapes above. |
| `_collision_key()` | every claim/lookup in `_validate_output_path_collisions()` | Single normalization function | ✓ WIRED (but incomplete normalization) | All map insertions/lookups do go through it — the gap is inside the function's own normalization completeness, not its wiring. |
| validator on `TypstBuilder` | `TypstPDFBuilder` | Inheritance | ✓ WIRED | `TypstPDFBuilder` does not override `_validate_output_path_collisions` or `_write_typst_files`; both gaps reproduce identically on `-b typstpdf` (confirmed for CR-01: `-b typstpdf` self-collision surfaces later as `TypstError: cyclic import`, not at write time — worse for discoverability, not better). |

### Behavioral Spot-Checks (independently run against this checkout)

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| BLD-03 self-collision, 1-element entry (`typst_documents = [("index",)]`, `-b typst`) | Real `sphinx-build` in a throwaway fixture | Exit 0, only an unrelated WARNING; `index.typ` on disk is the wrapper with a self-referential `#include("index.typ")`; content sentinel `CR01-CONTENT-SENTINEL-MARKER` count in output = 0 | ✗ FAIL — no collision detected, content silently destroyed |
| BLD-02 duplicate target via unnormalized path shape (`"./manual.typ"` vs `"manual.typ"`) | Real `sphinx-build` in a throwaway fixture | Exit 0, log claims "wrote 2 wrapper file(s) -- compile these: ./manual.typ, manual.typ"; only ONE `manual.typ` exists on disk, containing entry `other`'s wrapper only | ✗ FAIL — no collision detected, one wrapper silently clobbered |
| COMP-01/02/03/OUT-01/OUT-03 nested two-master build (`-b typstpdf`) | Real `sphinx-build` in a throwaway fixture | Exit 0; `index.typ`, `guide/index.typ` (content, docname-derived), `outer.typ`, `manuals/guide.typ` (wrappers, target-derived) all correct; `outer.pdf` and `manuals/guide.pdf` both compiled | ✓ PASS |
| Full existing gate suite for this phase | `uv run pytest tests/test_two_layer_output_gate.py tests/test_collision_validator_gate.py tests/test_typst_documents_collision_gate.py tests/test_builder_output_stem.py tests/test_out02_escape_target_gate.py -q` | 55 passed | ✓ PASS (as far as the suite's own shapes go — does not cover the two failing shapes above) |
| `_is_master_document` gone repo-wide | `grep -rn "_is_master_document" typsphinx/ tests/` | No hits in tracked source | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|----------------|--------------|--------|----------|
| COMP-01 | 47-01, 47-02, 47-04..09 | Docname-named content file, no template | ✓ SATISFIED | See truth #1 |
| COMP-02 | 47-01, 47-02, 47-04..09 | Wrapper at resolved target path, template + include | ✓ SATISFIED | See truth #2 |
| COMP-03 | 47-01, 47-02 | Nested master builds without `file not found` (B-1) | ✓ SATISFIED | See truth #3 |
| COMP-04 | 47-01, 47-02 | No mid-body template re-expansion (B-2) | ✓ SATISFIED | See truth #4 |
| OUT-01 | 47-02, 47-03 | Target as path relative to outdir | ✓ SATISFIED | See truth #5 |
| OUT-02 | 47-02, 47-03, 47-10 | Escaping target refused, safe fallback | ✓ SATISFIED | See truth #6; already `[x]` in REQUIREMENTS.md |
| OUT-03 | 47-01, 47-02, 47-08 | Content files docname-derived regardless of wrapper placement | ✓ SATISFIED | See truth #7 |
| BLD-02 | 47-01, 47-08, 47-09 | Duplicate target collision detected and reported | ✗ BLOCKED | See gap #1 — false negative on unnormalized-but-equivalent path shapes |
| BLD-03 | 47-01, 47-04..07, 47-08, 47-09 | Wrapper/content self-collision detected | ✗ BLOCKED | See gap #2 — false negative on under-length `typst_documents` entries |
| BLD-04 | 47-01, 47-09, 47-10 | Case-insensitive collision detection | ✓ SATISFIED | See truth #10; already `[x]` in REQUIREMENTS.md |

**No orphaned requirements** — REQUIREMENTS.md's phase-mapping table (lines ~242-261) assigns exactly these 10 IDs to Phase 47, matching the union of every plan's `requirements:` frontmatter field exactly.

**Bookkeeping note (not a phase-goal gap):** REQUIREMENTS.md currently shows only OUT-02 and BLD-04 checked `[x]`; the other 8 IDs are unchecked because worktree executors could not reach `gsd-tools.cjs` to mark them. Per this verification, COMP-01, COMP-02, COMP-03, COMP-04, OUT-01, and OUT-03 are genuinely satisfied and their checkboxes should be updated to `[x]` once the two gaps below are closed and this phase is re-verified; BLD-02 and BLD-03 should stay unchecked until the underlying defects are fixed.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `typsphinx/writer.py` | 104-156 | `_resolve_entry_element()` is fully implemented and unit-tested (`tests/test_entry_metadata_precedence.py`) but has zero production call sites — `render_wrapper()` uses `_entry_element_value()` exclusively (confirmed: `grep -rn "_resolve_entry_element(" typsphinx/*.py` → only its own definition) | ⚠️ Warning | Dead code with passing tests gives false confidence that this logic is exercised in a real build. Does not affect any requirement's correctness (WR-01 in `47-REVIEW.md`), but should be deleted or explicitly documented as retained-for-reference. |

No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` markers found in `typsphinx/builder.py` or `typsphinx/writer.py`. No debt-marker gate violation.

### Human Verification Required

None. Both gaps are deterministic, reproduced with a real `sphinx-build` subprocess run directly by this verification (not inferred from `47-REVIEW.md`'s narrative), and require no runtime/visual/UX judgment to confirm.

### Gaps Summary

The phase is **substantially but not fully achieved**. Eight of the ten requirement IDs (COMP-01
through COMP-04, OUT-01 through OUT-03, BLD-04) are genuinely satisfied, independently re-proven
against this checkout with real `sphinx-build`/`typst.compile()`/`pypdf` evidence — not merely
inferred from the green 1031-test suite or SUMMARY.md's narrative. The content/wrapper split, the
target-as-path reversal, the security half of the escape guard, and the case-insensitive-filesystem
collision handling all hold up under direct reproduction, including on real Windows/macOS CI lanes.

However, the phase's own headline claim for its fourth success criterion — "every 'two logical
files want one physical path' case is loud, and both policies are decided before code is
written... never silently dropping one master's body" — is **not true for two real, common-enough
input shapes**:

- **BLD-03 (self-collision detection)** silently fails for a `typst_documents` entry with fewer
  than 2 elements naming a real docname (e.g. `[("index",)]`), which the malformed-entry write
  loop still treats as a valid wrapper-producing entry — destroying that docname's own translated
  content with no error, only an unrelated warning about the empty target name.
- **BLD-02 (duplicate-target detection)** silently fails whenever two targets are textually
  different but resolve to the same physical file once written (e.g. a redundant `./` prefix),
  because `_collision_key()` only normalizes case and separator STYLE, never path SHAPE.

Both were independently reproduced against this exact checkout (not taken on the review's word),
producing exit-0 builds with silent data loss — precisely the failure mode the phase's own
`_validate_output_path_collisions()` docstring claims is now structurally impossible. This is a
**must-have failure**, not a nice-to-have: BLD-02 and BLD-03 are named, explicit ROADMAP success
criteria for this phase (SC#4) and explicit PLAN 47-09 `must_haves.truths` (items 1 and 3), and the
1031-green full suite did not catch either because no fixture exercises either input shape — a
"laundered gate" in the sense binding constraint #6 warns against, though here the omission is in
what shapes the tests choose to cover rather than in the assertions themselves.

The fixes identified by `47-REVIEW.md` (CR-01, CR-02) are narrow and precisely located
(`typsphinx/builder.py`'s `_collision_key()` and `_write_typst_files()`'s wrapper loop); this is a
closure-plan-sized gap, not a phase redesign.

---

_Verified: 2026-08-11T13:14:48Z_
_Verifier: Claude (gsd-verifier)_
