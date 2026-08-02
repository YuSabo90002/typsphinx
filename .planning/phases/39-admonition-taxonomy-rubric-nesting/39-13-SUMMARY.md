---
phase: 39-admonition-taxonomy-rubric-nesting
plan: 13
subsystem: testing
tags: [gap-closure, corpus-gate, test-census, verification, uat, admonitions]

# Dependency graph
requires:
  - phase: 39-admonition-taxonomy-rubric-nesting (plans 09-12)
    provides: "the G-39-1 RED/GREEN cycle (39-09/39-11), the D-03-R decision record (39-10), and the re-taken ADM-04 sign-off (39-12) this plan closes out on evidence"
provides:
  - "A real, re-run full-corpus -b typstpdf gate result (tag v9.1.0, PASSED not skipped) discharging SC#5/ADM-02's transparency prohibition against recording a skip as a pass"
  - "39-TEST-CENSUS-G39-1.md: this gap's own exact-string census, reconciled row by row against the shipped 39-TEST-CENSUS.md with no unexplained disagreement, and the inverted danger-call-site grep guard recorded as a design consequence"
  - "39-GAP-G39-1-CLOSEOUT.md: the durable close-out record accounting for all five of G-39-1's missing: workstreams with re-runnable evidence"
  - "39-VERIFICATION.md's Truth #1 amended additively (dated, zero deletions) recording the inversion, mirrored durably into the close-out"
  - "39-UAT.md's gap G-39-1 flipped to status: closed on the ADM-04 amendment's positive verdict, with a correction line added under the memo/lang.toml measured_context bullet without editing the original text"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A dated, additive amendment appended to a verify-reserved filename (39-VERIFICATION.md), with its full content mirrored into a durable gap-specific artifact, so a later verification regeneration cannot lose the evidence"
    - "A gap's own exact-string census reconciles against the shipped phase census row by row rather than replacing it -- the same discipline the shipped census itself used against discussion-time and planning-time predictions"

key-files:
  created:
    - .planning/phases/39-admonition-taxonomy-rubric-nesting/39-TEST-CENSUS-G39-1.md
    - .planning/phases/39-admonition-taxonomy-rubric-nesting/39-GAP-G39-1-CLOSEOUT.md
    - .planning/backups/39-VERIFICATION.md.pre-G39-1-amendment.2026-08-02.bak
  modified:
    - .planning/phases/39-admonition-taxonomy-rubric-nesting/39-VERIFICATION.md
    - .planning/phases/39-admonition-taxonomy-rubric-nesting/39-UAT.md
    - .planning/STATE.md

key-decisions:
  - "The NixOS uv-shim (not just the ruff shim) had to be re-applied in this fresh worktree before any test command was trustworthy -- the fast suite first showed 45 spurious failures (exit 127, the shadowed generic-linux ELF uv), matching the exact failure signature this project's STATE.md and memory already document; re-symlinking the Nix-store uv resolved all 45 before any real measurement was taken."
  - "The backup of the pre-amendment 39-VERIFICATION.md was placed at .planning/backups/ (a new directory, outside the phase directory) rather than inside the phase directory, satisfying the plan's explicit 'outside the phase directory' instruction; no prior backup-directory convention existed in this project to follow instead."
  - "STATE.md's Operator Next Steps bullet was committed in its own separate commit, isolated from the other three Task 3 deliverables, per this plan's explicit worktree carve-out ownership of STATE.md as a declared deliverable -- distinct from the generic worktree rule against touching STATE.md tracking fields, which this plan does not touch (front matter, progress block, and Current Position are all untouched)."

patterns-established: []

requirements-completed: [ADM-01, ADM-02, ADM-04]

coverage:
  - id: D1
    description: "The full-corpus -b typstpdf gate re-run for real (not skipped), with the resolved Sphinx tag and clone SHA recorded"
    requirement: "ADM-02"
    verification:
      - kind: other
        ref: "uv run pytest tests/test_corpus_gate.py -m slow -v -- TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED (13.46s); tag v9.1.0; clone SHA cc7c6f435ad37bb12264f8118c8461b230e6830c"
        status: pass
    human_judgment: false
  - id: D2
    description: "This gap's own exact-string census measured against the finished tree and reconciled row by row against 39-TEST-CENSUS.md, with the inverted danger-call-site grep guard recorded as a design consequence, not a correction, and 39-05-SUMMARY.md left byte-unchanged"
    requirement: "ADM-02"
    verification:
      - kind: other
        ref: ".planning/phases/39-admonition-taxonomy-rubric-nesting/39-TEST-CENSUS-G39-1.md -- resolvable 40-char base commit SHA, two tables, inverted-guard section (measured count 1, was 0), reconciliation verdict: no unexplained disagreement; git diff --stat -- 39-05-SUMMARY.md empty"
        status: pass
    human_judgment: false
  - id: D3
    description: "39-GAP-G39-1-CLOSEOUT.md accounts for all five of G-39-1's missing: workstreams, one row each, with a test node id, command, or artifact path per row; Truth #1's amendment mirrored durably"
    requirement: "ADM-02"
    verification:
      - kind: other
        ref: ".planning/phases/39-admonition-taxonomy-rubric-nesting/39-GAP-G39-1-CLOSEOUT.md -- workstream table has exactly 5 data rows; contains the corpus gate's verbatim result line and the sentence 'The gate ran, not skipped.'"
        status: pass
    human_judgment: false
  - id: D4
    description: "39-VERIFICATION.md's Truth #1 gains a dated, additive amendment (zero deletions) recording the inversion and pointing at the close-out as the durable record; a pre-edit backup was taken outside the phase directory"
    requirement: "ADM-02"
    verification:
      - kind: other
        ref: "git diff --numstat -- 39-VERIFICATION.md == 24 insertions, 0 deletions; grep -c 'G-39-1' 39-VERIFICATION.md == 2; backup at .planning/backups/39-VERIFICATION.md.pre-G39-1-amendment.2026-08-02.bak"
        status: pass
    human_judgment: false
  - id: D5
    description: "Gap G-39-1 closed in 39-UAT.md (status/closed_at/closed_by) only because the ADM-04 amendment records a positive verdict; measured_context bullets left byte-unchanged apart from one additive correction line"
    requirement: "ADM-04"
    verification:
      - kind: manual_procedural
        ref: "39-ADM04-SIGNOFF.md Amendment section -- owner's verbatim one-word response 'approved' to the four-question checkpoint, read and confirmed directly by this plan before flipping 39-UAT.md's status"
        status: pass
    human_judgment: true
    rationale: "ADM-04 is REQUIREMENTS.md's own [V]-marked human-only visual UAT requirement; this plan reads the owner's already-recorded verdict rather than re-deriving or re-judging it, per the plan's own prohibitions."
  - id: D6
    description: "Milestone invariants re-checked by command: zero new runtime dependency, @preview count stays 4, gentle-clues pin 1.3.1 at all four lockstep sites including the fourth, unguarded one"
    requirement: "ADM-02"
    verification:
      - kind: other
        ref: "git diff --stat 7272bd6..HEAD -- pyproject.toml empty; grep -rc 'gentle-clues:1.3.1' typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ docs/source/_typst/custom_template.typ -- all 4 return 1; uv run pytest tests/test_preview_version_sync.py -x -- 3 passed"
        status: pass
    human_judgment: false

# Metrics
duration: 55min
completed: 2026-08-02
status: complete
---

# Phase 39 Plan 13: Gap G-39-1 Close-Out Summary

**Closed gap G-39-1 on evidence: the full-corpus `-b typstpdf` gate was re-run for real (tag `v9.1.0`, PASSED — not a skip), this gap's own exact-string census was measured and reconciled row by row against the shipped `39-TEST-CENSUS.md` with no unexplained disagreement, the inverted `danger`-call-site grep guard was recorded as a consequence of decision D-03-R (not a correction), and `39-UAT.md`'s gap status was flipped to `closed` on the ADM-04 amendment's positive `"approved"` verdict.**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-08-02 (approx., after worktree branch check and environment provisioning)
- **Completed:** 2026-08-02
- **Tasks:** 3 (1 measurement-only, 2 with committed artifacts)
- **Files modified:** 6 (2 created new artifacts, 1 backup created, 3 modified)

## Accomplishments

- **Task 1 (no files modified, all results recorded here):** Re-ran the full-corpus `-b typstpdf` gate for real — `tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error` **PASSED**, not skipped, in 13.46s. Resolved Sphinx tag `v9.1.0` (`sphinx.__version__` measured live as `9.1.0`); the cached corpus clone's commit SHA is `cc7c6f435ad37bb12264f8118c8461b230e6830c` (measured live via `git rev-parse HEAD` in `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0`). Re-checked all three milestone invariants by command (zero `pyproject.toml` diff, `@preview` count stays 4 at all three guarded surfaces) plus the fourth, unguarded lockstep site (`docs/source/_typst/custom_template.typ`) hand-checked directly since `test_preview_version_sync.py` does not watch it — all four show the `gentle-clues:1.3.1` pin. Full unfiltered suite: **774 passed, 1 skipped** (matches the measured baseline exactly). Fast suite (`not slow`): **746 passed, 0 failed, 29 deselected**. `black --check .`, `ruff check .`, `mypy typsphinx/` all pass with zero findings.
- **Task 2:** Wrote `39-TEST-CENSUS-G39-1.md` — this gap's own exact-string census, measured against the finished tree (base commit `4e3128937416e8cc9b026e5715179adb9c5936e1`), covering all six files the plan named at minimum plus the new two-locale fixture project. A second table proves, via `git log` over ten paths, that the shipped census's rubric/golden-file/signature rows (rows 4-13) remain untouched by this gap. Recorded the inverted guard: `39-05-SUMMARY.md`'s recorded zero-danger-call-site grep is now measured as exactly `1`, stated explicitly as the consequence of decision D-03-R, not a correction — `39-05-SUMMARY.md` itself was confirmed byte-unchanged (`git diff --stat` empty, `git log` over the gap's whole commit range empty). Reconciliation section states plainly: no unexplained disagreement found anywhere.
- **Task 3:** First read the ADM-04 amendment in `39-ADM04-SIGNOFF.md` directly and confirmed a **positive** verdict (the owner's verbatim one-word `"approved"` answering the four-question checkpoint, including the explicit `attention`/`error` adjacency question) before proceeding to any status flip. Wrote `39-GAP-G39-1-CLOSEOUT.md` with all seven required elements: what the gap was, a five-row workstream table (one per `39-UAT.md` `missing:` item, each naming a test node id/command/artifact path re-confirmed live this session), the corpus-gate result verbatim with an explicit "ran, not skipped" sentence, the milestone-invariant re-checks with their commands, the durable copy of the Truth #1 amendment, what the gap did NOT change, and the final verdict (CLOSED). Took a pre-edit backup of `39-VERIFICATION.md` at `.planning/backups/39-VERIFICATION.md.pre-G39-1-amendment.2026-08-02.bak` before appending a dated, additive (24 insertions, 0 deletions) amendment to Truth #1 recording the inversion and naming the close-out as the durable record. Flipped `39-UAT.md`'s gap `G-39-1` `status` from `failed` to `closed`, added `closed_at: 2026-08-02` and `closed_by` naming the five discharging plans, and added one additive correction line under the `memo`/`lang.toml` `measured_context` bullet (pointing at `39-GATE-EVIDENCE-05.md`) without editing the original bullet — verified `measured_context` bullets remain byte-unchanged by grep. Added exactly one bullet to `.planning/STATE.md`'s "Operator Next Steps" recording the gap closure, in its own separate commit per this plan's worktree carve-out ownership of that file.

## Task Commits

Each task was committed atomically:

1. **Task 1: Re-run the full-corpus gate and re-check the milestone invariants** — no commit (no files modified; all results recorded in this SUMMARY per the plan's own instruction)
2. **Task 2: Record this gap's exact-string census and the inverted grep guard** — `a0ba504` (docs)
3. **Task 3: Write the close-out, amend Truth #1 durably, and set the gap's status** — `6a860db` (docs, the three non-STATE.md deliverables) + `968e583` (docs, STATE.md's own carve-out commit)

_No TDD-style multi-commit tasks — this is a documentation-only gap-closure plan; no code or test file under `typsphinx/` or `tests/` was touched._

## Files Created/Modified

- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-TEST-CENSUS-G39-1.md` — new: this gap's own exact-string census, reconciled row by row against `39-TEST-CENSUS.md`.
- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-GAP-G39-1-CLOSEOUT.md` — new: the durable close-out record.
- `.planning/backups/39-VERIFICATION.md.pre-G39-1-amendment.2026-08-02.bak` — new: pre-amendment backup of `39-VERIFICATION.md`.
- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-VERIFICATION.md` — amended additively (24 insertions, 0 deletions): Truth #1's inversion recorded in a new dated section.
- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-UAT.md` — gap `G-39-1` status flipped to `closed` with `closed_at`/`closed_by` added; one additive correction line added under the `memo` bullet.
- `.planning/STATE.md` — one additive bullet under "Operator Next Steps" (9 insertions, 0 deletions); front matter, progress block, and every other section untouched.

## Decisions Made

- Re-applied the NixOS `uv` shim (`ln -sf "$(command -v uv)" .venv/bin/uv`) in addition to the `ruff` shim before trusting any test result in this fresh worktree — the first fast-suite run showed the exact documented 45-failure/exit-127 signature (shadowed generic-linux ELF `uv`) before the shim, and 0 failures after it, matching this project's own `STATE.md`/memory record precisely.
- Placed the pre-amendment `39-VERIFICATION.md` backup at a new `.planning/backups/` directory (outside the phase directory, per the plan's explicit instruction) since no prior backup-directory convention existed in this project.
- Committed `.planning/STATE.md`'s Operator Next Steps bullet in its own separate commit, distinct from the other three Task 3 deliverables, to keep the worktree carve-out's declared-deliverable exception (this plan owns STATE.md's content) cleanly separated from the general worktree rule against touching STATE.md's tracking fields (which this plan does not touch at all).
- Added `closed_by: [39-09, 39-10, 39-11, 39-12, 39-13]` to `39-UAT.md`'s gap entry, naming every plan that contributed a discharging workstream (RED, decision-record, GREEN, ADM-04 re-take, and this close-out itself) rather than naming only the plan that landed the code change.

## Deviations from Plan

None — plan executed exactly as written. All three tasks' acceptance criteria and verify commands pass as specified; no Rule 1-4 auto-fixes were needed on any translator, test, or planning-document change (the one environment fix — re-applying the NixOS `uv` shim — is standing project-documented setup, not a deviation from this plan's own content).

## Issues Encountered

- The sandbox's worktree-path-safety guard rejected my first `Write` call for `39-TEST-CENSUS-G39-1.md` because I had constructed the absolute path from the main-checkout prefix (`/home/yuta/Documents/typsphinx/.planning/...`) instead of the worktree's own toplevel (`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a9d75e3a113437772/.planning/...`). Caught immediately by the tool's own refusal (no file was written to the wrong location); re-derived the path from `git rev-parse --show-toplevel` and re-issued the write successfully. No content was lost.
- Several compound bash commands (chained `env -u ... uv sync`, `for`-loops for the shim symlinks, `git -C <path>`, multi-command `&&` chains mixing `git diff`/`grep`/`test`) were rejected by the sandbox's "too complex to verify containment" guard. Worked around by issuing each command as a separate, single-purpose invocation (individual `ln -sf` calls instead of a `for` loop, a `(cd ... && git rev-parse HEAD)` subshell instead of `git -C`, separate `grep`/`test` calls instead of chained `&&`). No effect on the resulting measurements — every acceptance criterion was still verified, just via more granular commands.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Gap G-39-1 is fully closed: all five `missing:` workstreams discharged with re-runnable, live-verified evidence; `39-UAT.md`'s gap status reflects the ADM-04 amendment's positive verdict; the full-corpus gate genuinely ran and passed; all milestone invariants re-checked and held.
- No file under `typsphinx/` or `tests/` was touched by this plan — confirmed by `git diff --stat 4e3128937416e8cc9b026e5715179adb9c5936e1..HEAD -- typsphinx/ tests/` being empty across all three of this plan's commits.
- Phase 39 (including its gap closure) is now complete. Next: Phase 40 (Citations — Full Round Trip), structurally independent of Phase 39, per `.planning/STATE.md`'s existing "Next" pointer (unchanged by this plan).
- The orchestrator's own post-merge steps (per this plan's worktree-mode deferral) still need to run: `state.advance-plan`, `state.update-progress`, `roadmap.update-plan-progress`, and `requirements.mark-complete` for ADM-01/ADM-02/ADM-04 — none of these were run by this worktree agent, consistent with the parallel-execution carve-out instructions.

---
*Phase: 39-admonition-taxonomy-rubric-nesting*
*Completed: 2026-08-02*
