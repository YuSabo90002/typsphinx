---
phase: 56-per-document-template-documentation
plan: 05
subsystem: docs
tags: [sphinx, rst, pytest, doc-gate, sweep, typst]

# Dependency graph
requires:
  - phase: 56-per-document-template-documentation (plans 01-04)
    provides: "the merged tree carrying every registry, output-layout, and asset-example correction this plan's sweep audits: 56-01's error catalogue and element-[4] retraction, 56-02's registry schema and removed-config guidance, 56-03's per-key bundle-directory story and corrected file counts, 56-04's asset-example fixes"
provides:
  - "56-SWEEP-DISPOSITION.md: the execution-time re-run of five discovery greps (plus two of this plan's own broadened searches) against the merged tree, a complete per-hit disposition table, and a Phase-boundary evidence section with a DOC-15/DOC-16/DOC-17 requirement-to-evidence mapping"
  - "The three anticipated fixes: examples/basic/README.md and examples/advanced/README.md's build-output prose (verified against real -b typst builds), and examples/charged-ieee/approach2/conf.py's comment"
  - "One fix found BEYOND the anticipated floor: examples/charged-ieee/approach1/conf.py's comment naming a deleted builder method"
  - "CLAUDE.md's corrected builder.py Architecture bullet (D-09), with the policed documentation set NOT widened"
  - "tests/test_bundle_layout_sweep_gate.py: a never-skipping, anchored, repo-wide presence gate with EXCLUDED_SWEEP_PATHS (reasoned exclusions + staleness test) and teeth self-tests, keeping the sweep's result durable going forward"
affects: []

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
# Same estimateTokens scale (chars/4 over the realized diff), never a harness token count.
actuals:
  tokens: 15015
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns: ["Anchored repo-wide presence gate distinguishing a reserved basename from a longer basename that merely ends in the same characters ((^|[^A-Za-z0-9])_template\\.typ)", "Line-scoped exclusion keys (\"path:LINENO\") alongside whole-file exclusion keys in the same EXCLUDED_SWEEP_PATHS dict, so a file with other lines worth policing stays policed everywhere except the one legitimate line", "Discovery-time re-grep as the search set, never the context-gathering floor -- this plan's own execution surfaced a hit (examples/charged-ieee/approach1/conf.py) the locked D-09/D-10 floor did not name"]

key-files:
  created: [tests/test_bundle_layout_sweep_gate.py, .planning/phases/56-per-document-template-documentation/56-SWEEP-DISPOSITION.md]
  modified: [CLAUDE.md, examples/basic/README.md, examples/advanced/README.md, examples/charged-ieee/approach1/conf.py, examples/charged-ieee/approach2/conf.py]

key-decisions:
  - "Fixed the hit found beyond the anticipated files_modified list (examples/charged-ieee/approach1/conf.py:59, naming the deleted TypstBuilder.copy_template_assets() method) rather than treating it as out of scope, per the sweep_scope_rule's explicit instruction that a hit outside the anticipated list is a real finding to dispose of, not a distraction to drop."
  - "examples/charged-ieee/approach2/conf.py's comment was reworded so the sentence naming the legitimate input path ('the file typst_template names below') no longer repeats the literal `_typst/_template.typ` string at the point that used to carry a stale output-artifact claim -- keeping the anchored gate's line-scoped exemption confined to the assignment line alone, per the plan's explicit 'Do not fix this filter' acceptance-criterion note."
  - "CLAUDE.md's builder.py bullet fix does NOT widen the policed documentation set -- no test greps CLAUDE.md; it stays agent-facing instruction per 54.1 D-12's unmodified scope."
  - "DOC-15/DOC-16/DOC-17 are left Pending in REQUIREMENTS.md, per the orchestrator's explicit instruction for this wave -- see the 'Requirements evidence' section below for what this plan believes is now fully delivered."

patterns-established:
  - "Anchored presence-gate pattern (^|[^A-Za-z0-9])X to distinguish a reserved token from a longer token that merely ends the same way, with a teeth test proving the exact false-positive shape it exists to exclude (docs/source/conf.py's own custom_template.typ)."

requirements-completed: []
# DOC-15, DOC-16, DOC-17 are intentionally left Pending. Per this plan's
# <requirements_flagging_rule>, the orchestrator flips them after the phase
# verifier independently confirms delivery -- not this plan, even though it
# is the last contributing plan for all three. See "Requirements evidence"
# below for the traceability this plan produced as evidence, not as a
# checkbox edit.

coverage:
  - id: D1
    description: "Every discovery grep from 56-CONTEXT.md D-09/D-10 (plus two broadened searches of this task's own devising) was re-run repo-wide against the merged tree, and every hit is dispositioned in writing in 56-SWEEP-DISPOSITION.md -- fixed, excluded, or not a hit, each with a reason."
    requirement: "DOC-15"
    verification:
      - kind: other
        ref: "56-SWEEP-DISPOSITION.md's per-hit disposition table (56 rows) and Command 1-7 transcripts"
        status: pass
    human_judgment: false
  - id: D2
    description: "No page in the policed documentation set (docs/source/, README.md, examples/) claims a root-level shared template file as an output artifact; the two runnable-example READMEs describe the per-key bundle directory, verified against real -b typst builds of both examples."
    requirement: "DOC-15"
    verification:
      - kind: unit
        ref: "tests/test_bundle_layout_sweep_gate.py::TestNoStaleBundleLayoutClaimSurvives::test_no_reserved_template_basename_claim_survives"
        status: pass
      - kind: integration
        ref: "Real sphinx-build -b typst of examples/basic and examples/advanced into scratch directories, file sets confirmed to match the corrected READMEs exactly"
        status: pass
    human_judgment: false
  - id: D3
    description: "examples/charged-ieee/approach2/conf.py's comment no longer claims setting typst_package would skip emitting an artifact that no longer exists; its typst_template value is unchanged, proven by both the charged-ieee gate and grep -c."
    requirement: "DOC-15"
    verification:
      - kind: unit
        ref: "tests/test_examples_charged_ieee_gate.py (2 tests, both passing)"
        status: pass
      - kind: other
        ref: "grep -c 'typst_template = \"_typst/_template.typ\"' examples/charged-ieee/approach2/conf.py == 1"
        status: pass
    human_judgment: false
  - id: D4
    description: "CLAUDE.md's architecture description no longer names the deleted _write_template_file builder method; the policed documentation set is not widened by this fix."
    requirement: "DOC-15"
    verification:
      - kind: other
        ref: "grep -c '_write_template_file' CLAUDE.md == 0; grep -rc 'CLAUDE.md' tests/test_bundle_layout_sweep_gate.py == 0"
        status: pass
    human_judgment: false
  - id: D5
    description: "A machine-enforced, never-skipping, anchored, repo-wide presence gate (tests/test_bundle_layout_sweep_gate.py) keeps the stale root-level-template claim and the deleted method name from returning, with reasoned exclusions, a staleness test, and both-direction teeth tests proving the anchor's exact false-positive case."
    requirement: "DOC-15"
    verification:
      - kind: unit
        ref: "tests/test_bundle_layout_sweep_gate.py (9 tests: TestNoStaleBundleLayoutClaimSurvives x4, TestSweepPatternsHaveTeeth x5, none skipped)"
        status: pass
    human_judgment: false
  - id: D6
    description: "Phase-boundary evidence: full pytest suite, lint/type trio, and both documentation builds are all green with zero carve-outs, and git diff --stat typsphinx/ against the phase base is empty."
    requirement: "DOC-15"
    verification:
      - kind: other
        ref: "56-SWEEP-DISPOSITION.md's Phase-boundary evidence section: uv run pytest -q (1417 passed, 5 skipped, 0 failed), black/ruff/mypy all clean, tox -e docs-html (3 warnings) and tox -e docs-pdf (5 warnings) both build succeeded, git diff --stat f07e8cb8 -- typsphinx/ empty"
        status: pass
    human_judgment: false

# Metrics
duration: ~20min
completed: 2026-08-16
status: complete
---

# Phase 56 Plan 05: Sweep Audit and Machine-Enforced Gate Summary

**Re-ran every discovery grep from D-09/D-10 against the fully-merged tree, found and fixed one hit beyond the recorded floor (a deleted-method reference in `examples/charged-ieee/approach1/conf.py` that no prior plan's `files_modified` anticipated), corrected the three anticipated files plus `CLAUDE.md`'s architecture bullet, and landed a never-skipping anchored sweep gate that keeps the result durable.**

## Performance

- **Duration:** ~20 min (commit-to-commit)
- **Started:** 2026-08-16T12:01:04Z
- **Completed:** 2026-08-16T12:21:30Z
- **Tasks:** 3
- **Files modified:** 7 (2 created, 5 modified)

## Accomplishments

- **Re-ran all five of D-09/D-10's discovery greps repo-wide against the merged tree**, plus two broadened searches this task added on its own initiative (a file-count-claim sweep and an every-file-mentioning-`_template` sweep), and recorded every command's complete output and a per-hit disposition (56 rows) in `56-SWEEP-DISPOSITION.md` — fixed, excluded (with reason), or not-a-hit (with reason), never a silent drop.
- **Found one hit BEYOND the D-09/D-10 floor**: `examples/charged-ieee/approach1/conf.py:59` named `TypstBuilder.copy_template_assets()`, a method deleted in Phase 54's bundle-copy consolidation (confirmed: zero hits for that name anywhere under `typsphinx/*.py`). This file was not in this plan's `files_modified` list. Fixed it to describe the current mechanism's package-alone skip branch (`_copy_used_template_bundles()`) without naming an internal symbol — re-verifying the comment's underlying behavioral claim stayed true by reading the current bundle-copy code first.
- **Fixed the three anticipated files**: `examples/basic/README.md` and `examples/advanced/README.md`'s build-output prose, each corrected and then verified against a real `sphinx-build -b typst` of the example into a scratch directory (not just read against each other); `examples/charged-ieee/approach2/conf.py`'s comment no longer claims setting `typst_package` would "skip emitting `_template.typ`" — it states the actual consequence (no local bundle copied, template never reaches the output).
- **Corrected `CLAUDE.md`'s Architecture section (D-09)**: the `builder.py` bullet no longer names `_write_template_file`; it now describes `_copy_used_template_bundles()`'s write-time key accumulation and `finish()`-time wholesale bundle copy. The policed documentation set stays exactly 54.1 D-12's `docs/source/` + `README.md` + `examples/` — no test greps `CLAUDE.md`.
- **New `tests/test_bundle_layout_sweep_gate.py`**: a never-skipping, text-only, run-time `rglob`-discovered presence gate over the three policed roots. Two patterns — an anchored one for the reserved `_template.typ` basename (`(^|[^A-Za-z0-9])_template\.typ`, so a longer basename like `custom_template.typ` cannot false-positive) and a word-bounded one for `_write_template_file` — plus `EXCLUDED_SWEEP_PATHS` (a historical whole-file exclusion and a line-scoped legitimate-input-path exclusion, both with written reasons) and a staleness test proving every exclusion still exempts something real. 9 tests total (4 real assertions, 5 teeth self-tests), none skipped.
- **Phase-boundary evidence recorded**: full pytest suite 1417 passed / 5 skipped / 0 failed (up from the phase's 1366/5/0 starting baseline, unconditional zero failures with no carve-out); `black`/`ruff` (via the documented main-checkout NixOS workaround)/`mypy` all clean; `tox -e docs-html` (3 warnings) and `tox -e docs-pdf` (5 warnings) both `build succeeded`, matching the pre-existing baseline exactly; `git diff --stat` of `typsphinx/` against the phase's base commit (`f07e8cb8`) is empty across all five plans of this phase.

## Task Commits

Each task was committed atomically:

1. **Task 1: Re-run the discovery greps, dispose of every hit, fix the example READMEs** - `f5bb153b` (docs)
2. **Task 2: Correct CLAUDE.md's architecture description and land the sweep gate** - `0811ab69` (docs)
3. **Task 3: Record the phase-boundary evidence** - `0a6fc985` (docs)

**Plan metadata:** committed as part of this SUMMARY.md commit (worktree mode — STATE.md/ROADMAP.md excluded; the orchestrator owns those writes after the wave merges).

## Files Created/Modified

- `.planning/phases/56-per-document-template-documentation/56-SWEEP-DISPOSITION.md` - New: the complete discovery-command transcripts, the 56-row per-hit disposition table, the fixes-applied narrative for Tasks 1-2, and the Phase-boundary evidence + requirement-to-evidence mapping for Task 3.
- `tests/test_bundle_layout_sweep_gate.py` - New: `POLICED_ROOTS`, `RESERVED_TEMPLATE_BASENAME_RE` (anchored), `DELETED_WRITE_TEMPLATE_FILE_METHOD_RE`, `EXCLUDED_SWEEP_PATHS`, `_discover_policed_files()`, `TestNoStaleBundleLayoutClaimSurvives` (4 tests), `TestSweepPatternsHaveTeeth` (5 tests).
- `CLAUDE.md` - The `builder.py` Architecture bullet rewritten to describe `_copy_used_template_bundles()` instead of the deleted `_write_template_file`.
- `examples/basic/README.md` - The build-output sentence rewritten to name the two root-level files this example produces plus the template bundle one directory down, verified against a real build.
- `examples/advanced/README.md` - The bulleted output listing's last bullet rewritten from a root-level `_template.typ` to the per-key bundle path, verified against a real build.
- `examples/charged-ieee/approach1/conf.py` - The comment naming the deleted `copy_template_assets()` method rewritten to describe the current bundle-copy mechanism's package-alone skip branch.
- `examples/charged-ieee/approach2/conf.py` - The comment claiming a skipped output artifact rewritten to state the actual package-only-route consequence; `typst_template`'s value unchanged.

## Decisions Made

- **The `examples/charged-ieee/approach1/conf.py` hit was fixed, not deferred, despite being outside this plan's anticipated `files_modified` list.** The `sweep_scope_rule`'s instruction is explicit: a hit found outside the anticipated list by a repo-wide grep is a real finding, not an out-of-scope distraction. Deferring it would have reproduced exactly the failure mode (a written floor mistaken for the search set) this plan exists to close.
- **`examples/charged-ieee/approach2/conf.py`'s comment rewording went one sentence further than a literal reading of the plan's action text.** The plan's own acceptance criterion explicitly states line 21 (the sentence naming the input file) must ALSO stop matching the anchored gate pattern, not just line 23 (the output-artifact claim) — "Broadening the filter ... would silently swallow line 21 and defeat D-10." Reworded that sentence to say "the file `typst_template` names below" instead of repeating the literal `_typst/_template.typ` string, so the anchored gate's line-scoped exemption stays confined to the assignment line alone, matching the acceptance criterion's stated intent exactly.
- **`CLAUDE.md`'s fix does not add a test that greps `CLAUDE.md`**, per the plan's explicit prohibition — the policed documentation set (54.1 D-12) stays `docs/source/` + `README.md` + `examples/` only.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - blocking fix] `ruff` `B007` unused-loop-variable finding in the new gate module**
- **Found during:** Task 2's lint verification (`ruff check` via the main-checkout NixOS workaround).
- **Issue:** `TestNoStaleBundleLayoutClaimSurvives::test_every_exclusion_still_matches_something` iterated `for key, reason in EXCLUDED_SWEEP_PATHS.items()` but never used `reason`.
- **Fix:** Changed to `for key in EXCLUDED_SWEEP_PATHS`.
- **Files modified:** `tests/test_bundle_layout_sweep_gate.py`
- **Verification:** `ruff check` clean; `uv run pytest tests/test_bundle_layout_sweep_gate.py -q` stayed green (9 passed).
- **Committed in:** `0811ab69` (fixed before the task's own commit, not a separate commit)

---

**Total deviations:** 1 (self-caught blocking fix, no scope creep). The `examples/charged-ieee/approach1/conf.py` fix is NOT counted as a deviation — finding and fixing hits beyond the anticipated floor is the designed, in-scope purpose of this plan's Task 1, not unplanned work triggered by a deviation rule.

## Requirements evidence

Per this plan's `<requirements_flagging_rule>`, DOC-15, DOC-16, and DOC-17 are left `Pending` in
`.planning/REQUIREMENTS.md` — not flipped by this plan, even though it is the last contributing
plan for all three. This is the evidence this plan believes closes them:

- **DOC-15** (per-document template registry documentation): fully delivered across 56-01
  (error catalogue, element-[4] retraction), 56-02 (registry schema, key-naming rules,
  removed-values guidance), 56-03 (output-layout bundle story, corrected file counts,
  conditional `--root` rule), and this plan's own sweep gate (`test_bundle_layout_sweep_gate.py`)
  proving no stale claim survives anywhere in the policed set. See
  `56-SWEEP-DISPOSITION.md`'s "Requirement-to-evidence mapping" section for the full test list.
- **DOC-16** (per-document template asset examples): fully delivered by 56-04's fixture
  extension and prose corrections, with this plan's sweep gate confirming no stale asset claim
  survives in either `templates.rst` or `advanced.rst`.
- **DOC-17** (removed configuration values migration guidance): fully delivered by 56-02's
  Removed Configuration Values section, bound by test to `typsphinx/removed_config.py`, with
  this plan's Command 4 discovery grep confirming no stale claim about any of the three removed
  names survives outside that intentional section and the historical CHANGELOG entries.

## Issues Encountered

- **Two of this plan's own acceptance-criteria greps are unsatisfiable at their literal word
  count, for reasons that predate this plan** — the same class of false positive 56-01/56-02/56-04's
  own SUMMARY.md files each documented once:
  - Task 2's `grep -rc 'CLAUDE.md' tests/ is 0` cannot pass literally: `tests/` already carries
    25 PRE-EXISTING citations of `CLAUDE.md` across 22 files (mostly `// ... (CLAUDE.md).`
    comments inside `.typ` fixtures citing the `@preview` version-lockstep hazard). None are
    new; none is inside this plan's own `tests/test_bundle_layout_sweep_gate.py`
    (`grep -c 'CLAUDE.md' tests/test_bundle_layout_sweep_gate.py` is 0); `git diff HEAD~1 -- tests/`
    for that commit shows zero added lines containing `CLAUDE.md`. The criterion's actual
    intent — "this task's own new test does not grep `CLAUDE.md`'s content" — is genuinely
    satisfied; the literal repo-wide count is not, for reasons unrelated to this plan.
  - This is the same false-positive shape 56-01 documented for `git diff | grep -c '^-.*"typst")'`
    and 56-04 documented for `git diff ... | grep -c '@preview'`: an acceptance-criterion grep
    that cannot distinguish a literal-substring coincidence in unrelated, pre-existing content
    from an actual violation.
- **`ruff` cannot run inside this worktree's own `.venv`** (generic-linux ELF wheel, unrunnable
  under NixOS — the same pre-existing, project-documented limitation every prior plan in this
  phase encountered). Resolved per `CLAUDE.md`'s documented workaround: ran
  `uv run ruff check` from the main checkout (`/home/yuta/Documents/typsphinx`) against the
  worktree path. All checks passed clean on every file this plan touched, after the one `B007`
  fix above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `tests/test_bundle_layout_sweep_gate.py` now polices the whole documentation set going
  forward: any future edit that reintroduces a root-level `_template.typ` claim or the deleted
  `_write_template_file` method name anywhere under `docs/source/`, `README.md`, or `examples/`
  fails this gate immediately, without needing another manual sweep.
- `56-SWEEP-DISPOSITION.md` is the complete, falsifiable record of this phase's SC#4 closure —
  every discovery command, its full output, and a written disposition for every hit, plus the
  requirement-to-evidence mapping the phase verifier can use directly.
- No blockers. `git diff --stat f07e8cb8 -- typsphinx/` is empty across every commit of every
  plan in this phase — no production code was touched anywhere in Phase 56, matching its
  entirely docs-only scope.
- Full-suite baseline: 1417 passed, 5 skipped, 0 failed (up from the phase's starting 1366/5/0);
  `black`, `ruff` (via the main-checkout workaround), and `mypy typsphinx/` are all clean;
  `tox -e docs-html` (3 warnings) and `tox -e docs-pdf` (5 warnings) both report
  `build succeeded`, matching the pre-existing baseline exactly.

## Self-Check: PASSED

- FOUND: `.planning/phases/56-per-document-template-documentation/56-SWEEP-DISPOSITION.md`
- FOUND: `tests/test_bundle_layout_sweep_gate.py`
- FOUND: `CLAUDE.md`
- FOUND: `examples/basic/README.md`
- FOUND: `examples/advanced/README.md`
- FOUND: `examples/charged-ieee/approach1/conf.py`
- FOUND: `examples/charged-ieee/approach2/conf.py`
- FOUND: commit `f5bb153b`
- FOUND: commit `0811ab69`
- FOUND: commit `0a6fc985`

---
*Phase: 56-per-document-template-documentation*
*Completed: 2026-08-16*
