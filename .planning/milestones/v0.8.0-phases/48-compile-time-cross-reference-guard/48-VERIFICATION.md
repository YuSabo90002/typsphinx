---
phase: 48-compile-time-cross-reference-guard
verified: 2026-08-14T05:34:48Z
status: passed
score: 19/19 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 9/9
  previous_verified: 2026-08-12T06:57:54Z
  scope_note: "The 2026-08-12 report covered plans 48-01..48-04 only. This report is a full
    re-verification covering all SEVEN plans, including the gap-closure wave (48-05/06/07) for
    UAT gap G-48-4 and the post-review CR-01 correction (d3f29605)."
  gaps_closed:
    - "G-48-4 — whole-document `:doc:` references emitted as dead `link(\"<docname>.pdf\", ...)` URI
       actions (ERR_FILE_NOT_FOUND). Closed by 48-05/06/07: independently re-measured on the built
       docs PDF as 72 internal /Dest (was 37) and 5 remaining `.pdf`-suffixed URI actions (was 40),
       matching the pre-declared expected value of 5 exactly."
    - "All four human-verification items from the 2026-08-12 report — discharged by the owner in
       48-UAT.md (status: complete, 16/16 pass, 0 issues, updated 2026-08-14T14:25+09:00, i.e.
       AFTER the CR-01 fix at 13:57 and the rebuild at 13:56)."
    - "CR-01 (code review BLOCKER) — `_whole_document_reference_eligible` shipped without the
       `node.get(\"internal\")` conjunct. Fixed in d3f29605; the conjunct is present at
       translator.py:3149-3153 and the discriminating regression test passes."
    - "WR-01 (code review WARNING) — no test isolated the `internal` conjunct. Closed by the same
       commit's `test_non_internal_reference_onto_known_document_not_guarded`."
  gaps_remaining: []
  regressions: []
---

# Phase 48: Compile-Time Cross-Reference Guard — Verification Report

**Phase Goal:** Whether a cross-document reference's target label exists is decided by Typst at
compile time, per compiled wrapper, instead of by a build-time boolean derived from
`master_included_docnames`. The validated guard shape is
`context { if query(<label>).len() > 0 { link(<label>, …) } else { … } }`.

**Verified:** 2026-08-14T05:34:48Z
**Status:** passed
**Re-verification:** Yes — full re-verification over all seven plans (the 2026-08-12 report is
superseded; it predated plans 48-05/48-06/48-07 and the CR-01 correction).

## Verification Environment

Everything below was run by the verifier in the MAIN checkout at `/home/yuta/Documents/typsphinx`
(HEAD `f8b692cf`, working tree clean). No SUMMARY.md claim was accepted without independent
re-execution. No implementation or test file was modified.

## Goal Achievement

### Observable Truths

Truths 1-4 are ROADMAP.md's four Success Criteria (the binding contract). Truths 5-9 come from
plans 48-01..48-04's `must_haves.truths`. Truths 10-19 come from the gap-closure plans
48-05/48-06/48-07 (`gap_closure: true`, `gap_ids: [G-48-4]`) and were NOT covered by the previous
report.

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | **SC#1 (XREF-03):** a reference whose target is absent from the compiling master degrades to plain text and the compile succeeds; the master that includes the target gets a real link annotation; both read back through `pypdf`, no `TypstError` | ✓ VERIFIED (behavioral) | `uv run python -m pytest tests/test_xref_compile_time_guard_render_gate.py` → 6 passed, 0 xfail, 0 XPASS (re-run inside the full-suite run). The gate is a real `sphinx-build -b typstpdf` → `typst.compile()` → `pypdf` round trip over the two-master fixture `tests/fixtures/xref_per_master_guard_gate/`. Guard emission read directly at `typsphinx/translator.py:5305-5308`. |
| 2 | **SC#2 (XREF-04):** every label-reference emission site routes through one shared guard helper; open question #1 (`translator.py:4291`'s nature) closed by reading the code | ✓ VERIFIED | `grep -c 'query(<{label}>)' typsphinx/translator.py` → **1** (single derivation point, self-run). `grep -n '_label_existence_guard('` → one definition (`:3266`) and exactly four call sites: `visit_citation` `:3524` and `:3536`, `visit_pending_xref` `:4575`, `visit_reference` `:5305`. Open question #1's answer recorded in `48-EVIDENCE.md` §"SC#2 — site enumeration": `visit_pending_xref` is a fourth independent degradation site, not routed through `_reference_anchor_decision`. |
| 3 | **SC#3 (XREF-04):** the build-time mechanism is deleted, not left half-alive | ✓ VERIFIED | `grep -rn 'master_included_docnames\|_compute_master_included_docnames\|degrade_xref_to_text' typsphinx/` → exit 1, zero matches (self-run). `_ReferenceAnchorDecision` read directly: no degrade field, and `opens_wrapper = bool(refuri or refid)` consults no builder state (`translator.py:3234`). |
| 4 | **SC#4:** the guard is applied only where needed — same-document anchors keep the unguarded form, asserted explicitly — and the full-corpus compile cost is measured, not assumed | ✓ VERIFIED | Both same-document branches read directly: bare-refid at `translator.py:5239-5244` and `#`-prefixed refuri at `:5277-5282`, each emitting the plain `link(<label>, ` form under an explicit "SC#4/D-06 (Phase 48): deliberately UNGUARDED" comment. Asserted negatively by `tests/test_label_existence_guard_unit.py::test_bare_refid_reference_emits_no_guard` and `::test_hash_prefixed_internal_refuri_emits_no_guard` (both green). Cost: `48-EVIDENCE.md` §"D-11 compile-time cost" records −2.37% (28.92/27.21s after vs. 28.93/28.56s before), bottom tier, tiers quoted verbatim above the number; arithmetic re-derived correct. Owner accepted (48-UAT test 2). |
| 5 | Own-anchor composition (D-14 bracket-wrap + D-07 guard) compiles and the attached label stays queryable | ✓ VERIFIED (behavioral) | `depart_reference` read directly (`translator.py:5355-5370`): the guard close string is emitted strictly BEFORE the D-14 own-anchor block, so `#label("…")]` lands outside the `context { … }` block. Exercised green by `tests/test_citation_render_gate.py` (in the full-suite run). |
| 6 | The three migrated build-time-premise test modules assert post-fix behaviour with zero residual xfail | ✓ VERIFIED | `tests/test_citation_degradation_gate.py`, `tests/test_xref_orphan_degrade_render_gate.py`, `tests/test_master_include_set_predicate_gate.py` all green in the full-suite run; suite-wide `0 xfailed, 0 xpassed`. |
| 7 | D-05: the captioned-code-block citation dangling-label fatal is closed | ✓ VERIFIED | `tests/test_citation_caption_dangling_label_gate.py` green in the full-suite run, no xfail remaining. |
| 8 | The label-collision false-negative class is measured at compile level and filed, not merely argued | ✓ VERIFIED | `tests/fixtures/xref_label_collision_guard_gate/` exists and its gate is green; `.planning/todos/pending/2026-08-12-label-collision-false-negative-in-compile-time-xref-guard.md` exists. Owner accepted the trade-off (48-UAT test 1, pass). |
| 9 | The phase closes green: full pytest suite + `black` + `ruff` + `mypy` | ✓ VERIFIED | `uv run python -m pytest -q` → **1080 passed, 5 skipped, 0 failed, 0 xfailed, 0 xpassed** (self-run, 100s). `uv run black --check typsphinx/ tests/` → 272 files unchanged. `uv run ruff check .` → All checks passed. `uv run mypy typsphinx/` → Success, no issues in 6 source files. The 5 skips are environment gates unrelated to this phase (4× myst-parser absent from the dev extra, 1× `TYPSPHINX_CORPUS_REPORT` env gate). |
| 10 | **(48-05)** the pre-fix dead-link population in the built docs PDF is enumerated by a pasted reproducible transcript, bucketed into internal-destination / URI-action / other, with every `out_suffix`-suffixed URI target listed with its count | ✓ VERIFIED | `48-RED-EVIDENCE.md` "Baseline 4": 37 internal `/Dest`, 465 URI actions, 0 other (502 total); 40 `.pdf`-suffixed URI actions across 20 distinct targets, each listed. Transcript and snippet pasted; the same snippet is re-run in 48-07's re-measurement, so the two are subtractable. |
| 11 | **(48-05)** the two sub-populations are separated by measurement, not assumption, and the UAT's own count for sub-population B is re-derived rather than copied forward, with the divergence stated | ✓ VERIFIED | Sub-population A (resolves onto a real docname): 15 targets / 35 annotations. Sub-population B (Sphinx-generated virtual pages): 5 targets / 5 annotations, each enumerated with its citing docname and `in_found_docs=False`. The UAT gap entry states the correction from 4 to 5 in plain text with both numbers shown (`48-UAT.md` `measured_scope`, and commit `28293342`). |
| 12 | **(48-05)** the policy for Sphinx-generated pages is decided by the owner at a blocking checkpoint, and the chosen option's expected post-fix count is written down BEFORE any emitter change exists (binding constraint #6) | ✓ VERIFIED | `48-EXPECTED-STRUCTURE.md` §6 "The owner's decision (Task 2 checkpoint), recorded verbatim" — **option-a**, "guard only references that resolve onto a real document", with the expected post-fix count fixed at **5**. Commit ordering proves the sequence: expected values `3ef57116` (12:46) → RED gates `79a18007`/`67f28df0`/`b5c8c1ab` (12:59-13:10) → emitter `d3cb9eee` (13:24). |
| 13 | **(48-05)** the self-anchor token is named and its collision-safety argued from the sanitizer's own rules and verified by running `make_id`, not asserted | ✓ VERIFIED (independently re-measured) | Token `_WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN = "__tsx-doc__"` at `translator.py:44`. I re-ran `docutils.nodes.make_id` on seven adversarial probes myself: `'__tsx-doc__'→'tsx-doc'`, `'_tsx_doc_'→'tsx-doc'`, `'a_b'→'a-b'` — **`make_id` never emits an underscore**, so the token is unreachable from any `make_id`-derived raw id. Claim 2 (Sphinx domain ids are built from Python identifiers, which exclude `-`) independently re-confirmed by the code reviewer against installed Sphinx 9.1.0. |
| 14 | **(48-05/06) prohibition:** no change to `typsphinx/` in plans 48-05 and 48-06 — the gates must be proven RED against the UNFIXED emitter | ✓ VERIFIED | `git show --name-only` on every 48-05 commit (`4b0ee584`, `3ef57116`, `3fac169f`) → planning artifacts only. Every 48-06 commit (`79a18007`, `67f28df0`, `b5c8c1ab`, `e7f519c8`) → fixtures / tests / `48-RED-EVIDENCE.md` only. Zero `typsphinx/` bytes in either wave. |
| 15 | **(48-06)** a real `sphinx-build -b typstpdf` acceptance fixture exercises the whole-document path in BOTH directions at once (one included target, one `:orphan:` target); flipping assertions landed as `xfail(strict=True)` first and are plain green now | ✓ VERIFIED (behavioral) | Fixture `tests/fixtures/xref_whole_document_guard_gate/{conf.py,index.rst,included.rst,orphan.rst}` — `index.rst` carries exactly one `:doc:` to `included` (toctree-reachable) and one to `orphan` (excluded). `git show b5c8c1ab:tests/test_xref_whole_document_guard_render_gate.py` → 8 `xfail` occurrences at RED time; the current file has **zero active markers** (the 3 remaining hits are prose). Self-run: `tests/test_whole_document_xref_unit.py` + `tests/test_xref_whole_document_guard_render_gate.py` → 10 + 8 = 18 passed, 0 xfail, 0 XPASS. |
| 16 | **(48-06)** the invariance guard pinning "a relative link to a real file asset is never routed through the guard" is present and actually discriminating | ✓ VERIFIED (after the CR-01/WR-01 correction) | At 48-06/48-07 time this guard existed but could not isolate the `internal` conjunct (code review WR-01) — which is exactly how CR-01 shipped. `d3f29605` restored the conjunct AND added the discriminating case. Self-run by name: `tests/test_whole_document_xref_unit.py::TestReferenceAnchorDecisionWholeDocumentPolicy::test_non_internal_reference_onto_known_document_not_guarded` → **PASSED**. Predicate body read directly (`translator.py:3149-3153`): `if not node.get("internal"): return False` then `target_docname in getattr(getattr(self.builder, "env", None), "found_docs", ())`. |
| 17 | **(48-07)** a whole-document cross-reference is emitted as a guarded internal link against a real per-document self-anchor — the emitted `.typ` proves it and the compiled PDF proves it | ✓ VERIFIED (behavioral) | Emitted `.typ` from the real docs build: `docs/_build/pdf/quickstart.typ` line 12 carries `[#metadata(none) <quickstart:__tsx-doc__>]`, and the "What's Next?" links are `query(<user_guide_u2f_configuration:__tsx-doc__>)`, `…builders…`, `…templates…`, `query(<examples_u2f_index:__tsx-doc__>)` — the four exact links the owner reported dead. Compiled PDF: I re-ran the pypdf enumeration myself on `docs/_build/pdf/typsphinx.pdf` (see truth 19). Render gate `test_index_typ_carries_both_guard_expressions`, `test_index_typ_carries_no_string_url_link_to_targets`, `test_pdf_positional_destination_resolves_to_included_page` all green. |
| 18 | **(48-07)** every content file emits exactly one stable self-anchor, derived through `_namespace_label` (D-13) from ONE module-level token constant, so definition site and reference site byte-match by construction | ✓ VERIFIED | One constant (`translator.py:44`), consumed at exactly two places: the definition site `visit_document` (`:733-736`) and the reference site `visit_reference` (`:5302-5304`), both through `_namespace_label`. `visit_document` gates on `_current_docname()` so hand-built doctrees stay byte-identical. Gate `test_included_and_orphan_typ_each_carry_self_anchor_once` green. |
| 19 | **(48-07)** the rebuilt documentation PDF's count of URI actions targeting a file the build never produces drops from the 48-05 baseline to the single number the owner's recorded decision fixed — measured, not argued | ✓ VERIFIED (independently re-measured) | I ran the enumeration myself against `docs/_build/pdf/typsphinx.pdf` (119 pages): **internal `/Dest` 72, URI actions 430, other 0, total 502; `.pdf`-suffixed URI actions = 5 across 5 distinct targets** — `../genindex.pdf`, `../py-modindex.pdf`, `genindex.pdf`, `py-modindex.pdf`, `search.pdf`, each ×1. Baseline was 37 / 465 / 0 / 502 with 40 across 20. Sub-population A: 35 → **0**. Measured 5 equals the value pre-declared in `48-EXPECTED-STRUCTURE.md` §6 before the emitter existed. Total annotation count unchanged (502 → 502): every closed annotation converted to a real internal destination; none vanished. |

**Score:** 19/19 truths verified (0 present-but-behavior-unverified, 0 overrides)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/translator.py::_label_existence_guard` (`:3266`) | The single D-07 guard-string derivation point | ✓ VERIFIED | One definition, four call sites, `grep -c 'query(<{label}>)'` → 1. |
| `typsphinx/translator.py:44` `_WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN` | One module constant, `"__tsx-doc__"` | ✓ VERIFIED | Read directly; consumed at both the definition and reference sites through `_namespace_label`. |
| `typsphinx/translator.py::visit_document` (`:733-736`) | Per-document self-anchor emitted exactly once, in the existing zero-width `metadata` anchor form | ✓ VERIFIED | Read directly; confirmed in real emitted output (`docs/_build/pdf/quickstart.typ:12`). |
| `typsphinx/translator.py::_whole_document_reference_eligible` (`:3084-3153`) | Routing predicate implementing option-a: `internal` AND `found_docs` | ✓ VERIFIED | Both conjuncts present post-`d3f29605`; defensive nested `getattr` keeps hand-built doctrees byte-unchanged. |
| `typsphinx/translator.py::_resolve_xref_docname` (`:4904`) | Whole-document refuri resolves to `(docname, "")` instead of `None`; policy stays out of the resolver | ✓ VERIFIED | Read directly; docstring states it answers "which document and which anchor", never policy. |
| `typsphinx/builder.py` | `master_included_docnames` / `_compute_master_included_docnames` gone | ✓ VERIFIED | Repo-wide grep over `typsphinx/` → zero matches. |
| `tests/fixtures/xref_whole_document_guard_gate/` | Two-outcome acceptance fixture (included + `:orphan:`) | ✓ VERIFIED | 4 files present; `index.rst` carries both reference directions. |
| `tests/test_whole_document_xref_unit.py` | Offline resolver / policy / self-anchor gate | ✓ VERIFIED | 10 passed, 0 xfail (self-run). |
| `tests/test_xref_whole_document_guard_render_gate.py` | Real `sphinx-build → typst.compile() → pypdf` gate | ✓ VERIFIED | 8 passed, 0 xfail (self-run). |
| `tests/test_xref_compile_time_guard_render_gate.py` | Two-master per-compile guard gate | ✓ VERIFIED | 6 passed (full-suite run). |
| `tests/test_label_existence_guard_unit.py` | Helper contract + D-06 exemption + single-derivation-point pins | ✓ VERIFIED | 16 tests, all green; includes the two SC#4 negative assertions. |
| `48-RED-EVIDENCE.md` | Pre-fix RED transcripts incl. Baseline 4 dead-link enumeration | ✓ VERIFIED | Present; Baseline 4 numbers reconcile with the post-fix re-measurement. |
| `48-EXPECTED-STRUCTURE.md` | Pre-declared expected values incl. §6 owner decision and the `5` target | ✓ VERIFIED | Present; commit `3ef57116` (12:46) precedes the emitter commit `d3cb9eee` (13:24). |
| `48-EVIDENCE.md` | D-11 / D-09 / SC#2 / SC#3 / D-01 / label-collision / green gate / G-48-4 post-fix re-measurement / CR-01 addendum | ✓ VERIFIED | All sections present and read; the G-48-4 re-measurement numbers match my own independent enumeration exactly. |
| `48-UAT.md` | Completed UAT discharging the human items | ✓ VERIFIED | `status: complete`, 16 tests, 16 pass, 0 issues; gap G-48-4 marked `resolved`. Updated 2026-08-14T14:25+09:00 — AFTER the CR-01 fix (13:57) and the rebuild it was checked against (13:56). |
| `48-SECURITY.md` | Security audit | ✓ VERIFIED | `status: verified`, `threats_open: 0`. |
| `48-REVIEW.md` | Code review with CR-01/WR-01 | ✓ VERIFIED | `status: resolved`, `resolved_in: d3f29605`; both findings independently re-confirmed fixed. |
| `.planning/todos/pending/2026-08-12-label-collision-…md` | Filed remediation todo for the accepted limit | ✓ VERIFIED | Present. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `_WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN` | `visit_document` self-anchor emission | `_namespace_label(docname, TOKEN)` | ✓ WIRED | `translator.py:733-736`; observed in real output as `<quickstart:__tsx-doc__>`. |
| `_WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN` | `visit_reference` whole-document label | `_namespace_label(target_docname, anchor or TOKEN)` | ✓ WIRED | `translator.py:5302-5304`; observed in real output as `query(<user_guide_u2f_configuration:__tsx-doc__>)` — the demand side byte-matches the supply side by construction (both routed through the one constant and the one namespacer). |
| `_resolve_xref_docname` (pure path arithmetic) | `_whole_document_reference_eligible` (policy) | Single call site in `_reference_anchor_decision` (`:3216-3230`) | ✓ WIRED | Resolution and policy are separated exactly as the owner's option required; the policy is consulted once, immediately after the resolver. |
| `_reference_anchor_decision.xref` | `visit_reference`'s guarded branch | `elif xref is not None:` | ✓ WIRED | Empty-anchor (whole-document) and non-empty-anchor (anchored) cases enter the SAME guarded branch and the SAME `query(<label>).len() > 0` else path. |
| `visit_reference` (open) | `depart_reference` (close) | `self._reference_guard_close` | ✓ WIRED | Set at `:5309`, consumed and cleared at `:5364-5366`, defensively cleared in the skip-wrapper branch. |
| `visit_pending_xref` (open) | `depart_pending_xref` (close) | Dedicated `_pending_xref_guard_close` slot | ✓ WIRED | Unchanged by the gap-closure wave (verified: 48-07's diff touches none of those hunks). |
| Baseline enumeration (48-05 task 1) | Post-fix re-enumeration (48-07 task 3) | Same build invocation, same snippet | ✓ WIRED | Both `uv run tox -e docs-pdf` + the same pypdf snippet; I re-ran the snippet myself and reproduced the post-fix figures byte-for-byte. |
| Owner decision (48-05 §6) | Expected post-fix count `5` | Written before any emitter change | ✓ WIRED | Commit-time ordering proves it (12:46 vs. 13:24). |

### Data-Flow Trace (Level 4)

| Artifact | Data variable | Source | Produces real data | Status |
|----------|---------------|--------|--------------------|--------|
| `visit_reference` guarded branch | `label` | `_namespace_label(target_docname, anchor or TOKEN)` — target docname from `_resolve_xref_docname`'s real path arithmetic over `builder.get_target_uri()` | Yes — observed non-empty, correctly namespaced labels in real emitted `.typ` | ✓ FLOWING |
| `_whole_document_reference_eligible` | `found_docs` | `builder.env.found_docs` (13 real docnames in the docs corpus, enumerated in the evidence) | Yes | ✓ FLOWING |
| `visit_document` self-anchor | `docname` | `_current_docname()` | Yes — one anchor per content file, verified in emitted output and by the render gate's once-per-file assertion | ✓ FLOWING |
| Built PDF link annotations | `/Dest` destinations | Typst `link(<label>, …)` resolved at compile time | Yes — 72 internal destinations, up from 37 | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full suite green, no xfail/XPASS | `uv run python -m pytest -q` | 1080 passed, 5 skipped (env-gated), 0 failed, 0 xfailed, 0 xpassed | ✓ PASS |
| Four named gates green | `uv run python -m pytest tests/test_whole_document_xref_unit.py tests/test_xref_whole_document_guard_render_gate.py tests/test_duplicate_include_label_render_gate.py tests/test_pdf_render_gate.py -q -rxX` | 50 passed, no xfail/XPASS reported | ✓ PASS |
| CR-01 regression isolated (single named test) | `pytest "…::test_non_internal_reference_onto_known_document_not_guarded" -v` | PASSED | ✓ PASS |
| Single guard-string derivation point | `grep -c 'query(<{label}>)' typsphinx/translator.py` | `1` | ✓ PASS |
| Build-time mechanism absent | `grep -rn 'master_included_docnames\|_compute_master_included_docnames\|degrade_xref_to_text' typsphinx/` | exit 1, no output | ✓ PASS |
| Docs PDF dead-link population (G-48-4 close) | `pypdf` enumeration of `docs/_build/pdf/typsphinx.pdf` | 119 pages; `/Dest` 72, URI 430, other 0 (502); `.pdf`-suffixed URI actions = **5** (the 5 option-a virtual pages only) | ✓ PASS |
| Self-anchor + guard visible in real emitted output | inspect `docs/_build/pdf/quickstart.typ` | `[#metadata(none) <quickstart:__tsx-doc__>]` at line 12; four `query(<…:__tsx-doc__>)` guards; same-document ref still `link(<quickstart:your-first-pdf>, ` | ✓ PASS |
| `make_id` collision-safety claim re-derived | `python -c "from docutils.nodes import make_id; …"` (7 adversarial probes) | No probe produced an underscore → `__tsx-doc__` unreachable | ✓ PASS |
| Lint / format / types | `black --check`, `ruff check .`, `mypy typsphinx/` | 272 files unchanged; All checks passed; Success (6 files) | ✓ PASS |
| Docs PDF rebuild from scratch by the verifier | `tox -e docs-pdf` | ? SKIP — `myst-parser` is not installed in the main checkout's dev venv (it lives in the `docs` extra), so I could not rebuild. Mitigated: I enumerated the committed 2026-08-14 13:56 build artifact directly, and the CR-01 conjunct provably cannot change this corpus's numbers (no hand-written `out_suffix`-suffixed link exists under `docs/source/`, and all 35 closed annotations are `internal=True` `make_refnode` outputs). | ? SKIP (mitigated) |

### Probe Execution

No `scripts/*/tests/probe-*.sh` probes exist in this repository and no plan declares one — this
project's equivalent runnable checks are the pytest render gates, executed above.

### Prohibition Check (must-NOTs)

Each plan's `must_haves.prohibitions` entries are plain judgment-tier statements (no
`{statement, status, verification}` shape). Each was checked against code/git evidence rather than
accepted silently. The owner-judgment half of these (the accepted trade-offs) is separately and
explicitly discharged in `48-UAT.md` (status `complete`, tests 1-3 and 6 all `pass`).

| Prohibition | Status | Evidence |
|-------------|--------|----------|
| Must not swallow or suppress Sphinx's own broken-reference diagnostics | ✓ NOT VIOLATED | The docs build still reports "build succeeded, 5 warnings" (same warning population as the pre-fix baseline); no `logger` suppression, filter, or `SkipNode` was added anywhere in the phase diff. |
| A present-target reference must not render differently from a degraded one (D-02) | ✓ NOT VIOLATED | `test_reference_visible_text_present_in_pdf` and `test_orphan_body_marker_never_appears_in_master_pdf` green; the evidence records identical extracted "What's Next?" prose before and after. |
| No second, competing degrade decision under any name | ✓ NOT VIOLATED | `grep -c 'query(<{label}>)'` → 1; zero `master_included_docnames`; `_whole_document_reference_eligible` is a ROUTING predicate (which of the guard's two existing outcomes a reference enters), never a degrade decision — the degrade is still made only by Typst's `query(<label>).len() > 0` else branch. |
| No change to `typsphinx/` in plans 48-05 and 48-06 | ✓ NOT VIOLATED | `git show --name-only` over all seven commits in those two waves → planning/tests/fixtures only. |
| No assertion softened to pass pre-fix; no copying of fresh build output into an expected block | ✓ NOT VIOLATED | RED transcripts pasted in `48-RED-EVIDENCE.md`; gates committed with 8 `xfail(strict=True)` markers at `b5c8c1ab` and flipped only by the emitter commit; expected values committed at 12:46, emitter at 13:24. |
| No second guard-string derivation point / no second label helper / no re-derivation inside the guard | ✓ NOT VIOLATED | Single definition, single `query(<{label}>)` occurrence, `test_helper_calls_no_label_derivation_routine` green. |
| No replacement for the deleted build-time degrade warning under any name (D-01) | ✓ NOT VIOLATED | Every `logger.warning` in `translator.py` enumerated (8 sites); none is on the cross-document degrade path — the one inside `visit_reference` (`:5263`) is the pre-existing empty-URL warning. |
| No widening beyond G-48-4 (anchored xref, citation backref, `pending_xref` paths keep shipped behaviour) | ✓ NOT VIOLATED | 48-07's translator diff is six hunks: the constant, `visit_document`, the new predicate, `_reference_anchor_decision`, `_resolve_xref_docname`, `visit_reference`. The citation backref sites (`:3524`/`:3536`) and `visit_pending_xref` (`:4575`) are outside every hunk. |
| No typing-import modernization while touching these files (binding constraint #9) | ✓ NOT VIOLATED | `git diff e72dc323^..HEAD -- typsphinx/translator.py \| grep -E "^[-+].*(from typing\|import typing\|Dict\|List)"` → no output. |

### Requirements Coverage

| Requirement | Source plans | Description | Status | Evidence |
|-------------|--------------|-------------|--------|----------|
| XREF-03 | 48-01, 48-02, 48-04, 48-05, 48-06, 48-07 | A cross-document reference whose target label is absent from the compiling master degrades to plain text at compile time instead of aborting | ✓ SATISFIED | Truths 1, 5, 8, 10-19. `REQUIREMENTS.md:70-73` `[x]` with evidence citations that resolve to real, read sections. Extended by the gap-closure wave to the whole-document case. |
| XREF-04 | 48-01, 48-02, 48-03, 48-04, 48-07 | Every label-reference emission site routes through one shared guard, and `master_included_docnames` is removed | ✓ SATISFIED | Truths 2, 3, 18; `REQUIREMENTS.md:75-77` `[x]`. Traceability matrix rows 260-261 read "Phase 48 | Complete" for both. |

**Orphaned requirements:** none. `REQUIREMENTS.md`'s Phase 48 mapping lists exactly XREF-03 and
XREF-04, and every plan's `requirements:` frontmatter (including 48-05 `[XREF-03]`, 48-06
`[XREF-03]`, 48-07 `[XREF-03, XREF-04]`) is a subset of that set. Full accounting both ways.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | Debt markers (`TBD`/`FIXME`/`XXX`) | none | `grep -nE "TBD\|FIXME\|XXX"` over all 28 files touched across the full phase range (`e72dc323^..HEAD`, `typsphinx/` + `tests/`) → exit 1, zero matches. |
| `typsphinx/translator.py` | 5867 | Literal `TODO-01` | ℹ️ Info (false positive) | A requirement/threat identifier inside `visit_todo_node`'s docstring (the `sphinx.ext.todo` handler), not a debt marker. |
| `typsphinx/translator.py` | 4441-4457 | `visit_pending_xref`'s guard uses a fixed `"#"` prefix regardless of markup mode | ℹ️ Info (pre-existing, IN-02) | Carried forward unchanged; documented in the code's own comment as an unreachable defence-in-depth path. |
| `typsphinx/translator.py` | 4336-4338 | Stale comment claiming the preceding closing token is "always `)`" | ℹ️ Info (IN-01) | Cosmetic only. |
| `docs/_build/pdf/typsphinx.pdf` | — | 5 remaining dead links (`genindex`, `py-modindex`, `search`, and two `../` forms) | ℹ️ Info (accepted by policy) | Deliberate option-a residual, chosen by the owner at the 48-05 blocking checkpoint and re-confirmed in 48-UAT test 6 (`pass`). Not a defect. |
| `tests/fixtures/xref_label_collision_guard_gate/` | — | Label-namespace collision false negative (WR-02) | ℹ️ Info (accepted + filed) | Owner-accepted (48-UAT test 1) and filed as a pending todo; verified unworsened by the whole-document path, which queries a token no `make_id` output can produce. |

**Code-review findings status:** both `48-REVIEW.md` findings are resolved and independently
re-confirmed by me — CR-01 (BLOCKER, the missing `internal` conjunct) by reading the restored
predicate body and running the discriminating test, WR-01 by confirming the module docstring now
describes the implemented two-conjunct policy.

### Human Verification Required

**None outstanding.** All four items raised by the 2026-08-12 report were answered by the owner and
are recorded in `48-UAT.md` (`status: complete`, 16/16 pass, 0 issues, 0 pending):

1. Label-collision false-negative trade-off — accepted (test 1).
2. D-11 compile-time cost tier (−2.37%) — accepted (test 2).
3. D-01 diagnostic-visibility loss — accepted (test 3).
4. PDF cross-reference links navigate correctly — originally reported as an issue
   (`ERR_FILE_NOT_FOUND`, gap G-48-4), closed by plans 48-05/06/07 and re-confirmed by the owner
   against the post-fix build (test 5, `pass`); the 5-link option-a residual explicitly accepted
   (test 6, `pass`).

No new human-judgment item arose from this re-verification. The one automated check I could not
run in this environment (a from-scratch `tox -e docs-pdf`, blocked by a missing `myst-parser`) is
recorded as a mitigated SKIP above, not as a human item: the committed build artifact was
enumerated directly and reproduces the pre-declared numbers exactly.

### Gaps Summary

None. All 19 must-haves verified, both requirement IDs satisfied, all nine prohibitions checked
against evidence and not violated, both code-review findings resolved, the UAT complete with zero
open issues, and the security audit verified with zero open threats.

The phase goal is achieved as stated: the degrade decision now lives in Typst
(`context { if query(<label>).len() > 0 { link(<label>, …) } else { … } }`, one derivation point,
four call sites), the build-time union is gone from the tree, same-document anchors are provably
exempt, the cost is measured (−2.37%), and the gap-closure wave extended the same single mechanism
to whole-document `:doc:` references — converting 35 dead `file://` URI actions into real internal
PDF destinations with the annotation total unchanged.

---

_Verified: 2026-08-14T05:34:48Z_
_Verifier: Claude (gsd-verifier)_
_Supersedes: the 2026-08-12T06:57:54Z report (plans 48-01..48-04 only)_
