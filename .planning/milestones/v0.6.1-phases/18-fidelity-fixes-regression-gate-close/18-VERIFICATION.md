---
phase: 18-fidelity-fixes-regression-gate-close
verified: 2026-07-19T14:15:00Z
status: passed
resolved: 2026-07-19T14:25:00Z
score: 11/11 must-haves verified
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Confirm no OTHER corpus table (i.e. not the extdev/deprecated repro anchor) exhibits a NEW silent, non-fatal column collision after the uniform fr-column change (D-02) was applied to every table in the ~689-page Sphinx doc/ corpus."
    expected: "No such silent collision exists anywhere in the corpus, OR any found instance is triaged as a next-milestone backlog item (F1-F15 style), not a Phase 18 regression."
    why_human: "Both 18-01-PLAN.md and 18-02-PLAN.md tag this exact claim `verification: backstop` (non-inferable from the spec alone -- D-02's own text says 'Typst cannot know a table's natural width at translate time, so there is no reliable translate-time is-this-table-too-wide test'). GATE-03's automated corpus gate only asserts fatal-free compilation + empty unknown_visit catalogue -- it does NOT scan extracted PDF text for collision signatures on any table other than the one repro fixture (wide_table_render_gate / extdev's own single-anchor visual check). The 18-02-SUMMARY's confirmatory human check covered only 3 of 689 pages (239, 241, 245 -- the extdev/deprecated anchor). No wired held-out test or full-corpus text-extraction scan exists to rule out a residual silent collision elsewhere. Per the honest-verifier contract (never a silent pass on a backstop-tagged truth without explicit evidence), this abstains to human_needed with reason insufficient_spec rather than being marked VERIFIED or FAILED."
    resolution: "RESOLVED via 18-UAT.md test 1 (2026-07-19). A held-out full-corpus scan was performed against the fresh post-fix build (689 pp., built after the FID-01a fix commit): all pages text-extracted, wide-table pages rendered to PNG and visually inspected. BODY-cell wrapping (the FID-01a target) is correct corpus-wide (extdev/deprecated pp.239/242/245 + the only other wide table, restructuredtext 'Tables' p459). One NEW finding surfaced -- the extdev/deprecated HEADER row's 'Deprecated'/'Removed' labels overflow their narrow fr-sized columns and collide ('DeprecatedRemoved', pp.239/242/245), a regression the fr-column change traded in. Per the expected clause's explicit allowance, the user triaged this to next-milestone backlog (recorded as F16 in 17-AUDIT-CATALOGUE.md), NOT a Phase 18 blocker. Human item satisfied: found-and-triaged is a permitted PASS outcome."
---

# Phase 18: Fidelity Fixes + Regression-Gate Close Verification Report

**Phase Goal:** Fix every high-severity issue in the AUD-01 catalogue — each fix proven by a real `typst.compile()` regression fixture (GATE-01 pattern) that would fail without the fix — then close milestone v0.6.1 by re-running the full-corpus gate to confirm fatal-free non-regression (GATE-02: index.pdf produced, 0 errors) and the elimination of the `todo_node`/`manpage` drops from the `unknown_visit` catalogue.
**Verified:** 2026-07-19
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

All 11 must-haves truths across both plans (18-01: 7, 18-02: 4) were independently re-verified against the live codebase — not taken from SUMMARY.md claims. Evidence column records what THIS verification session directly ran/read, not what the SUMMARY asserted.

| # | Truth (source) | Status | Evidence |
|---|---|---|---|
| 1 | Wide multi-column table with long unbroken inline-literal identifiers wraps in-block; no cross-column merge in extracted PDF text (18-01 SC#1) | VERIFIED | Ran `uv run pytest tests/test_wide_table_render_gate.py -m slow -q` live: 1 passed. |
| 2 | `depart_table` emits `columns: (Nfr, …)` from `colspec['colwidth']`; `visit_colspec` captures `colwidth` before `raise SkipNode` instead of discarding it (18-01 D-01/D-02) | VERIFIED | Read `typsphinx/translator.py` lines 2221-2400 directly: `visit_colspec` (line 2390-2400) appends `node.get("colwidth")` to `self.table_colwidths` before `raise nodes.SkipNode`; `depart_table` calls `self._build_columns_fr_arg()` at both former `columns: {self.table_colcount}` sites (lines 2332, 2336). |
| 3 | In-table `raw()` literal content gets U+200B injected after `.`/`_`, gated on `self.in_table`, applied before `escape_typst_string` | VERIFIED | Read `typsphinx/translator.py` lines 1149-1189: `if self.in_table:` block uses `chr(0x200B)` (confirmed via `python3` byte-search of the file: no literal invisible U+200B byte in source) and runs BEFORE the `escape_typst_string` call. |
| 4 | Missing/all-zero/length-mismatched `colwidth` falls back to equal `1fr` per column — never empty `columns: ()` nor non-positive weight | VERIFIED | Directly invoked `_build_columns_fr_arg()` via `uv run python3` with 5 constructed cases (missing/`None`, all-zero, length-mismatch, negative, valid-ordered): all invalid cases correctly returned `(1fr, 1fr)`; the empty-`columns: ()` case is additionally structurally impossible because the caller only invokes this helper inside `if self.table_colcount > 0:`. |
| 5 | Emitted `columns: (…fr, …)` tuple preserves docutils colspec left-to-right order | VERIFIED | Same direct invocation: `widths=[40,10,10,40]` → `(40fr, 10fr, 10fr, 40fr)`, exact left-to-right order preserved. |
| 6 | New fixture fails RED pre-fix (collision-absence assertion), passes GREEN post-fix, proven by real compile + pypdf extraction | VERIFIED | Independently reproduced RED: checked out `typsphinx/translator.py` at commit `c55bab8` (pre-fix, the Task-1 commit) over the working tree and re-ran the test — it FAILED exactly at the `target_deprecated_collision not in full_text` assertion with the exact `_long_path8.7` collision text visible in the extracted PDF. Restored the fixed file (`git diff --stat` confirmed clean) and re-ran — GREEN. This is a genuine regression proof, not a tautology. |
| 7 | `fr` columns compose with the existing LEN-01 `block(width: …)[#table(…)]` wrapper | VERIFIED | Ran `uv run pytest tests/test_pdf_render_gate.py::TestTableWidthRenderGate -m slow -q` live: 1 passed — this test performs a real `typst.compile()` (no try/except) on the fr-columned table wrapped in `block(width: …)[#table(…)]`, which would abort on an incompatible shape. |
| 8 | Full corpus (`doc/`) still compiles fatal-free through `typstpdf`: non-empty `index.pdf` with valid `%PDF` magic, 0 fatal errors (18-02 SC#2/GATE-03) | VERIFIED | Ran `uv run pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -q -s` live: 1 passed in 13.35s against the real cached Sphinx v9.1.0 corpus (network-available, cache present). |
| 9 | Corpus build produces a non-empty `index.pdf` (empty edge rejected) | VERIFIED | Same live run; `test_corpus_compiles_with_no_fatal_error` asserts `pdf_path.exists()`, `st_size > 0`, and `%PDF` magic bytes (read source at lines 330-339) — these assertions executed and passed in the live run above. |
| 10 | Re-run `unknown_visit` catalogue is empty of `todo_node`/`manpage` (18-02 SC#3) | VERIFIED | Same live run printed `Unknown Visit Catalogue: []` to stdout — confirmed empty. |
| 11 | Zero new runtime deps, no `@preview` bump, 3-way version-sync surface unchanged (SC#4) | VERIFIED | Ran `uv run pytest tests/test_preview_version_sync.py -q` live: 2 passed. Ran `git diff --stat` for the pre-phase-18 baseline (`65566f2`) through `HEAD` restricted to `typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ pyproject.toml`: empty diff. |

**Score:** 11/11 truths verified (0 present-but-behavior-unverified)

### Non-Inferable (Backstop) Items — Abstained

Two must_haves entries (one per plan, functionally the same claim) are tagged `verification: backstop` in the PLAN frontmatter `key_links` — the plans themselves flag this as non-inferable from spec alone (D-02: "Typst cannot know a table's natural width at translate time, so there is no reliable translate-time is-this-table-too-wide test"). Per the honest-verifier contract, a backstop item without explicit confirming evidence must abstain to `human_needed` (reason `insufficient_spec`) rather than being silently passed.

| Item | Explicit evidence found? | Disposition |
|---|---|---|
| "GATE-03's fatal-only corpus re-run does not machine-detect a NEW silent (non-fatal) collision on a corpus table other than the extdev/deprecated repro" (18-01 key_links backstop) | No — GATE-03 only asserts fatal-free + empty unknown_visit; it does not text-extract/scan every table in the 689-page corpus for a collision signature. | ABSTAIN → human_needed / insufficient_spec |
| Same claim, restated as the residual guard (18-02 key_links backstop) — "the confirmatory human visual check on extdev/deprecated is the residual guard" | Partial — 18-02-SUMMARY documents a human visual check, but it covered only 3 of 689 pages (239, 241, 245 — the single repro anchor), not the full corpus. This is not evidence that no OTHER table collides. | ABSTAIN → human_needed / insufficient_spec |

This is not a phase-goal failure — both plans and REQUIREMENTS.md/CONTEXT.md explicitly scope this residual risk as "a future-audit candidate, not a Phase 18 regression" (18-RESEARCH.md Assumption A2). It is called out here per the honest-verifier contract so it is never silently absorbed into a clean "passed" status.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `typsphinx/translator.py` | `self.table_colwidths` accumulator, `_build_columns_fr_arg()`, fr-column emission, in-table ZWSP injection | VERIFIED | All present, read directly at lines 66-95, 1149-1189, 2221-2400; `black --check`, `ruff check`, `mypy` all pass live. |
| `tests/test_wide_table_render_gate.py` | Real-compile GATE-01 acceptance gate for FID-01a | VERIFIED | Exists, collects, RED-then-GREEN reproduced live (see Truth #6). |
| `tests/fixtures/wide_table_render_gate/conf.py` + `index.rst` | Mini Sphinx project + wide list-table with double-backtick literal cells | VERIFIED | Both files read directly; `conf.py` declares `index` in `typst_documents`; `index.rst` uses `` `` `` double-backtick literal cells with the sentinel tokens. |
| `tests/test_table_in_list_item_render_gate.py` | Updated `columns: 2,` → `columns: (50fr, 50fr),` assertion | VERIFIED | `grep -n "columns:"` confirms only the updated assertion at line 174; no stale `columns: 2` occurrence anywhere in the file; live test run passes. |
| `.planning/phases/18-fidelity-fixes-regression-gate-close/18-02-SUMMARY.md` | Records GATE-03 outcome + SC#4 confirmation | VERIFIED | Exists, records the corpus-gate result — independently re-confirmed live rather than trusted. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `visit_colspec` colwidth capture | `depart_table` fr-columns emission | `self.table_colwidths` accumulator | WIRED | Confirmed by direct source read: init in `__init__`/`visit_table`, appended in `visit_colspec`, consumed+reset in `depart_table`. |
| `visit_literal` ZWSP injection | wrappable in-table literal content | `self.in_table` gate | WIRED | Confirmed by direct source read; also confirmed the RED-fixture required BOTH halves (fr-columns alone reproduced RED — this is the exact "Critical Finding" the plans document). |
| 18-01 fr-column + ZWSP fix | `test_corpus_gate.py::test_corpus_compiles_with_no_fatal_error` | Full-corpus real re-run (D-04) | WIRED | Live run confirmed the gate passes post-fix with the uniform fr-column change applied to every corpus table. |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| FID-01 | 18-01 | Every AUD-01 high-severity issue fixed w/ real-compile regression fixture | SATISFIED | FID-01a (the sole high-severity item) fixed and proven per Truths 1-7 above. REQUIREMENTS.md marks `[x]` (checkbox-only diff, no scope edits — confirmed via `git diff`). |
| FID-01a | 18-01 | Wide-table rendering fix | SATISFIED | Same as above. |
| GATE-03 | 18-02 | Corpus fatal-free + unknown_visit clear of todo_node/manpage | SATISFIED | Truths 8-10 above, live-confirmed. REQUIREMENTS.md marks `[x]`. |

No orphaned requirements — `grep -E "Phase 18" .planning/REQUIREMENTS.md` shows exactly FID-01 and GATE-03, both declared in plan frontmatter `requirements:` fields and both accounted for above. The Out-of-Scope table and Future Requirements section are byte-unchanged (only checkbox `[ ]`→`[x]` and Traceability status column edited — confirmed via `git diff 65566f2 HEAD -- .planning/REQUIREMENTS.md`).

### Anti-Patterns Found

None. Grepped `typsphinx/translator.py`, `tests/test_wide_table_render_gate.py`, `tests/fixtures/wide_table_render_gate/*`, and `tests/test_table_in_list_item_render_gate.py` for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER|placeholder|not yet implemented|coming soon` — the only matches are pre-existing, unrelated code (the `visit_todo_node`/`_visit_graphical_placeholder` handlers from Phase 16, not touched by Phase 18).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Wide-table collision-absence fixture | `uv run pytest tests/test_wide_table_render_gate.py -m slow -q` | 1 passed | PASS |
| RED-before-fix reproduction | translator.py reverted to pre-fix commit `c55bab8`, same test re-run | 1 failed at the intended collision-absence assertion (`_long_path8.7` found in extracted text) | PASS (confirms genuine regression proof) |
| `test_table_conversion` (fr-column unit shape) | `uv run pytest -m "not slow" -q` (full fast suite) | 477 passed, 23 deselected | PASS |
| `_build_columns_fr_arg` fallback/order logic | direct `uv run python3` invocation with 5 constructed cases | all correct (`(1fr, 1fr)` fallback ×4, `(40fr, 10fr, 10fr, 40fr)` ordered) | PASS |
| LEN-01/fr composition | `uv run pytest tests/test_pdf_render_gate.py::TestTableWidthRenderGate -m slow -q` | 1 passed (real `typst.compile()`, no try/except) | PASS |
| Corpus GATE-03 | `uv run pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -q -s` | 1 passed in 13.35s, `Unknown Visit Catalogue: []` | PASS |
| SC#4 invariant | `uv run pytest tests/test_preview_version_sync.py -q` | 2 passed | PASS |
| Lint/format/type parity | `black --check`, `ruff check`, `mypy typsphinx/` | all clean | PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` probes declared or referenced by this phase's PLAN/SUMMARY files. Step 7c: SKIPPED (no probe-based verification declared for this phase — the render-gate/corpus-gate pytest fixtures above are the phase's actual acceptance mechanism, not shell probes).

### Human Verification Required

1. **Confirm no residual silent column-collision exists on any corpus table other than the `extdev/deprecated` repro anchor**
   **Test:** Spot-check a sample of other wide tables across the ~689-page corpus build (or write a held-out full-corpus text-extraction scan) for the audit's cross-column glyph-collision signature, now that fr-columns + ZWSP apply uniformly to every table (D-02).
   **Expected:** No new silent collision found — or if found, triage it as a next-milestone backlog item (matching the F1-F15 medium/low pattern), not a Phase 18 blocker.
   **Why human:** Both plans explicitly tag this claim `verification: backstop` (non-inferable from the spec — D-02 itself states there is no reliable translate-time "is this table too wide" test). GATE-03's automated gate only proves fatal-free compilation + empty `unknown_visit`; it does not scan for this collision signature outside the one fixture. The 18-02 confirmatory check covered only 3 of 689 pages. Per the honest-verifier contract, this cannot be marked VERIFIED without a wired held-out test or a full-corpus scan, and it is not a code defect either — so it abstains rather than being silently passed or falsely failed.

### Gaps Summary

No gaps. All 11 concrete, inferable must-haves truths across both plans are independently VERIFIED against the live codebase (not SUMMARY claims) — the two-half FID-01a fix (fr-columns + ZWSP) is genuinely present, correctly wired, and proven by a real RED→GREEN regression fixture I personally reproduced by reverting and re-applying the translator.py fix. GATE-03's corpus close is independently re-confirmed live (not just re-stated from the prior session's SUMMARY): the full ~689-page corpus compiles fatal-free, `unknown_visit` is empty, and SC#4's zero-new-deps/no-`@preview`-bump invariant holds. The only open item is a documented, plan-acknowledged residual risk (a possible NEW silent, non-fatal collision on some OTHER corpus table) that neither the automated gate nor the prior session's targeted human check rules out — this is routed to human verification per the honest-verifier contract rather than silently passed.

---

*Verified: 2026-07-19*
*Verifier: Claude (gsd-verifier)*

## Acknowledged Gate Overrides

- **Gate:** `api-coverage.verify-pre` (verify:pre, blocking)
- **Result:** `block: true` — false positive.
- **Cause:** The detector matched `verb: wraps / noun: apis` in prose from `18-02-SUMMARY.md` describing the "Deprecated **APIs**" grid table whose cell text **wraps** within its column. This is a Typst wide-table rendering fix, not external-API integration; no COVERAGE.md is applicable.
- **Decision (2026-07-19):** User acknowledged the false positive and elected to proceed with UAT. No COVERAGE.md required for this phase.
