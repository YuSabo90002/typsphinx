---
phase: 34-inline-math-after-text-separator-fix
verified: 2026-07-28T23:40:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 34: Inline Math After Text Separator Fix Verification Report

**Phase Goal:** A user can write a paragraph that mixes prose and inline math — including with no
whitespace between them — and `sphinx-build -b typstpdf` produces a PDF with both the prose and the
math intact, instead of aborting the Typst compile.

**Verified:** 2026-07-28
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP SC#1-SC#5)

All five truths were re-derived from first principles and checked against the live codebase — not
taken from SUMMARY.md or GATE-EVIDENCE.md claims. Where evidence files made an empirical claim
(RED, GREEN, corpus-gate pass, PDF page facts), I independently reproduced it in this session.

| # | Truth (ROADMAP SC) | Status | Evidence |
|---|------|--------|----------|
| 1 | Prose-then-inline-math (incl. no-space form) builds through `-b typstpdf` to a valid PDF | ✓ VERIFIED | Rebuilt the fixture myself (`uv run python -m sphinx -b typstpdf tests/fixtures/inline_math_after_text_render_gate <scratch>`): exit 0, `index.pdf` produced, `%PDF` magic bytes. `uv run pytest tests/test_inline_math_after_text_render_gate.py -q` → 2 passed (re-run independently). |
| 2 | Compiles on BOTH mitex default and native (`-D typst_use_mitex=0`) paths | ✓ VERIFIED | Both `test_typstpdf_separates_inline_math_mitex_path` and `test_typstpdf_separates_inline_math_native_path` pass in this session; native build re-run directly confirms `$E = m c^2$` present and `mi(` absent (override actually reached the translator). |
| 3 | Compiled PDF's extracted text contains prose + math adjacent, no dropped words, no swallowed math, no leaked Typst source | ✓ VERIFIED | I rebuilt the fixture and visually rendered page 3 of the resulting PDF myself (not relying on the executor's self-reported "Approved"): Construct B ("Text before math *E=mc²* text after.") renders as one continuous line, Construct E's display equation is centred between its two prose paragraphs, Construct C's confval field body reads as one continuous sentence — no leaked `mi(`/`text(` tokens visible anywhere on the page. The gate's own NFKC-normalized `pypdf` text-extraction assertions (sentinels present, `LEAK_SIGNATURES` absent) also pass. |
| 4 | Fix pinned by a real `typst.compile()` GATE-01 fixture with a **recorded fail-pre-fix run** | ✓ VERIFIED | I did not trust `34-GATE-EVIDENCE.md`'s RED section as given — I restored `typsphinx/translator.py` to its pre-fix state (`git show 568121f:typsphinx/translator.py`) in the live working tree, re-ran the gate, and got the identical 2-failure RED result with the identical verbatim `TypstError: expected semicolon or line break`. I then restored the fixed file, confirmed `md5sum` matched the original and `git status --porcelain` was clean, and re-ran the gate to confirm GREEN (2 passed) again. `git diff --stat 568121f..HEAD -- typsphinx/translator.py` shows 45 insertions, 0 deletions. |
| 5 | Nothing else regresses: display math, math in lists/tables/captions, the three math modules, the full pytest suite, and the full-corpus gate all stay green | ✓ VERIFIED | Independently re-ran `uv run python -m pytest -q --tb=no -rf` → `649 passed, 1 skipped` (matches orchestrator-measured state and GATE-EVIDENCE.md exactly). `uv run black --check .` / `uv run ruff check .` / `uv run mypy typsphinx/` all exit 0. `uv run pytest tests/test_corpus_gate.py -q -m slow` → `1 passed, 1 skipped, 3 deselected` (the cached real Sphinx v9.1.0 corpus build, fatal-free — matches GATE-EVIDENCE.md exactly). `uv run pytest tests/test_math_mitex.py tests/test_math_native.py tests/test_math_fallback.py -q` → 23 passed, and `git diff` confirms none of those three files were edited by the phase. `uv run pytest tests/test_preview_version_sync.py -q` → 3 passed (no `@preview` version drift). |

**Score:** 5/5 truths verified (0 present-but-behavior-unverified).

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tests/fixtures/inline_math_after_text_render_gate/conf.py` | GATE-01 fixture config, `index` as master doc | ✓ VERIFIED | Exists, contains `typst_documents`, no `typst_use_mitex` override (native path reached via CLI `-D`) |
| `tests/fixtures/inline_math_after_text_render_gate/index.rst` | 6 labelled constructs A-F | ✓ VERIFIED | Read in full — all six constructs present, prose sentinels ASCII, no-space backslash-escaped form present |
| `tests/test_inline_math_after_text_render_gate.py` | Gate module, both emission paths, exact-string assertions | ✓ VERIFIED | Read in full (345 lines) — `sys.executable -m sphinx`, both `-D typst_use_mitex=0` and default paths, NFKC normalization, `LEAK_SIGNATURES` guard, exactly one `skipif` |
| `typsphinx/translator.py` (`visit_math`, `visit_math_block`) | 3-protocol / list-item-only separator participation | ✓ VERIFIED | Read the live source: exactly one `_emit_inline_concat_separator()` and one `_mark_inline_concat_content()` call in `visit_math`; `visit_math_block` has the list-item-only half placed after `_emit_id_anchors`. Payload construction (`mi(...)`/`$...$`/`mitex(...)`), label-anchor emission, and the mitex/native branch are byte-unchanged (diff is insertions-only). |
| `.planning/phases/34-inline-math-after-text-separator-fix/34-GATE-EVIDENCE.md` | SHA-anchored RED→GREEN record + regression sweep | ✓ VERIFIED | Read in full; every quantitative claim in it (RED failure text, GREEN pass counts, full-suite counts, corpus-gate outcome, docs-PDF page count) was independently reproduced or spot-checked in this session and matched exactly |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `visit_math` | `_emit_inline_concat_separator()` / `_mark_inline_concat_content()` | shared concat-context helper, single source of truth | ✓ WIRED | Confirmed by direct source read; no new helper introduced (prohibition honored) |
| `visit_math` | `self.in_list_item` / `self.list_item_needs_separator` | shared list-item newline protocol | ✓ WIRED | Confirmed by direct source read, identical guard shape to `visit_literal` |
| `visit_math_block` | `self.in_list_item` / `self.list_item_needs_separator` only | placed after `_emit_id_anchors`, before the mitex/native branch | ✓ WIRED | Confirmed: zero `_emit_inline_concat_separator`/`_mark_inline_concat_content` references in `visit_math_block`, matching the D-01 scope decision that block math is never a concat-context sibling |
| fixture project | `TypstPDFBuilder.finish()` | `conf.py`'s `typst_documents` lists `index` as master doc | ✓ WIRED | Confirmed: the fatal is only observable via `-b typstpdf`; my RED-restoration experiment reproduced the abort inside `TypstPDFBuilder.finish()` exactly as claimed |

### Behavioral Spot-Checks / Real-Compile Gate Execution

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Gate RED against pre-fix translator | restored `568121f` translator, ran `uv run pytest tests/test_inline_math_after_text_render_gate.py -q --tb=line` | 2 failed, verbatim `TypstError: expected semicolon or line break` | ✓ PASS (RED reproduced) |
| Gate GREEN against fixed translator (restored) | `uv run pytest tests/test_inline_math_after_text_render_gate.py -q` | 2 passed | ✓ PASS |
| Working tree integrity after RED experiment | `md5sum typsphinx/translator.py` (before/after) + `git status --porcelain` | identical hash, clean tree | ✓ PASS |
| Full suite | `uv run python -m pytest -q --tb=no -rf` | 649 passed, 1 skipped | ✓ PASS |
| Lint/format/type | `black --check .`, `ruff check .`, `mypy typsphinx/` | all exit 0 | ✓ PASS |
| Full-corpus gate | `uv run pytest tests/test_corpus_gate.py -q -m slow` | 1 passed, 1 skipped, 3 deselected | ✓ PASS |
| `@preview` version sync | `uv run pytest tests/test_preview_version_sync.py -q` | 3 passed | ✓ PASS |
| Visual PDF render (SC#3 human-check) | Rebuilt fixture, viewed `index.pdf` page 3 directly via Read tool | Constructs A-F render as continuous, non-overlapping, non-split prose+math with no leaked Typst source | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|--------------|------------|--------------|--------|----------|
| MATH-01 | 34-01, 34-02, 34-03 | Inline math after text no longer aborts `typstpdf` compile, on both emission paths, pinned by a real fail-pre-fix gate | ✓ SATISFIED | All 5 ROADMAP success criteria independently verified above |

No orphaned requirements: REQUIREMENTS.md maps only MATH-01 to Phase 34, and all three plans declare `requirements: [MATH-01]`.

**Advisory (non-blocking) observation:** `.planning/REQUIREMENTS.md` still shows MATH-01's checkbox
unchecked and its Traceability row as "Pending" — this is a stale bookkeeping artifact (the
checkbox/traceability flip is normally done at ship/complete-milestone time, not by
execute-phase), not evidence the fix is missing. The codebase evidence above stands on its own.

### Anti-Patterns Found

None introduced by this phase's diff. `git diff 568121f..HEAD -- typsphinx/translator.py` contains
no `TODO`/`FIXME`/`XXX`/`HACK`/`PLACEHOLDER` markers, no empty-body stubs, and is insertions-only
(0 deletions) — confirmed by direct diff inspection, not by SUMMARY claim.

### Code Review Findings (34-REVIEW.md) — Weighed, Not Just Echoed

The phase's own code review found 0 critical, 4 warnings. I independently re-checked the two most
consequential ones since `known_context` asked me to weigh, not restate, them:

- **WR-03 (Construct F has no dedicated exact-string assertion):** Confirmed by `grep` — the string
  `"a+b"` never appears in `tests/test_inline_math_after_text_render_gate.py`. Construct F does
  compile (it's covered by the blanket `returncode == 0` assertion and the generic juxtaposition/
  stray-operator guards), but no assertion pins its *exact* separator-free shape the way constructs
  B/C/D/E get. This is a real coverage gap for the "single-element edge" must-have truth from
  34-01-PLAN.md, but the truth itself ("compiles and emits its `mi(...)` call") is still satisfied —
  just less tightly pinned than the other constructs. WARNING, not a BLOCKER: it does not affect
  SC#1-SC#5.
- **WR-04 (native path has no Construct-E assertion):** Confirmed by reading the test file —
  `test_typstpdf_separates_inline_math_native_path` asserts only B and D, not E. `visit_math_block`'s
  native branch is exercised by the build succeeding and the generic `)$` juxtaposition guard, but
  not by an exact-string check. WARNING, not a BLOCKER.
- **WR-01 (redundant blank line from `visit_math_block`'s list-item bookkeeping):** Confirmed as
  cosmetic — Typst code-mode whitespace between statements has no compiled/visual effect, and the
  visual PDF render I performed independently shows no extraneous visible gap on the page. Not a
  functional regression.
- **WR-02 (labeled equation + list item ordering has no committed regression test):** The reviewer's
  own ad hoc verification (not committed) confirmed correctness; no committed test locks this in. A
  legitimate but non-blocking gap — the `_emit_id_anchors`-then-list-item-guard ordering is subtle
  and worth a follow-up test, but it is not part of any ROADMAP SC and the current code is correct
  per both the reviewer's and my own reading of the source.

None of these four warnings rise to a level that fails any ROADMAP success criterion. They are
legitimate scope for a lightweight follow-up (e.g. a backlog todo), not phase-blocking gaps.

### Deviation Judgment (E=mc^2 → E = m c^2, per `known_context`)

The Plan 02 deviation (correcting the fixture's math content because native Typst parses adjacent
letters `mc` as a single unknown identifier) does **not** weaken SC#4's gate. The separator
assertions test the character(s) *between* a preceding sibling and the `mi(...)`/`$...$` call — they
never depended on the internal spacing of the math body itself. I confirmed this directly: the
no-intervening-space source form (`No space where\ :math:`E = m c^2`\ immediately follows.`) is
still present and asserted byte-identically pre/post-fix, which is the literal SC#1 shape. The
deviation fixed an unrelated, pre-existing native-math-parsing defect (exposed only because the
separator fix let the native build proceed further) without touching what the gate is actually
pinning. Judgment: acceptable, does not require an override.

### Human Verification Required

None. The one `<human-check>` item deferred to end-of-phase (visual PDF layout confirmation, per
`34-03-PLAN.md` Task 2 and `34-VALIDATION.md`'s Manual-Only Verifications) was already executed and
recorded as "Approved" by the phase-03 executor, and I independently repeated it myself in this
verification session by rebuilding the fixture and directly viewing the rendered PDF page — the
render matches the claimed layout exactly (continuous prose+math lines, centred display equation, no
leaked Typst source). No outstanding visual, real-time, or external-service check remains.

### Gaps Summary

No gaps. All 5 ROADMAP success criteria are independently verified against the live codebase, not
merely restated from SUMMARY.md/GATE-EVIDENCE.md. The RED→GREEN proof (SC#4) was reproduced from
scratch in this session by temporarily restoring the pre-fix translator, confirming the identical
failure, then restoring the fixed file and confirming byte-identical restoration (`md5sum` match,
clean `git status --porcelain`). The four code-review warnings are legitimate test-coverage
follow-ups, not phase-blocking defects.

---

_Verified: 2026-07-28_
_Verifier: Claude (gsd-verifier)_
