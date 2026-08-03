---
phase: 40-citations-full-round-trip
verified: 2026-08-02T00:00:00Z
status: passed
score: 5/5 must-haves verified (ROADMAP SC#1..SC#5); 6/6 CIT requirements verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 40: Citations — Full Round Trip Verification Report

**Phase Goal:** A document containing docutils citations stops failing the Typst compile and
instead renders a real reference list — a labelled hanging-indent entry per citation, a working
`[Label]` → definition link, docutils' own back-references to every same-document citing site, and
document order preserved — to the point where the citation syntax Phase 22.2 stripped out of
`examples/charged-ieee/` is restored and both samples build clean.

**Verified:** 2026-08-02
**Status:** passed
**Re-verification:** No — initial verification

## Method

This report does not take any SUMMARY.md claim on faith. Every load-bearing claim below was
independently re-executed on the merged tree (branch `gsd/v0.7.0-api-rendering-design-overhaul`,
HEAD at verification time — `2f5eeca` and prior citation-phase commits `927431d`, `12a2bee`,
`622ba76`, `da2684f`, `51912df`, `ae355f6`) rather than read out of a SUMMARY or a GATE-EVIDENCE
file. Commands and their actual output are recorded per truth below.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria, verbatim from `.planning/ROADMAP.md`)

| # | Truth (ROADMAP SC) | Status | Evidence |
|---|---|---|---|
| SC#1 | A document containing a citation compiles to a valid PDF; the classic GATE-01 RED is captured against the unfixed translator. | ✓ VERIFIED | Independently re-ran `uv run pytest tests/test_citation_render_gate.py::TestCitationRenderGateRealCompile -v` → PASS against merged tree. Independently restored `typsphinx/translator.py` to `8b22bf6` (pre-40-03, byte-identical to phase start) and re-ran the whole module: **9 failed** (matches orchestrator's and 40-05's own re-proof exactly), including the real compile test failing on `TypstError: expected semicolon or line break` per `40-GATE-EVIDENCE-01.md` §3. Restored `HEAD`; `git status --porcelain` empty afterward. |
| SC#2 | A citation definition renders as `[Label]` + entry body, continuation lines aligned past the label — hanging indent measured from `pypdf` bounding boxes, not by eye. | ✓ VERIFIED | Read `test_layout_hanging_indent_and_widest_label_alignment` (`tests/test_citation_render_gate.py:883-952`): uses `pypdf.PdfReader(...).extract_text(extraction_mode="layout")` on a real compiled `index.pdf`, measures `_marker_column` (the sentinel's own start column, corrected in 40-05 from a broken line-leading-whitespace measurement) and asserts the continuation line's column equals it and is `>0`, plus that all 5 References siblings share that column. This is a real `pypdf`-derived geometric assertion, not a `.typ`-string check and not an eye check, per ROADMAP's explicit demand. Re-ran: PASSED. |
| SC#3 (amended, D-09) | Citing reference resolves to definition; each definition carries back-references to every same-document citing site in `backrefs`; cross-document site gets forward link, no back-ref; duplicate key across 2 documents does not abort the compile. | ✓ VERIFIED | `.planning/ROADMAP.md` § Phase 40 SC#3 already contains the amended same-document-scope wording, with a matching dated 2026-08-02 Roadmap Evolution bullet naming D-08/D-09 — confirmed by direct read, both `.planning/ROADMAP.md` lines 165-171 and 730-736. Code: `visit_citation` derives `backref_targets` solely from `node.get("backrefs")` (docutils itself only populates same-document sites, confirmed in `40-CONTEXT.md`'s "measured starting position" — I did not re-derive this docutils behavior myself but the code path is a direct, unmodified pass-through of docutils' own `backrefs` list, which is the load-bearing claim). D-13's namespacing (`_namespace_label(node["docname"], ...)`, never `_current_docname()`) confirmed present at `typsphinx/translator.py:2854,2862,2885`. `test_namespace_duplicate_key_is_document_scoped` and `test_backref_markers_order_and_pdf_link_geometry`'s D-08 no-cross-document-backref assertion both re-ran PASSED. |
| SC#4 | Citation entries appear in document order, unsorted, asserted against the compiled PDF's extracted text order. | ✓ VERIFIED | `test_order_references_sentinels_match_document_order` (`tests/test_citation_render_gate.py:1076-1113`) extracts real `pypdf` `extraction_mode="layout"` text from the compiled PDF and asserts the five sentinels' byte offsets are monotonically increasing. Re-ran: PASSED. This is a compiled-PDF assertion, not a `.typ`-string or eye check. |
| SC#5 | Both `examples/charged-ieee/` approaches carry citation syntax again and build clean via `-b typstpdf`; new handlers checked against all three separator protocols (paragraph, code-mode concat, list-item). | ✓ VERIFIED | `git hash-object` on both restored files independently re-run → both `82831eb092b9f52cba8b1247b95f7e148f499bb2` (exact match to the pre-removal blob). `diff -q` between the two files → identical (exit 0). `uv run pytest tests/test_examples_charged_ieee_gate.py -v` re-ran → 2 passed, PDF magic-byte + non-empty assertions in that test module confirmed by direct read (`tests/test_examples_charged_ieee_gate.py:173-220`). `git diff ccb37b2..HEAD -- tests/test_examples_charged_ieee_gate.py` → empty (module genuinely never edited across the phase). `test_separator_paragraph_concat_and_list_item_boundaries` re-ran PASSED, and its three lettered sub-checks (paragraph/concat/list-item) were read directly in the test source, confirming all three protocols are checked as distinct assertions rather than by analogy. |

**Score:** 5/5 ROADMAP success criteria verified, 0 behavior-unverified.

### Requirements Coverage (CIT-01..CIT-06)

| Requirement | Source Plan | Status | Evidence |
|---|---|---|---|
| CIT-01 | 40-01, 40-03 | ✓ SATISFIED | Classic compile RED→GREEN flip independently re-proven (see SC#1 row). `.planning/REQUIREMENTS.md` line 157 ticked, traceability row "Complete" (line 309). |
| CIT-02 | 40-01, 40-03, 40-05 | ✓ SATISFIED | Hanging-indent `pypdf` geometric assertion independently re-run PASSED (see SC#2 row). Ticked line 162, traceability "Complete" line 310. |
| CIT-03 | 40-01, 40-03, 40-05 | ✓ SATISFIED | Link-target/anchor-agreement test (`test_link_citing_site_targets_match_definition_anchors_and_own_ids`) re-ran PASSED. Ticked line 165, traceability "Complete" line 311. Minor stale note: the requirement's own explanatory parenthetical ("`citation_reference.refid` resolves directly to `citation.ids[0]`") describes bare docutils, not Sphinx's actual citation-domain transform — `40-CONTEXT.md`'s own "measured starting position" section flags this explicitly, but the ROADMAP text (the graded artifact) was corrected while this REQUIREMENTS.md parenthetical was not. This is a stale-documentation nit, not a functional gap — the requirement's core clause ("links to its definition") is correctly implemented and tested. Not filed as a gap. |
| CIT-04 | 40-01, 40-03, 40-05 | ✓ SATISFIED | `test_backref_markers_order_and_pdf_link_geometry` re-ran PASSED (D-01/D-02/D-03/D-08 all exercised: 2-marker case, 1-marker case, bare-comma separator, no-cross-document-backref). Ticked line 170, traceability "Complete" line 312. |
| CIT-05 | 40-02, 40-03 | ✓ SATISFIED | See SC#5 row. Ticked line 173, traceability "Complete" line 313. |
| CIT-06 | 40-01, 40-03 | ✓ SATISFIED | See SC#4 row. Ticked line 177, traceability "Complete" line 314. |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s Phase 40 traceability table lists exactly CIT-01..CIT-06 (6 requirements), matching every plan's `requirements:` frontmatter field across 40-01 through 40-05 with no additional Phase-40-mapped ID outside this set.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `typsphinx/translator.py` | `visit_citation`/`depart_citation`/`visit_label` + `_citation_run_neighbour`/`_find_citing_reference`/`_citing_reference_has_own_anchor` + D-14 `visit_reference`/`depart_reference` guard | ✓ VERIFIED | All six symbols read directly at their claimed line numbers (2644-2942, 4210-4230, 4359-4366). `git diff ccb37b2..HEAD -- typsphinx/translator.py` → 348 insertions, 0 deletions, one file — purely additive. |
| `tests/test_citation_render_gate.py` | 9-test gate, 8 `-k` selectors | ✓ VERIFIED | Collected and re-ran: 9 passed against merged tree, 9 failed against `8b22bf6` (independently re-proven, not merely re-read from evidence file). |
| `tests/fixtures/citation_render_gate/{conf.py,index.rst,second.rst}` | 2-document fixture, 11 scenarios | ✓ VERIFIED | Files exist; fixture builds and is consumed by the passing gate module. |
| `examples/charged-ieee/{approach1,approach2}/source/index.rst` | Restored to pre-removal blob | ✓ VERIFIED | `git hash-object` independently confirmed both equal `82831eb092b9f52cba8b1247b95f7e148f499bb2`. |
| `.planning/ROADMAP.md` (SC#3 correction) | Same-document scope, dated evolution bullet | ✓ VERIFIED | Read directly; amended text and 2026-08-02 D-08/D-09 bullet both present. |
| `40-GATE-EVIDENCE-01.md`, `40-GATE-EVIDENCE-02.md`, `40-NONREGRESSION.md` | RED/GREEN evidence trail | ✓ VERIFIED | All three exist, non-empty, contents cross-checked against independently-reproduced command output (not merely assumed accurate). |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `visit_citation`'s run-adjacency scan | `node.parent.children` | `_citation_run_neighbour` skipping comment/system_message | ✓ WIRED | Read at `typsphinx/translator.py:2644-2683`; `test_references_run_and_run_break_grid_counts` (comment-does-not-break-run, paragraph-does-break-run) re-ran PASSED. |
| Definition's back-reference link targets | Citing-site D-14 anchors | `_find_citing_reference` + `_namespace_label(node["docname"], refid)` | ✓ WIRED | `test_backref_markers_order_and_pdf_link_geometry` independently re-ran PASSED, extracting both sides from real emitted output/resolved doctree, never a hard-coded literal (confirmed by reading the test body — uses `_citing_site_own_anchors` reading `env.get_and_resolve_doctree`). |
| `visit_label`'s `SkipNode` | citation's already-consumed label child | positional skip, buffer-swap render in `visit_citation` | ✓ WIRED | Read at `typsphinx/translator.py:2922+`; the render happens via buffer-swap in `visit_citation` before `visit_label` fires, consistent with docstrings and passing `uncited`/`namespace` selectors. |
| `_namespace_label(node["docname"], ...)` | citation node's own `docname` attribute, never `_current_docname()` | D-13 | ✓ WIRED | Confirmed by direct read at lines 2854, 2862, 2885 — all three call sites use `docname = node.get("docname")`, never `self._current_docname()`. |

### Data-Flow Trace (Level 4)

The citation grid's rendered content (label text, entry body, back-reference count/targets) is
sourced from real docutils/Sphinx data at every step — `node.get("backrefs")`, `node.get("ids")`,
`node.get("docname")`, and the label node's own children walked through the normal visitor chain
(no hardcoded/static fallback). Traced directly in `typsphinx/translator.py:2840-2888`. No hollow
props or static empty-array fallbacks found.

### Behavioral Spot-Checks (independently re-executed, not trusted from SUMMARY/evidence files)

| Behavior | Command | Result | Status |
|---|---|---|---|
| Gate module green against merged translator | `uv run pytest tests/test_citation_render_gate.py -v` | 9 passed | ✓ PASS |
| Gate module RED against pre-40-03 translator | `git checkout 8b22bf6 -- typsphinx/translator.py && pytest -v && git checkout HEAD -- typsphinx/translator.py` | 9 failed, tree restored clean | ✓ PASS (RED confirmed, discrimination proven) |
| Shipped-sample gate green | `uv run pytest tests/test_examples_charged_ieee_gate.py -v` | 2 passed | ✓ PASS |
| Sample restoration byte-exact | `git hash-object` both files | both `82831eb0...` | ✓ PASS |
| Full suite green | `uv run pytest -q` | 783 passed, 1 skipped | ✓ PASS (matches orchestrator measurement exactly) |
| Full-corpus `-b typstpdf` gate actually ran | `uv run pytest tests/test_corpus_gate.py -m slow -v` | `test_corpus_compiles_with_no_fatal_error` PASSED (not skipped); sibling test skipped for unrelated env-var reason | ✓ PASS |
| `@preview`/dependency invariants | `git diff --stat ccb37b2..HEAD -- pyproject.toml uv.lock` + `pytest tests/test_preview_version_sync.py -v` | empty diff; 3 passed | ✓ PASS |
| No debt markers in touched files | `grep -n -E "TBD\|FIXME\|XXX" typsphinx/translator.py tests/test_citation_render_gate.py examples/charged-ieee/*/source/index.rst` | no matches | ✓ PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` files exist in this project; no probes are declared in Phase 40's
PLAN/SUMMARY files. Skipped — not applicable to this phase's verification methodology (it uses
pytest render-gates, not standalone probe scripts).

### Anti-Patterns Found

None blocking. `git diff ccb37b2..HEAD -- typsphinx/translator.py` is purely additive (348
insertions, 0 deletions). No stub returns, no hardcoded empty fallbacks, no debt markers.

### Code Review Findings (from `40-REVIEW.md`, cross-checked)

0 critical, 3 warnings, 1 info — all already filed in `.planning/phases/40-citations-full-round-trip/40-REVIEW.md`. Read and cross-checked against the source directly:

- **WR-01** (`typsphinx/translator.py:2856-2862`): `_find_citing_reference` returning `None` falls through to emitting a backref target anyway instead of skipping, unlike the sibling `_citing_reference_has_own_anchor is False` case immediately next to it. Confirmed by direct read — the asymmetry is real. Not proven to fire against the fixture or the shipped `examples/` content (every `backrefs` id in both currently resolves to a live reference node). This is a latent dangling-label hazard for citing-site topologies outside the phase's own 11-scenario fixture, not a demonstrated failure of any ROADMAP SC or CIT requirement.
- **WR-02** (`typsphinx/translator.py:2644-2683`): `_citation_run_neighbour` treats an ids-less `nodes.target` sibling as a real (run-breaking) node even though it emits zero bytes, unlike comment/system_message which are correctly skipped. Narrow RST construct (anonymous target directly between two citation definitions), not exercised by the fixture or `examples/`.
- **WR-03**: D-14 eligibility logic duplicated across `visit_reference` and `_citing_reference_has_own_anchor` with an implicit, unenforced invariant between them.
- **IN-01**: `_find_citing_reference` is an O(citations × backrefs × references) full-document scan per backref — explicitly out of scope for this review depth (performance, not correctness).

None of these three warnings falsifies any ROADMAP success criterion or CIT requirement as scoped
and tested by this phase's own fixture (which the 40-CONTEXT.md decisions and 40-01-PLAN.md's
`must_haves` explicitly bound the phase to). They are legitimate hardening items for citing-site
topologies beyond the phase's documented scope and are already recorded for the project's own
future reference — surfaced here for visibility, not as blocking gaps.

### Human Verification Required

None. All 5 ROADMAP success criteria and all 6 CIT requirements are backed by re-executed,
machine-checkable evidence (pytest assertions using real `pypdf` PDF measurements, real `git
hash-object` blob comparisons, real RED/GREEN re-proofs against a named pre-fix commit). No visual,
real-time, or external-service-dependent claim exists in this phase's scope.

### Gaps Summary

No gaps. All must-haves were independently re-verified against the actual merged codebase rather
than trusted from SUMMARY.md or GATE-EVIDENCE files:

- The RED-to-GREEN flip for CIT-01 was re-proven from scratch in this verification session (not
  copied from 40-05's or 40-04's own record): 9/9 RED against `8b22bf6`, 9/9 GREEN against merged
  HEAD, tree restored clean afterward.
- SC#2's hanging-indent claim and SC#4's document-order claim were confirmed, by direct source
  read, to be real `pypdf`-based compiled-PDF measurements (`extraction_mode="layout"`), not `.typ`
  string checks and not eye checks — satisfying the verification-focus concern raised for this
  phase.
- 40-05's six corrections to the gate module (the plan flagged in the verification-focus concern as
  worth scrutinizing since it edited a module two other plans were forbidden to touch) were checked
  against the ROADMAP/CONTEXT decisions they claim to measure: the layout fix now measures the
  marker's own column (verified in source, matches the D-05 hanging-indent requirement); the concat
  fix tolerates D-14's bracket-wrap (verified against the actual `visit_reference` D-14
  implementation, which does emit that bracket-wrap unconditionally for eligible citing references —
  confirmed by direct code read, not just trusting the SUMMARY's claim); none of the six corrections
  weakens, skips, or hard-codes an observed value (confirmed: `grep -n '28'
  tests/test_citation_render_gate.py` → no matches).
- The one Wave-1→Wave-2 caution flag (40-03's SUMMARY conservatively left CIT-02/03/04/05
  unticked pending the gate-module fix) was correctly resolved by 40-05, and REQUIREMENTS.md now
  reflects all six as Complete with traceability rows matching.

Minor documentation staleness (CIT-03's REQUIREMENTS.md parenthetical describing bare-docutils
mechanics rather than Sphinx's actual citation-domain transform) is noted but does not affect the
functional correctness of the implementation or any test — not filed as a gap.

---

_Verified: 2026-08-02_
_Verifier: Claude (gsd-verifier)_
