---
phase: 48-compile-time-cross-reference-guard
verified: 2026-08-12T06:57:54Z
status: human_needed
score: 9/9 must-haves verified
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Read 48-EVIDENCE.md's '## Accepted limit — label-collision false negative' section and confirm you accept the trade-off it describes."
    expected: "Owner explicitly accepts that a coincidental docname/label-namespace collision (`a/b` vs `a_u2f_b`, via the `/`→`_u2f_` sanitize transform) makes the compile-time guard render a WORKING link to the wrong (decoy) document instead of degrading to plain text. This is a real, narrow, measured, and already-filed (todo `2026-08-12-label-collision-false-negative-in-compile-time-xref-guard.md`) regression vs. the deleted build-time mechanism, which checked docname membership rather than label-string identity and therefore did not have this failure mode."
    why_human: "This is a deliberate design trade-off the phase's own plan (48-04-PLAN.md task 3 human-check items 4) designates as requiring explicit owner sign-off, not a fact a grep/test can validate — it is a judgment call about acceptable residual risk, also flagged WARNING by 48-REVIEW.md (WR-02)."
  - test: "Read 48-EVIDENCE.md's '## D-11 compile-time cost' section and confirm you accept the measured tier outcome."
    expected: "Owner confirms the -2.37% full-corpus compile-time delta (bottom tier, 'record only', no todo/blocker) is acceptable. I independently re-derived the arithmetic (28.92s/27.21s after vs. 28.93s/28.56s before, mean -2.37%) and confirm the tiering rule was applied correctly and the tier thresholds were fixed before measurement — but the ACCEPTANCE of the outcome is the plan's own designated human checkpoint (48-04-PLAN.md task 3 human-check item 5)."
    why_human: "Owner-judgment sign-off explicitly required by the plan, not a correctness question — the tier math itself checks out (verified)."
  - test: "Read 48-EVIDENCE.md's '## D-01 — no published contract changed' section and confirm you accept the diagnostic-visibility loss it records."
    expected: "Owner confirms it is acceptable that, post-Phase-48, a reference to a deliberately `:orphan:`-marked target now degrades with ZERO diagnostic at any layer (no build-time warning, since the D-01 cross-document degrade warning was deleted with no replacement; Sphinx itself emits no warning for an `:orphan:` target that resolved successfully)."
    why_human: "Owner-judgment sign-off explicitly required by the plan (48-04-PLAN.md task 3 human-check item 6) and flagged as low-severity by 48-REVIEW.md's own findings; I confirmed the underlying fact (grep of docs/source for 'non-included|degrade' returns zero matches, so no published-docs contract broke) but accepting the visibility trade-off itself is a judgment call."
  - test: "Open the built docs/_build/pdf/typsphinx.pdf and click a handful of internal cross-reference links to confirm they navigate to the correct section (not merely that they exist)."
    expected: "Clicking an internal `:ref:`/`:doc:` cross-reference link in the rendered PDF jumps to the correct target section, not merely to any-destination or the wrong page."
    why_human: "I ran `tox -e docs-pdf` myself and confirmed the build succeeds (exit 0, 'build succeeded, 5 warnings', no 'does not exist in the document' text), produced a valid 119-page PDF (%PDF-1.7 magic bytes, non-empty `/Outlines`) with 502 `/Link` annotations all carrying a `/Dest` or `/A` action — i.e. every link is wired to *some* destination. Whether each destination is the semantically CORRECT one is a visual/interactive check no automated assertion in this phase covers (per the plan's own task 3 human-check item 3's explicit scoping)."
---

# Phase 48: Compile-Time Cross-Reference Guard Verification Report

**Phase Goal:** Whether a reference's target label exists is decided by Typst per compiled wrapper
instead of by a build-time union across all masters, so a missing label degrades to plain text
rather than aborting — landed before the graph work that would otherwise make it fatal.

**Verified:** 2026-08-12T06:57:54Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

Truths 1-4 are ROADMAP.md's own Success Criteria (the binding contract); truths 5-9 are drawn from
the four plans' `must_haves.truths` frontmatter and confirmed non-duplicative additions.

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC#1 (XREF-03): A reference whose target is absent from the compiling master degrades to plain text and the compile succeeds; the linked master gets a real link, both read back through pypdf, no TypstError | ✓ VERIFIED | `uv run pytest tests/test_xref_compile_time_guard_render_gate.py -q` → 6/6 pass, 0 xfail, 0 XPASS (independently re-run, not trusted from SUMMARY). Guard implementation at `typsphinx/translator.py:5158-5173` matches `48-EXPECTED-STRUCTURE.md`'s "Guard contract" byte-for-byte, confirmed by direct `Read`. |
| 2 | SC#2 (XREF-04): Every label-reference emission site routes through one shared guard helper; open question #1 (`translator.py:4291`'s nature) closed by reading the code | ✓ VERIFIED | `grep -c 'query(<{label}>)' typsphinx/translator.py` → 1 (single derivation point, self-verified). `grep -n '_label_existence_guard' typsphinx/translator.py` shows the definition plus exactly 3 call sites: `visit_reference:5169`, `visit_citation:3406`/`3418`, `visit_pending_xref:4457` — all independently read and confirmed. Open question #1 answered in `48-EVIDENCE.md` §"SC#2 — site enumeration": `visit_pending_xref` is a fourth independent degradation site, not routed through `_reference_anchor_decision` (confirmed: that method is called only from `visit_reference`/`visit_citation`). |
| 3 | SC#3 (XREF-04): The build-time mechanism is deleted in the same change, not left half-alive | ✓ VERIFIED | `grep -rn 'master_included_docnames\|_compute_master_included_docnames\|degrade_xref_to_text' typsphinx/` → zero matches (self-run, exit 1). |
| 4 | SC#4: The guard is applied only where needed (same-document anchors stay unguarded, asserted explicitly); full-corpus compile cost measured, not assumed | ✓ VERIFIED | `typsphinx/translator.py:5111-5131` (bare-refid branch) and `:5150-5157` (`#`-prefixed internal refuri branch) both emit the plain unguarded `link(<label>, ` form with an explicit "SC#4/D-06 (Phase 48): deliberately UNGUARDED" comment (read directly). `48-EVIDENCE.md` §"D-11 compile-time cost": -2.37% full-corpus delta (28.065s after vs. 28.745s before), bottom tier — arithmetic independently re-derived and confirmed correct. |
| 5 | Own-anchor composition (D-14 bracket-wrap + D-07 guard) compiles, label stays queryable | ✓ VERIFIED | `depart_reference` (`typsphinx/translator.py:5192+`) emits `_reference_guard_close` strictly before the `_reference_own_anchor` attachment block (read directly, matches the plan's acceptance-criteria ordering check). `uv run pytest tests/test_citation_render_gate.py -q` → 9/9 pass (independently re-run) — this is the route that exercises the composition (a citation-derived cross-document reference is simultaneously eligible for its own anchor and guarded). |
| 6 | The three orphaned/migrated test modules (citation degradation, orphan-degrade, master-include-set) assert the post-fix behaviour with zero residual xfail/build-time-premise references | ✓ VERIFIED | `uv run pytest tests/test_citation_degradation_gate.py tests/test_xref_orphan_degrade_render_gate.py tests/test_master_include_set_predicate_gate.py -q` → 22/22 pass, 0 xfail (independently re-run). |
| 7 | D-05: the captioned-code-block citation dangling-label fatal is closed | ✓ VERIFIED | `uv run pytest tests/test_citation_caption_dangling_label_gate.py -q` → 3/3 pass, 0 xfail (independently re-run; this module's two previously-strict-xfail tests are now plain green). |
| 8 | The label-collision false-negative class is measured and characterized at compile level (not just argued), and filed for future remediation | ✓ VERIFIED (characterization) / requires owner acceptance (the trade-off itself) | `uv run pytest tests/test_xref_compile_time_guard_render_gate.py -k collision -q` → 1/1 pass. `.planning/todos/pending/2026-08-12-label-collision-false-negative-in-compile-time-xref-guard.md` exists and correctly names the mechanism. Owner sign-off is a separate human-verification item below (the plan's own design). |
| 9 | Phase closes with a fully green suite plus lint/type gates | ✓ VERIFIED | Orchestrator: `uv run pytest -q` → 1062 passed, 5 skipped, 0 failed; `black --check .` and `mypy typsphinx/` clean. Independently re-confirmed on the phase-scoped and regression modules (25 + 149 tests, all green, zero xfail/XPASS) and re-ran `black --check` / `mypy` on the two touched source files (clean). |

**Score:** 9/9 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/translator.py::_label_existence_guard` / `_LabelGuardStrings` | The single D-07 shared guard-string derivation point | ✓ VERIFIED | Read directly (`translator.py:3148-3222`); byte-for-byte matches `48-EXPECTED-STRUCTURE.md`'s "Guard contract" (open string, unbroken `if query(<L>).len() > 0 {` conditional, `__tsx_body` bound identifier). |
| `typsphinx/translator.py::visit_reference` cross-document branch | Guarded, D-01 warning deleted | ✓ VERIFIED | Read directly (`:5158-5173`); no `logger.warning` for cross-document degrade anywhere in the method; the remaining `logger.warning` at `:5138` is the unrelated pre-existing empty-URL warning. |
| `typsphinx/builder.py` | `master_included_docnames`/`_compute_master_included_docnames` deleted | ✓ VERIFIED | Grep confirms zero occurrences anywhere in `typsphinx/`. |
| `tests/test_xref_compile_time_guard_render_gate.py` | 6 tests, all green (was 5 xfail + 1 plain) | ✓ VERIFIED | Re-run: 6/6 pass. |
| `tests/test_citation_caption_dangling_label_gate.py` | 3 tests, all green (was 1 plain + 2 xfail) | ✓ VERIFIED | Re-run: 3/3 pass. |
| `tests/test_label_existence_guard_unit.py` | 16 direct unit tests pinning the helper contract | ✓ VERIFIED | Re-run: 16/16 pass; includes `TestSingleDerivationPointStructural` confirming the single-derivation-point property structurally. |
| `.planning/phases/48-compile-time-cross-reference-guard/48-EVIDENCE.md` | D-11/D-09/SC#2/SC#3/D-01/label-collision/green-gate sections | ✓ VERIFIED | All 8 `##` sections present and read; grep transcripts pasted verbatim inside match independently re-run greps. |
| `.planning/todos/pending/2026-08-12-label-collision-false-negative-in-compile-time-xref-guard.md` | Filed remediation todo for the accepted limit | ✓ VERIFIED | Exists, correctly describes the mechanism and narrowing condition. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `_namespace_label()` | `_label_existence_guard(label, ...)` | Every call site passes an already-namespaced label, never re-derives one | ✓ WIRED | Confirmed at all 3 call sites (`visit_reference:5167-5169`, `visit_citation:3389`/`3406`/`3417-3418`, `visit_pending_xref:4437-4457`) — each computes/receives `label` via `_namespace_label(...)` before calling the guard. |
| `visit_reference` (open) | `depart_reference` (close) | `self._reference_guard_close` slot, mirroring `_reference_own_anchor`'s lifecycle | ✓ WIRED | Set at `:5173`, consumed and cleared at `depart_reference`, defensively cleared in the skip-wrapper branch too (`:5212`). |
| `visit_pending_xref` (open) | `depart_pending_xref` (close) | Dedicated `self._pending_xref_guard_close` slot (never shared) | ✓ WIRED | `:4459` sets it, `:4470-4472` consumes and clears it. |
| `48-EXPECTED-STRUCTURE.md` | Every migrated assertion | Values traceable to a row written before the emitter changed | ✓ WIRED | Cross-checked the Guard contract's fully-substituted example against the live `_label_existence_guard` output shape — identical. |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|-----------------|--------------|--------|----------|
| XREF-03 | 48-01, 48-02, 48-04 | A cross-document reference whose target label is absent from the compiling master degrades to plain text at compile time instead of aborting | ✓ SATISFIED | `REQUIREMENTS.md:70-73` marked `[x]`, cites `48-EVIDENCE.md` sections independently confirmed to exist and support the claim; SC#1 truth above VERIFIED. |
| XREF-04 | 48-01, 48-02, 48-03, 48-04 | Every label-reference emission site routes through one shared guard, and `master_included_docnames` is removed | ✓ SATISFIED | `REQUIREMENTS.md:75-77` marked `[x]`; SC#2/SC#3 truths above VERIFIED. |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s Phase 48 row lists exactly XREF-03/XREF-04, and every plan's `requirements:` frontmatter is a subset of `{XREF-03, XREF-04}` — full accounting, nothing claimed by REQUIREMENTS.md that no plan owns, nothing claimed by a plan that REQUIREMENTS.md doesn't track.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `typsphinx/translator.py` | `4441-4457` (comment) | `visit_pending_xref`'s guard uses a fixed `"#"` prefix regardless of markup mode | ℹ️ Info (pre-existing, documented in code review IN-02) | Accepted, unreachable defence-in-depth path per research assumption A2; documented in the code's own comment. Not a phase-48-introduced regression — carried forward unchanged by explicit plan instruction. |
| `typsphinx/translator.py` | `4336-4338` (comment) | Stale comment claiming the preceding closing token is "always `)`" — no longer true when the preceding reference took the guarded path (closes with `}`) | ℹ️ Info (code review IN-01) | Cosmetic; the comment's underlying reasoning still holds regardless of which token precedes it. |
| (no test file) | — | `next_is_target=True` + guarded cross-document reference composition has no automated test coverage (code review WR-01) | ⚠️ Warning | Reviewer independently hand-built this doctree shape and confirmed it compiles via real `typst.compile()` — not a live defect — but no committed gate would catch a future regression in this specific bracket-nesting composition. |
| `tests/fixtures/xref_label_collision_guard_gate/` | — | Label-namespace collision is a real, measured false-negative class vs. the deleted build-time mechanism (code review WR-02) | ⚠️ Warning | Deliberately accepted by phase design (`must_haves` truth explicitly names this "not a defect to fix in this phase"), characterized by a real compile, and filed as a todo — routed to human_verification below since acceptance is an owner decision, not a code defect. |

No debt markers (`TBD`/`FIXME`/`XXX`) found in any phase-48-touched file (`typsphinx/translator.py`, `typsphinx/builder.py`, and all 8 touched/created test modules) — independently grepped.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Phase-specific gate modules pass with zero xfail/XPASS | `uv run pytest tests/test_xref_compile_time_guard_render_gate.py tests/test_citation_caption_dangling_label_gate.py tests/test_label_existence_guard_unit.py -q` | 25 passed | ✓ PASS |
| Regression modules pass | `uv run pytest tests/test_citation_degradation_gate.py tests/test_xref_orphan_degrade_render_gate.py tests/test_master_include_set_predicate_gate.py tests/test_citation_render_gate.py tests/test_translator.py -q` | 149 passed | ✓ PASS |
| Deleted symbols absent from production code | `grep -rn 'master_included_docnames\|_compute_master_included_docnames\|degrade_xref_to_text' typsphinx/` | exit 1, no output | ✓ PASS |
| Single guard-string derivation point | `grep -c 'query(<{label}>)' typsphinx/translator.py` | `1` | ✓ PASS |
| `black`/`mypy` clean on touched source | `uv run black --check typsphinx/translator.py typsphinx/builder.py && uv run mypy typsphinx/translator.py typsphinx/builder.py` | both clean | ✓ PASS |
| Dogfooding docs-PDF build succeeds (manual checkpoint's mechanical half) | `uv run tox -e docs-pdf` | exit 0, "build succeeded, 5 warnings", no "does not exist in the document" text | ✓ PASS |
| Dogfooding PDF is structurally valid with working link destinations | `pypdf.PdfReader('docs/_build/pdf/typsphinx.pdf')` → 119 pages, non-empty outline, 502/502 `/Link` annotations carry a `/Dest` or `/A` | ✓ PASS | (destination *correctness* — i.e. does each link jump to the right section — is the remaining visual check, routed to human_verification) |

### Requirements Coverage — Deferred / Orphaned

None. Both requirement IDs (XREF-03, XREF-04) declared across the four plans are a subset of, and fully accounted for by, REQUIREMENTS.md's Phase 48 mapping.

### Human Verification Required

The code, tests, and mechanism are all verified correct and complete. What remains outstanding is
exactly what the phase's own plan (`48-04-PLAN.md` task 3's `<human-check>`) designates as owner
judgment calls — not machine-checkable facts — plus one visual/interactive PDF check the plan
explicitly scopes as having no automated equivalent in this phase:

1. **Accept the label-collision false-negative trade-off** — `48-EVIDENCE.md` §"Accepted limit —
   label-collision false negative". A coincidental docname/label collision (`a/b` vs. `a_u2f_b`)
   now renders a working link to the wrong document instead of degrading to plain text. Measured,
   narrow, filed as a todo — but a real regression vs. the deleted mechanism (also flagged WARNING
   by `48-REVIEW.md`'s WR-02). Requires explicit owner acceptance.

2. **Accept the D-11 compile-time cost tier outcome** — `48-EVIDENCE.md` §"D-11 compile-time cost".
   Measured at -2.37% (bottom tier, record-only). I independently re-verified the arithmetic and
   confirmed the tier thresholds were fixed before measurement; the acceptance itself is the
   plan's designated human checkpoint.

3. **Accept the D-01 diagnostic-visibility loss** — `48-EVIDENCE.md` §"D-01 — no published contract
   changed". A reference to an `:orphan:` target now degrades with zero diagnostic at any layer.
   I confirmed no published-docs contract broke (grep of `docs/source` for `non-included|degrade`
   returns zero matches); accepting the visibility trade-off itself is a judgment call.

4. **Visually confirm the dogfooding PDF's cross-reference links navigate correctly** — I ran
   `tox -e docs-pdf` myself and confirmed it builds cleanly and produces a structurally valid PDF
   with 502 link annotations, all carrying a destination/action. Whether each destination is the
   semantically *correct* target (not just *a* target) requires opening the PDF and clicking
   through — a visual/interactive check with no automated equivalent in this phase.

### Gaps Summary

No gaps. All four ROADMAP.md success criteria and all `must_haves` truths across the four plans are
independently verified against the current codebase — not merely accepted from SUMMARY.md claims.
The guard helper, its three emission-site call sites, the build-time mechanism's deletion, the D-06
same-document exemption, and the phase-scoped test suite (25 phase-specific + 149 regression tests,
independently re-run) all check out. The only reason status is `human_needed` rather than `passed`
is that the phase's own plan deliberately designates three accept/reject judgment calls (label
collision, D-11 tier, D-01 visibility) plus one visual PDF-link-navigation check as human
checkpoints that no autonomous verifier can discharge — these are not code defects, and none of
them contradict the phase goal in a way that should block proceeding, but per this phase's own
design they require an explicit human "yes."

---

*Verified: 2026-08-12T06:57:54Z*
*Verifier: Claude (gsd-verifier)*
