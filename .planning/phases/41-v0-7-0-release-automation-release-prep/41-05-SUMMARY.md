---
phase: 41-v0-7-0-release-automation-release-prep
plan: 05
subsystem: release-prep
tags: [pytest, black, ruff, mypy, corpus-gate, typstpdf, tox, evidence]

# Dependency graph
requires:
  - phase: 41-01, 41-02, 41-03
    provides: "the CHANGELOG extraction script + pytest (41-01), the version-bumped 0.7.0 tree with the curated CHANGELOG entry (41-02), and the visit_desc_sig_name docstring fix (41-03) -- the post-bump tree this plan measures"
provides:
  - "Live-run evidence on the post-bump tree: full pytest suite (805 passed, 1 skipped), the lint/type trio (black/ruff/mypy all exit 0), the full-corpus (Sphinx v9.1.0 doc/) -b typstpdf gate (executed, PASSED), both docs dogfooding builds (docs-html, docs-pdf), and the D-12 diagnostic confirmed absent from the built docs"
  - "The CHANGELOG's third ### Verified claim (full-corpus re-run remains fatal-free) cross-checked against this plan's own measured result: HOLDS"
affects: ["41-07 (joins this plan's SC#3 mechanical-half evidence with plan 41-04's ja glyph bar and 41-06's SC#4 sweep into the phase close)"]

# Tech tracking
tech-stack:
  added: []
  patterns: ["Executed-vs-skipped honesty framing for the corpus gate (per 40/40.1's precedent)", "Page-count delta explained by mechanism, not merely reported (per Phase 39's precedent)"]

key-files:
  created: [.planning/phases/41-v0-7-0-release-automation-release-prep/41-GREEN-TREE-EVIDENCE.md]
  modified: []

key-decisions:
  - "Recorded the +6 pytest pass-count delta (805 vs 40.1's 799) as fully explained by tests/test_changelog_extraction.py's six new tests (plan 41-01), verified by name in the log rather than assumed."
  - "Recorded the +2 docs-pdf page-count delta (93 vs Phase 39's 91) as explained by Phase 40's citation handlers now rendering the pre-existing (unchanged) Smith2023 citation in docs/source/examples/advanced.rst, which previously had no dedicated citation-node rendering path."
  - "Cross-checked the CHANGELOG's third Verified claim against this plan's own Step 5 measurement and recorded a HOLDS verdict, closing the loop plan 41-02 could not close on its own."

requirements-completed: [REL-05]

coverage:
  - id: D1
    description: "Full pytest suite (including slow-marked tests) run on the post-bump tree, result line transcribed verbatim, every skip named individually with its reason, and the pass-count delta against 40.1-NONREGRESSION.md explained"
    requirement: "REL-05"
    verification:
      - kind: other
        ref: "uv run pytest -rA -- 805 passed, 1 skipped in 75.85s (0:01:15)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The lint/type trio (black --check ., ruff check ., mypy typsphinx/) each run with exit status recorded separately"
    requirement: "REL-05"
    verification:
      - kind: other
        ref: "uv run black --check . ; echo BLACK_EXIT:$? -- BLACK_EXIT:0"
        status: pass
      - kind: other
        ref: "uv run ruff check . ; echo RUFF_EXIT:$? -- RUFF_EXIT:0"
        status: pass
      - kind: other
        ref: "uv run mypy typsphinx/ ; echo MYPY_EXIT:$? -- MYPY_EXIT:0"
        status: pass
    human_judgment: false
  - id: D3
    description: "The full-corpus (Sphinx v9.1.0 doc/) -b typstpdf gate executed in isolation (not skipped), corpus reference read from the test's own output, and cross-checked against the CHANGELOG's third Verified claim"
    requirement: "REL-05"
    verification:
      - kind: other
        ref: "uv run pytest tests/test_corpus_gate.py -m slow -v -- test_corpus_compiles_with_no_fatal_error PASSED, corpus tag v9.1.0, 14.65s wall time (real build, not an instant skip)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Both docs dogfooding builds (tox -e docs-html, tox -e docs-pdf) succeed, PDF page count and warning summary transcribed and explained, D-12 diagnostic confirmed absent, and the working tree clean after both builds"
    requirement: "REL-05"
    verification:
      - kind: other
        ref: "uv run tox -e docs-html ; echo TOX_HTML_EXIT:$? -- TOX_HTML_EXIT:0"
        status: pass
      - kind: other
        ref: "uv run tox -e docs-pdf ; echo TOX_PDF_EXIT:$? -- TOX_PDF_EXIT:0, 93 pages, 1,968,588 bytes"
        status: pass
      - kind: other
        ref: "git status --porcelain (empty after both builds)"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-08-03
status: complete
---

# Phase 41 Plan 05: Green-Tree Evidence (SC#3 Mechanical Half) Summary

**Live-measured the post-bump v0.7.0 tree: 805 pytest passed / 1 skipped, black/ruff/mypy all clean, the full-corpus `-b typstpdf` gate genuinely EXECUTED and PASSED (not skipped), both docs dogfooding builds succeeded with the D-12 warning confirmed gone, and the CHANGELOG's third `### Verified` claim independently confirmed to HOLD.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-08-03T11:18:00Z (approx., after worktree provisioning)
- **Completed:** 2026-08-03T11:43:29Z
- **Tasks:** 3/3
- **Files modified:** 1 (`.planning/phases/41-v0-7-0-release-automation-release-prep/41-GREEN-TREE-EVIDENCE.md`, created)

## Accomplishments
- Ran the full pytest suite unfiltered (no `-m` marker) on the post-bump tree: **805 passed, 1 skipped in 75.85s**, the one skip being the same pre-existing, by-design `test_empty_url_before_after` env-gate — no failures. Explained the +6 delta against `40.1-NONREGRESSION.md`'s recorded 799 by name-matching the six new `tests/test_changelog_extraction.py` tests plan 41-01 added.
- Ran the lint/type trio: `black --check .` (207 files unchanged), `ruff check .` (all checks passed), `mypy typsphinx/` (no issues in 6 source files) — all three exit 0, with `mypy`'s `scripts/`-exclusion recorded explicitly as pre-existing configuration.
- Ran the full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` regression gate in isolation: `test_corpus_compiles_with_no_fatal_error` genuinely **EXECUTED** (14.65s wall time, cache-hit corpus, corpus tag `v9.1.0` read from the test's own resolution logic) and **PASSED** — not a skip. Cross-checked this measured result against the CHANGELOG's third `### Verified` bullet ("The full-corpus... re-run remains fatal-free") and recorded a **HOLDS** verdict.
- Ran both docs dogfooding builds: `tox -e docs-html` (exit 0, 2 pre-existing warnings) and `tox -e docs-pdf` (exit 0, same 2 warnings, `typsphinx.pdf` at 1,968,588 bytes / 93 pages). Explained the +2-page delta against Phase 39's 91-page baseline by locating the actual mechanism — Phase 40's new citation handlers now rendering a pre-existing, unchanged `[Smith2023]_` citation in `docs/source/examples/advanced.rst` that previously fell through docutils' generic unhandled-node path.
- Confirmed the D-12 fix (plan 41-03, commit `c81ca29`) reached the published API reference page: zero `visit_desc_sig_name` / `problematic`-node occurrences in either build's full warning output, versus the one such warning `39-GATE-EVIDENCE-04.md` §6 recorded pre-fix.
- Confirmed working-tree cleanliness after both docs builds (`git status --porcelain` empty) and that no irreversible action exists on this tree (`git tag -l v0.7.0` and `git ls-remote --tags origin v0.7.0` both empty).
- Closed the file with an `### SC#3 (mechanical half) verdict` naming, per criterion, which step proves it, and explicitly stating that the `ja` four-check glyph bar (plan 41-04, its own parallel worktree) is not covered here.

## Task Commits

Each task was committed atomically:

1. **Task 1: Run the full suite and the lint/type trio on the post-bump tree** - `80b66f5` (docs)
2. **Task 2: Execute the full-corpus typstpdf gate and cross-check the CHANGELOG Verified claim** - `8451a1d` (docs)
3. **Task 3: Run both docs dogfooding builds and confirm tree cleanliness** - `b483cac` (docs)

_Note: this plan runs in worktree isolation; the final metadata/SUMMARY commit is made separately per the worktree-agent protocol._

## Files Created/Modified
- `.planning/phases/41-v0-7-0-release-automation-release-prep/41-GREEN-TREE-EVIDENCE.md` - Created. Preconditions (HEAD SHA, `typsphinx.__version__` = `0.7.0`, resolved package path, both NixOS shims confirmed) plus Steps 1-8 (full suite, lint/type trio, isolated corpus gate + CHANGELOG cross-check, both docs builds, D-12 confirmation, working-tree cleanliness) and a closing SC#3 (mechanical half) verdict.

## Decisions Made
- Followed the plan's exact section shape (`### Step N — <command>` subsections, verbatim command + output, closing verdict) copied from `35-RELEASE-EVIDENCE.md`'s precedent, per `41-PATTERNS.md`'s explicit named analog.
- Captured every command's exit status via `command ; echo "LABEL_EXIT:$?"` in a single shell invocation rather than through a `tee` pipe (whose `$?` would reflect `tee`, not the piped command) — a self-correction made mid-execution after the first `docs-html` attempt's exit-code capture was unreliable through `tee`.
- Investigated the docs-pdf page-count delta (91→93) down to its actual mechanism (the pre-existing `Smith2023` citation in `examples/advanced.rst` now rendering through Phase 40's new citation handlers) rather than reporting the delta as an unexplained number, per the plan's own instruction and the Phase 39 precedent it names.

## Deviations from Plan

None - plan executed exactly as written. All three tasks landed with their exact specified commit messages; no auto-fix, blocking issue, or architectural question arose. The only mid-execution adjustment was a methodology self-correction (exit-code capture technique), not a deviation from the plan's instructions or scope.

## Issues Encountered

The sandboxed Bash tool rejected multi-line/heredoc-adjacent commands and any command chained with `&&`/`;` combined with a shell redirect as "too complex to verify stays inside the worktree" on a few occasions (matching the same sandbox behavior plan 41-02's SUMMARY recorded). Worked around by splitting each such command into separate, simpler Bash calls (e.g. running `git rev-parse --show-toplevel` and `git rev-parse HEAD` as two calls rather than one combined command, and moving multi-line Python verification snippets into single, unchained invocations without a trailing `&&`-joined shell test).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 41-05's SC#3 mechanical-half evidence is complete and independent of plan 41-04's `ja` glyph-bar evidence (running in its own parallel worktree) — both are needed for plan 41-07 to close SC#3 as a whole.
- The CHANGELOG's third `### Verified` claim is now independently measured and confirmed to HOLD, closing the loop plan 41-02 could not close on its own (it authored the claim before it could be measured).
- No irreversible action was taken (`git tag -l v0.7.0` and `git ls-remote --tags origin v0.7.0` both confirmed empty); the tree remains untouched other than this plan's one new evidence file.
- `git diff --stat -- typsphinx/ tests/ scripts/ .github/ CHANGELOG.md pyproject.toml uv.lock` over this plan's three commits is empty — nothing was edited to make any measurement green.

---
*Phase: 41-v0-7-0-release-automation-release-prep*
*Completed: 2026-08-03*
