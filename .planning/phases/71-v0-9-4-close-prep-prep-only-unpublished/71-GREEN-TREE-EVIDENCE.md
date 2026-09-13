# Phase 71 — Local Green-Tree Evidence (SC#3, local half)

## Head check and provisioning

- `date -u +%FT%TZ`: `2026-09-13T08:44:21Z`
- `pwd -P`: `/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a43d13d9aa59679b9`
- `test -f .git; echo "exit:$?"`: `exit:0`
- `grep -c typsphinx-fhs-run "$(command -v uv)"`: `2`
- Provisioning line run:
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13`
  Tail of output:
  ```
  Installed 90 packages in 57ms
   ...
   + typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a43d13d9aa59679b9)
   + typst==0.15.0
   + urllib3==2.7.0
   + uv==0.12.13
   + virtualenv==21.5.1
  ```

BASE_71_03 = 7a42bf996b1aaca24a8b17346be78459e6d41e2b

SCRATCH_71_03 = /tmp/claude-1000/-home-yuta-Documents-typsphinx/2ab7ea40-2eb1-4a24-8331-4523dc2e4c54/scratchpad/p7103_6qoXbt

`git log --oneline -8`:
```
7a42bf99 docs(phase-71): update tracking after wave 1, mark wave 2 executing
e66d7b6e chore: merge executor worktree (worktree-agent-a571bab6fc41395dc)
c20ebaae chore: merge executor worktree (worktree-agent-a1002cdd91840430e)
fdc4ed14 docs(71-02): complete REL-13 closeout guard, SC#1 obs1, COVERAGE.md plan
5460c11a docs(71-01): complete v0.9.4 CHANGELOG bullet plan
1c6876a8 test(71-01): prove the CHANGELOG bullet is pure addition against the clean docs baseline
7610872f docs(71-02): write reasoned no-external-API COVERAGE.md, gate passes
9b0dd645 fix(71-02): put CODE_FREEZE_ANCHOR on its own bare key line
```

## Tree identity

- `uv run python -c "import typsphinx, sys; print(typsphinx.__version__); print(typsphinx.__file__)"`:
  ```
  0.9.2
  /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a43d13d9aa59679b9/typsphinx/__init__.py
  ```
  The path lies inside this worktree, proving the worktree's own editable copy is measured, not
  the main checkout's.

TYPSPHINX_FILE = /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a43d13d9aa59679b9/typsphinx/__init__.py

- `uv run python -c "import myst_parser; print(myst_parser.__version__)"`: `5.1.0` — proves the
  docs extra is present.

- `.venv/pyvenv.cfg` (this worktree):
  ```
  home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
  implementation = CPython
  uv = 0.11.25
  version_info = 3.13.13
  include-system-site-packages = false
  prompt = typsphinx
  ```

PYVENV_HOME_71_03 = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin

PYVENV_VERSION_71_03 = 3.13.13

- `/home/yuta/Documents/typsphinx/.venv/pyvenv.cfg` (main checkout, read-only):
  ```
  home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
  implementation = CPython
  uv = 0.11.25
  version_info = 3.13.13
  include-system-site-packages = false
  prompt = typsphinx
  ```

MAIN_PYVENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin

MAIN_PYVENV_VERSION = 3.13.13

Both trees' `pyvenv.cfg` `home` and `version_info` are identical — CPython 3.13.13, same nix store
path. No interpreter difference exists between this worktree and the main checkout, so counts
compared below are compared across identical interpreters.

## Product-tree delta and D-05

PHASE_BASE_SHA (from `71-CLOSEOUT-GUARD.md`) = f1f7d54a61d74c3972f1df0508ac994c001dda7e

- `git diff --stat f1f7d54a61d74c3972f1df0508ac994c001dda7e HEAD -- . ':(exclude).planning'`:
  ```
   CHANGELOG.md | 10 ++++++++++
   1 file changed, 10 insertions(+)
  ```
  Exactly one file, `CHANGELOG.md`, 10 insertions, zero deletions.

PRODUCT_DELTA = CHANGELOG.md

- `git fetch origin main` ran cleanly (FETCH_HEAD updated).
- `git rev-parse origin/main`:

ORIGIN_MAIN_SHA_71_03 = d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d

- `git merge-base HEAD origin/main`: `d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d` — equal to
  `MILESTONE_BASE` from `71-SC1-INVARIANTS.md` (`d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d`).

MAIN_ABSORBED = no

- `git merge-base --is-ancestor origin/main HEAD; echo "exit:$?"`: `exit:0`.
  `exit:0` means `origin/main` has not moved past the milestone base, so there is nothing to
  absorb (D-05 today). The merge-base equals `MILESTONE_BASE` exactly, which is what D-05
  requires; a merge-base different from `MILESTONE_BASE` would have been the breach, and none
  occurred.

The non-empty `CHANGELOG.md`-only delta is the positive control on the anchor: it proves the diff
command actually detects change (it is not silently comparing a tree to itself), and the single
file is why 71-01's docs comparison and this plan's final-tree docs comparison (Task 3) apply to
the same product tree — nothing else moved between 71-01's post-edit measurement and this plan's
run.

## Full suite

- `uv run pytest --collect-only -q -p no:cacheprovider` tail:
  ```
  ======================== 1548 tests collected in 1.62s =========================
  ```

COLLECTED_71_03 = 1548

- `uv run pytest -q -rs -p no:cacheprovider` ran in the foreground, exit 0, one pass (no split
  needed — completed in 127.97s). Short summary and final line, verbatim:
  ```
  SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
  1547 passed, 1 skipped in 127.97s (0:02:07)
  ```

FULL_SUMMARY = 1547 passed, 1 skipped

FULL_FAILED = 0

FULL_SKIPPED = 1

The one skip is `tests/test_corpus_gate.py:530`, an env-gated SC#3 before/after measurement
(`TYPSPHINX_CORPUS_REPORT=1` required) — the same skip reason Phase 70's after-side run recorded,
by design (RESEARCH Open Question 1).

Phase 70's `PYTEST_RESULT_AFTER` (from `70-AFTER-RUNTIME-EVIDENCE.md:73`) is `1547 passed 1
skipped`, on CPython 3.13.13. `FULL_SUMMARY` here is `1547 passed, 1 skipped`, also on CPython
3.13.13 — the two agree exactly, on the same interpreter version. Since Phase 70's after-side
measurement, only the `CHANGELOG.md` bullet changed (per the Product-tree delta above), and that
change carries no test-visible effect, consistent with the identical counts.

No failure occurred; no `## HALT` heading is written in this section.
