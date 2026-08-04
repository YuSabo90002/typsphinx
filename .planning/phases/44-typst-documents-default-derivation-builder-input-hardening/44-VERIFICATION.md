---
phase: 44-typst-documents-default-derivation-builder-input-hardening
verified: 2026-08-04T08:00:00Z
status: passed
score: 6/6 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 5/6
  gaps_closed:
    - "A user who follows the Quick Start exactly gets a PDF, without a reachable configuration-free path to silent content loss or a hard build failure (CR-01)."
  gaps_remaining: []
  regressions: []
prohibitions_flagged: []
human_verification: []
---

# Phase 44: `typst_documents` Default Derivation + Builder Input Hardening Verification Report

**Phase Goal:** A user who follows the Quick Start exactly gets a PDF. Today `typst_documents`
defaults to `[]` and `TypstPDFBuilder.finish()` returns early on it, so `sphinx-build -b typstpdf`
exits 0, emits one `WARNING`, and produces zero PDFs. This phase derives a Sphinx-native default
(mirroring `latex_documents`) and hardens `TypstPDFBuilder.finish()` against a non-`str` docname
(BLD-01).
**Verified:** 2026-08-04T08:00:00Z
**Status:** passed
**Re-verification:** Yes — after gap closure (plan 44-05, closing CR-01)

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC#1 — a project whose `conf.py` never mentions `typst_documents`, built with `sphinx-build -b typstpdf`, produces a PDF named `make_filename_from_project(project)`, warning gone | ✓ VERIFIED (regression-checked) | `44-GATE-EVIDENCE-01.md` §§1,3 (original evidence, unchanged); re-confirmed here via the full-suite re-run (`863 passed, 1 skipped`, includes `tests/test_default_typst_documents_gate.py`) and direct read of `typsphinx/builder.py:28-47` (`_default_typst_documents`), unchanged by plan 44-05 except for the docstring's added CR-01 sentence. |
| 2 | SC#2 — an explicit `typst_documents` always wins, producing exactly the targets it names and nothing else | ✓ VERIFIED (regression-checked) | `44-GATE-EVIDENCE-01.md` §5 (original evidence, unchanged); the `explicit_typst_documents_wins_gate` fixture is still exercised in the full-suite re-run. |
| 3 | SC#3 — a non-`str` docname reaching `TypstPDFBuilder.finish()` fails with an actionable typsphinx-level error naming the offending value, not a raw `TypeError` | ✓ VERIFIED (regression-checked) | `44-GATE-EVIDENCE-02.md` §§1-2 (original evidence, unchanged); guard read directly at `typsphinx/builder.py:966`, present and unmodified by plan 44-05. |
| 4 | SC#4 — the output-filename rename is measured, not assumed, and the measured pair is handed to Phase 46 as CHANGELOG source text | ✓ VERIFIED (regression-checked) | `44-GATE-EVIDENCE-03.md` §§1-9 and `44-GATE-EVIDENCE-04.md` §8 (original evidence, unchanged); the fixture that discharges SC#4 (`default_typst_documents_gate`, `project = "Quickstart Default Gate"`) is collision-free by construction, so plan 44-05's guard does not touch its output — confirmed by the full-suite re-run showing no change to this fixture's expected content. |
| 5 | SC#5 — every existing test that encoded the old `[]`-default is updated deliberately and traceably; full suite, `black`/`ruff`/`mypy`, and the full-corpus `-b typstpdf` gate are green | ✓ VERIFIED (re-measured) | Independently re-run by this verifier on current HEAD (`35d05ca`, main tree, not a worktree): `uv run python -m pytest -q` → `863 passed, 1 skipped in 79.37s` (the +8 over the `855 passed, 1 skipped` 44-04 baseline is exactly plan 44-05's new tests — 5 collision-gate subprocess tests + 3 unit tests); `uv run black --check .` → clean (`230 files would be left unchanged`); `uv run ruff check .` → `All checks passed!`; `uv run mypy typsphinx/` → `Success: no issues found in 6 source files`. No source file has changed since this suite ran (`git diff --name-only f891eee..HEAD -- typsphinx tests pyproject.toml` is empty), so the result still holds at the tip commit verified here. |
| 6 | A user who follows the Quick Start exactly gets a PDF, without a reachable configuration-free path to silent content loss or a hard build failure (phase goal statement; CR-01, closed by plan 44-05) | ✓ VERIFIED | **Gap closed.** Independently reproduced by this verifier against current HEAD, not merely re-read from `44-GATE-EVIDENCE-05.md` or `44-05-SUMMARY.md`: built `tests/fixtures/derived_docname_collision_gate` (`project = "Chapter 1"`, `index.rst` toctree-including `chapter1.rst`) with `uv run python -m sphinx -b typst`. Exit 0; BOTH `index.typ` and `chapter1.typ` present on disk; `grep -c UNIQUE-CHAPTER-MARKER-XYZ chapter1.typ` = 1 (the real chapter's body is intact, not overwritten); stderr contains `WARNING: typst_documents target name 'chapter1.typ' for docname 'index' collides with an existing document or the reserved template file -- falling back to 'index'`. Same fixture with `-b typstpdf`: exit 0; `index.pdf` produced, 19976 bytes, first four bytes `%PDF`; no `cyclic import` text anywhere in the output. `typsphinx/builder.py::_resolve_output_stem` (lines 264-283) read directly: the guard computes `effective = self._directory_preserving_relpath(docname, stem)`, compares against `getattr(self.env, "found_docs", None) or set()` and the reserved `"_template"` basename, warns, and falls back to the docname — exactly matching the fix sketch in `44-REVIEW.md`'s original CR-01 finding. `uv run python -m pytest tests/test_typst_documents_collision_gate.py tests/test_builder_output_stem.py -q` → `32 passed` (5 subprocess gate tests covering all four scenarios — derived-docname, derived-template, explicit-docname, explicit-template — plus 27 unit tests including the 3 new collision/edge-case ones). |

**Score:** 6/6 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/builder.py::_default_typst_documents` | Pure derivation callable | ✓ VERIFIED | Present at lines 28-47, unchanged by plan 44-05. |
| `typsphinx/__init__.py` registration | `add_config_value("typst_documents", _default_typst_documents, "html", [list])` | ✓ VERIFIED | Present, unchanged. |
| `typsphinx/builder.py` BLD-01 guard | `isinstance(docname, str)` guard | ✓ VERIFIED | Present at line 966, unchanged. |
| `typsphinx/builder.py` collision guard (CR-01 fix) | A check rejecting a resolved stem that collides with `self.env.found_docs` or `"_template"` | ✓ VERIFIED (was MISSING in prior verification) | Present at `typsphinx/builder.py:264-283`, inside `_resolve_output_stem`, read directly. Uses `self._directory_preserving_relpath(docname, stem)` as the comparison value (not the bare stem), matching planning measurement 1 in `44-05-PLAN.md` about nested docnames. Falls back to the docname with an f-string `logger.warning`, matching the sibling D-06/D-07 style. |
| `tests/test_typst_documents_collision_gate.py` | Real `sphinx-build` subprocess gate covering (docname collision x reserved-template clobber) x (derived-default path x explicit path) | ✓ VERIFIED | Exists, 5 tests, all pass independently (`uv run python -m pytest tests/test_typst_documents_collision_gate.py -q` → `5 passed`). |
| `tests/test_builder_output_stem.py` (extended) | 3 new unit tests for the collision guard and the `found_docs`-absent edge case | ✓ VERIFIED | `test_resolve_output_stem_falls_back_on_docname_collision`, `test_resolve_output_stem_falls_back_on_reserved_template_name`, `test_resolve_output_stem_tolerates_env_without_found_docs` all present and passing. |
| Four new fixture directories | `derived_docname_collision_gate`, `derived_template_collision_gate`, `explicit_docname_collision_gate`, `explicit_template_collision_gate` | ✓ VERIFIED | All four exist with the expected `conf.py`/`.rst` files; contents match the plan's described load-bearing properties (e.g. `derived_docname_collision_gate/conf.py` has no `typst_documents` line, `project = "Chapter 1"`). |
| `44-GATE-EVIDENCE-05.md` | RED/GREEN record + gap-closure verdict for both `missing:` items | ✓ VERIFIED | Sections 1-7 present; § 7's two-row verdict table marks both `missing:` items `GAP CLOSED` with test node ids that this verifier independently re-ran and confirmed pass. |
| `44-REVIEW.md` | Post-44-05 code review including a new finding, CR-02 | ✓ VERIFIED (see judgment below) | Present; CR-02 independently reproduced by this verifier (see "New Finding Outside Declared Scope" below). |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `typsphinx/__init__.py::setup` | `typsphinx/builder.py::_default_typst_documents` | `add_config_value` | ✓ WIRED | Unchanged, confirmed by direct read. |
| `_default_typst_documents` output / any explicit `typst_documents` target | `self.env.found_docs` / `"_template"` reserved name | collision check inside `_resolve_output_stem` | ✓ WIRED (was NOT_WIRED in prior verification) | `typsphinx/builder.py:274-283` reads `found_docs = getattr(self.env, "found_docs", None) or set()` and compares `effective` against it and against `"_template"`, warning and falling back. Both `TypstBuilder.write_doc` and `TypstPDFBuilder.finish` call this same normalization site, so `-b typst` and `-b typstpdf` cannot disagree. Confirmed by direct read and by independent build reproduction above. |
| `TypstPDFBuilder.finish` loop | terminal `ExtensionError` | non-str-docname failures append to `failures` | ✓ WIRED | Unchanged, confirmed by direct read. |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| CONF-08 | 44-01, 44-02, 44-03, 44-04, 44-05 | With `typst_documents` unset, `-b typstpdf` produces a PDF; derived from `root_doc`/`project`/`author`; explicit setting always wins; derivation is now also collision-safe | ✓ SATISFIED | Truths 1, 2, 5, 6 above. `.planning/REQUIREMENTS.md:73` marked `[x]`/`Complete` at line 179 — this flip (made by the 44-05 executor in commit `c8d0f84`, before this re-verification) is confirmed accurate by this verdict; no revert needed. |
| BLD-01 | 44-02, 44-04, 44-05 | A non-`str` docname reaching `finish()` fails with an actionable typsphinx-level error | ✓ SATISFIED | Truth 3 above. `.planning/REQUIREMENTS.md:87` marked `[x]`/`Complete` at line 180 — confirmed accurate. |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s "Phase 44" mappings cover exactly CONF-08 and BLD-01, and every plan (44-01 through 44-05) lists at least one of them in its `requirements:` frontmatter.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `typsphinx/builder.py` | 929 | `if not typst_documents:` also fires for `typst_documents = None`, but the message unconditionally asserts "explicitly set to an empty list" (WR-01) | ⚠️ Warning | Cosmetic/diagnostic-accuracy only. Owner-excluded from plan 44-05's scope; carried forward as a deferred note in `44-GATE-EVIDENCE-05.md` §7. Does not block the phase goal. |
| `tests/test_default_typst_documents_gate.py` | 120 | Vacuous assertion against old pre-phase wording (IN-01) | ℹ️ Info | Test-hygiene only; owner-excluded from plan 44-05's scope. Does not block the phase goal. |
| `typsphinx/builder.py` | 880-1039 | `write_doc()` and `finish()` both re-resolve the same docname's stem independently, so any warning branch (including the new CR-01 collision warning) logs twice under `-b typstpdf` (WR-02, new in `44-REVIEW.md`) | ⚠️ Warning | Cosmetic duplicate-logging only — behavior (warn + safe fallback) is correct; only the count is doubled. Does not block the phase goal or any SC. Not remediated by this phase; carried forward as a finding for a future phase or backlog. |
| `typsphinx/builder.py` | 156-288, 925-1039 | `_resolve_output_stem` and `finish()` are both large multi-concern functions, flagged as the kind of surface where a sibling collision case (CR-02) is easy to miss (IN-02, new in `44-REVIEW.md`) | ℹ️ Info | Maintainability note only, no functional defect. |

None of these rise to blocker severity; none contain unresolved `TBD`/`FIXME`/`XXX` markers (`grep -n -E "TBD|FIXME|XXX" typsphinx/builder.py tests/test_typst_documents_collision_gate.py tests/test_builder_output_stem.py` returns nothing).

### New Finding Outside Declared Scope — CR-02 (judged out of scope for Phase 44)

`44-REVIEW.md` (post-44-05 review) reports CR-02: two `typst_documents` entries whose **target names collide with each other** (neither is itself a docname) silently overwrite one master's output with the other's — `-b typst` exits 0 with zero warning, `-b typstpdf` reports "Generated PDF" twice for the same path with zero warning. This verifier independently reproduced it against current HEAD (not merely re-read from the review): a fixture with `typst_documents = [("index", "manual.typ", ...), ("other", "manual.typ", ...)]` and real `index.rst`/`other.rst` builds with `-b typst` at exit 0, no collision warning, writes only one `manual.typ`, and the `index` master's marker count in that file is `0` while `other`'s is `1` — matching the review's transcript exactly.

**Judgment: CR-02 is a real, reproducible defect, but it is out of scope for Phase 44's goal and its five ROADMAP Success Criteria, for these reasons:**

1. **Not reachable via the Quick Start path.** The phase goal is "a user who follows the Quick Start exactly gets a PDF" — i.e., `typst_documents` left unset, or set to a single explicit entry (SC#2's fixture). `_default_typst_documents` only ever derives one tuple (for `root_doc`), so it can never itself produce two colliding entries. CR-02 requires a user to deliberately author **two or more** explicit `typst_documents` entries with the same target name — an affirmative, non-default configuration action no Quick Start user takes.
2. **Pre-existing mechanism, not introduced by this phase.** The entry-lookup loop in `_resolve_output_stem` that CR-02 exploits (matching `entry[0] == docname` per explicit entry) predates the CONF-08 derivation — explicit `typst_documents` target names were already a feature (Issue #117, cited in the method's own docstring) before Phase 44 touched this method. Two explicit entries sharing a target could always collide this way, with or without a derived default.
3. **None of the five ROADMAP SCs mention multi-master explicit-vs-explicit collision detection** — SC#2 only requires a *single* explicit entry to win over the derived default; it does not test two explicit entries against each other.
4. **Already transparently recorded, not silently dropped.** Plan 44-05's own planning measurement 8 flagged this exact mechanism as "out of scope, recorded not planned" before execution, and `44-GATE-EVIDENCE-05.md` §7 lists it under "deferred notes" as a distinct mechanism from CR-01 that this phase's guard does not address.

This verifier's recommendation: **route CR-02 to a follow-up phase or the backlog** (e.g. an explicit-vs-explicit collision guard extending the same `_resolve_output_stem` site, per the review's own fix sketch using a per-build `_claimed_output_paths` map) rather than treating it as a Phase 44 blocker. It does not change this phase's `passed` verdict because it cannot fire on the zero-configuration or single-explicit-entry paths the phase goal and its SCs describe. WR-02 (double-logging of the same warning under `-b typstpdf`) is a related, lower-severity cosmetic finding from the same review, also deferred for the same reason (cosmetic only, not a data-loss/build-failure path).

### Human Verification Required

None. CR-01's closure is a code-level, deterministically-reproducible fix (guard present, wired, gate-tested, independently reproduced twice more by this verifier). CR-02 is likewise deterministic but judged out of scope above; it needs a planning decision (route to a phase), not human UAT.

### Gaps Summary

No gaps remain against Phase 44's goal or its five ROADMAP Success Criteria. The single gap from the prior verification (CR-01 — the derived default made a pre-existing collision mechanism reachable with zero configuration) is closed: the guard exists at the single normalization site (`_resolve_output_stem`), is wired into both the `-b typst` write path and the `-b typstpdf` read-back path, is gate-tested across all four scenario combinations named in the prior verification's `missing:` list, and was independently reproduced fixed by this verifier via real `sphinx-build` invocations (not merely re-read from `44-05-SUMMARY.md` or `44-GATE-EVIDENCE-05.md`). All five original ROADMAP Success Criteria remain independently verified on regression check, and the full suite/lint/type gate is green at `863 passed, 1 skipped` — exactly the 44-04 baseline (`855 passed, 1 skipped`) plus plan 44-05's 8 new tests, with no source change since that run.

A new finding, CR-02 (explicit-vs-explicit target collision, distinct mechanism from CR-01), surfaced in the post-44-05 code review and was independently reproduced by this verifier. It is judged out of scope for Phase 44 (see above) because it requires a deliberately duplicated explicit `typst_documents` configuration unreachable via the Quick Start path or any of the five SCs, and the mechanism predates this phase. It is recorded here, not silently dropped, so it can be routed to a follow-up phase or the backlog rather than lost.

---

*Verified: 2026-08-04T08:00:00Z*
*Verifier: Claude (gsd-verifier)*
