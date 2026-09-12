# Phase 68 Plan 01 — CLAUDE.md Evidence

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-12T15:46:36Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a2eb538334cf0cc75

$ test -f .git; echo "exit:$?"
exit:0

$ command -v uv
/nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
```

UV_SHIM_PATH = /nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv
UV_SHIM_FHS_COUNT = 2

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
... (tail)
 + typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a2eb538334cf0cc75)
 + typst==0.15.0
 + urllib3==2.7.0
 + uv==0.12.13
 + virtualenv==21.5.1
```

```
$ git merge-base HEAD gsd/v0.9.3-toolchain-and-dependency-update-repair
0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a

$ git rev-parse HEAD
0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a
```

BASE_68_01 = 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a

Measured directly in this session (never copied from executor/orchestrator metadata); equals `git rev-parse HEAD` at this point, before any commit.

## Baseline

```
$ sed -n 's/^home = //p;s/^version_info = //p' .venv/pyvenv.cfg
/home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
3.14
```

PYVENV_HOME_68_01 = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
PYVENV_VERSION_68_01 = 3.14

```
$ uv run pytest --collect-only -q -p no:cacheprovider
... (tail)
======================== 1548 tests collected in 1.24s =========================
```

COLLECT_BEFORE_68_01 = 1548

```
$ sed -n '11p;73p;77p;80p' CLAUDE.md
Development uses `uv` for env/dependency management and `tox` (with `tox-uv-bare`) as the task runner.
## Conventions & gotchas
- `tox.ini` pins `tox-uv-bare~=1.35` (not `>=1.35,<2`) deliberately — see the comment in that file; tox's ini parser splits a single-line `requires` on commas and breaks otherwise. The `-bare` package is also deliberate (QUA-04, Phase 45.2): the plain `tox-uv` meta package bundles a PyPI `uv` wheel whose generic-linux ELF cannot exec on NixOS, and `uv.find_uv_bin()` searches `.venv/bin` first and reads no environment variable. Do not "simplify" it back to `tox-uv`.
### Worktree-isolated execution
```

## D-02 evidence at base

```
$ git log --oneline -S "ln -sf" 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a -- CLAUDE.md
(no output — 0 lines)
```

LNSF_COMMITS = 0

```
$ git log --oneline -S patchelf 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a -- CLAUDE.md
(no output — 0 lines)
```

PATCHELF_COMMITS = 0

```
$ git grep -nE 'ln -sf|patchelf' 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a -- ':!.planning'
(no output — 0 lines)
```

LNSF_PATCHELF_GREP_HITS_BEFORE = 0

All three are 0, as expected. The vacuity claim holds: no manual `ln -sf` / `patchelf` step has ever been introduced into, or documented in, `CLAUDE.md`. That guidance never lived in `CLAUDE.md`; it lived only in the maintainer's out-of-repository memory.

## D-08 rewrite

```
$ sed -n '11p;77p' CLAUDE.md
Development uses `uv` for env/dependency management and `tox` (with `tox-uv`) as the task runner.
- `tox.ini` pins `tox-uv~=1.35` (not `>=1.35,<2`) — see the comment in that file; tox's ini parser splits a single-line `requires` on commas, so `>=1.35,<2` breaks tox's startup and `~=1.35` is the comma-free equivalent. The pin was earlier `tox-uv-bare` (QUA-04, Phase 45.2) only because the `uv` bundled with `tox-uv` could not exec on NixOS; the NixOS FHS shims now handle that, which is why plain `tox-uv` is correct again.
```

```
$ git diff -U0 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a -- CLAUDE.md
diff --git a/CLAUDE.md b/CLAUDE.md
index 4f808a58..4f36fb30 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -11 +11 @@ typsphinx is a Sphinx extension that adds Typst output builders. It converts doc
-Development uses `uv` for env/dependency management and `tox` (with `tox-uv-bare`) as the task runner.
+Development uses `uv` for env/dependency management and `tox` (with `tox-uv`) as the task runner.
@@ -77 +77 @@ User-facing config values (all registered in `__init__.py`, prefix `typst_`) inc
-- `tox.ini` pins `tox-uv-bare~=1.35` (not `>=1.35,<2`) deliberately — see the comment in that file; tox's ini parser splits a single-line `requires` on commas and breaks otherwise. The `-bare` package is also deliberate (QUA-04, Phase 45.2): the plain `tox-uv` meta package bundles a PyPI `uv` wheel whose generic-linux ELF cannot exec on NixOS, and `uv.find_uv_bin()` searches `.venv/bin` first and reads no environment variable. Do not "simplify" it back to `tox-uv`.
+- `tox.ini` pins `tox-uv~=1.35` (not `>=1.35,<2`) — see the comment in that file; tox's ini parser splits a single-line `requires` on commas, so `>=1.35,<2` breaks tox's startup and `~=1.35` is the comma-free equivalent. The pin was earlier `tox-uv-bare` (QUA-04, Phase 45.2) only because the `uv` bundled with `tox-uv` could not exec on NixOS; the NixOS FHS shims now handle that, which is why plain `tox-uv` is correct again.
```

The only removed lines are the old line 11 and the old line 77, matching the plan's two-line-removal fence.

```
$ awk '/^When operating inside a worktree, provision/{f=1} f' CLAUDE.md | sha256sum
2c39540d38d94116d19ee5c2552cc5c105b0ef1228932713c082cdb8041a9b9a  -

$ git show 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a:CLAUDE.md | awk '/^When operating inside a worktree, provision/{f=1} f' | sha256sum
2c39540d38d94116d19ee5c2552cc5c105b0ef1228932713c082cdb8041a9b9a  -
```

Equal. The provisioning recipe tail is byte-identical to base.
