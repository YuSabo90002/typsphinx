---
phase: 40-citations-full-round-trip
plan: 05
subsystem: testing
tags: [sphinx, typst, docutils, citations, pytest, pypdf, regex]

requires:
  - phase: 40-citations-full-round-trip (plan 01)
    provides: "tests/test_citation_render_gate.py -- the 9-test gate this plan repairs, and 40-GATE-EVIDENCE-01.md's original classic-RED record"
  - phase: 40-citations-full-round-trip (plan 03)
    provides: "typsphinx/translator.py: visit_citation/depart_citation/visit_label (definition side) and the D-14 guarded own-ids anchor in visit_reference/depart_reference (citing side) -- the merged implementation this plan's corrected assertions measure against"
provides:
  - "tests/test_citation_render_gate.py: all four originally-diagnosed defective assertions corrected (two get_and_resolve_doctree tags= call sites, the layout marker-column measurement, the concat D-14 bracket-wrap tolerance), plus two further test-measurement defects the first four exposed once reachable (the D-14 own-anchor detection regex, and the single-backref marker-group check) -- 9/9 passing against the merged translator, and re-proved 9/9 RED against the pre-40-03 translator"
  - "40-GATE-EVIDENCE-01.md Section 8: a dated amendment recording all six corrections against measurement, with the original RED (Sections 1-7) byte-unchanged"
  - ".planning/REQUIREMENTS.md: CIT-02, CIT-03, CIT-04, CIT-05 ticked and their traceability rows moved to Complete -- all six CIT requirements now proven"
  - "Fixed the worktree's .venv/bin/uv shim (was a stale regular ELF from `uv sync`, not the NixOS-compatible symlink the earlier shim loop was supposed to create) -- unblocks the 4 integration test files that invoke `subprocess.run(['uv', 'run', 'sphinx-build', ...])` internally"
affects: ["40-04-citations-full-round-trip (final phase verification, if scheduled)"]

tech-stack:
  added: []
  patterns:
    - "Marker-column vs line-leading-whitespace: when a construct's first line carries a label cell ahead of the content marker (unlike test_rubric_indent_invariance.py's construct, where the marker IS the line's first glyph), measure line.index(marker_substring) not len(line) - len(line.lstrip(' '))"
    - "Detecting Typst label attachment across BOTH syntactic forms this translator uses -- the markup-mode bracket-postfix shorthand [... <label>] and the explicit #label(\"...\") function-call form -- since <name> is parser sugar for #label(\"name\") and both attach identically"
    - "Scanning raw .typ SOURCE text for a construct's own emission fragment (e.g. text(\" (\") for the 2+-backref marker group) rather than a regex shaped for the construct's COMPILED/rendered appearance, which may never occur verbatim in source"

key-files:
  created: []
  modified:
    - tests/test_citation_render_gate.py
    - .planning/phases/40-citations-full-round-trip/40-GATE-EVIDENCE-01.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Two additional test-measurement defects (beyond the plan's four orchestrator-diagnosed ones) were corrected in the same tests/test_citation_render_gate.py file, not deferred: _attached_anchor_tokens only recognised the <label> bracket shorthand and read D-14's real, working #label(\"...\") anchor as missing, and the single-backref D-03 guard's \\(\\d+\\) regex both false-positived on unrelated body prose (a publication year in parens) AND could never have matched the real 2+-marker shape in .typ source in the first place. Both were unreachable by the orchestrator's own single-pass measurement (masked by the tags= exception and the missing-grid RED respectively) and were discovered only by re-reproducing after each documented fix, exactly as this plan's own instructions require. Both are test-detection-precision defects, not translator defects -- confirmed by the real -b typstpdf compile passing clean in the same run -- and typsphinx/ could not be touched regardless, so correcting the test was the only path to this plan's own Task 2 acceptance bar of 9/9 passing."
  - "_leading_columns is corrected IN PLACE (renamed _marker_column) rather than given a sibling helper, because all six call sites of its sole caller (_find_page_and_column) want the same corrected quantity -- the marker's own start column, not the line's leading whitespace. No call site needed the old (wrong) semantics."
  - "The .venv/bin/uv shim gap (a stale regular ELF left over from `uv sync`, never actually replaced by a symlink because an earlier shim attempt's `command -v uv` self-resolved to that same stale .venv/bin/uv once .venv/bin was already first on this worktree's ambient PATH) was fixed inline as a Rule 3 blocking-issue auto-fix: it silently made 45 unrelated integration tests fail with the NixOS stub-loader error before the fix, and the fix (re-pointing the symlink at the resolved nix-store uv) is required for Task 3's own \"no failure anywhere in the suite\" acceptance bar. Zero relation to citation rendering; documented for the record since it is a worktree-provisioning correction, not a test-content change."

requirements-completed: [CIT-02, CIT-03, CIT-04, CIT-05]

coverage:
  - id: D1
    description: "The two RemovedInSphinx11Warning-raising env.get_and_resolve_doctree call sites are repaired with tags=builder.tags, letting test_link_... and test_backref_... reach their citation assertions instead of erroring on a Sphinx API deprecation"
    requirement: "CIT-03"
    verification:
      - kind: unit
        ref: "tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_link_citing_site_targets_match_definition_anchors_and_own_ids"
        status: pass
      - kind: unit
        ref: "tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_backref_markers_order_and_pdf_link_geometry"
        status: pass
    human_judgment: false
  - id: D2
    description: "CIT-02/D-05/D-06: the layout hanging-indent and widest-label alignment assertion now measures the marker's own start column (not the line's leading whitespace, which was always 0 on an entry's first line due to the preceding label cell) -- the assertion could never have passed in either direction before this fix"
    requirement: "CIT-02"
    verification:
      - kind: unit
        ref: "tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_layout_hanging_indent_and_widest_label_alignment"
        status: pass
    human_judgment: false
  - id: D3
    description: "SC#5's concat-boundary sub-check now tolerates D-14's [#link(...)#label(\"...\")] bracket-wrap instead of demanding a bare link( immediately after the '+' operator, and adds a region-wide no-dangling-operator guard"
    verification:
      - kind: unit
        ref: "tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_separator_paragraph_concat_and_list_item_boundaries"
        status: pass
    human_judgment: false
  - id: D4
    description: "CIT-04/D-01/D-02/D-03/D-08: the single-backref guard now scans for the marker group's own source fragment (text(\" (\")) instead of a bare \\(\\d+\\) that both false-positived on unrelated body prose and could never have matched the real marker shape"
    requirement: "CIT-04"
    verification:
      - kind: unit
        ref: "tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_backref_markers_order_and_pdf_link_geometry"
        status: pass
    human_judgment: false
  - id: D5
    description: "CIT-05: examples/charged-ieee/ restoration (landed in 40-02/40-03) remains fully green -- CIT-05 ticked in this plan on the strength of tests/test_examples_charged_ieee_gate.py, which this plan does not and did not touch (git diff ccb37b2..HEAD -- tests/test_examples_charged_ieee_gate.py is empty)"
    requirement: "CIT-05"
    verification:
      - kind: integration
        ref: "tests/test_examples_charged_ieee_gate.py::TestChargedIeeeExamplesGate (both approach1/approach2 tests)"
        status: pass
    human_judgment: false
  - id: D6
    description: "The corrected module re-proved RED (9/9) against the pre-40-03 translator (8b22bf6), confirming no correction was a laundered gate -- the module's ability to fail was verified, not assumed"
    verification:
      - kind: manual_procedural
        ref: "40-GATE-EVIDENCE-01.md Section 8.6 -- verbatim `git checkout 8b22bf6 -- typsphinx/translator.py` + `pytest -v` run recording all nine FAILED, followed by `git checkout HEAD -- typsphinx/translator.py` restoring a clean tree"
        status: pass
    human_judgment: false

duration: 21min
completed: 2026-08-02
status: complete
---

# Phase 40 Plan 05: Citation Gate Assertion Repair Summary

**Corrected the four defective assertions in `tests/test_citation_render_gate.py` that survived 40-03's implementation (a stale Sphinx API keyword, a line-vs-marker column confusion, and a bracket-wrap-intolerant concat check), plus two further test-measurement defects the first four's fixes exposed once reachable -- flipping the gate from 5/9 to 9/9 green, re-proving all nine still fail against the pre-40-03 translator, and closing CIT-02 through CIT-05.**

## Performance

- **Duration:** ~21 min (commit-to-commit; d2143ed 18:54:33 -> 51912df 19:15:34 JST)
- **Started:** 2026-08-02T18:54:33+09:00
- **Completed:** 2026-08-02T19:15:34+09:00
- **Tasks:** 3
- **Files modified:** 3 (`tests/test_citation_render_gate.py`, `.planning/phases/40-citations-full-round-trip/40-GATE-EVIDENCE-01.md`, `.planning/REQUIREMENTS.md`)

## Accomplishments

- **Task 1:** Repaired the two `env.get_and_resolve_doctree(docname, builder)` call sites (`_expected_own_id_anchors`, `_citing_site_own_anchors`) with `tags=builder.tags` -- a call-signature repair confirmed behaviour-preserving by reading Sphinx's own deprecation branch, which assigns exactly that value when the keyword is omitted. Corrected two stale comments/messages claiming `visit_reference` is unmodified by this phase (true when 40-01 authored them, false since 40-03 Task 1 added D-14's anchor). No `assert` condition changed.
- **Task 2:** Corrected the layout hanging-indent/widest-label assertion (`_leading_columns` -> `_marker_column`, now returning the marker's own start column instead of the line's leading whitespace, which was structurally incapable of validating CIT-02/D-05 in either direction) and the concat-boundary assertion (tolerates D-14's bracket-wrap, adds a region-wide dangling-operator guard). Discovered and fixed two further defects the same run exposed once reachable: `_attached_anchor_tokens` didn't recognise D-14's `#label("...")` anchor form (only the `<label>` bracket shorthand), and the single-backref D-03 guard's `\(\d+\)` regex both false-positived on an unrelated publication year in body prose and could never have matched the real 2+-marker shape in `.typ` source to begin with. All six corrections stay relational/derived -- no observed measurement or anchor/label token was transcribed as a literal (`grep -n '28' tests/test_citation_render_gate.py` returns nothing).
- **Task 3:** Committed Tasks 1-2 first, then temporarily restored `typsphinx/translator.py` to `8b22bf6` (the pre-40-03 translator) and re-ran the module: all nine tests RED, confirming the corrected module still discriminates. Restored the merged translator (`git status --porcelain` and `git diff HEAD --stat` both empty afterward). Appended a dated amendment section to `40-GATE-EVIDENCE-01.md` recording all six corrections against measurement, without touching the file's original RED record. Ticked CIT-02/CIT-03/CIT-04/CIT-05 in `.planning/REQUIREMENTS.md` and moved their traceability rows to Complete.
- 9/9 tests pass against the merged translator; the same 9/9 fail against `8b22bf6`. Full suite (`-m "not slow"`): 755 passed, 0 failed, 29 deselected. `black --check .`, `ruff check .`, `mypy typsphinx/` all clean. `git diff --stat -- typsphinx/ examples/ pyproject.toml uv.lock` is empty across all three of this plan's commits; the only test module touched under `tests/` is `test_citation_render_gate.py`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Repair the two deprecated-API helpers and the two stale visit_reference comments** - `622ba76` (fix)
2. **Task 2: Make the layout and concat assertions measure what they claim to measure** - `da2684f` (fix)
3. **Task 3: Re-prove the corrected module still goes RED against the unfixed translator, then record the amendments** - `51912df` (docs)

**Plan metadata:** (this commit, following)

## Files Created/Modified

- `tests/test_citation_render_gate.py` - `tags=builder.tags` at both `get_and_resolve_doctree` call sites; two stale comments corrected; `_leading_columns` renamed `_marker_column` and corrected to return the marker's own start column; `_find_page_and_column` updated in place; the concat-boundary sub-check now tolerates D-14's bracket-wrap and adds a dangling-operator guard; `_attached_anchor_tokens` broadened to recognise both the `<label>` and `#label("...")` attachment forms; the single-backref D-03 guard corrected to scan for the marker group's own source fragment.
- `.planning/phases/40-citations-full-round-trip/40-GATE-EVIDENCE-01.md` - Section 8 appended: a dated amendment recording all six corrections against measurement, plus the RED re-proof against `8b22bf6`. Sections 1-7 byte-unchanged (pure append confirmed via `git diff`).
- `.planning/REQUIREMENTS.md` - CIT-02/CIT-03/CIT-04/CIT-05 checkboxes ticked; their traceability rows moved from Pending to Complete. No other requirement's state touched.

## Decisions Made

- Corrected two further test-measurement defects beyond the plan's four orchestrator-diagnosed ones (the D-14 anchor-detection regex gap and the single-backref marker-group check), rather than halting, because: (a) both are unreachable-until-now defects the orchestrator's single-pass measurement structurally could not have seen (masked by the tags= exception and the missing-grid RED, respectively), consistent with this plan's own instruction to re-reproduce after each fix; (b) both are proven test-detection-precision defects, not translator defects, by direct evidence (the real `-b typstpdf` compile passes clean in the same build, and the D-14 `#label(...)` idiom is the SAME one `visit_target`'s pre-existing `next_is_target` case already used before this phase); (c) `typsphinx/translator.py` could not be touched regardless of diagnosis, so correcting the test was the only route to Task 2's own explicit "9 passed, 0 failed" acceptance bar; (d) both corrections follow the identical philosophy as the plan's four documented fixes -- fully relational, derived via `_expected_namespace_label`/the translator's own source, no literal transcription, and confirmed to still discriminate in the Task 3 re-proof.
- `_leading_columns` corrected in place (renamed `_marker_column`) rather than given a sibling helper -- all six call sites of its sole caller wanted the corrected quantity; none needed the old semantics, so no ambiguous pair of helpers was left behind.
- Fixed a stale `.venv/bin/uv` shim (a regular ELF from `uv sync`, never actually replaced by a symlink because the ambient worktree PATH already had `.venv/bin` first when an earlier shim attempt ran, so `command -v uv` self-resolved to the very file being replaced) as a Rule 3 blocking-issue auto-fix -- it silently failed 45 unrelated integration tests via the NixOS stub-loader error, blocking Task 3's "no failure anywhere in the suite" bar. Zero relation to citation rendering.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug in test measurement] `_attached_anchor_tokens` didn't recognise D-14's `#label("...")` anchor form**
- **Found during:** Task 2, re-running `test_link_citing_site_targets_match_definition_anchors_and_own_ids` after Task 1's tags= fix let it reach its own D-14 assertion for the first time.
- **Issue:** `_ATTACHED_ANCHOR_RE` only matched the `[... <label>]` bracket-postfix shorthand. D-14's own-ids anchor (`visit_reference`/`depart_reference`) emits the semantically equivalent but syntactically different `#label("...")` function-call form -- the same idiom `visit_target`'s pre-existing `next_is_target` case already used before this phase. `<name>` is parser sugar for `#label("name")`; both attach identically. A real `-b typst` build confirmed the exact emission (`[#link(<index:krizhevsky2012>, ...)#label("index:id1")]`), and the corresponding real-compile test passed clean in the same run, proving the attachment resolves.
- **Fix:** broadened `_attached_anchor_tokens` to the union of both forms (added `_ATTACHED_ANCHOR_CALL_RE`).
- **Files modified:** `tests/test_citation_render_gate.py`
- **Verification:** `test_link_citing_site_targets_match_definition_anchors_and_own_ids` passes; Task 3's RED re-proof confirms it still fails against `8b22bf6` (zero own-ids anchors exist there in either form).
- **Committed in:** `da2684f` (Task 2 commit)

**2. [Rule 1 - Bug in test measurement] Single-backref D-03 guard's `\(\d+\)` regex was unsound in both directions**
- **Found during:** Task 2, re-running `test_backref_markers_order_and_pdf_link_geometry` after the layout/concat fixes let it reach this assertion for the first time.
- **Issue:** the region scanned (`refs_grid[alpha_idx:bravo_idx]`) still carries the tail of the PRECEDING entry's own body prose ("Hinton, G. E. (2012)"), which the bare `\(\d+\)` scan misread as a marker (false positive). Independently, the regex could never have matched a REAL 2+-backref marker in `.typ` SOURCE: reading `typsphinx/translator.py` confirmed each ordinal is emitted inside a `[1]`/`[2]` content block passed to `link(...)`, never adjacent to a literal `(` (false negative, unreachable in this fixture but a latent defect).
- **Fix:** scan for the marker group's own source fragment, `text(" (")`, which `visit_citation` only appends when 2+ backrefs exist and cannot appear in ordinary body prose.
- **Files modified:** `tests/test_citation_render_gate.py`
- **Verification:** `test_backref_markers_order_and_pdf_link_geometry` passes; Task 3's RED re-proof confirms it still fails against `8b22bf6`.
- **Committed in:** `da2684f` (Task 2 commit)

**3. [Rule 3 - Blocking] Stale `.venv/bin/uv` shim silently failed 45 unrelated integration tests**
- **Found during:** Task 3's full-suite verification (`uv run pytest -m "not slow" -q`), unscoped to the citation module.
- **Issue:** `.venv/bin/uv` was a leftover regular ELF binary from `uv sync --extra dev` (the generic-linux `uv` wheel, incompatible with this NixOS sandbox's stub loader) rather than a symlink to the working nix-store `uv`. An earlier attempt at this session's start to shim it (per `CLAUDE.md`'s NixOS worktree-provisioning note) silently no-op'd: because the worktree's ambient PATH already had `.venv/bin` first, `command -v uv` inside that shim loop resolved to the very file being replaced, so `ln -sf` produced a no-op. This caused every test that internally shells out via `subprocess.run(["uv", "run", "sphinx-build", ...])` (4 unrelated files: `test_examples_basic.py`, `test_integration_advanced.py`, `test_integration_basic.py`, `test_integration_multi_doc.py`, `test_integration_nested_toctree.py`) to fail with `Could not start dynamically linked executable: uv` (exit 127).
- **Fix:** re-pointed `.venv/bin/uv` at the resolved nix-store path (`ln -sf $(command -v uv) .venv/bin/uv`, run as a plain command outside a loop this time).
- **Files modified:** none tracked by git (`.venv/` is gitignored, worktree-local environment state only).
- **Verification:** full suite re-run: 45 failed -> 0 failed (755 passed, 29 deselected).
- **Committed in:** not applicable (untracked `.venv/` state, not a git change).

---

**Total deviations:** 3 auto-fixed (2 Rule 1 test-measurement bugs discovered downstream of the plan's own four documented fixes, both required to meet Task 2's own "9 passed, 0 failed" bar and both re-proved RED in Task 3; 1 Rule 3 worktree-provisioning blocker, unrelated to citation rendering, required to meet Task 3's "no failure anywhere in the suite" bar).
**Impact on plan:** All three auto-fixes were necessary to reach the plan's own explicitly-stated acceptance criteria; none touched `typsphinx/`, `examples/`, or any test module other than `tests/test_citation_render_gate.py`. No scope creep into translator behavior — every correction targets the test module's own measurement precision, following the identical philosophy as the plan's four originally-diagnosed fixes.

## Issues Encountered

See "Deviations from Plan" above. No blockers remain; all four originally-diagnosed defects plus the two further discoveries are corrected, re-proved RED against the pre-40-03 translator, and recorded in `40-GATE-EVIDENCE-01.md`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `tests/test_citation_render_gate.py` is fully green (9/9) against the merged translator and fully RED (9/9) against the pre-40-03 baseline -- the gate 40-04's verification depends on is now trustworthy across all eight `-k` selectors.
- All six CIT requirements (CIT-01 through CIT-06) are ticked in `.planning/REQUIREMENTS.md` with traceability rows Complete.
- `40-GATE-EVIDENCE-01.md` carries a complete, dated amendment trail alongside its original classic-RED record -- nothing was rewritten or waived.
- Full suite green (755 passed / 0 failed / 29 deselected), lint/type trio clean, no changes outside this plan's declared file scope.
- No blockers to Phase 40's final verification (40-04, if scheduled) or to closing the phase.

---
*Phase: 40-citations-full-round-trip*
*Completed: 2026-08-02*
