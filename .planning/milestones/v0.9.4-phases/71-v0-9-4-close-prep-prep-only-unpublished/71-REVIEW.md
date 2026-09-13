---
phase: 71-v0-9-4-close-prep-prep-only-unpublished
reviewed: 2026-09-13T09:38:23Z
depth: standard
files_reviewed: 1
files_reviewed_list:
  - CHANGELOG.md
findings:
  critical: 0
  warning: 0
  info: 1
  total: 1
status: clean
---

# Phase 71: Code Review Report

**Reviewed:** 2026-09-13T09:38:23Z
**Depth:** standard
**Files Reviewed:** 1
**Status:** clean

## Summary

The phase's only product-tree change is a pure addition to `CHANGELOG.md`: one new bold-lead
bullet (10 lines added, 0 removed, 1 diff hunk) appended as the fourth item under the existing
`## [Unreleased]` → `### Changed`, immediately before `### Planned for Future Releases`. The rest
of the file is byte-identical to its prior state (confirmed via `git diff
f1f7d54a61d74c3972f1df0508ac994c001dda7e HEAD -- CHANGELOG.md`).

Verification performed:
- **Diff shape**: exactly one hunk, 10 added lines (9 bullet-content lines + 1 trailing blank
  separator), 0 removed lines, matching the `71-CHANGELOG-EVIDENCE.md` transcript.
- **House register**: bold lead ending in trailing requirement-ID parentheses (`QUA-09, QUA-11,
  QUA-12, DOC-22, DOC-23`), followed by prose, matches the three bullets above it (`tox-uv`,
  Dependabot `uv`, `flake.nix`).
- **D-01 (bold-lead verb)**: "Type annotations in typsphinx's source now use builtin generics"
  carries a verb ("use"), avoiding the bare-noun-phrase defect flagged as WR-01 in Phase 69's
  review.
- **D-02 (no ja/Japanese/catalog wording)**: `grep -iE 'japan|\bja\b|catalog'` over the bullet's
  lines returns no match.
- **D-03 (exactly one evidence sentence, one number)**: the bullet contains exactly one
  "byte-identical" claim sentence, and its only content number is `167`, which traces to
  `70-CORPUS-DOCS-BASE-EVIDENCE.md:45` (`CORPUS_PROJECT_COUNT = 167`) and
  `70-AFTER-RUNTIME-EVIDENCE.md:360` (`LEG_D_VERDICT = MET`) — not from this phase's own files.
- **No version numbers**: `grep -iE '0\.9\.[34]'` over the bullet's lines returns no match.
- **D-04 (everything else byte-identical)**: confirmed by the diff itself — no other hunks, no
  changes to the `### Planned for Future Releases` block or the tail link block.
- **Factual accuracy, spot-checked against code** (not just against evidence files):
  - `typsphinx/builder.py:11` imports `Iterator` from `collections.abc` (confirmed via direct
    `grep`), matching the bullet's specific claim.
  - `tests/test_include_ledger_removal_gate.py:46` also imports `Iterator` from `collections.abc`,
    confirming the bullet's claim that both `typsphinx/` and `tests/` moved.
  - No remaining `Dict[`/`List[`/`Set[`/`Tuple[` typing-alias usage in `typsphinx/*.py` or
    `tests/*.py` (confirmed via `grep`).
  - `pyproject.toml`'s `[tool.ruff.lint]` selects the `UP` rule group and does not ignore `UP006`
    or `UP035`, supporting "the linter now enforces this style."
  - `CLAUDE.md:75` documents the builtin-generics / `collections.abc` convention, supporting "the
    contributor notes in `CLAUDE.md` describe it."
- **Markup hygiene**: backtick count within the bullet is even (34, all pairs balanced), bold
  markers are paired (2), no trailing whitespace, no CRLF, valid UTF-8, 2-space continuation
  indentation matching the three bullets above it, single blank-line separators on both sides
  (consistent with existing bullet spacing).
- **Docs rendering** (per `71-CHANGELOG-EVIDENCE.md`): a clean `rm -rf docs/_build` +
  `docs-html`/`docs-pdf` rebuild before and after the edit produced identical warning counts (3 and
  5 respectively) with an identical set of warning messages — no new MyST/docutils warning is
  attributable to the new bullet, and the bullet does not break list continuation or block
  adjacency with the following `### Planned for Future Releases` heading.

No BLOCKER or WARNING-level defects were found in this diff. One INFO-level observation is
recorded below for the phase record.

## Info

### IN-01: "byte-identical" evidence sentence could be read as implying all 167 fixtures compiled successfully

**File:** `CHANGELOG.md:43-45`
**Issue:** The sentence "The Typst output typsphinx generates and its runtime behaviour are
unchanged: the `.typ` output is byte-identical across the test-fixture corpus of 167 projects" is
literally accurate (confirmed in `70-AFTER-RUNTIME-EVIDENCE.md`: the post-conversion manifest's
SHA-256 equals the pre-conversion manifest's SHA-256 for all 167 entries, `LEG_D_VERDICT = MET`).
However, 21 of those 167 fixtures are deliberately-failing error-path fixtures that produce zero
`.typ` output on both sides (`typ=0`, digest = SHA-256 of the empty string) — for those, "the `.typ`
output is byte-identical" holds vacuously (no output vs. no output) rather than describing an
actual rendered-and-compared Typst file. A reader of the published changelog page unfamiliar with
the internal corpus composition could read this as "167 real documents rendered identical Typst
markup," when roughly one in eight produced no markup at all by design. `71-CHANGELOG-EVIDENCE.md`
already discusses and consciously chooses this wording over "every project compiles" (which would
be false), so this is not a factual inaccuracy — it is a residual scope-legibility gap for an
external reader who has no access to that evidence file.
**Fix:** Optional; no change required given the evidence file's stated rationale. If a future edit
pass wants tighter legibility, a parenthetical such as "(including projects whose build is expected
to fail)" would close the gap without adding a second number.

---

_Reviewed: 2026-09-13T09:38:23Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
