---
phase: 68-documentation-follow-through-claude-md-tox-ini-flake-nix
verified: 2026-09-13T00:00:00Z
status: passed
score: 9/9 must-haves verified
covered_files:
  - ".planning/REQUIREMENTS.md"
  - ".planning/ROADMAP.md"
  - ".planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-01-PLAN.md"
  - ".planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-01-SUMMARY.md"
  - ".planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-02-PLAN.md"
  - ".planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-02-SUMMARY.md"
  - ".planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-03-PLAN.md"
  - ".planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-03-SUMMARY.md"
  - ".planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-04-PLAN.md"
  - ".planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-04-SUMMARY.md"
  - ".planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-CLAUDEMD-EVIDENCE.md"
  - ".planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-CLOSURE-EVIDENCE.md"
  - ".planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-CONTEXT.md"
  - ".planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-FLAKE-EVIDENCE.md"
  - ".planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-REVIEW.md"
  - ".planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-TOX-EVIDENCE.md"
  - "CLAUDE.md"
  - "flake.nix"
  - "tests/test_pdf_render_gate.py"
  - "tests/test_toolchain_config_gate.py"
  - "tox.ini"
covered_digest: "v1:sha256:7a6e105beff2d0e857ff8150dcf5f90636689f08be1a8eccd3d1f8439da41b16"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 68: Documentation Follow-Through — `CLAUDE.md`, `tox.ini`, `flake.nix` — Verification Report

**Phase Goal:** The three documentation surfaces (`CLAUDE.md`, `tox.ini`'s `requires` rationale
comment, `flake.nix`'s notes) describe the mechanism that actually landed in Phases 64 and 65, not
the one that was planned.
**Verified:** 2026-09-13
**Status:** passed
**Re-verification:** No — initial verification

## Independent Re-Measurement Summary

All measurements below were re-run by the verifier directly against the merged tree at HEAD
(`gsd/v0.9.3-toolchain-and-dependency-update-repair`), not copied from SUMMARY.md/EVIDENCE.md
prose:

| Check | Command | Result | Matches evidence? |
|---|---|---|---|
| Full suite | `uv run pytest -q` | 1547 passed, 1 skipped, 0 failed | Yes — matches orchestrator's post-merge baseline note |
| Collected count | `uv run pytest --collect-only -q` | 1548 tests collected | Confirms the wave-1 plans' non-anchored re-measurement (1548 before/after); the documented sed-anchor defect (orchestrator note 3) does not affect the substantive invariant |
| Target tests | `uv run pytest tests/test_toolchain_config_gate.py tests/test_pdf_render_gate.py -q` | 35 passed | Both D-13/D-14-touched files green |
| Format | `uv run black --check .` | clean, 355 files unchanged | Yes |
| Lint | `uv run ruff check .` | All checks passed | Yes |
| Types | `uv run mypy typsphinx/` | no issues, 9 files | Yes |
| tox requires read-back | `uv run tox config -e py312 --core -k requires` | `tox-uv~=1.35` | Yes |
| Diff scope (excl. `.planning/`) | `git diff --name-only 0bd33617 HEAD -- . ':!.planning'` | `CLAUDE.md`, `flake.nix`, `tests/test_pdf_render_gate.py`, `tests/test_toolchain_config_gate.py`, `tox.ini` | Yes — exactly the 5 declared edit targets, nothing more |
| `nix flake check` | `nix flake check --all-systems --no-build` | all checks passed | Yes |
| Derivation identity (4 systems) | `nix eval --raw ".#devShells.<sys>.default.drvPath"` for x86_64-linux, aarch64-linux, x86_64-darwin, aarch64-darwin | all 4 byte-identical to `DRV_BEFORE_*`/`DRV_AFTER_*` in `68-FLAKE-EVIDENCE.md` | Yes — verifier-obtained values are byte-identical to both the plan's before and after values |
| `git log -S "ln -sf"` / `-S patchelf` on `CLAUDE.md` | `git log --oneline -S ... -- CLAUDE.md` | exactly 1 commit each, `322b8a4f` — the phase's own wave-1 commit that introduces the new negative sentence | Confirms D-02's vacuity claim: no pre-existing manual-step guidance existed anywhere in `CLAUDE.md`'s history before this phase |
| `tox-uv-bare` repo-wide grep | `git grep -n tox-uv-bare -- ':!.planning' ':!uv.lock'` | 25 hits, all historical (C1) or gate-forbidden-value citations (C2); zero "rationale presented as current" (C3) | Yes — independently re-classified by the verifier, matches `68-CLOSURE-EVIDENCE.md`'s D-15 table |
| Debt markers | `grep -nE 'TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER'` across the 5 edited files | Only `TODO-01` (a pre-existing, unrelated requirement ID in `test_pdf_render_gate.py`, untouched by this phase) | No unresolved debt marker introduced by this phase |

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | SC#1 literal reading — clauses (a),(b),(c),(e),(f) | ✓ VERIFIED | See table below. Clause (d) is the one clause the AMENDED block was written to correct. |
| 1b | SC#1 literal reading — clause (d) "unaffected and unassisted by `flake.nix`" | ✗ CONTRADICTED BY DESIGN | Verified false on this NixOS machine (NIX-05, Phase 64); this is the expected, owner-approved outcome — see amended reading below, D-01 |
| 1c | SC#1 amended reading (D-01) — recipe unchanged/mandatory, `flake.nix` does not substitute, recipe runs through shims on NixOS, shims arrive by PATH inheritance not direnv | ✓ VERIFIED | `CLAUDE.md:100` boundary paragraph states all four elements verbatim; recipe-tail hash equality confirmed independently (see below); ROADMAP AMENDED block present at `ROADMAP.md:646-658` |
| 2 | D-02: manual `ln -sf`/`patchelf` guidance retirement is vacuously satisfied and evidenced | ✓ VERIFIED | `git log -S` on both terms against `CLAUDE.md` returns exactly one commit each — the phase's own wave-1 commit adding the negative sentence; zero pre-existing commits |
| 3 | D-04..D-08: CLAUDE.md's `### NixOS development shell` subsection and line 11 / Conventions bullet describe the landed mechanism (7 shims, FHS sandbox, exit-127, `uv` two-leg fallback, launch prerequisite + check, locale, interpreter caution, rationale pointer) | ✓ VERIFIED | `CLAUDE.md:11,77,80-94` read directly; content matches D-04..D-08 verbatim; no dotted version number in the interpreters sentence; "Do not simplify it back to tox-uv" instruction is gone (`grep simplify` → no hits) |
| 4 | Worktree provisioning recipe stays byte-identical (D-01/D-03) | ✓ VERIFIED | `68-CLOSURE-EVIDENCE.md` records matching SHA-256 (`2c39540d...`) for the recipe-tail block before/after; text of `CLAUDE.md:102-114` matches the pre-phase recipe verbatim on inspection |
| 5 | SC#2 / DOC-20: `tox.ini`'s `requires` rationale comment describes the current `tox-uv~=1.35` pin, keeps the `~=` ini-parser constraint in full, and states why `tox-uv` is safe now | ✓ VERIFIED | `tox.ini:4-17` read directly; content matches D-16; `tox config -e py312 --core -k requires` prints `tox-uv~=1.35` (comments never parsed, confirmed independently) |
| 6 | SC#2: repository-wide grep finds no surviving `tox-uv-bare` rationale presented as current | ✓ VERIFIED | Independently re-ran `git grep -n tox-uv-bare -- ':!.planning' ':!uv.lock'`; all 25 hits classified — 14 historical (C1), 11 gate-forbidden-value citations (C2), 0 rationale-as-current (C3) |
| 7 | D-13/D-14: the two test files' stale prose is rewritten to the post-Phase-68 state, text only, assertion logic untouched | ✓ VERIFIED | `tests/test_toolchain_config_gate.py:302-305,366-369` and `tests/test_pdf_render_gate.py:167-171` read directly and match D-13/D-14; both files pass (`35 passed`); suite-wide pass count unchanged (1547 passed / 1 skipped, matching pre-phase baseline) |
| 8 | SC#3 / DOC-21: `flake.nix` header explains the FHS wrapper + 2 falsified alternatives, which commands are shimmed and why (namespace inheritance), and the darwin guard (unverified by construction, no CI lane, report directly); per-element notes restated; no decision IDs, no phase-relative phrasing; archival-stable citations | ✓ VERIFIED | `flake.nix:8-46` read directly and matches D-09..D-12 verbatim; `grep -nE 'D-[0-9]' flake.nix` → no output; citations use "v0.9.3 Phase NN, `FILE.md`" form throughout |
| 9 | SC#3: comment-only edit — derivation identity preserved on all 4 systems, `nix flake check` exits 0 | ✓ VERIFIED | Verifier independently ran `nix eval --raw` for all 4 systems; all 4 drvPaths byte-identical to `68-FLAKE-EVIDENCE.md`'s `DRV_BEFORE_*`/`DRV_AFTER_*` values; `nix flake check --all-systems --no-build` exits 0 |

**Score:** 9/9 truths verified (SC#1's clause (d) is reported as a distinct, by-design "contradicted"
sub-finding rather than a phase failure — see below).

### SC#1: Literal vs. Amended Reading (reported separately per D-01, Phase 65 D-01 precedent)

| Clause | Text | Verdict |
|---|---|---|
| (a) manual `ln -sf`/`patchelf` guidance gone, retired not conditional | "The manual `ln -sf` / `patchelf` guidance is gone" | MET (vacuously — never existed; see truth #2) |
| (b) section describes what Phase 64 actually landed | — | MET (`### NixOS development shell` subsection) |
| (c) executors keep using the unchanged recipe | — | MET (byte-identical hash) |
| (d) executors "unaffected and unassisted by `flake.nix`" | — | **CONTRADICTED BY MEASUREMENT, BY DESIGN.** NIX-05 (Phase 64) proved a fresh worktree's `.venv` runs on a generic-linux CPython that NixOS refuses outside FHS, so `uv run` in a worktree depends on the `uv` shim's FHS entry, inherited via PATH from the launching session. This is not a phase defect — it is the exact discrepancy the phase was chartered to fix (see ROADMAP §"Phase 68" AMENDED block, owner-approved 2026-09-12). |
| (e) a worktree is a directory direnv has never seen | — | MET |
| (f) if shims are reachable, section still keeps recipe mandatory | — | MET |

**SC1_LITERAL_VERDICT: PARTIAL** (5 of 6 clauses MET; clause (d) is the literal text's known-false
premise that the AMENDED block exists to correct — expected, not a gap).

**SC1_AMENDED_VERDICT: MET.** Verified independently: `CLAUDE.md:100`'s boundary paragraph states,
in its own words, that (1) the recipe is unchanged and mandatory on every machine, (2) `flake.nix`
does not substitute for it, (3) on the maintainer's NixOS machine the recipe itself runs through the
shims, and (4) the shims arrive by PATH inheritance from a session launched in the direnv-loaded main
checkout, never by direnv in the worktree. The ROADMAP.md `AMENDED 2026-09-12` block
(`ROADMAP.md:646-658`) is present, owner-approved, and correctly transcribes the NIX-05 finding.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `CLAUDE.md` | Line 11 + Conventions bullet rewritten (D-08); new `### NixOS development shell` subsection (D-02..D-07); boundary paragraph in `### Worktree-isolated execution` (D-01) | ✓ VERIFIED | All present, content matches decisions verbatim, recipe tail hash-identical to base |
| `tox.ini` | `requires` rationale comment (lines 4-17) rewritten (D-16); `requires = tox-uv~=1.35` and everything below untouched | ✓ VERIFIED | Comment block matches D-16; `tox config` read-back confirms parsed value unchanged |
| `flake.nix` | Header block above `outputs` + per-element notes rewritten, comments only (D-09..D-12) | ✓ VERIFIED | Content matches; all 4 devShell drvPaths byte-identical before/after (independently re-measured) |
| `tests/test_toolchain_config_gate.py` | Docstring/assert-message text at ~302-305, ~366-369 updated (D-13) | ✓ VERIFIED | Text matches post-Phase-68 state; assertion logic untouched (test passes) |
| `tests/test_pdf_render_gate.py` | One sentence added to `_run_sphinx_build_typst` docstring (~167-171) (D-14) | ✓ VERIFIED | Sentence present, historical QUA-04 sentence and closing sentence both kept verbatim; test passes |
| `.planning/ROADMAP.md` | SC#1 `AMENDED 2026-09-12` block (D-01) | ✓ VERIFIED | Present at `ROADMAP.md:646-658`, original text retained above it |

### Key Link Verification

| From | To | Via | Status |
|---|---|---|---|
| `CLAUDE.md` § NixOS development shell | `flake.nix` header notes | pointer sentence "recorded in `flake.nix`'s own header notes" | ✓ WIRED |
| `CLAUDE.md` shim check | the `uv` shim on PATH | `grep -q typsphinx-fhs-run "$(command -v uv)"` | ✓ WIRED — independently confirmed `grep -c typsphinx-fhs-run "$(command -v uv)"` = 2 in the current shell |
| `flake.nix` `venvShimNames` + `uv` | `CLAUDE.md` § Commands | each of the 7 names begins a documented command line | ✓ WIRED — independently confirmed via `awk` extraction of both lists |
| `CLAUDE.md:77` tox-uv pin bullet | `tox.ini`'s `requires` comment | both describe the same `tox-uv~=1.35` pin and ini-parser constraint | ✓ WIRED — cross-checked verbatim |
| boundary paragraph (`### Worktree-isolated execution`) | unchanged provisioning recipe | placement immediately above "When operating inside a worktree, provision" | ✓ WIRED — confirmed by reading file order |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| DOC-19 | 68-01, 68-02, 68-04 | `CLAUDE.md`'s NixOS/worktree-provisioning section describes the landed mechanism, no manual shim step | ✓ SATISFIED | SC#1 amended reading MET; D-02 vacuity evidenced; no `ln -sf`/`patchelf` mentions outside the "No manual step" sentence |
| DOC-20 | 68-02, 68-04 | `tox.ini`'s `tox-uv-bare` rationale comment replaced by one describing the current pin, `~=` constraint kept | ✓ SATISFIED | SC#2 MET; 0 C3 rows in repo-wide grep; `tox config` read-back correct |
| DOC-21 | 68-03, 68-04 | `flake.nix` carries notes on the FHS wrapper, shimmed commands, and the darwin guard | ✓ SATISFIED | SC#3 MET; derivation identity preserved on all 4 systems; darwin-unverified-by-construction note present and accurate |

No orphaned requirements: `REQUIREMENTS.md`'s Phase 68 row maps exactly DOC-19/DOC-20/DOC-21, and
all three appear in at least one plan's `requirements:` frontmatter (68-01: DOC-19; 68-02: DOC-20,
DOC-19; 68-03: DOC-21; 68-04: DOC-19, DOC-20, DOC-21).

Note: `REQUIREMENTS.md` still shows DOC-19/DOC-20/DOC-21 as `[ ]` (Pending) as of this verification
— the checkbox flip is a tracking-update step that follows phase closure, not a gap in the
implementation itself; the codebase evidence above independently confirms all three are satisfied.

### Anti-Patterns Found

None blocking. `grep -nE 'TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER'` across the five edited files
surfaces only pre-existing `TODO-01` (an unrelated, long-standing requirement ID inside
`tests/test_pdf_render_gate.py`, not touched by this phase's diff) — not a debt marker introduced
here.

### Code Review Cross-Check (`68-REVIEW.md`)

0 critical, 1 warning, 2 info. Warning (WR-01) proposes an optional future "toolchain pin sync
hazard" callout, similar to the existing `@preview` version-sync section — a quality suggestion, not
a defect; does not block phase completion. Info items (IN-01 direnv-allow-list phrasing precision,
IN-02 a pre-existing, out-of-footprint archival-path citation) are both non-blocking observations
about phrasing/style, not correctness defects. Verifier independently confirmed the review's central
claims (no `D-NN` IDs remain in `flake.nix`, the 7 shim names match across files, no CI lane
evaluates `flake.nix`) during this session's own re-measurement.

### Known, Accepted Format/Oracle Deviations (per orchestrator notes, re-confirmed here)

1. **Wave-1 plans' pytest-collected-count oracle defect** (68-01 Task 2, 68-02 Task 3, 68-03 Task
   2): their `<automated>` verify used an anchored `sed` pattern that never matches pytest's
   `====`-padded summary line. Executors re-measured with a non-anchored pattern (1548 before/after,
   confirmed independently by the verifier via `pytest --collect-only -q`). The substantive
   invariant — collected count unchanged — holds. Not a gap; a plan-authoring defect already
   worked around during execution.
2. **`68-CLOSURE-EVIDENCE.md` verdict-key format deviation:** verdict keys carry trailing
   parenthetical prose (e.g. `SC2_VERDICT = MET (C3_ROWS = 0 and ...)`) rather than a bare
   `KEY = VALUE`. A literal `[ "$(k SC2_VERDICT)" = MET ]`-style automated check would not match
   exactly, but the verifier read and judged the verdict content directly — all verdicts (SC1_LITERAL
   = PARTIAL by design, SC1_AMENDED / SC2 / SC3 / DOC19 / DOC20 / DOC21 = MET) are substantively
   correct as re-measured above. Not a gap; a cosmetic formatting deviation in the evidence file.

### Human Verification Required

None. All must-haves resolved to VERIFIED or the expected by-design "contradicted" state (SC#1
clause (d), which the AMENDED block exists to document). No behavior-dependent state transitions are
in scope for a prose/comment-only phase — every claim was checked either by direct file inspection
or by independently re-running the underlying command (pytest, black, ruff, mypy, tox config, git
log/grep, nix eval, nix flake check).

### Gaps Summary

No gaps. All three requirements (DOC-19, DOC-20, DOC-21) are satisfied by codebase evidence
independently re-measured by the verifier, not merely asserted by SUMMARY.md. The one clause that
reads as "failed" under a literal interpretation (SC#1 clause (d)) is the precise discrepancy this
phase was chartered to correct via the ROADMAP AMENDED block, and D-01 (owner-approved) requires it
to be reported separately rather than folded into the overall verdict — which this report does.

---

_Verified: 2026-09-13_
_Verifier: Claude (gsd-verifier)_
