---
phase: 25-captioned-table-figure-wrap-cross-references-reimplement-pr
verified: 2026-07-24T00:30:00Z
status: passed
score: 7/7 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 25: Captioned Table Figure Wrap + Cross-References Verification Report

**Phase Goal:** A captioned table renders as a numbered "Table N" figure that can be cross-referenced, while a caption-less table stays a plain table.
**Verified:** 2026-07-24T00:30:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC#1: `.. table:: Caption` renders as `figure(table(...), caption:, kind: table)` with native "Table N" numbering, no stray `heading()`, inline markup preserved | VERIFIED | `typsphinx/translator.py` `depart_table` (lines 2558-2588) emits `figure(\n{table_code},\n  caption: {{...}},\n  kind: table\n)`; `visit_title`/`depart_title` (lines 513-522, 603-610) buffer the caption via `table_cell_content` and `return` before any `heading()` emission. Proven by `tests/test_translator.py::test_captioned_table_buffers_caption_no_heading`, `::test_captioned_table_renders_as_figure`, `::test_table_caption_supports_inline_markup` (all PASS, confirmed by direct run: 8/8 targeted + 116/116 full `test_translator.py`), and real-compile `tests/test_pdf_render_gate.py::TestCaptionedTableRenderGate::test_typ_source_uses_figure_kind_table_with_no_heading_above` (PASS, confirmed by direct run) |
| 2 | SC#2: caption-less table stays a plain `table()`, never figure-wrapped | VERIFIED | `depart_table`'s `else` branch (line 2596-2603) is byte-for-byte the pre-existing plain-table path, gated on `if self.table_caption:` (truthy check). `tests/test_translator.py::test_uncaptioned_table_not_wrapped_in_figure` PASS (confirmed by direct run) |
| 3 | SC#3: caption + `:width:` compose (`block(width:)[#figure(... kind: table) <label>]`) | VERIFIED | `depart_table` lines 2572-2588 mirror `depart_figure`'s three-way width/ids branch exactly. `tests/test_translator.py::test_captioned_table_with_width_composes_figure_and_block` PASS; real-compile `TestCaptionedTableRenderGate::test_each_caption_sentinel_appears_exactly_once` includes the width-table sentinel (`TBLCAPWIDTHSENTINEL`), confirmed PASS |
| 4 | SC#4: 2nd-and-later captioned table keeps its own caption (stale-buffer fix) | VERIFIED | `depart_table` deletes (not resets) `table_cell_content` (line 2621-2622) — the documented root-cause fix. `tests/test_translator.py::test_table_caption_not_lost_after_previous_table` (both captions present, PASS) AND the real-compile 2-table fixture `tests/fixtures/captioned_table_render_gate/index.rst` (`TBLCAPFIRSTSENTINEL`/`TBLCAPSECONDSENTINEL`) asserted `count == 1` each in `TestCaptionedTableRenderGate::test_each_caption_sentinel_appears_exactly_once` (PASS, confirmed by direct run) — a single-table fixture could not expose this bug, so this is genuine behavioral proof, not presence-only |
| 5 | SC#5: `:numref:`/`:ref:` to a captioned table resolves; single `<label>` from ids[0]; no collision with `_emit_id_anchors` | VERIFIED | `visit_table` (line 2427-2429) skips `_emit_id_anchors(node)` when captioned; `depart_table` (line 2595) calls it with `skip_ids=set(node.get("ids", [])[:1])` after the figure's own `<label>` postfix. Unit: `test_captioned_table_single_label` (label count == 1, PASS). Real-compile: `TestCaptionedTableRenderGate::test_xref_numref_ref_resolve_no_empty_link` (`link(<` present, `link("",` absent, PASS) plus a genuine `typst.compile()` of the fixture succeeding at all (a double-anchor would abort the whole compile — this is the strongest possible proof). Durable fail-pre-fix proof: `TestCaptionedTablePreFixBasisFailureProof::test_double_anchor_basis_raises` reconstructs the pre-fix double-anchor shape and confirms `typst.compile()` raises (PASS, confirmed by direct run) |
| 6 | Backstop: a whitespace-only table caption strips to empty (falsy) and falls back to a plain `table()`, never an empty-caption `figure()` | VERIFIED | `depart_table` gates on `if self.table_caption:` (truthiness, not `is not None`) — line 2558. `tests/test_translator.py::test_empty_table_title_falls_back_to_plain_table` PASS (confirmed by direct run) |
| 7 | D-01 invariant: `templates/base.typ` byte-unchanged; no `@preview` version bump; no new runtime dependency | VERIFIED | `git status --short -- typsphinx/templates/base.typ` empty; `git log` shows no phase-25 commit touching `base.typ`, `writer.py`, or `template_engine.py`; all three `@preview` version-sync sites (`writer.py:151-154`, `template_engine.py:374-377`, `templates/base.typ:8,9,14,19`) grep-identical to pre-phase values; `tests/test_preview_version_sync.py` PASS |

**Score:** 7/7 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/translator.py` | caption buffering + figure-wrap emission + deferred id-anchoring | VERIFIED | `table_caption`/`_in_table_caption`/`_caption_saved_list_state` state (lines 98-107); `visit_title`/`depart_title` new branches (513-522, 603-610); `visit_table` captioned pre-check (2427-2429); `depart_table` figure-wrap + label + deferred anchor + `del table_cell_content` (2503-2622) |
| `tests/test_translator.py` | 8 new unit tests | VERIFIED | `test_captioned_table_buffers_caption_no_heading`, `test_captioned_table_renders_as_figure`, `test_table_caption_supports_inline_markup`, `test_table_caption_not_lost_after_previous_table`, `test_uncaptioned_table_not_wrapped_in_figure`, `test_captioned_table_single_label`, `test_captioned_table_with_width_composes_figure_and_block`, `test_empty_table_title_falls_back_to_plain_table` — all present and passing (8/8 targeted run, 116/116 full-file run) |
| `tests/fixtures/captioned_table_render_gate/conf.py` | minimal Sphinx config, `numfig = True` | VERIFIED | present, correct (`typst_documents` master tuple for `index`, `numfig = True`) |
| `tests/fixtures/captioned_table_render_gate/index.rst` | 2+ captioned tables, caption+width, numref/ref, csv/list-table | VERIFIED | present: 2 plain captioned tables (stale-buffer proof), 1 caption+`:width:` table, `:numref:`/`:ref:` paragraph, captioned csv-table + list-table |
| `tests/test_pdf_render_gate.py` | `TestCaptionedTableRenderGate` + `TestCaptionedTablePreFixBasisFailureProof` | VERIFIED | both classes present (lines 2441, 2554); 6 tests total, all PASS on direct real-compile run |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `add_text()` in_table routing | `self.table_cell_content` buffer | caption capture reuses this dispatch | WIRED | `visit_title`'s captioned branch resets `self.table_cell_content = []` and relies on `add_text`'s existing `self.in_table and hasattr(self, "table_cell_content")` routing rule (line 283-285) |
| `depart_table` figure-wrap | existing `:width:` `block(width:)[...]` wrap | block wraps the WHOLE figure (D-04) | WIRED | Lines 2572-2588 mirror `depart_figure`'s three-way ids/width branch |
| `depart_table` figure `<label>` | `visit_table` `_emit_id_anchors` skip | double-anchor collision fix | WIRED | `visit_table` line 2427-2429 skips for captioned tables; `depart_table` line 2595 anchors with `skip_ids={ids[0]}` after the label postfix — proven not just present but functionally correct by a REAL `typst.compile()` succeeding on a `:name:`-tagged captioned table (a double-anchor would abort the whole compile) |

### Behavioral Spot-Checks / Probe Execution (real `typst.compile()` GATE-01)

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full `tests/test_translator.py` unit suite | `uv run python -m pytest tests/test_translator.py -q` | 116 passed | PASS |
| Targeted captioned/uncaptioned/caption/empty-title unit tests | `uv run pytest tests/test_translator.py -q -k "captioned_table or uncaptioned_table or table_caption or empty_table_title"` | 8 passed | PASS |
| GATE-01 real-compile captioned-table gate | `uv run python -m pytest tests/test_pdf_render_gate.py -k Captioned -v` | 6 passed (`TestCaptionedTableRenderGate` x4, `TestCaptionedTablePreFixBasisFailureProof` x2) | PASS |
| `@preview` version-sync invariant | `uv run python -m pytest tests/test_preview_version_sync.py -q` | 2 passed | PASS |
| Fast full suite (excluding slow) | `uv run python -m pytest -q -m "not slow"` | 567 passed, 29 deselected | PASS (matches documented expected baseline) |
| Lint / format | `nix-shell -p ruff --run "ruff check ..."`, `uv run black --check ...` | clean | PASS |
| `base.typ` diff | `git status --short -- typsphinx/templates/base.typ` | empty | PASS |

All commands above were run directly by the verifier in this session (sandbox lifted, real `typst`/`pypdf` available) — not taken from SUMMARY.md claims.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|--------------|------------|-------------|--------|----------|
| TBL-01 | 25-01, 25-02 | Figure wrap, no stray heading, caption-less stays plain, inline markup, caption+width, 2nd-table stale-buffer | SATISFIED | Truths #1-4, #6 above; unit tests + real-compile gate |
| TBL-02 | 25-01, 25-02 | `:numref:`/`:ref:` resolves to `<label>` from ids[0], no `_emit_id_anchors` collision | SATISFIED | Truth #5 above; unit test + real-compile gate + durable fail-pre-fix proof |

No orphaned requirements: REQUIREMENTS.md maps only TBL-01/TBL-02 to Phase 25, and both are declared in both plans' `requirements` frontmatter field.

**Note (informational, not a gap):** `.planning/REQUIREMENTS.md` still shows `- [ ]` (unchecked) for TBL-01/TBL-02 and the traceability table still says "Pending" for Phase 25. Per the observed project convention (Phase 24's `5b76e9e docs(phase-24): complete phase execution` commit), these checkboxes and ROADMAP.md's phase-25 `[ ]` are updated in a separate "complete phase execution" step that follows verification — not evidence of incomplete work.

### Anti-Patterns Found

None. `grep -n -E "TBD|FIXME|XXX"` across `typsphinx/translator.py`, `tests/test_translator.py`, `tests/test_pdf_render_gate.py`, and the new fixture files returned zero hits. No stub returns, no empty handlers, no `node.astext()` usage for caption text (confirmed by reading the caption-emission code path — it routes through `table_cell_content`, which is only ever populated by the normal inline-visitor chain via `add_text()`).

### Human Verification Required

None. Every truth in this phase (including the two state-transition/invariant-shaped ones — SC#4 stale-buffer and SC#5 double-anchor collision) has a passing behavioral test that actually exercises the invariant: SC#4 via a real two-table `typst.compile()` with an exact-once sentinel-count assertion (not obtainable from a single-table fixture), and SC#5 via a real `typst.compile()` that would abort entirely on a double-anchor (plus a durable fail-pre-fix reconstruction proving the assertion is genuinely discriminating). No visual/appearance-only claim remains unverified — Typst's native "Table N" numbering is produced by Typst's own `kind: table` figure machinery once `figure(..., kind: table)` compiles successfully, which is directly proven by the real-compile gate.

### Gaps Summary

No gaps. All 7 must-have truths (5 ROADMAP Success Criteria + 1 backstop + 1 milestone invariant) are verified with direct evidence: source-code inspection confirming the described logic exists at the cited line numbers, a passing unit-test suite (116/116 `test_translator.py`, including 8 new tests), a passing real-`typst.compile()` GATE-01 fixture (6/6, run directly in this session, not taken on SUMMARY.md's word), a passing durable fail-pre-fix proof, and confirmation that no forbidden surface (`templates/base.typ`, `@preview` versions, new runtime deps) was touched. The fast full suite (567 passed) matches the documented pre-existing baseline with no new failures attributable to this phase.

---

*Verified: 2026-07-24T00:30:00Z*
*Verifier: Claude (gsd-verifier)*
