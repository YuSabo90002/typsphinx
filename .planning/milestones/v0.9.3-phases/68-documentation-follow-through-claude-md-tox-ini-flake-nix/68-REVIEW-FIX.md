---
phase: 68-documentation-follow-through-claude-md-tox-ini-flake-nix
fixed_at: 2026-09-13T00:00:00Z
review_path: .planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-REVIEW.md
iteration: 1
findings_in_scope: 1
fixed: 1
skipped: 2
status: partial
---

# Phase 68: Code Review Fix Report

**Fixed at:** 2026-09-13
**Source review:** .planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope (fix_scope=critical_warning: CR-*/BL-*/WR-* only): 1 (WR-01)
- Fixed: 1
- Skipped: 2 (IN-01, IN-02 — Info-tier, out of scope per orchestrator instruction)

## Fixed Issues

### WR-01: The tox-uv/tox-uv-bare toolchain pin has no explicit "keep these in sync" hazard note, unlike the analogous `@preview` package pattern

**Files modified:** `CLAUDE.md`
**Commit:** `98b05fb134851410528328b7788a4ff30a6484d4` (`fix(68): WR-01 add toolchain-pin sync hazard callout to CLAUDE.md`)
**Applied fix:** Added one new bullet to the `## Conventions & gotchas` section, immediately after the existing `tox.ini pins tox-uv~=1.35 ...` bullet (near `CLAUDE.md:77`), mirroring the structure of the existing "The `@preview` version-sync hazard" section. The new bullet names every place the `tox-uv` vs `tox-uv-bare` rationale is restated and must move together on a future change:
- `pyproject.toml`'s `dev` extra (the actual pin)
- `tox.ini`'s `requires` line and its comment
- `flake.nix`'s header/`uvShim` comments
- `CLAUDE.md`'s own two mentions
- `tests/test_toolchain_config_gate.py`'s `test_dev_extra_pins_tox_uv_not_tox_uv_bare` docstring (the gate that enforces the pin)

The list was verified against the actual repository state via `git grep -n -e tox-uv -e tox-uv-bare -- ':!.planning' ':!uv.lock'` before writing the bullet, rather than trusting the REVIEW.md's file list alone.

Wording was written as a forward-looking maintenance instruction ("update all of them in the same commit"), not as a present-tense claim about which pin is currently in force, per the orchestrator's SC#2 constraint. Scope was kept to one paragraph/bullet, no version numbers beyond the existing `tox-uv~=1.35` reference already present in the surrounding text, and no restatement of the Phase 65 history beyond the one clause needed to justify the callout ("this drifted out of sync once already").

**Constraint verification performed:**
- Guarded-region check: the `CLAUDE.md` text from `"When operating inside a worktree, provision"` to end of file was NOT touched. `sha256sum` of that region before and after the edit: `2c39540d38d94116d19ee5c2552cc5c105b0ef1228932713c082cdb8041a9b9a` (matches the required value in both cases).
- Heading-count check: `grep -c "^## Conventions & gotchas" CLAUDE.md` → `1` (unchanged, exactly one heading, as required by a test string that cites it).
- Files-touched check: `git diff --stat HEAD~1` →
  ```
   CLAUDE.md | 1 +
   1 file changed, 1 insertion(+)
  ```
  Only `CLAUDE.md` changed; `tox.ini`, `flake.nix`, `pyproject.toml`, `uv.lock`, the test files, `typsphinx/`, and `.github/` were untouched, as required.
- No test run was performed (CLAUDE.md-only prose change, no code/test files touched, per orchestrator instruction). Verification ran directly in the main checkout on the current branch (`gsd/v0.9.3-toolchain-and-dependency-update-repair`) — no isolated worktree was used for this fix, since it is a documentation-only, single-file change and the orchestrator instructed operating on the main checkout directly.
- Commit used normal hooks (no `--no-verify`) and message form `fix(68): WR-01 ...`.

**Note on commit history:** the fix was first committed with an incorrect finding-ID label (`CR-01` — this repository's REVIEW.md format uses CR-* only for Critical-tier findings; the WR-01 label was mistakenly typed as CR-01). This was corrected via `git commit --amend` immediately afterward, before any other commit or push occurred, so only the final message (`WR-01`) is visible in history. No file content changed between the two commit attempts — only the commit message subject line.

## Skipped Issues

### IN-01: "a worktree's own `.envrc` is never allowed there" is ambiguous phrasing for a file that does exist in every worktree

**File:** `CLAUDE.md:100`
**Reason:** Out of scope. `fix_scope` for this run is `critical_warning`, and IN-01 is an Info-tier finding. Per explicit orchestrator instruction, IN-01 and IN-02 are recorded here as skipped/out-of-scope rather than fixed, to keep this fix pass limited to WR-01.
**Original issue:** `.envrc` is git-tracked and present in every worktree checkout; the sentence "never allowed there" is technically correct only under direnv's per-path allow-list semantics, and could be misread as "the file doesn't exist" or "must not be created there."

### IN-02: Pre-existing non-archival-stable path reference in `test_toolchain_config_gate.py`'s module docstring

**File:** `tests/test_toolchain_config_gate.py:46`
**Reason:** Out of scope. `fix_scope` for this run is `critical_warning`, and IN-02 is an Info-tier finding, explicitly excluded by the orchestrator's scope instruction. Additionally, the orchestrator's constraints for this run forbid editing anything under the test files for this fix pass.
**Original issue:** The module docstring (lines 1-60, unchanged by Phase 68) cites a live `.planning/phases/…` path for the Phase 65 revert evidence, rather than the archival-safe "milestone + phase + file name" citation style Phase 68 established in `flake.nix`. This path will break once the milestone archives.

---

_Fixed: 2026-09-13_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
