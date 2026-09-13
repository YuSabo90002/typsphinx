# Phase 65: `tox-uv-bare` → `tox-uv` Revert — Pattern Map

**Mapped:** 2026-09-12
**Files analyzed:** 5 (3 mandatory edit-footprint files + 1 widened test file + N evidence markdowns)
**Analogs found:** 5 / 5

This phase is a toolchain/config revert with no application code. All "files" are config, one test,
and evidence markdown — there is no controller/service/component tier. Roles are drawn from the
config/test/doc vocabulary instead.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|-----------------|---------------|
| `pyproject.toml` (dev extra, line ~38) | config | transform (declared-dep swap) | same file, prior commit `e603f36e` (Phase 45.2, the inverse swap) | exact — literal reverse diff |
| `tox.ini` (`requires`, line 11) | config | transform | same file, prior commit `e603f36e` | exact — literal reverse diff |
| `uv.lock` | config (generated) | batch (lockfile regen) | `uv.lock` state before/after `e603f36e` (42 deletions there; this phase adds them back) | exact — regenerate via `uv lock`, never hand-edit |
| `tests/test_toolchain_config_gate.py::test_dev_extra_pins_tox_uv_bare_not_tox_uv` (lines 269-362) + module docstring G5 paragraph (lines 35-49) | test | request-response (static assertion gate, no I/O) | sibling tests in the same file (`test_uv_venv_lock_runner_requires_extras_forbids_deps`, `test_runtime_dependencies_carry_no_toolchain_package`) and the file's own `_load_pyproject()`/`_load_tox_ini()` helpers | exact — same file, same idiom, invert two assertions in place |
| `65-*-EVIDENCE.md` (control/observation/CI evidence, names at Claude's discretion) | test (evidence doc) | request-response (verbatim transcript recording) | `64-GAP-REMEASURE-EVIDENCE.md`, `64-NIX07-RENAME-EVIDENCE.md`, `64-LIBZ-FIX-EVIDENCE.md`, `64-CI-EVIDENCE.md` | exact — same phase family, same evidence convention (Phase 64 D-05) |
| Plan files (`65-0N-PLAN.md`) | config (plan spec) | request-response | `64-02-PLAN.md`/`64-06-PLAN.md` (measurement plans), `64-04-PLAN.md` (push + one CI dispatch) | exact — same phase family, same frontmatter/precondition shape |

## Pattern Assignments

### `pyproject.toml` + `tox.ini` (config, transform)

**Analog:** commit `e603f36ebeb07a6a146e24a740601fd1215f08ec` (Phase 45.2), which performed the exact
inverse of this phase's edit. Reverting it is close to `git revert -n e603f36e` in spirit, but must be
done as fresh edits (D-04: `uv.lock` must be a plain `uv lock` regeneration, not the old pre-45.2
lock resurrected byte-for-byte) plus one extra file this commit's message doesn't cover (the gate test).

**`e603f36e`'s own summary (for commit-message convention — mirror its structure, invert its direction):**
```
fix(45.2-02): replace tox-uv meta package with tox-uv-bare

- pyproject.toml dev extra: rename tox-uv>=1.35,<2 to tox-uv-bare>=1.35,<2,
  dropping the bundled uv wheel whose generic-linux ELF cannot exec on NixOS
- tox.ini: requires = tox-uv-bare~=1.35 (comma-splitting comment rewritten
  for the new name, per SC#5)
- tox.ini [testenv:type]: deps block replaced with extras = dev, matching
  the docs environments' working shape (D-02) — proves the tracer path
  end to end via `tox -e type`
- uv.lock regenerated: removes tox-uv and uv package blocks, adds nothing
  unrelated (tox-uv-bare was already present as a transitive dependency)

 pyproject.toml |  2 +-
 tox.ini        | 12 ++++--------
 uv.lock        | 42 ++----------------------------------------
 3 files changed, 7 insertions(+), 49 deletions(-)
```

**Current `pyproject.toml:38` (the line to edit — one token):**
```toml
    "tox-uv-bare>=1.35,<2",
```
→ becomes `"tox-uv>=1.35,<2",` (keep the `>=1.35,<2` range exactly; D-01/TOX-01 only swap the name).

**Current `tox.ini:4-11` (the line to edit — one token, comment rewrite is OUT of scope per D-06):**
```ini
# tox-uv-bare pinned via ~= (not >=1.35,<2): tox's own ini-list loader splits
# single-line `requires` values on "," (only multi-*entry* lists preserve
# newline-splitting), so a literal ">=1.35,<2" is parsed as two bogus
# requirements ("tox-uv-bare>=1.35" and "<2") and tox fails to even start.
# ~=1.35 is the packaging-spec equivalent of >=1.35,<2 (see D-07) with no
# comma, sidestepping the parser bug. Verified equivalent via
# `packaging.specifiers.SpecifierSet` in 04-01-SUMMARY.md.
requires = tox-uv-bare~=1.35
```
Edit ONLY the `requires =` line's value to `requires = tox-uv~=1.35`. Per D-06 the comment text
(which still says "tox-uv-bare") is explicitly left stale for Phase 68/DOC-20 — do not touch it in
this phase even though it now reads oddly.

**`e603f36e`'s diff shape to mirror (inverse direction) for `pyproject.toml`:**
```diff
-    "tox-uv>=1.35,<2",
+    "tox-uv-bare>=1.35,<2",
```
This phase produces the exact opposite hunk (`tox-uv-bare` → `tox-uv`), same location, same file.

**`uv.lock` regeneration — command sequence and exact expected output (D-04, this session's live measurement):**
```
$ uv lock
Using CPython 3.14.4
Resolved 91 packages in 1.17s
Added tox-uv v1.36.0
Updated tox-uv-bare v1.35.2 -> v1.36.0
Added uv v0.12.13
$ uv lock --check
Resolved 91 packages in 0.59ms
$ echo exit:$?
exit:0
$ uv sync --extra dev --locked
 ... (91 packages resolved, all installed)
$ echo exit:$?
exit:0
```
Header stays `version = 1` / `revision = 3`. No `--upgrade`, no `--upgrade-package`, no hand edit —
run plain `uv lock` and commit exactly what it produces (ride-along version bumps included).

**Do NOT touch** `tox.ini`'s `[testenv:type]` `extras = dev` block (already correct, unrelated to
this phase) or any other section — `e603f36e` also touched that block but this phase's D-06 footprint
is narrower.

---

### `tests/test_toolchain_config_gate.py` — invert `test_dev_extra_pins_tox_uv_bare_not_tox_uv` (test, request-response)

**Analog:** the file's own sibling tests and helpers — same file, same conventions, no external analog
needed.

**Imports pattern (lines 67-76, already present, no change needed):**
```python
import configparser
import tomllib
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

REPO_ROOT = Path(__file__).resolve().parents[1]
TOX_INI_PATH = REPO_ROOT / "tox.ini"
PYPROJECT_TOML_PATH = REPO_ROOT / "pyproject.toml"
```

**Shared helper pattern already in the file (lines 97-115) — reuse `_load_pyproject()` unchanged:**
```python
def _load_pyproject() -> dict:
    """Parse pyproject.toml via tomllib. ..."""
    assert (
        PYPROJECT_TOML_PATH.exists()
    ), f"{PYPROJECT_TOML_PATH} does not exist -- all project configuration lives here"
    with open(PYPROJECT_TOML_PATH, "rb") as f:
        try:
            data = tomllib.load(f)
        except Exception as e:
            raise AssertionError(
                f"{PYPROJECT_TOML_PATH} could not be parsed -- tomllib may have "
                f"encountered a syntax error: {e}"
            ) from e
    return data
```
Note the `raise AssertionError(...) from e` idiom (ruff B904 compliance) — mirror this exactly in any
new/edited error path in the test.

**Current assertions to invert (lines 336-362, exact text to flip):**
```python
    # G5 requirement 1: dev extra MUST contain tox-uv-bare.
    assert canonicalize_name("tox-uv-bare") in dev_names, (
        "dev extra does not contain 'tox-uv-bare' (on normalized distribution name) -- "
        ...
    )

    # G5 requirement 2: dev extra MUST NOT contain tox-uv.
    assert canonicalize_name("tox-uv") not in dev_names, (
        "dev extra contains 'tox-uv' (on normalized distribution name) -- "
        ...
    )
```
Per CONTEXT D-06's AMENDED block: invert to "MUST name `tox-uv` and MUST NOT name `tox-uv-bare`
directly (both on the normalized distribution name, keeping the existing `canonicalize_name`
mechanism)". Concretely, swap the two literal strings passed to `canonicalize_name(...)` in both
assertions (`"tox-uv-bare"` ↔ `"tox-uv"`) and rewrite each message body to describe the Phase 65
revert (FHS shims dissolve the stub-ld defect; reverting to `tox-uv-bare` is now the regression) —
do not delete the test, do not delete the `canonicalize_name`/`Requirement`-parsing mechanism above it
(lines 324-333), which stays untouched:
```python
    dev_names = set()
    for req_string in dev_extra:
        try:
            req = Requirement(req_string)
            dev_names.add(canonicalize_name(req.name))
        except Exception as e:
            raise AssertionError(
                f"Could not parse requirement '{req_string}' in dev extra: {e}"
            ) from e
```

**Function docstring to rewrite (lines 270-301):** currently frames `tox-uv-bare` as correct and
`tox-uv` as the NixOS-breaking regression, cites `45.2-CONTEXT.md`/`45.2-TOOLCHAIN-EVIDENCE.md`. Per
D-06 AMENDED, rewrite to describe the Phase 65 revert: the stub-ld defect is dissolved by Phase 64's
FHS shims, `tox-uv` is upstream-default and now safe, `tox-uv-bare` is the stale pin this gate now
rejects. Keep the "naming trap" explanation (lines 287-291, "tox-uv-bare contains the substring
tox-uv") — that mechanism note is orientation-independent and stays true.

**Module docstring G5 paragraph to rewrite (lines 35-49):** same direction-flip — currently states
"[project.optional-dependencies].dev MUST name `tox-uv-bare` ... MUST NOT name `tox-uv`"; invert to
match the new assertions, and update the CLAUDE.md quote reference (CLAUDE.md itself is NOT edited
this phase per D-06 — the docstring's citation of CLAUDE.md's now-stale "-bare is deliberate" sentence
should be reworded or dropped, not left claiming a CI-invisible NixOS-only defect that Phase 64
already fixed).

**Untouched in the same file (confirm, do not edit):** `test_uv_venv_lock_runner_requires_extras_forbids_deps`
(lines 118-149+), `test_runtime_dependencies_carry_no_toolchain_package` (starts line 365, checks
`[project].dependencies` — unaffected, this phase only touches the `dev` extra), and the
`wheel_build_env`/`package = editable` gate (lines 260-266). Full-suite re-run after the edit must show
this file's remaining tests still pass and the inverted test now passes against the swapped
`pyproject.toml`.

---

### `65-*-EVIDENCE.md` files (evidence doc, verbatim-transcript recording)

**Analogs:** `64-GAP-REMEASURE-EVIDENCE.md` (worktree head check + transcript), `64-NIX07-RENAME-EVIDENCE.md`
/ `64-LIBZ-FIX-EVIDENCE.md` (RED-then-GREEN control recording), `64-CI-EVIDENCE.md` (branch census →
push → dispatch → 12-job census).

**Convention (Phase 64 D-05, reused verbatim by 65-CONTEXT D-03/TOX-03):** no new script, no new test
file — every measurement is a shell transcript pasted into the evidence markdown exactly as it printed,
headed by a short prose sentence stating what the transcript proves and which prior evidence file's
numbers it must match or diverge from.

**`64-GAP-REMEASURE-EVIDENCE.md` head-check pattern to copy for D-02/D-09 confirmation (lines 1-23):**
```
Measured shape: genuine D-09 shape — inherited session PATH of a session relaunched after 64-05 merged;
no nix develop wrapper, no direnv exec.

## Session check

$ command -v ruff
/nix/store/vxcr1f2x7ywkyvwli0sykhgwsmkg800k-ruff/bin/ruff
...
```
For Phase 65, the equivalent opening section is the worktree provisioning + shim confirmation
(`command -v uv` / `command -v tox` pointing at the Phase 64 shims, per CONTEXT "Carried forward")
before any `tox -vv -e py312` observation is trusted.

**`64-CI-EVIDENCE.md` branch-census + push pattern to copy for TOX-04 (lines 1-58):**
```
## Branch census

Re-measured per constraint 9 — never trusted from the RESOLVED note.

$ git branch --list 'gsd/v0.9.3*' -v
...
$ git rev-parse gsd/v0.9.3-toolchain-and-dependency-update-repair
...
$ git ls-remote --heads origin | grep -c '0\.9\.3'
0

## Tip identity and lock check

$ git rev-parse HEAD
...
**`PUSHED_SHA = <sha>`**

Pre-dispatch lock check (every ci.yml job's first substantive step):
$ uv sync --extra dev --locked
Resolved N packages in ...
Checked N packages in ...
$ echo "exit:$?"
exit:0
```
Reuse this exact section shape for TOX-04's push + `gh workflow run CI --ref` + 12-job census
(`64-04-PLAN.md`'s job list: 6 `test` matrix jobs [ubuntu×2, windows×2, macos×2], `Lint and Format
Check`, `Type Check`, `Code Coverage`, `Build Package`, `Integration Test - basic`,
`Integration Test - advanced`).

**D-02/D-03 observation excerpts to paste verbatim (already captured in RESEARCH.md's Architecture
Patterns section, reproduce with the real worktree paths, not the scratch ones):**
```
py312: 272 D using bundled uv from: <tree>/.venv/bin/uv [tox_uv/_venv.py:237]
...
DEBUG uv 0.12.13 (x86_64-unknown-linux-gnu)
...
  py312: OK (0.58 seconds)
```
and the D-03 control:
```
$ /nix/store/l9k0…-python3-3.13.13/bin/python3 -m venv ctrl-venv
$ cat ctrl-venv/pyvenv.cfg
home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
...
py312: 93 D using bundled uv from: <tree>/ctrl-venv/bin/uv [tox_uv/_venv.py:237]
...
Could not start dynamically linked executable: <tree>/ctrl-venv/bin/uv
...
  py312: FAIL code 127 (0.00 seconds)
```

---

### Plan files (`65-0N-PLAN.md`)

**Analogs:** `64-02-PLAN.md`/`64-06-PLAN.md` (measurement-shaped plans executed in a worktree),
`64-04-PLAN.md` (push + single CI dispatch + observe-to-completion plan).

**`64-04-PLAN.md` frontmatter/precondition shape to copy (lines 1-53):**
```yaml
---
phase: 64-fhs-wrapper-and-command-shims-in-flake-nix
plan: 04
type: execute
wave: 3
depends_on: ["64-02", "64-03"]
files_modified:
  - .planning/phases/.../64-CI-EVIDENCE.md
autonomous: true
requirements: [NIX-01]

estimate:
  tokens: 45000
  ...
must_haves:
  truths:
    - 'Constraint 9: ... A decoy with zero unique commits is deleted ...'
    - 'SC#5: the canonical branch ..., and no other ref, is on origin ...'
    - 'SC#5: exactly one CI run is dispatched, with gh workflow run CI --ref ...'
    - 'SC#5: every job conclusion is transcribed literally; ...'
  artifacts:
    - path: .planning/phases/.../64-CI-EVIDENCE.md
      provides: 'branch census, push, dispatch, the completed run and its full job census'
      contains: 'windows-latest'
  key_links:
    - from: '...'
      to: '...'
      via: '...'
      pattern: '...'
  prohibitions:
    - statement: 'MUST NOT create a tag, open a pull request, trigger release.yml by any route, force-push, ...'
      status: resolved
      verification: test
---
```
For Phase 65's TOX-04 plan, mirror this exactly: `prohibitions` should include "MUST NOT dispatch a
second CI run" and "MUST NOT set `TOX_UV_PATH` anywhere" (D-02's anti-pattern); `must_haves.truths`
should quote SC#3's DIVERGENT-result-halts-not-recovers language and SC#4's 12-job transcription
requirement verbatim, the same way `64-04-PLAN.md` quotes SC#5.

**`<objective>`/`<execution_context>`/`<context>` block shape (lines 55-86) — copy verbatim structure,
substitute phase-65 file references:**
```
<objective>
...
Requirement mapping: ...
Output: `64-CI-EVIDENCE.md`.
</objective>

<execution_context>
@/home/yuta/Documents/typsphinx/.claude/gsd-core/workflows/execute-plan.md
@/home/yuta/Documents/typsphinx/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/.../64-CONTEXT.md
@.planning/phases/.../64-02-SUMMARY.md
@.github/workflows/ci.yml
@CLAUDE.md
</context>
```

## Shared Patterns

### Worktree provisioning (applies to every executable plan this phase produces)
**Source:** CLAUDE.md § "Worktree-isolated execution" (already quoted in full in the system context) —
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` then run everything via `uv run`;
first confirm `command -v uv` / `command -v tox` resolve through the Phase 64 shims (D-09 head check,
copy the exact `64-GAP-REMEASURE-EVIDENCE.md` transcript shape above).
**Apply to:** every plan in this phase (config edit, lock regen, D-02 observation, D-03 control,
TOX-04 CI dispatch) — none may skip this precondition.

### Evidence-not-test-file convention
**Source:** Phase 64 D-05, reused by 65-CONTEXT D-03's "no new script, no new test" — record verbatim
shell transcripts in `*-EVIDENCE.md`, never add a pytest test or shell script to assert D-02/D-03/TOX-04
observations.
**Apply to:** all D-02/D-03/TOX-04 measurement work in this phase.

### DIVERGENT-result-halts-never-self-recovers
**Source:** D-02/D-03 explicit language ("that is a DIVERGENT result — record it and HALT, do not
'recover' on the executor's own judgement") and the memory note on `executor-red-claims-need-remeasuring`.
**Apply to:** any plan whose SC#3/D-02/D-03 observation doesn't match the expected `.venv/bin/uv`
path/branch/version — must stop and report, not patch `tox.ini`/`flake.nix` to force the expected
result.

### `raise ... from e` / `canonicalize_name` idiom
**Source:** `tests/test_toolchain_config_gate.py` lines 111-114, 324-333 (existing, unchanged this
phase).
**Apply to:** the one test edit in this phase — do not introduce a bare `except Exception:` or drop
the `from e` chaining when rewriting the two assertion messages.

## No Analog Found

None. Every file/edit in this phase's footprint has a strong exact analog: `pyproject.toml`/`tox.ini`
in commit `e603f36e` (the literal inverse edit), the test in its own sibling assertions, and evidence/
plan shape in Phase 64's files.

## Metadata

**Analog search scope:** `pyproject.toml`, `tox.ini`, `uv.lock`, `tests/test_toolchain_config_gate.py`,
`.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/*.md`, git history (`git show e603f36e`).
**Files scanned:** 3 config files, 1 test file (445 lines, read in full via CONTEXT/RESEARCH's own
prior full read plus targeted re-reads of lines 1-125 and 260-370 here), 1 prior commit, 3 evidence
markdowns, 1 plan file.
**Pattern extraction date:** 2026-09-12
