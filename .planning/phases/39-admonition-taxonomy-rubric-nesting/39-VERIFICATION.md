---
phase: 39-admonition-taxonomy-rubric-nesting
verified: 2026-08-02T03:33:10Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 39: Admonition Taxonomy + Rubric Nesting Verification Report

**Phase Goal:** Admonitions land in the reference's four colour buckets with the generic directive
styled and titled; a rubric inherits its container's indent
**Verified:** 2026-08-02T03:33:10Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth (ROADMAP SC / requirement) | Status | Evidence |
|---|---|---|---|
| 1 | SC#1/ADM-01/ADM-02: `seealso` routes to the same bucket as `hint`/`tip` (`tip()`); `attention`/`danger` route to the same bucket as `error` (`error()`) | VERIFIED | `typsphinx/translator.py:4468` (`visit_seealso` → `_visit_admonition(node, "tip")`), `:4517`/`:4525` (`visit_danger`/`visit_attention` → `_visit_admonition(node, "error")`). Live-run: `tests/test_admonition_bucket_render_gate.py::test_seealso_routes_to_tip_bucket`, `::test_attention_routes_to_error_bucket`, `::test_danger_routes_to_error_bucket` — all pass (re-ran directly, 10/10 in that module). PDF half: `tests/test_pdf_render_gate.py::TestAdmonitionPdfRenderGate::test_admonitionbuckettitlegate` passes. `grep -c '_visit_admonition([^)]*"danger"'` returns 0 — `danger` is no longer emitted as a distinct function. |
| 2 | SC#2/ADM-03: a generic `.. admonition:: Custom Title` renders as a styled box (`notify(...)`) carrying that title, surviving into the compiled PDF; `.. topic::` renders as a styled box (`abstract(...)`) | VERIFIED | `typsphinx/translator.py:4560` (`visit_admonition` → `notify`), `:4589` (`visit_topic`, non-`contents` branch → `abstract`). `grep -c '_visit_admonition([^)]*"clue"'` returns 0 — the base `clue` function no longer appears anywhere. Re-ran `tests/test_admonition_bucket_render_gate.py::test_generic_admonition_routes_to_notify`, `::test_topic_routes_to_abstract`, `::test_no_real_admonition_type_ever_uses_base_clue` — all pass. `_visit_admonition`'s title path is unconditional (`_pending_admonition_title` / `_custom_admonition_title` → `title:` arg), so the directive's own title always attaches — confirmed by the ten-type `admonitionlabels` catalog lookup at `translator.py:4386` plus the directive-supplied-title precedence test `tests/test_admonitions.py::test_note_with_own_title_wins_over_catalog` (pass). |
| 3 | SC#3/ADM-05 (corrected per D-12, an invariance guard): a rubric inside a description body — including a nested `py:class::`/`py:method::` — has a left edge equal to its containing body's edge and strictly greater than the page margin, at every nesting level, using only relative (`==`/`>`/`<=`) `pypdf` column comparisons | VERIFIED | `tests/test_rubric_indent_invariance.py` (7 tests) — re-ran directly, all pass; confirmed every assertion in the file is a relative comparison (`==`, `>`, `<=` between two measured columns), no pinned literal. `visit_rubric`/`depart_rubric` add no indent logic of their own (Phase 38's `pad(left: SHARED_INDENT_STEP, …)` around `desc_content` is the sole mechanism, confirmed unmodified this phase — no hunk touches `desc_content`'s pad wrapper). |
| 4 | SC#3 corollary (folded defects, D-11/D-13): a rubric with an inline `strong` child no longer corrupts the shared list-item/paragraph state for the rest of the document (D-13); an anchored (propagated-target) rubric emits exactly one separator newline, not three (D-11) | VERIFIED (behavioral) | Behavior-dependent (state-corruption / ordering invariant), so presence alone would not be sufficient — ran the actual behavioral tests directly rather than trusting the SUMMARY: `tests/test_rubric_strong_nesting_render_gate.py` (6/6 pass, including the three previously-RED document-wide `par()`-wrapper assertions) and `tests/test_desc_rubric_decoupling_render_gate.py` (5/5 pass, including the D-11 newline-run-of-1 assertion and the golden-byte-identity test). Code confirms the mechanism: `visit_rubric`/`depart_rubric` (`translator.py:5804-5975`) now save/restore under `_rubric_was_*` names (not the `_strong_was_*` names still shared, unmodified, by `visit_strong`/`depart_strong` at line 1476 and `visit_desc_signature`/`depart_desc_signature` at line 5119), and gate both the unconditional leading newline and the list-item separator check on whether `_emit_id_anchors` already emitted something (`anchors_were_emitted`). |
| 5 | SC#4/ADM-04 ([V], human-only visual UAT): the four admonition kinds remain distinguishable in a greyscale render of the compiled PDF, without hue | VERIFIED (recorded human sign-off, not re-derived) | `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-SIGNOFF.md` exists, is legible, and records an operative decision: **MET on icon-shape grounds**, title-band luminance uniform and recorded as an explicit caveat (not a defect). Artifact `39-ADM04-GREYSCALE.png` (35,570 bytes, mode `L`, 1240×1754) is committed and its provenance (commit `dedae01`, rendered after the bucket-routing fix, pre-render green-gate confirmation) is recorded in the sign-off. Per this task's instructions, this verdict is taken as given and not re-judged. |
| 6 | SC#5: the phase's exact-string blast radius is migrated by hand-derived expected strings (not copied from failing output), and the full-corpus `-b typstpdf` gate actually runs green (a skip is not a pass) | VERIFIED | `tests/test_corpus_gate.py -m slow` re-run directly: `1 passed, 1 skipped, 3 deselected` — the 1 passed is the corpus gate itself (confirmed by node id `test_full_corpus_render_gate` under the `.s` collection order); the skip is an unrelated env-gated diagnostic. `39-TEST-CENSUS.md` records a re-measured (not recalled) census matching both the discussion-time and planning-time predictions with no disagreement. Full suite re-run directly: `763 passed, 1 skipped, 0 failed` (matches the orchestrator's independently measured cross-check exactly). |

**Score:** 5/5 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `typsphinx/translator.py` (`_visit_admonition`/`_depart_admonition` + 12 per-type visitors) | Bucket re-routing + catalog-title lookup | ✓ VERIFIED | Re-read directly; matches the bucket table exactly (note→info, warning/caution/important→warning, tip/hint/seealso→tip, error/danger/attention→error, todo→task, admonition→notify, topic→abstract). `admonitionlabels` imported at line 13, looked up once at line 4386. |
| `typsphinx/translator.py` (`visit_rubric`/`depart_rubric`, lines 5804-5975) | Own `_rubric_was_*` slots; anchor-aware separator guard | ✓ VERIFIED | Re-read directly; slots renamed, guard present, `visit_strong`/`visit_desc_signature` confirmed untouched (still share `_strong_was_*`). |
| `tests/test_admonition_bucket_render_gate.py` | Region-scoped GATE-01 RED→GREEN for all 5 bucket moves + catalog titles | ✓ VERIFIED | Re-ran directly: 10/10 pass. |
| `tests/test_rubric_strong_nesting_render_gate.py` | D-13 document-wide RED→GREEN | ✓ VERIFIED | Re-ran directly: 6/6 pass. |
| `tests/test_desc_rubric_decoupling_render_gate.py` | D-11 newline-run RED→GREEN + golden byte-identity | ✓ VERIFIED | Re-ran directly: 5/5 pass. |
| `tests/test_rubric_indent_invariance.py` | ADM-05/SC#3 relative-column invariance guard | ✓ VERIFIED | Re-ran directly: 7/7 pass; confirmed no pinned literals. |
| `scripts/render_admonition_greyscale.py` + `tests/fixtures/admonition_greyscale_probe/` | ADM-04 render pipeline | ✓ VERIFIED | Pipeline test re-ran directly: 2/2 pass. |
| `.planning/phases/.../39-ADM04-GREYSCALE.png` + `39-ADM04-SIGNOFF.md` | Committed render + recorded owner verdict | ✓ VERIFIED | Both present on disk; sign-off records MET verdict (taken as given, not re-derived). |
| `pyproject.toml` `[dev]` extra | `pillow` added, runtime deps untouched | ✓ VERIFIED | `grep pillow pyproject.toml` → 1 hit in `[dev]`; `git diff` scope confined to the dev array. |
| `.planning/REQUIREMENTS.md` | ADM-01..ADM-05 flipped to `[x]` | ✓ VERIFIED | Re-read directly; all five checked, ADM-04 entry quotes the sign-off verbatim. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `visit_seealso`/`visit_danger`/`visit_attention` | `_visit_admonition` | direct call with re-routed `clue_type` arg | WIRED | Confirmed by direct read of `translator.py`. |
| `_visit_admonition` | `sphinx.locale.admonitionlabels` | module-level import + `catalog_key in admonitionlabels` lookup | WIRED | Confirmed; `todo_node`/`admonition`/`topic` correctly excluded (not catalog keys). |
| `_depart_admonition` (static title branch) | `escape_typst_string` | `escape_typst_string(str(self._custom_admonition_title))` | WIRED | Confirmed at line ~4413; catalog values (lazy i18n proxies) coerced to `str` before escaping. |
| `visit_rubric` | `_emit_id_anchors` | `len(self.body)` delta measures whether anchoring emitted anything | WIRED | Confirmed; both halves of the double-count (unconditional newline + separator-flag check) gated on the same `anchors_were_emitted` boolean. |
| `visit_rubric`/`depart_rubric` | rubric's own `_rubric_was_*` attributes | save/restore pair, independent of `visit_strong`'s `_strong_was_*` | WIRED | Confirmed no name collision remains; `visit_strong`/`visit_desc_signature` still use `_strong_was_*` unmodified. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Bucket-routing gate (5 DEFECT-CASE + catalog-title, all types) | `uv run pytest tests/test_admonition_bucket_render_gate.py -q` | 10 passed | ✓ PASS |
| D-13 document-wide `par()`-wrapper preservation (behavior-dependent) | `uv run pytest tests/test_rubric_strong_nesting_render_gate.py -q` | 6 passed | ✓ PASS |
| D-11 separator-run + golden byte-identity (behavior-dependent) | `uv run pytest tests/test_desc_rubric_decoupling_render_gate.py -q` | 5 passed | ✓ PASS |
| ADM-05 relative-column invariance guard | `uv run pytest tests/test_rubric_indent_invariance.py -q` | 7 passed | ✓ PASS |
| Admonition/topic unit + compiled-PDF regression | `uv run pytest tests/test_admonitions.py tests/test_topics.py tests/test_pdf_render_gate.py -q` | 54 passed | ✓ PASS |
| Greyscale render pipeline smoke test | `uv run pytest tests/test_admonition_greyscale_pipeline.py -q` | 2 passed | ✓ PASS |
| `@preview` version-sync (gentle-clues pin unchanged) | `uv run pytest tests/test_preview_version_sync.py -q` | 3 passed | ✓ PASS |
| Full-corpus `-b typstpdf` gate (must actually run, not skip) | `uv run pytest tests/test_corpus_gate.py -m slow -q` | 1 passed, 1 skipped (unrelated env-gated diagnostic), 3 deselected | ✓ PASS |
| Full unfiltered suite (regression check) | `uv run python -m pytest -q` | 763 passed, 1 skipped, 0 failed | ✓ PASS — matches orchestrator's independently measured cross-check |

### Probe Execution

No `scripts/*/tests/probe-*.sh` convention is used by this project; this phase's equivalent "probe" gates are the pytest render-gate/corpus-gate modules above, executed directly rather than assumed from SUMMARY narration.

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| ADM-01 | 39-01 (RED), 39-05 (fix), 39-08 (close) | `seealso` joins the `hint`/`tip` bucket | ✓ SATISFIED | `visit_seealso` → `tip`; gate tests pass |
| ADM-02 | 39-01 (RED), 39-05 (fix), 39-08 (close) | `attention` joins `danger`/`error` bucket | ✓ SATISFIED | `visit_danger`/`visit_attention` → `error`; gate tests pass |
| ADM-03 | 39-01 (RED), 39-05 (fix), 39-08 (close) | Generic admonition styled + titled; topic styled | ✓ SATISFIED | `visit_admonition` → `notify`, `visit_topic` → `abstract`; title path unconditional |
| ADM-04 | 39-04 (tooling), 39-07 (sign-off), 39-08 (close) | Greyscale distinguishability, human UAT | ✓ SATISFIED | `39-ADM04-SIGNOFF.md` records MET (taken as given per task instructions) |
| ADM-05 | 39-02/39-03 (RED/guard), 39-06 (fix), 39-08 (close) | Rubric inherits container indent; folded D-11/D-13 defects fixed | ✓ SATISFIED | Invariance guard green; D-11/D-13 behavioral tests green |
| ADM-06 | Phase 36 (pre-existing, not this phase's scope) | `rubric` owns its own emission (no `visit_strong` delegation) | ✓ SATISFIED (carried, unaffected) | REQUIREMENTS.md already marks Complete under Phase 36; this phase's plans confirm `visit_rubric` continues to own its pair and only its *save-slot names* changed, not its ADM-06 decoupling |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s Phase 39 traceability rows (ADM-01..ADM-05) all appear in at least one plan's `requirements:` frontmatter (checked via `grep -n "requirements:" *-PLAN.md` across all 8 plans); none are missing a claiming plan.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `tests/test_admonitions.py` | 31-70, 113-130, 325-365 | Six-plus pre-existing unit tests (`test_note_converts_to_info`, `test_warning_converts_to_warning`, `test_tip_converts_to_tip`, `test_caution_converts_to_warning`, `test_hint_converts_to_tip`, `test_error_converts_to_error`) assert only the gentle-clues function name/body wrapper, not the new `, title: "..."` argument every one of these types now carries; several docstrings are factually stale (e.g. "converts to `warning[]`" when real output is `warning({...}, title: "Warning")`) | ⚠️ Warning | Test-coverage gap, not a production defect — confirmed independently by reading the file myself (matches `39-REVIEW.md`'s WR-01 finding exactly). `tests/test_admonition_bucket_render_gate.py::test_admonition_titles_match_locale_catalog` does cover the title text end-to-end today, so the actual emitted output is verified elsewhere; a future regression here would only be caught by that render-gate module, not by this unit file. Does not block phase goal achievement. |

No debt markers (`TBD`/`FIXME`/`XXX`) or unresolved `TODO`/`HACK`/`PLACEHOLDER` found in this phase's changed files (`typsphinx/translator.py`, `scripts/render_admonition_greyscale.py`) — confirmed by direct grep against the phase-start diff.

### Human Verification Required

None. ADM-04 (the phase's only `[V]`-class requirement) already has a recorded, operative human sign-off (`39-ADM04-SIGNOFF.md`) confirming the requirement is MET; per this verification task's explicit instructions, that verdict is taken as given and is not re-opened, re-rendered, or re-judged here.

### Gaps Summary

None. All five ROADMAP success criteria (SC#1-SC#5) and all five requirement IDs assigned to this phase (ADM-01..ADM-05) are verified against the actual codebase — not merely against SUMMARY.md narration:

- The bucket-routing table in `typsphinx/translator.py` was read directly and matches 39-CONTEXT.md's locked table exactly, with zero remaining call sites passing `"danger"` or `"clue"`.
- The rubric's D-11/D-13 fixes were verified both by direct code reading (own `_rubric_was_*` slots, anchor-aware separator guard) and by re-running the actual behavioral tests myself (not trusting the SUMMARY's pass claims) — all green.
- The ADM-05 indentation invariance guard was confirmed to use only relative column comparisons.
- The full test suite (763 passed, 1 skipped, 0 failed) and the full-corpus `-b typstpdf` gate (actually ran, not skipped) were both re-run directly and match the orchestrator's independently measured cross-check exactly.
- One WARNING-level finding (WR-01, a test-coverage gap in `tests/test_admonitions.py`) is carried forward from `39-REVIEW.md` and independently confirmed — real, but does not block the phase goal since the actual emitted behavior is covered elsewhere (the render-gate module).

---

_Verified: 2026-08-02T03:33:10Z_
_Verifier: Claude (gsd-verifier)_
