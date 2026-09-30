---
phase: 17-rendering-fidelity-audit
plan: 04
subsystem: docs
tags: [requirements, audit-catalogue, backlog-generation, rendering-fidelity, typst-table]

# Dependency graph
requires:
  - phase: 17-rendering-fidelity-audit (17-03)
    provides: human-confirmed, severity-final `17-AUDIT-CATALOGUE.md` (14 accepted rows: 1 high [F12], 11 medium, 2 low; 1 rejected [F4])
provides:
  - "FID-01a: the sole high-severity root-cause requirement (F12, table/tgroup wide-table overflow) appended to REQUIREMENTS.md, ready for Phase 18 to consume as a handler-level fix + real-compile regression fixture"
  - "A single medium/low pointer under REQUIREMENTS.md Future Requirements, referencing the catalogue's 13 medium/low findings without enumerating them as requirements"
  - "17-AUDIT-CATALOGUE.md finalized: Root-cause groups (D-10) section + Validation (five mechanical checks) section, all recorded PASS"
affects: [phase-18-fidelity-fixes]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Root-cause grouping (D-10): one FID-01x per (node-kind, failure-mode) group, not per occurrence — occurrences listed inside the single requirement entry"
    - "Fresh-build re-verification pattern: reuse tests/test_corpus_gate.py's unmodified helpers (get_or_clone_corpus + wire_typsphinx_into_corpus_conf + _run_corpus_sphinx_build) to produce a persistent fresh build for both SC#1's include()-walk and D-07's provenance freshness check in one pass"

key-files:
  created: []
  modified:
    - .planning/REQUIREMENTS.md
    - .planning/phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md

key-decisions:
  - "Confirmed the severity tally independently before appending (1 high [F12], 2 low [F8,F10], 11 medium) — matched the plan's stated expectation exactly, so exactly one FID-01x (FID-01a) was assigned."
  - "Recorded F6 (medium, inline-literal right-margin clip) as a kinship note alongside FID-01a's root-cause group, without promoting it to FID-01x — same overflow symptom family as F12 but a different node kind (literal vs. table/tgroup), so it stays medium per D-08/D-11."
  - "Committed Task 1 (REQUIREMENTS.md append + catalogue root-cause grouping) and Task 2 (catalogue Validation section) as two separate atomic commits by reconstructing an intermediate catalogue state, rather than one combined commit — see Deviations."
  - "D-07 freshness check ran genuinely (not environmentally limited) this session: pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow passed, and a separate fresh rebuild's index.pdf matched the provenance header byte-for-byte (15,153,646 bytes), unknown_visit catalogue empty."

requirements-completed: [AUD-01]

coverage:
  - id: D1
    description: "FID-01a appended to REQUIREMENTS.md as the sole high-severity root-cause requirement (F12: table/tgroup wide-table column collision + right-margin clip), with occurrence pages and a Phase 18 fixture pointer"
    requirement: "AUD-01"
    verification:
      - kind: other
        ref: "python -c \"import re; r=open('.planning/REQUIREMENTS.md').read(); ids=sorted(set(re.findall(r'FID-01[a-z]+', r))); assert all(x in r for x in ['TODO-01','MAN-01','LEN-01','AUD-01','FID-01','GATE-03','DEG-03','XREF-02','CFG-01'])\" (plan's Task 1 automated verify)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Single medium/low pointer added under REQUIREMENTS.md Future Requirements, referencing 17-AUDIT-CATALOGUE.md's 13 medium/low findings (F1,F2,F3,F5,F6,F7,F8,F9,F10,F11,F13,F14,F15) without enumerating them individually"
    requirement: "AUD-01"
    verification:
      - kind: other
        ref: "grep -A2 'Rendering fidelity backlog (medium/low)' .planning/REQUIREMENTS.md"
        status: pass
    human_judgment: false
  - id: D3
    description: "17-AUDIT-CATALOGUE.md finalized with a Root-cause groups (D-10) section and a Validation section recording all five mechanical consistency checks as PASS"
    requirement: "AUD-01"
    verification:
      - kind: other
        ref: "test -z \"$(git status --porcelain | grep -E '\\.(png|pdf)$')\" && grep -qi Validation .planning/phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md (plan's Task 2 automated verify)"
        status: pass
      - kind: integration
        ref: "pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -q"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-07-19
status: complete
---

# Phase 17 Plan 4: Backlog Generation + Mechanical Validation Summary

**Grouped the human-confirmed catalogue's single high-severity finding (F12, wide-table overflow) into `FID-01a`, appended it plus a medium/low pointer to REQUIREMENTS.md, and passed all five mechanical consistency checks against a freshly rebuilt corpus.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-07-19 (following 17-03 COMPLETE)
- **Completed:** 2026-07-19T12:41:00Z
- **Tasks:** 2 completed
- **Files modified:** 2 (`REQUIREMENTS.md`, `17-AUDIT-CATALOGUE.md`)

## Accomplishments

- Independently re-confirmed the catalogue's severity tally from the active Issue Table (14 accepted rows: 1 high [F12], 2 low [F8, F10], 11 medium) before grouping — matched the human-confirmed state exactly.
- Added a "Root-cause groups (D-10)" section to the catalogue: exactly one high-severity root-cause group (F12, `table`/`tgroup` wide-table column collision + right-margin clip), with a deterministic-ordering note and a non-binding kinship note pointing to the related-but-distinct medium finding F6.
- Appended `FID-01a` under REQUIREMENTS.md's "Rendering Fidelity Audit" section (scoped `Edit`, additive-only) — root cause, occurrence pages (`extdev/deprecated` pp.239,240,241), and a Phase 18 fixture pointer to the multi-page "Deprecated APIs" grid table, contrasted against the narrow `extdev/appapi` tables that render fine.
- Added a single medium/low pointer entry under REQUIREMENTS.md's "Future Requirements" section, referencing the 13 medium/low findings recorded in the catalogue rather than enumerating them.
- Ran and recorded all five RESEARCH Validation Architecture mechanical checks in a new catalogue "Validation" section, all PASS, against a fresh corpus rebuild (not stale artifacts).
- Confirmed all nine pre-existing requirement IDs (TODO-01, MAN-01, LEN-01, AUD-01, FID-01, GATE-03, DEG-03, XREF-02, CFG-01) are byte-for-byte unchanged.

## Task Commits

Each task was committed atomically:

1. **Task 1: Group high-severity rows by root cause and append FID-01a to REQUIREMENTS.md** - `d360c25` (docs)
2. **Task 2: Run the five mechanical consistency checks and record outcomes** - `793074d` (docs)

**Plan metadata:** commit hash recorded after this SUMMARY is committed (see completion report).

## Files Created/Modified

- `.planning/REQUIREMENTS.md` — Appended `FID-01a` under "Rendering Fidelity Audit" (root cause, occurrences, Phase 18 fixture pointer); added a single medium/low pointer under "Future Requirements". Nine pre-existing requirement IDs unchanged.
- `.planning/phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md` — Added "Root-cause groups (D-10)" section (grouping table + kinship note) and "Validation (Plan 17-04 mechanical checks)" section (all five checks + a bonus artifact-hygiene check, all PASS); updated the top status line to reflect Plan 17-04 completion.

## Decisions Made

- Confirmed the severity tally (1 high, 2 low, 11 medium = 14 accepted) directly from the catalogue's active Issue Table before grouping, rather than trusting the plan prompt's stated expectation blindly — it matched exactly, so exactly one `FID-01x` (`FID-01a`) was the correct output.
- Kept F6 (medium, inline-literal right-margin clip) out of the FID-01 backlog despite its symptom-family kinship to F12 (both are right-edge overflow), because it is a different node kind (`literal` inline run vs. `table`/`tgroup`) — recorded the kinship as a non-binding awareness note for Phase 18's planner instead of merging or promoting it.
- Ran a fresh corpus rebuild (reusing `tests/test_corpus_gate.py`'s unmodified helpers) rather than relying on stale scratch artifacts from prior sessions, to satisfy both SC#1's "fresh recursive `#include()` walk" requirement and D-07's freshness check from a single build.
- Scoped the SC#3 grep to the active Issue Table only (not the "Excluded (out-of-scope)"/"Rejected candidates" sections), per the plan's explicit note that an unscoped grep would self-invalidate against the catalogue's own out-of-scope documentation.
- Scoped the SC#4 `FID-01[a-z]` count to actual `- [ ] **FID-01<letter>**` checkbox lines, not the pre-existing narrative mentions of "`FID-01a`, `FID-01b`, …" inside FID-01's own template description and the Coverage/Phase-mapping prose (those are placeholder text describing the future append pattern, not appended entries).

## Deviations from Plan

### Auto-fixed Issues

**1. [Process — atomic per-task commits] Reconstructed an intermediate catalogue state to split Task 1 and Task 2 into separate commits**
- **Found during:** Task 2 (writing the Validation section)
- **Issue:** Both tasks' catalogue edits (Root-cause groups section for Task 1, status-line update + Validation section for Task 2) were made in the same working-tree session without an intermediate commit. Because both insertions landed adjacent to each other in the file (no unchanged lines between them), a single `git diff` on the finished file collapsed them into one hunk, which would have made `git add -p` splitting error-prone.
- **Fix:** Reconstructed a clean "Task 1 only" version of the catalogue from `git show HEAD:...` (the pre-plan state) plus just the Root-cause-groups block, wrote it to disk, staged, and committed. Then re-applied the status-line update and Validation section on top for Task 2's commit. This preserved the task_commit_protocol's atomicity guarantee (one commit per task, each independently `git log`-verifiable) despite the shared-file editing sequence.
- **Files modified:** `.planning/phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md` (both commits), `.planning/REQUIREMENTS.md` (Task 1 commit only)
- **Verification:** `git diff --stat` between the two commits confirms Task 1's commit touches only the Root-cause-groups block + REQUIREMENTS.md; Task 2's commit touches only the status-line rewrite + Validation section.
- **Committed in:** `d360c25` (Task 1), `793074d` (Task 2)

---

**Total deviations:** 1 auto-fixed (process/commit-splitting, no content change)
**Impact on plan:** Purely a git-history hygiene fix to honor per-task atomic commits; no scope creep, no content deviation from the plan's specified append/validation work.

## Issues Encountered

None. The NixOS sandbox's documented ELF-exec limitation (project memory `nixos-sandbox-test-env.md`) did NOT manifest this session — `pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -q` ran a real `typst.compile()` end-to-end and passed genuinely, so the D-07 check is a true PASS, not an environmentally-limited one.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

Phase 17 (`AUD-01`) is now fully complete: the catalogue is human-confirmed, severity-final, root-cause-grouped, and validated by all five mechanical checks. Phase 18 can start directly from `.planning/REQUIREMENTS.md`'s `FID-01a` entry (root cause, occurrence pages, and a minimal-repro/fixture pointer to the `extdev/deprecated` grid table are all present) — no further audit or backlog-generation work is needed before Phase 18 planning begins. No blockers.

---
*Phase: 17-rendering-fidelity-audit*
*Completed: 2026-07-19*

## Self-Check: PASSED

- FOUND: `.planning/phases/17-rendering-fidelity-audit/17-04-SUMMARY.md`
- FOUND: commit `d360c25` (Task 1)
- FOUND: commit `793074d` (Task 2)
