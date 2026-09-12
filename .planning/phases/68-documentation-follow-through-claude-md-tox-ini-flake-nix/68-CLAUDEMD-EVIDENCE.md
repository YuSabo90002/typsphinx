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

## NixOS subsection and boundary paragraph

```
$ awk '/^### NixOS development shell$/{f=1} /^### Worktree-isolated execution$/{f=0} f' CLAUDE.md
### NixOS development shell

**Scope.** This subsection applies only on the maintainer's NixOS machine, where `direnv` loads `flake.nix`'s devShell in the main checkout. CI and non-NixOS contributors have no shims and need none — nothing here changes how CI or a non-NixOS contributor runs any of these commands.

**What the shims are.** On that machine, PATH carries seven bare commands: `uv`, `tox`, `ruff`, `black`, `mypy`, `pytest` and `sphinx-build` — the same commands named in § Commands above. Each walks up from the current directory to this checkout's own `.venv/bin/<tool>` and runs it inside an FHS sandbox (`typsphinx-fhs-run`), which is what lets generic-linux binaries that `uv` installs or downloads execute, together with everything they spawn. A missing `.venv/bin/<tool>` fails loudly: a `typsphinx-shim:` line on stderr names the tool and prints the provisioning line as a hint, then the shim exits 127 — it never silently runs some other binary. `uv` alone also falls back to nixpkgs' own `uv`, so a fresh clone or worktree with no `.venv` yet can run its first `uv sync`. Once `.venv` exists, `uv --version` reports the version `uv.lock` pins.

**Prerequisite and check.** Launch Claude Code from a shell in which `direnv` has already loaded the main checkout's devShell. Before provisioning a worktree, confirm the shim is on PATH by running exactly: `grep -q typsphinx-fhs-run "$(command -v uv)"`.

**No manual step.** No manual `ln -sf` or `patchelf` step exists or is needed — those two words appear in this sentence and nowhere else in this file. A `Could not start dynamically linked executable` error means the shim is not on PATH (the session was not launched from the direnv-loaded checkout); relaunch from that shell — it is not a code regression.

**Locale.** The sandbox passes the host's `LANG` through unchanged, so Sphinx warning text stays localised inside it exactly as outside. CI runs in English, so a test asserting warning text should also be run under `LC_ALL=C` locally.

**Interpreters may differ.** A fresh worktree's `.venv` is built on uv-managed CPython, while the main checkout's may be on nixpkgs' `python3` — the two may differ. Compare both `.venv/pyvenv.cfg` `home` and `version_info` before comparing test counts between them.

**Rationale pointer.** Why the development shell is built this way is recorded in `flake.nix`'s own header notes — see that file, not this one.
```

NIXOS_SUBSECTION_HEADING = ### NixOS development shell

```
$ awk '/^### Worktree-isolated execution$/{f=1;next} /^When operating inside a worktree, provision/{f=0} f' CLAUDE.md
**Detection rule:** you are running inside an isolated git worktree when `.git` is a FILE (a `gitdir:` pointer), not a directory — check with `test -f .git`. Sequential main-tree execution has `.git` as a directory and needs none of the steps below.

**NixOS boundary.** The recipe below is unchanged and mandatory on every machine; `flake.nix` does not substitute for it. On the maintainer's NixOS machine the recipe itself runs through the shims described in the section above, because a worktree's `.venv` is built on a generic-linux interpreter that NixOS runs only inside the sandbox — so the worktree depends on those shims being present. The shims reach a worktree only because they are inherited through PATH from a session launched in the direnv-loaded main checkout: `direnv` never loads inside a worktree itself, and a worktree's own `.envrc` is never allowed there.
```

The subsection reports operational facts only (D-07): what the shims are, the prerequisite/check, the absence of a manual step, locale passthrough, and interpreter divergence, with a single pointer sentence to `flake.nix`'s own header notes for the rationale — it does not restate the devShell's shape, the falsified alternatives, or the process-inheritance argument. The boundary paragraph restates ROADMAP SC#1's `AMENDED 2026-09-12` reading in the file's own words: the recipe is unchanged and mandatory, `flake.nix` does not substitute for it, and the shims reach a worktree only by PATH inheritance from the launching session, never by direnv inside the worktree itself.

## Gates after the edit

```
$ grep -n -E '^## Conventions & gotchas$|^- CI \(|^### NixOS development shell$|^### Worktree-isolated execution$' CLAUDE.md
73:## Conventions & gotchas
78:- CI (`.github/workflows/ci.yml`) runs the py312–py313 + lint + type + cov matrix. A weekly `drift.yml` re-resolves latest allowed deps and files an issue on breakage. `release.yml` publishes to PyPI.
80:### NixOS development shell
96:### Worktree-isolated execution
```

Strictly increasing: 73 < 78 < 80 < 96.

```
$ awk '/^When operating inside a worktree, provision/{f=1} f' CLAUDE.md | sha256sum
2c39540d38d94116d19ee5c2552cc5c105b0ef1228932713c082cdb8041a9b9a  -

$ git show 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a:CLAUDE.md | awk '/^When operating inside a worktree, provision/{f=1} f' | sha256sum
2c39540d38d94116d19ee5c2552cc5c105b0ef1228932713c082cdb8041a9b9a  -
```

Equal — unchanged by the Task 2 edit as well.

```
$ git diff -U0 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a -- CLAUDE.md | grep '^-' | grep -v '^--- a/'
-Development uses `uv` for env/dependency management and `tox` (with `tox-uv-bare`) as the task runner.
-- `tox.ini` pins `tox-uv-bare~=1.35` (not `>=1.35,<2`) deliberately — see the comment in that file; tox's ini parser splits a single-line `requires` on commas and breaks otherwise. The `-bare` package is also deliberate (QUA-04, Phase 45.2): the plain `tox-uv` meta package bundles a PyPI `uv` wheel whose generic-linux ELF cannot exec on NixOS, and `uv.find_uv_bin()` searches `.venv/bin` first and reads no environment variable. Do not "simplify" it back to `tox-uv`.
```

Only the two lines Task 1 changed — Task 2 is purely additive.

```
$ grep -nE 'ln -sf|patchelf' CLAUDE.md
88:**No manual step.** No manual `ln -sf` or `patchelf` step exists or is needed — those two words appear in this sentence and nowhere else in this file. A `Could not start dynamically linked executable` error means the shim is not on PATH (the session was not launched from the direnv-loaded checkout); relaunch from that shell — it is not a code regression.
```

The only hit is inside the new subsection's "No manual step" paragraph, as required by D-02.

```
$ uv run pytest --collect-only -q -p no:cacheprovider
... (tail)
======================== 1548 tests collected in 0.27s =========================
```

COLLECT_AFTER_68_01 = 1548

Equals `COLLECT_BEFORE_68_01` (1548) — text-only change, no test count drift.

```
$ git diff --name-only 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a
.planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-CLAUDEMD-EVIDENCE.md
CLAUDE.md
```

Only `CLAUDE.md` and this evidence file changed relative to base (the `68-01-SUMMARY.md` this plan's `<output>` requires is committed alongside, after this evidence).
