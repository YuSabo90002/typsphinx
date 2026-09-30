---
phase: 50-pr-131-image-path-defects
plan: 03
subsystem: testing
tags: [sphinx, typst, image-tracking, unit-tests, evidence-audit]

requires:
  - phase: 50-02
    provides: TypstBuilder._track_image() widened with the srcdir-collision and outdir-escape relocation branches, both routed through RESERVED_IMAGE_NAMESPACE; D-11 SC#3 two-build manifest evidence
provides:
  - "Unit-level coverage of the three relocation branches the D-10 end-to-end render gate does not reach: srcdir-collision (silent), outdir-escape (warns once), Windows cross-drive ValueError catch"
  - "50-BRANCH-EVIDENCE.md — the phase's close-out audit: D-12 fixed-point re-proof, the RED->GREEN chain with its edit-scope proof, an audit of wave 2's SC#3 measurement taken from a later wave, and every phase gate recorded against a stated baseline"
affects: []

actuals:
  tokens: 6060
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Targeted os.path.relpath monkeypatch scoped to one specific first-argument value, delegating to the real implementation otherwise, to simulate a Windows cross-drive ValueError on a POSIX CI host without a blanket replacement that would break unrelated path work in the same call"
    - "Filesystem-probed collision fixture built with no pre-seeded self.images entry, so the branch decision is provably a filesystem probe (D-03) rather than a dict-order artifact"

key-files:
  created:
    - .planning/phases/50-pr-131-image-path-defects/50-BRANCH-EVIDENCE.md
  modified:
    - tests/test_builder.py

key-decisions:
  - "Expected key strings (_typst_converted/images/converted.png, _typst_converted/chart.png) and the warning-message substring (could not rehome image URI) are hardcoded literals taken from CONTEXT.md/the plan's <behavior> block, never read back out of the already-fixed builder.py -- per the plan's own anti-laundering instruction."
  - "Inserted the four new tests immediately after the second D-12-pinned test (test_copy_image_files_uses_override_source_for_absolute_uri) rather than at the file's end, keeping them physically beside the pinned pair per the plan's read_first framing, without editing, reordering, or extracting shared helpers from either pinned test."
  - "The escape test additionally asserts '..' not in img[\"uri\"].split(\"/\") -- an explicit assertion tying the test to the T-50-01 threat-model row's stated mitigation (the escaping URI's key never carries a parent segment reaching copy_image_files()), beyond what the plan's literal <behavior> text required."
  - "50-BRANCH-EVIDENCE.md's SC#3 audit (section 3) discloses a SECOND undisclosed-in-the-plan deviation from 50-VALIDATION.md's literal D-11 command sequence beyond the named --extra docs amendment: the .doctrees/-exclusion in the find command, already investigated and justified in 50-D11-EVIDENCE.md's own Finding 2. Both are reported with their measured justification rather than only the one the acceptance criterion names."

patterns-established: []

requirements-completed: [IMG-01, IMG-02]

coverage:
  - id: D1
    description: "The srcdir-collision, outdir-escape, and cross-drive-ValueError relocation branches each have at least one passing unit test, with expected values traceable to CONTEXT.md/the plan rather than to the fixed code"
    requirement: "IMG-01"
    verification:
      - kind: unit
        ref: "uv run pytest tests/test_builder.py -k \"rehome or escape or cross_drive or relocated\" -q (5 selected, 5 passed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "tests/test_builder.py's diff for the phase is additions only; both D-12-pinned tests pass unedited, byte-unchanged against the phase base commit"
    requirement: "IMG-02"
    verification:
      - kind: other
        ref: "git diff 2ccbbd3a -- tests/test_builder.py | grep -cE '^-[^-]' -> 0; uv run pytest tests/test_builder.py::test_post_process_images_rehomes_absolute_uri tests/test_builder.py::test_copy_image_files_uses_override_source_for_absolute_uri -q -> 2 passed"
        status: pass
    human_judgment: false
  - id: D3
    description: "50-BRANCH-EVIDENCE.md records the D-12 fixed-point audit, the RED->GREEN chain with its edit-scope proof, the SC#3 audit of wave 2's measurement, and every phase gate against a stated baseline"
    requirement: "IMG-01"
    verification:
      - kind: other
        ref: ".planning/phases/50-pr-131-image-path-defects/50-BRANCH-EVIDENCE.md (sections 1-4)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Phase 50's SC#1, SC#2 and SC#3 are each mapped to a named artifact and a named command"
    requirement: "IMG-02"
    verification:
      - kind: other
        ref: "50-BRANCH-EVIDENCE.md section 5 (Success Criteria -> Artifact -> Command Map)"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-08-14
status: complete
---

# Phase 50 Plan 03: Branch Coverage + Evidence-Chain Audit Summary

**Four additive unit tests in `tests/test_builder.py` close the srcdir-collision, outdir-escape, and Windows cross-drive `ValueError` branches the D-10 end-to-end gate does not reach, and `50-BRANCH-EVIDENCE.md` audits the phase's own evidence chain from a wave later than the ones that produced it — closing all three of Phase 50's success criteria against named artifacts and commands.**

## Performance

- **Duration:** ~55 min
- **Started:** worktree base commit `ac9cb950c806d350997b88a9cdbdd21d94ec1547` (wave 1+2 merged)
- **Completed:** 2026-08-14
- **Tasks:** 2/2 completed
- **Files touched:** 1 modified (`tests/test_builder.py`), 1 created (`50-BRANCH-EVIDENCE.md`)

## Accomplishments

- Appended four unit tests to `tests/test_builder.py`, sitting immediately beside the two D-12-pinned tests without editing either: `test_post_process_images_rehome_collision_relocates_silently` (real file at `srcdir/images/converted.png`, no pre-seeded `self.images` entry, asserts relocation to `_typst_converted/images/converted.png` with an empty WARNING-record list — D-01/D-02/D-03/D-04), `test_post_process_images_rehome_escape_relocates_with_warning` (an absolute URI built from the filesystem root, asserts relocation to `_typst_converted/chart.png` plus exactly one WARNING record containing `could not rehome image URI` and the offending URI — D-05/D-06), `test_post_process_images_rehome_cross_drive_value_error_relocates` (`os.path.relpath` monkeypatched to raise `ValueError` only for this test's specific absolute URI, asserting the relocation OUTCOME rather than the exception being caught — D-07), and `test_copy_image_files_relocated_key_destination_stays_under_outdir` (a hand-seeded `_typst_converted/images/converted.png` key, asserting the copied destination's resolved common path with `outdir` is `outdir` itself — T-50-01).
- Wrote `50-BRANCH-EVIDENCE.md`: re-ran and confirmed byte-unchanged the D-12 fixed-point pair against the phase base commit (`tests/test_absolute_image_render_gate.py` zero diff; `tests/test_builder.py` additions-only); quoted the pre-fix RED from `50-RED-EVIDENCE.md` alongside the current post-fix GREEN observation of the same two facts, with an `xfail`-filtered diff proving the only edit to the gate module across the whole phase was removing two decorator lines; audited wave 2's `50-D11-EVIDENCE.md`/manifests without re-running its builds, confirming byte-identical manifests and disclosing BOTH command-sequence deviations from `50-VALIDATION.md` (the plan-named `--extra docs` amendment and the independently-justified `.doctrees/`-exclusion); and recorded the full phase gate suite (1156 passed / 5 skipped against a stated 1152-passed pre-phase baseline, black/mypy clean, `ruff` unrunnable on this NixOS host with CI named as lint authority).
- Closed the file by mapping each of Phase 50's three success criteria to a named artifact and command, and mapping every new/pinned test to IMG-01 or IMG-02.

## Task Commits

1. **Task 1: Cover the three relocation branches with additive unit tests** - `7dd50ecd` (test)
2. **Task 2: Audit the phase's evidence chain and close the gates** - `8f7776e5` (docs)

## Files Created/Modified

- `tests/test_builder.py` - four new unit tests appended beside the two D-12-pinned tests; zero lines removed
- `.planning/phases/50-pr-131-image-path-defects/50-BRANCH-EVIDENCE.md` - phase close-out audit: D-12 re-proof, RED->GREEN chain, SC#3 audit of wave 2's measurement, phase gates, SC/test mapping tables

## Decisions Made

- Every expected string in the four new tests (`_typst_converted/images/converted.png`, `_typst_converted/chart.png`, `could not rehome image URI`) was typed from CONTEXT.md's D-01 through D-07 and this plan's `<behavior>` block, never read back out of the already-fixed `typsphinx/builder.py` — verified by writing the assertions before re-reading the implementation a second time.
- Added one assertion beyond the plan's literal `<behavior>` text in the escape test (`".." not in img["uri"].split("/")`), tying the test explicitly to the T-50-01 threat-model row's stated mitigation that the escaping URI's key never carries a parent segment through to `copy_image_files()`.
- The `50-BRANCH-EVIDENCE.md` SC#3 audit reports a second, plan-undisclosed deviation from `50-VALIDATION.md`'s literal D-11 command sequence (the `.doctrees/`-exclusion) alongside the one the acceptance criteria name (`--extra docs`) — both are already investigated and justified in wave 2's own `50-D11-EVIDENCE.md`, so this is a completeness choice in the audit's own reporting, not a new finding.

## Deviations from Plan

None — plan executed exactly as written. No `must_haves` truth, artifact, or prohibition was violated; the two decisions above are additions within the plan's own stated discretion (T-50-01's mitigation-test framing; the audit's own instruction to disclose deviations "rather than silently accepted").

## Issues Encountered

None. The worktree environment provisioned cleanly (`unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT && uv sync --extra dev`), and every command ran via `uv run` without incident. `ruff check .` is unrunnable on this NixOS host (a pre-existing, filed toolchain limitation, not an issue introduced by this plan) — recorded verbatim in `50-BRANCH-EVIDENCE.md` per Phase 45.2's precedent, with CI taken as lint authority.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

Phase 50's three success criteria (IMG-01/IMG-02 branch coverage, no collateral change to ordinary images) are all discharged against named artifacts and commands in `50-BRANCH-EVIDENCE.md` § 5. The D-12 fixed points hold byte-unchanged across the whole phase. Full suite: 1156 passed, 5 skipped (0 new failures against the stated 1152-passed pre-phase baseline). `black --check .` and `mypy typsphinx/` both clean; `ruff check .` unrunnable on this host, lint authority taken from CI. No open items are carried forward by this plan specifically — the phase's own next action (verification/UAT) can proceed on this evidence.

## Self-Check: PASSED

Confirmed on disk: `tests/test_builder.py` (4 new tests present, both D-12-pinned tests unedited), `.planning/phases/50-pr-131-image-path-defects/50-BRANCH-EVIDENCE.md`, this SUMMARY. Both task commits confirmed present in `git log`: `7dd50ecd` (test(50-03): cover IMG-01/IMG-02 relocation branches), `8f7776e5` (docs(50-03): audit phase 50's evidence chain, close the gates).

---
*Phase: 50-pr-131-image-path-defects*
*Completed: 2026-08-14*
