---
phase: 19-block-separation-fixes-cluster-a
verified: 2026-07-20T00:00:00Z
status: passed
score: 12/12 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 19: Block Separation Fixes (Cluster A) Verification Report

**Phase Goal:** The dominant audit root cause — adjacent block or sibling elements emitted with no
separator — is resolved as one coherent set of `visit_*`/`depart_*` separator fixes in
`typsphinx/translator.py`, so every affected construct renders with the visible separation the
`-b html` authority shows instead of concatenating.
**Verified:** 2026-07-20
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `_emit_forced_break(break_token)` shared helper exists with unconditional trailing newline (Pitfall 1) | ✓ VERIFIED | `typsphinx/translator.py:263-291`; `add_text(f"{break_token}\n")` unconditional; docstring documents the cosmetic-`\n` invariant |
| 2 | FID-02: consecutive `paragraph`s in a `list_item` render `parbreak()`-separated; first paragraph unaffected | ✓ VERIFIED | `visit_paragraph` L720-721 calls `_emit_forced_break("parbreak()")`; `depart_paragraph` L744-745 sets `list_item_needs_separator=True` (previously-missing piece). `tests/test_paragraph_concat_render_gate.py` passes; manually reverted the fix and re-ran — test FAILED with `assert 'parbreak()' in ...`; restored — test PASSED again (confirmed RED→GREEN independently, not just trusting SUMMARY) |
| 3 | FID-03: sibling `desc_signature`s render `linebreak()`-stacked; lone signature byte-unchanged | ✓ VERIFIED | `visit_desc` L4382 resets `_is_first_desc_signature=True`; `visit_desc_signature` L4416-4418 emits leading `linebreak()` for 2nd+ signature only. `TestDescSignatureSiblingsRenderGate::test_typstpdf_sibling_signatures_produce_pdf` asserts exactly 2 `linebreak()` tokens for 3 siblings and 0 around the lone `solo(source)` signature — PASSED |
| 4 | FID-04: rubric option-group heading renders `linebreak()`-separated from following option/field; harmless at end-of-document | ✓ VERIFIED | `depart_rubric` L4783-4784: explicit leading `\n` then `_emit_forced_break("linebreak()")`. `tests/test_rubric_option_concat_render_gate.py` PASSED (includes a trailing end-of-document rubric in the fixture, build succeeds) |
| 5 | FID-05: `depart_definition_list` emits `terms(separator: linebreak(), ...)` (both items and empty branches), NOT via the shared helper | ✓ VERIFIED | `translator.py:1762-1769` — both branches carry `separator: linebreak()`; not routed through `_emit_forced_break` (per Pitfall 3, correctly distinct implementation). `tests/test_deflist_term_concat_render_gate.py` (3 methods incl. 2 new sub-case methods) PASSED |
| 6 | FID-06: back-to-back body-less confvals render `parbreak()`-separated; with-body confvals unaffected | ✓ VERIFIED | `depart_desc` L4398: `self._emit_forced_break("parbreak()")` applied unconditionally. `tests/test_desc_bodyless_concat_render_gate.py` PASSED |
| 7 | Each new/extended GATE-01 gate fails pre-fix, passes post-fix (D-05) | ✓ VERIFIED | Independently reproduced for FID-02 (see truth #2 evidence); SUMMARYs document the same red/green proof for FID-03/04/05/06 with concrete failure messages (`assert 0 == 2`, `assert 'linebreak()' in ...`, `AssertionError: Expected the terms() call to carry separator...`) |
| 8 | The full ~684-page corpus gate stays green after all five fixes | ✓ VERIFIED | `uv run pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -q` → 1 passed (12.63s), run against the merged main tree |
| 9 | No new runtime dependency introduced | ✓ VERIFIED | `git diff 8ad17bf..HEAD -- pyproject.toml` — empty diff |
| 10 | No `@preview` package version bumped | ✓ VERIFIED | Same empty `pyproject.toml` diff; no changes to any `@preview` import declaration |
| 11 | `writer.py`/`template_engine.py`/`templates/base.typ` (3-way version-sync surface) untouched | ✓ VERIFIED | `git diff 8ad17bf..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ` — empty diff |
| 12 | All five sites' edits are confined to `translator.py` and land at exactly the documented line ranges | ✓ VERIFIED | `git diff 8ad17bf..HEAD -- typsphinx/translator.py` shows exactly 7 hunks at lines ~260-296, ~666-711, ~1703-1730, ~4314-4366 (2 hunks), ~4669-4701 — matching the helper + FID-02 + FID-05 + FID-06/FID-03 + FID-04 sites documented in the plans |

**Score:** 12/12 truths verified (0 present-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/translator.py::_emit_forced_break` | New shared helper | ✓ VERIFIED | Exists, substantive, wired (called from 4 sites: L721, L4398, L4417, L4784) |
| `tests/test_paragraph_concat_render_gate.py` | New GATE-01 module (FID-02) | ✓ VERIFIED | Exists, real subprocess sphinx-build + typst.compile() assertions, passes |
| `tests/fixtures/paragraph_concat_render_gate/{conf.py,index.rst}` | New fixture | ✓ VERIFIED | Exists |
| `tests/test_desc_bodyless_concat_render_gate.py` | New GATE-01 module (FID-06) | ✓ VERIFIED | Exists, passes |
| `tests/fixtures/desc_bodyless_concat_render_gate/{conf.py,index.rst}` | New fixture | ✓ VERIFIED | Exists |
| `tests/test_desc_signature_concat_render_gate.py` (extended) | New FID-03 test class | ✓ VERIFIED | `TestDescSignatureSiblingsRenderGate` added alongside pre-existing GATE-02 class, both pass |
| `tests/fixtures/desc_signature_siblings_render_gate/{conf.py,index.rst}` | New fixture | ✓ VERIFIED | Exists |
| `tests/test_rubric_option_concat_render_gate.py` | New GATE-01 module (FID-04) | ✓ VERIFIED | Exists, passes |
| `tests/fixtures/rubric_option_concat_render_gate/{conf.py,index.rst}` | New fixture | ✓ VERIFIED | Exists |
| `tests/test_deflist_term_concat_render_gate.py` (extended) | Two new FID-05 test classes | ✓ VERIFIED | `TestDeflistTermInListitemRenderGate`, `TestDeflistTermNestedListRenderGate` added, pre-existing GATE-02 class undisturbed, all 3 pass |
| `tests/fixtures/deflist_term_in_listitem_render_gate/{conf.py,index.rst}` | New fixture (sub-case a) | ✓ VERIFIED | Exists |
| `tests/fixtures/deflist_term_nested_list_render_gate/{conf.py,index.rst}` | New fixture (sub-case b) | ✓ VERIFIED | Exists |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `visit_paragraph`/`depart_paragraph` | `_emit_forced_break` | direct call + flag set | ✓ WIRED | Confirmed by reading code and by independent revert-and-rerun proof |
| `depart_desc` | `_emit_forced_break` | direct call | ✓ WIRED | L4398 |
| `visit_desc_signature` | `_emit_forced_break` | conditional call | ✓ WIRED | L4416-4417, gated on `_is_first_desc_signature` |
| `depart_rubric` | `_emit_forced_break` | leading `\n` + call | ✓ WIRED | L4783-4784, extra leading newline (deviation, documented, verified necessary) |
| `depart_definition_list` | `terms(separator: linebreak(), ...)` | direct parameter injection, NOT via helper | ✓ WIRED | L1767, L1769 — correctly bypasses the shared helper per Pitfall 3 |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 5 Cluster-A render gates pass together | `uv run pytest tests/test_paragraph_concat_render_gate.py tests/test_desc_bodyless_concat_render_gate.py tests/test_desc_signature_concat_render_gate.py tests/test_rubric_option_concat_render_gate.py tests/test_deflist_term_concat_render_gate.py -q` | 8 passed | ✓ PASS |
| Corpus gate (~684-page Sphinx doc/ corpus, fatal-free) | `uv run pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -q` | 1 passed (12.63s) | ✓ PASS |
| Translator unit suite (structural regression sample) | `uv run pytest tests/test_translator.py -q` | 108 passed | ✓ PASS |
| Full non-slow suite | `uv run pytest -q -m "not slow"` | 483 passed, 23 deselected, 0 failed | ✓ PASS (better than SUMMARY baseline — the documented ~45 pre-existing NixOS-sandbox integration failures do NOT reproduce on the merged main tree; re-ran `tests/test_integration_multi_doc.py tests/test_integration_nested_toctree.py` directly — 23/23 passed) |
| FID-02 RED→GREEN independently reproduced (not just trusting SUMMARY) | Manually reverted `visit_paragraph`'s `_emit_forced_break` call, ran `test_paragraph_concat_render_gate.py`, restored, re-ran | FAILED pre-revert-undo (`assert 'parbreak()' in ...` — token absent), PASSED after restore; `git diff --stat` confirmed byte-identical restore | ✓ PASS |
| black --check on all touched files | `uv run black --check typsphinx/translator.py <6 test files>` | "All done! 7 files would be left unchanged." | ✓ PASS |
| mypy on translator.py | `uv run mypy typsphinx/translator.py` | Success: no issues found | ✓ PASS |
| Milestone invariant: no writer.py/template_engine.py/templates/base.typ/pyproject.toml changes | `git diff 8ad17bf..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ pyproject.toml` | empty diff | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| FID-02 | 19-01 | Consecutive paragraphs in list_item concatenate | ✓ SATISFIED | `visit_paragraph`/`depart_paragraph` fix + passing gate + independently reproduced RED→GREEN |
| FID-03 | 19-02 | Sibling desc_signatures run together | ✓ SATISFIED | `visit_desc`/`visit_desc_signature` fix + passing gate with exact-count assertion |
| FID-04 | 19-02 | Rubric option-group heading merges onto following option | ✓ SATISFIED | `depart_rubric` fix + passing gate |
| FID-05 | 19-03 | Definition-list term merges onto its definition | ✓ SATISFIED | `depart_definition_list` `terms(separator: linebreak())` fix + 2 sub-case gates passing |
| FID-06 | 19-01 | Back-to-back body-less confvals concatenate | ✓ SATISFIED | `depart_desc` fix + passing gate |

No orphaned requirements — REQUIREMENTS.md maps exactly FID-02..FID-06 to Phase 19, and all five appear in a plan's `requirements` field. (Note: REQUIREMENTS.md's own checkboxes and the "Pending" status column, and ROADMAP.md's Phase 19 top-level checkbox, are still unchecked — these are bookkeeping fields updated by the ship/complete-milestone workflow, not blockers to this phase's goal achievement. Flagged as an informational note, not a gap.)

### Anti-Patterns Found

None. Scanned all files touched or created by this phase (`typsphinx/translator.py` plus all 6 new/extended test modules and 6 fixture pairs) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`/empty-implementation patterns. The only hits (`TODO-01` at translator.py:3983, `placeholder`-named graphviz/inheritance-diagram degrade helpers at translator.py:4314-4353) are pre-existing code from an earlier phase, confirmed NOT touched by this phase's diff (`git diff 8ad17bf..HEAD` hunks land only at the 5 documented sites: the helper, `visit_paragraph`/`depart_paragraph`, `depart_definition_list`, `depart_desc`/`visit_desc`/`visit_desc_signature`, `depart_rubric`).

### Human Verification Required

None. All truths are verified via structural `.typ` token assertions plus real `typst.compile()` → `%PDF` magic-byte checks (D-06's chosen verification tier for this milestone — rasterized glyph-position checks were explicitly rejected). This verifier additionally reproduced the FID-02 RED→GREEN proof independently rather than trusting the SUMMARY's narrative account.

### Gaps Summary

No gaps. All 12 must-have truths verified against the actual codebase (not just SUMMARY claims): the shared helper and all five `visit_*`/`depart_*` fixes exist at the exact documented sites, are wired correctly, are covered by real-compile render-gate tests that pass, the corpus gate stays green, milestone invariants (no new deps, no `@preview` bump, version-sync surface untouched) hold via direct git diff inspection, and one fix (FID-02) was independently revert-tested to confirm the RED→GREEN claim rather than trusting the SUMMARY narrative.

---

_Verified: 2026-07-20_
_Verifier: Claude (gsd-verifier)_
