---
phase: 20-signature-token-spacing-cluster-b
verified: 2026-07-20T12:15:00Z
status: passed
score: 4/4 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 20: Signature Token Spacing (Cluster B) Verification Report

**Phase Goal:** Intra-signature token spacing that is currently swallowed inside and around
signature/field tokens is restored, so Python and C/C++ signatures and object-description fields
read with correct inter-token spacing matching the `-b html` / `-b text` authority.
**Verified:** 2026-07-20T12:15:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `desc_annotation` "class "/"exception " keyword prefix keeps its trailing space on every `py:class`/`py:exception`/`autoclass` (FID-07) | VERIFIED | `visit_desc_sig_space`/`depart_desc_sig_space` reduced to `pass`/`pass` at translator.py:4825-4831 (append+SkipNode short-circuit gone, byte-shape-identical to sibling `desc_sig_keyword` pass/pass at 4817-4823). `tests/test_desc_sig_space_render_gate.py::test_pdf_extracted_text_has_no_merged_tokens` PASSED (real `-b typstpdf` compile + pypdf extracted text asserts `"class sphinx"` present, `"classsphinx"` absent). |
| 2 | C/C++ `desc_signature` and inline `c/cpp:expr` preserve all inter-token spaces: "Py_ssize_tnitems" → "Py_ssize_t nitems" (FID-08) | VERIFIED | Same pass/pass fix (single shared root cause with FID-07, per plan). `tests/test_desc_sig_space_render_gate.py` structural `.typ` assert (`text("PyObject")\ntext(" ")\ntext("*")\ntext("PyType_GenericAlloc")`) and pypdf assert (`"Py_ssize_t nitems"` present, `"Py_ssize_tnitems"` absent, `"a * f(a)"` present for inline cpp:expr) both PASSED. |
| 3 | `field_list` `:type:`/`:default:` fields render with colon-space and preserved field boundaries: "Type:int (a number)Default:42" → "Type: int (a number)  Default: 42" (FID-09) | VERIFIED | `depart_field_name` at translator.py:4701-4712 emits `' + text(": "))\n'` (colon-space); new `depart_field` at translator.py:4671-4683 emits sibling-guarded `'\ntext("  ")\n'` via `node.next_node(descend=False, siblings=True)`. `tests/test_confval_field_spacing_render_gate.py::test_pdf_extracted_text_matches_pinned_sc3_string` PASSED — pypdf-extracted text contains the exact pinned string `"Type: int (a number)  Default: 42"` byte-for-byte. |
| 4 | Each spacing fix ships or extends a real `typst.compile()` regression fixture (GATE-01); zero new runtime deps, no `@preview` bump, 3-way version-sync surface untouched | VERIFIED | Two new GATE-01 fixtures (`tests/test_desc_sig_space_render_gate.py` + `tests/fixtures/desc_sig_space_render_gate/`; `tests/test_confval_field_spacing_render_gate.py` + `tests/fixtures/confval_field_spacing_render_gate/`), all 7 phase-relevant gate tests pass. `git diff` across phase 20 commits touches only `typsphinx/translator.py` + `tests/**`; `writer.py`/`template_engine.py`/`templates/base.typ`/`pyproject.toml` are empty diffs (confirmed via `git diff --name-only`). |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/translator.py` :: `visit_desc_sig_space`/`depart_desc_sig_space` | reduced to `pass`/`pass` | VERIFIED | Lines 4825-4831; no `SkipNode`, no `self.body.append(" ")`; identical shape to sibling `desc_sig_keyword` handlers. |
| `typsphinx/translator.py` :: `depart_field_name` | colon becomes colon-space | VERIFIED | Line 4707: `self.body.append(' + text(": "))\n')`. |
| `typsphinx/translator.py` :: `depart_field` | emits sibling-guarded inter-field two-space | VERIFIED | Lines 4671-4683: guarded by `node.next_node(descend=False, siblings=True)`, emits `'\ntext("  ")\n'`. |
| `tests/test_desc_sig_space_render_gate.py` | GATE-01 render-gate (structural + compile + pypdf) | VERIFIED | Exists (10284 bytes), 2 tests, both PASSED. |
| `tests/fixtures/desc_sig_space_render_gate/{conf.py,index.rst}` | offline fixture project | VERIFIED | Both exist; `index.rst` contains `py:class`, `c:function`, inline `cpp:expr` repros. |
| `tests/test_confval_field_spacing_render_gate.py` | GATE-01 render-gate (structural + compile + pypdf) | VERIFIED | Exists (8627 bytes), 2 tests, both PASSED. |
| `tests/fixtures/confval_field_spacing_render_gate/{conf.py,index.rst}` | offline fixture project | VERIFIED | Both exist; uses the audit's no-blank-line `.. confval:: the_answer` repro. |
| `tests/test_field_list_in_list_item_render_gate.py` | locked colon assertion updated to colon-space form | VERIFIED | Line 171: `'strong(text("Author") + text(": "))'` (colon-space); exhaustive `grep -n 'text(":")' tests/*.py` returns only a docstring reference (no code assertion) in `test_confval_field_spacing_render_gate.py`. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `visit_desc_sig_space` (now pass) | `visit_Text` dispatch | node's `Text(" ")` child streams through unimpeded | WIRED | Confirmed via passing pypdf adjacency asserts — the emitted content-space actually renders in the compiled PDF, not just present in source. |
| `depart_field`/`depart_field_name` | rendered PDF | direct `self.body.append` emission, no intermediate helper | WIRED | Confirmed via passing pypdf exact-string assert against the pinned SC#3 string. |

### Behavioral Spot-Checks / Probe Execution

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| FID-07/08 gate (structural + real compile + pypdf) | `.venv/bin/python -m pytest tests/test_desc_sig_space_render_gate.py -v` | 2 passed | PASS |
| FID-09 gate (structural + real compile + pypdf exact string) | `.venv/bin/python -m pytest tests/test_confval_field_spacing_render_gate.py -v` | 2 passed | PASS |
| Regression: field-list locked assertion, concat gate | `.venv/bin/python -m pytest tests/test_field_list_in_list_item_render_gate.py tests/test_desc_signature_concat_render_gate.py -v` | 3 passed | PASS |
| Full fast suite (regression) | `.venv/bin/python -m pytest tests/ -m "not slow" -q` | 487 passed, 23 deselected | PASS |
| Lint / format / types | `black --check typsphinx/translator.py`, `ruff check typsphinx/translator.py`, `mypy typsphinx/` | all clean | PASS |
| Version-sync / dependency invariant | `git diff --name-only` across phase 20 commits vs `writer.py`/`template_engine.py`/`templates/base.typ`/`pyproject.toml` | empty | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| FID-07 | 20-01 | `class `/`exception ` annotation prefix trailing space | SATISFIED | pass/pass fix + passing GATE-01 pypdf adjacency assert; REQUIREMENTS.md marked Complete. |
| FID-08 | 20-01 | C/C++ desc_signature + inline cpp:expr inter-token spaces | SATISFIED | Same fix + passing structural/pypdf asserts covering pointer, type-to-identifier, and operator spacing; REQUIREMENTS.md marked Complete. |
| FID-09 | 20-02 | field_list `:type:`/`:default:` colon-space + inter-field boundary | SATISFIED | Two independent edits + passing GATE-01 exact pinned-string assert; REQUIREMENTS.md marked Complete. |

No orphaned requirements — `.planning/REQUIREMENTS.md` maps only FID-07/08/09 to Phase 20, and all three appear in plan frontmatter (`20-01-PLAN.md requirements: [FID-07, FID-08]`, `20-02-PLAN.md requirements: [FID-09]`).

### Anti-Patterns Found

None. Scanned all phase-modified files (`typsphinx/translator.py`, both new test files, both new fixture pairs) for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER`. One match (`TODO-01` at translator.py:3983) is pre-existing, unrelated code (outside this phase's diff hunks, confirmed via `git diff a8a59ad~1..HEAD -- typsphinx/translator.py`) — not introduced by this phase.

### Human Verification Required

None. All truths are verified by real `-b typstpdf` compiles with pypdf extracted-text adjacency/exact-string asserts, which is stronger evidence than visual/manual review for this class of change (glyph-level rendered spacing, not layout/UX).

### Gaps Summary

No gaps. All 4 ROADMAP Success Criteria for Phase 20 are verified against actual code (not SUMMARY claims): both `desc_sig_space` handlers are genuinely reduced to `pass`/`pass` (verified by reading translator.py directly), `depart_field_name`/`depart_field` genuinely emit the colon-space and inter-field double-space (verified by reading translator.py directly), both new GATE-01 fixtures exist and pass when executed in this session (not just per SUMMARY.md's self-report), the pre-existing locked colon assertion was genuinely updated (verified by reading the test file), the full fast suite (487 tests) passes with zero regressions, lint/format/type checks are clean, and the milestone invariant (no version-sync-surface touch, no new dependency) holds via direct `git diff` inspection.

---

*Verified: 2026-07-20T12:15:00Z*
*Verifier: Claude (gsd-verifier)*
