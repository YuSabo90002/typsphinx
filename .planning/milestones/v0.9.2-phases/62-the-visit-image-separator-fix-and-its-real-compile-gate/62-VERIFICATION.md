---
phase: 62-the-visit-image-separator-fix-and-its-real-compile-gate
verified: 2026-08-30T18:30:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 62: The `visit_image()` Separator Fix and Its Real-Compile Gate Verification Report

**Phase Goal:** `sphinx-build -b typstpdf` produces a PDF for every master document of a project
that places an image anywhere other than first in its container. `visit_image()`'s separator
discipline joins the rest of the translator, and the proof is a real `typst.compile()` over the
whole measured trigger matrix — not a string assertion.

**Verified:** 2026-08-30T18:30:00Z
**Status:** passed
**Re-verification:** No — initial verification

This verification was done by re-measuring every claim independently in this session (not by
reading `62-RED-EVIDENCE.md` and trusting it). Where the phase's own evidence transcript was
reproduced, that is noted explicitly below.

## Goal Achievement

### Observable Truths (ROADMAP Phase 62 Success Criteria, verbatim)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A project containing every failing shape builds a PDF for every one of its masters (SC#1). | ✓ VERIFIED | Independently ran `uv run python -m sphinx -b typstpdf tests/fixtures/inline_image_separator_render_gate /tmp/verify62_green` on the current (fixed) tree in this session: exit 0, `build succeeded`, **18** `*-out.pdf` files written including `index-out.pdf` (image-free master) and all 16 `fail_*` masters. Also independently ran `uv run pytest tests/test_inline_image_separator_render_gate.py -q`: **30 passed**. |
| 2 | The gate was RED against the unfixed tree, and the RED is transcribed (SC#2). | ✓ VERIFIED | Independently reproduced the RED run in this session: `git checkout 5a837238aadc126611b175228cbed5ac8b1058f8 -- typsphinx/translator.py` then `sphinx-build -b typstpdf` over the fixture reproduced the identical `expected semicolon or line break` refusal on all 17 masters (matches `62-RED-EVIDENCE.md` verbatim). Restored the fix with `git checkout HEAD -- typsphinx/translator.py`; `git status --porcelain -- typsphinx/translator.py` was empty (byte-identical restore, confirmed independently, not merely re-read from the evidence file). The gate module greps positive for the real-compile API: `import typst` / `TYPST_AVAILABLE` present at lines 48-52 of `tests/test_inline_image_separator_render_gate.py`. |
| 3 | All 9 must-keep-passing shapes still pass, and the fix stayed inside its branch (SC#3). | ✓ VERIFIED | Read `typsphinx/translator.py:4747-4790` directly: both `if self.in_figure:` / `else:` branch bodies in `visit_image()` are byte-identical to `PHASE_BASE_SHA`; the 9-line insertion sits strictly above the split. `git diff --numstat 5a837238..HEAD -- typsphinx/translator.py` = `9  0` (pure insertion, independently re-run). `grep -F -e 'endswith("\n")' -e 'rstrip().endswith' -e '[-1:]' typsphinx/translator.py` finds nothing (exit 1, independently re-run). `uv run pytest tests/test_nested_figure_render_gate.py tests/test_pdf_render_gate.py -q` → **38 passed**, and neither file appears in the phase's `tests/` diff. |
| 4 | Zero pre-existing test edits, measured rather than asserted (SC#4). | ✓ VERIFIED | `git diff --name-status 5a837238..HEAD -- tests/` independently re-run: all 40 lines begin `A`; `grep -cv '^A'` = 0. `git diff --name-only 5a837238..HEAD -- tests/test_translator.py` is empty (the 9 string-level image tests are untouched). |
| 5 | The milestone branch is on `origin` with a completed 3-OS CI run (SC#5). | ✓ VERIFIED | `git ls-remote --heads origin gsd/v0.9.2-inline-image-blocker-fix-and-release` returns the current tip `0366eca4...`. `git branch --list 'gsd/v0.9.2*' \| wc -l` = 1 (no decoy). `gh run view 33302087913 --json status,conclusion` (queried live against GitHub, independent of the evidence file) returns `{"conclusion":"success","status":"completed"}`. `gh run view 33302087913 --json jobs` independently confirms `Test Python 3.12/3.13 on windows-latest` = success and `Test Python 3.12/3.13 on macos-latest` = success, each named individually, plus `Lint and Format Check` = success. `git tag -l 'v0.9.2*'` and `git ls-remote --tags origin 'v0.9.2*'` both empty; `gh pr list --head gsd/v0.9.2-inline-image-blocker-fix-and-release` returns none. |

**Score:** 5/5 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/translator.py` (`visit_image`/`depart_image`) | 9-line pure-insertion separator triad, both `in_figure` branch bodies unmodified | ✓ VERIFIED | Read directly; diff confirmed `9/0`; content matches `62-RED-EVIDENCE.md`'s transcribed diff exactly |
| `tests/test_inline_image_separator_render_gate.py` | Real-compile gate module, `-k full_matrix` and `-k fail` selectors | ✓ VERIFIED | 30 tests collected; `-k full_matrix` selects 3, `-k fail` selects 17; all pass; `grep -c read_bytes` = 0 |
| `tests/fixtures/inline_image_separator_render_gate/` | 27 `.rst` docs (16 FAIL + 9 PASS + `index` + `pass_parent`), 18 `typst_documents` masters | ✓ VERIFIED | `ls *.rst \| wc -l` = 27; `fail_*.rst` = 16; `pass_[a-i]*.rst` = 9; `-out.typ` target-stem count in `conf.py` = 18; no `numref` usage anywhere |
| `tests/fixtures/inline_image_separator_render_gate/goldens/` | 9 committed PASS goldens + 1 pre-fix reference for shape C | ✓ VERIFIED | `diff` between `pass_c_...pre_fix.typ` and `pass_c_...typ` = exactly one added blank line (`16a17 >`), zero removed — matches Amendment 2's pinned delta exactly |
| `.planning/phases/.../62-RED-EVIDENCE.md` | Phase base SHA, RED transcript, golden capture, restore confirmation, SC#5 sections | ✓ VERIFIED | Present, 721 lines, all sections populated; RED transcript independently reproduced in this session and matches byte-for-byte |
| `.planning/phases/.../COVERAGE.md` | Reasoned no-external-API declaration | ✓ VERIFIED | Present, carries `{"detected":false,"signals":[]}` and the "No external API integration:" line |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `visit_image()` leading triad | `_add_paragraph_separator()` / `_emit_inline_concat_separator()` / `in_list_item`+`list_item_needs_separator` | direct call, hoisted above `if self.in_figure:` split | ✓ WIRED | Confirmed by direct source read; this is what closes the two legend shapes (`fail_09`, `fail_10`), independently re-compiled and confirmed PDF-producing |
| `depart_image()` trailing bookkeeping | `_mark_inline_concat_content()` early-return | inside `if not self.in_figure:` block, before the trailing `"\n\n"` | ✓ WIRED | Confirmed by direct source read; closes the field-list concat shape (`fail_14`), independently re-compiled and confirmed PDF-producing |
| `index.rst` toctree | 16 FAIL content files | `#include()` via toctree | ✓ WIRED | `index-out.pdf` independently confirmed non-empty/`%PDF`-prefixed on the fixed tree, and independently confirmed to fail on the restored unfixed tree — the blast-radius property (IMG-09) holds in both directions |
| `TypstPDFBuilder.finish()` | every configured master | independent per-master compile attempt inside one loop | ✓ WIRED | RED run independently reproduced: 17/18 masters refused, exactly `pass_parent` compiled — confirms per-master independence and the positive control (D-03) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Fixed tree compiles all 18 masters | `uv run python -m sphinx -b typstpdf tests/fixtures/inline_image_separator_render_gate <dir>` | exit 0, 18 `*-out.pdf` written | ✓ PASS |
| Unfixed tree fails identically to the transcript | same command, with `translator.py` restored to `PHASE_BASE_SHA` | exit non-zero, `expected semicolon or line break` × 17, `pass_parent` still green | ✓ PASS |
| Gate module passes | `uv run pytest tests/test_inline_image_separator_render_gate.py -q` | 30 passed | ✓ PASS |
| Full suite green, no phase regression | `uv run pytest -q` | 1543 passed, 5 skipped (all 5 pre-existing/unrelated: myst-parser docs-extra gap ×4, env-gated corpus report ×1) | ✓ PASS |
| `black`/`mypy` green | `uv run black --check .` / `uv run mypy typsphinx/` | both clean | ✓ PASS |
| Two exact-byte figure gates unedited and passing | `uv run pytest tests/test_nested_figure_render_gate.py tests/test_pdf_render_gate.py -q` | 38 passed | ✓ PASS |
| CI authority run | `gh run view 33302087913 --json status,conclusion,jobs` | completed/success; windows-latest ×2 and macos-latest ×2 jobs individually success; `Lint and Format Check` success | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| IMG-08 | 62-01, 62-02 | Image preceded by sibling content gets a separator, across all 16 measured failing shapes | ✓ SATISFIED | 16/16 FAIL shapes independently confirmed compiling on the fixed tree and refusing (identically) on the restored unfixed tree |
| IMG-09 | 62-01, 62-02, 62-04 | `-b typstpdf` produces a PDF for every master, including image-free ones | ✓ SATISFIED | 18/18 masters independently confirmed PDF-producing, including `index` (no image) |
| IMG-10 | 62-01, 62-03, 62-04 | Fix routes through the pre-existing triad; `in_figure` branch unmodified; zero pre-existing test edits | ✓ SATISFIED | Diff read directly (9/0 pure insertion, both branch bodies untouched); forbidden-predicate grep empty; `tests/` diff is 40/40 `A` |
| TEST-05 | 62-01, 62-02, 62-03 | One gate module binds FAIL+PASS matrix on a real `typst.compile()` | ✓ SATISFIED | Gate module greps positive for `typst.compile`/`TYPST_AVAILABLE`; RED-before-fix independently reproduced; 30/30 gate tests pass on the fixed tree |

No orphaned requirements: `REQUIREMENTS.md` maps only IMG-08, IMG-09, IMG-10, TEST-05 to Phase 62, and all four appear in plan frontmatter `requirements:` fields and are marked `[x]` in `REQUIREMENTS.md`.

### Anti-Patterns Found

`62-REVIEW.md` (independent code-review artifact for this phase, not authored by this verifier) found 0 critical, 2 warning, 2 info findings over the 30 phase-touched files. None blocks the phase goal:

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `typsphinx/translator.py` | 4750-4754 | `visit_image()`'s hoisted separator call can emit one extra blank line when the image is first in a paragraph or inside a concat context | Warning (non-blocking) | Functionally harmless (Typst only needs *a* newline boundary, not exactly one); this is the exact, intentional, already-pinned delta captured in the `pass_c` golden pair, re-confirmed independently in this session (`16a17 >`, one line added, zero removed) |
| `typsphinx/translator.py` | 4786-4792 | `depart_image()`'s new concat-aware bookkeeping has no rationale comment, unlike the file's established per-line-comment convention | Warning (non-blocking) | Maintainability risk for a future contributor, not a functional defect; no code path is broken |
| fixture matrix | — | No fixture combines "propagated target id" with "non-first sibling in a list item" | Info | Manually traced by the reviewer as producing at most a redundant blank line, not a compile failure |
| fixture matrix | — | No fixture wraps an image in a hyperlink (`:target:`) inside a paragraph/list item | Info | Manually traced by the reviewer as producing at most a redundant newline inside a parenthesized argument list, not a missing separator |

No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` markers found in the phase's touched files
(`typsphinx/translator.py` insertion region and `tests/test_inline_image_separator_render_gate.py`,
grepped directly in this session).

### Human Verification Required

None. The one `<human-check>` deferred by `62-04-PLAN.md` ("open the CI run URL and confirm by eye
that `windows-latest`/`macos-latest` are green and `Run lint with tox` succeeded") is a visual
restatement of exactly the job-conclusion data this verifier independently retrieved via
`gh run view 33302087913 --json status,conclusion,jobs` in this session — every named job's
`conclusion` field reads `success`, matching what the linked web page renders. This substantively
discharges the deferred check by direct measurement rather than narrative trust, so it is not
carried forward as an open human-verification item.

### Gaps Summary

None. Every ROADMAP Phase 62 Success Criterion was independently re-measured in this verification
session (not read-and-trusted from `62-RED-EVIDENCE.md`) and holds: the fixed tree compiles all 18
masters to valid PDFs; the restored-unfixed tree reproduces the identical RED transcript; the
`in_figure` branch bodies are byte-unmodified; the phase's `tests/` diff is entirely additive; and
the dispatched CI run (`33302087913`) is `completed`/`success` with both non-Linux lanes
individually green and `ruff`'s verdict sourced from that run alone. All four requirement IDs
(IMG-08, IMG-09, IMG-10, TEST-05) are satisfied and correctly reflected as `[x]` in
`REQUIREMENTS.md`. The two code-review warnings and two info items are legitimate, honestly
self-reported quality notes — one is an already-pinned, intentional, harmless byte delta; the other
three are documentation/coverage suggestions for future fixture expansion — none of them prevents
the phase goal from holding today.

---

_Verified: 2026-08-30T18:30:00Z_
_Verifier: Claude (gsd-verifier)_
