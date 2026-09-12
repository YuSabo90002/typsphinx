---
phase: 65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves
reviewed: 2026-09-12T00:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - pyproject.toml
  - tox.ini
  - tests/test_toolchain_config_gate.py
findings:
  critical: 0
  warning: 0
  info: 2
  total: 2
status: issues_found
---

# Phase 65: Code Review Report

**Reviewed:** 2026-09-12T00:00:00Z
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found (Info only — no Critical or Warning findings)

## Summary

This phase is a narrow, mechanical revert: `pyproject.toml`'s `dev` extra swaps
`tox-uv-bare>=1.35,<2` back to `tox-uv>=1.35,<2`, `tox.ini`'s `requires` line follows
suit (`tox-uv~=1.35`), and `tests/test_toolchain_config_gate.py`'s G5 gate
(`test_dev_extra_pins_tox_uv_bare_not_tox_uv` → `test_dev_extra_pins_tox_uv_not_tox_uv_bare`)
is inverted in lockstep, with both its assertions and its module-level/function-level
docstrings rewritten to match.

I verified the change mechanically rather than only reading it:
- `tomllib.load(pyproject.toml)` confirms the `dev` extra now contains `tox-uv>=1.35,<2`
  and no longer contains a `tox-uv-bare` literal entry.
- `pytest tests/test_toolchain_config_gate.py -q` → `4 passed` against the current tree.
- `tox config -e py312 --core -k requires` confirms tox's own ini loader parses
  `requires = tox-uv~=1.35` into a single well-formed requirement (`tox-uv~=1.35`), not
  the two-bogus-requirement failure mode the adjacent comment warns about.
- `uv.lock` confirms the docstring's transitive-dependency claim is factually correct:
  `tox-uv==1.36.0` depends on both `tox-uv-bare` and `uv`, while `tox-uv-bare==1.36.0`
  depends only on `packaging` and `tox` (no bundled `uv` wheel) — so the revert does
  reintroduce the PyPI `uv` wheel into the dependency graph, consistent with the
  docstring's claim that this is now safe because of the Phase 64 FHS shims.
- `canonicalize_name` normalizes hyphens/underscores/case but does not strip the
  `-bare` suffix, so `tox-uv` and `tox-uv-bare` remain distinguishable after
  normalization — the "naming trap" the docstring calls out is correctly handled by
  parsing each requirement's distribution name via `packaging.requirements.Requirement`
  rather than substring-matching the raw string.

No Critical or Warning issues found. The two Info items below are pre-existing
patterns/decisions that this diff continues rather than defects this diff introduces;
they're recorded for completeness per the review's own scope notes.

## Info

### IN-01: tox.ini header comment (lines 4-10) still narrates `tox-uv-bare`, not `tox-uv`

**File:** `tox.ini:4-10`
**Issue:** The block comment directly above `requires = tox-uv~=1.35` still reads
"`tox-uv-bare pinned via ~= (not >=1.35,<2)`" and references "`tox-uv-bare>=1.35`" as
the illustrative bogus-parse example — both now describe a package name that no longer
appears on the line below. Per the orchestrator's scope notes this is explicitly
deferred to Phase 68 (DOC-19/DOC-20/DOC-21, owner decision D-06), so this is not a new
defect introduced by this diff and is not asking for action here — flagged once, as
instructed, for completeness.
**Fix:** (deferred) Phase 68 rewrites this comment block to name `tox-uv` instead of
`tox-uv-bare`, matching the DOC-19/20/21 plan already on record.

### IN-02: G5 explanation is duplicated near-verbatim between the module docstring and the function docstring

**File:** `tests/test_toolchain_config_gate.py:35-49` and `tests/test_toolchain_config_gate.py:268-309`
**Issue:** The ~15-line explanation of why the dev extra must name `tox-uv` and not
`tox-uv-bare` (FHS shims, `find_uv_bin()` discovery order, CI vs. NixOS asymmetry) is
written out in full twice — once in the module-level docstring's "GAP G5" paragraph and
again in `test_dev_extra_pins_tox_uv_not_tox_uv_bare`'s own docstring. This is a
pre-existing pattern in this file (the same duplication existed for the pre-revert G5
text, and both copies were kept in sync in this very diff), not a defect newly
introduced by this phase, so it's Info rather than Warning. It's worth naming because
the duplication is exactly the kind of thing that silently drifts on the *next* edit:
a future change to one copy (e.g. a Phase 68 doc pass) that misses the other would
leave contradictory explanations sitting a few hundred lines apart in the same file,
with no test catching the mismatch (the assertions themselves don't reference the prose).
**Fix:** Not urgent enough to block this phase. If touched again, consider having the
function docstring state only what's specific to the assertions (the two `assert`
lines) and pointing to the module docstring's GAP G5 paragraph as the single source of
the shared narrative, rather than repeating it.

---

_Reviewed: 2026-09-12T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
