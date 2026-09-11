# Phase 64 — `flake.nix` FHS Wrapper and Shim Evidence

Every shim invocation in this evidence file is **DIAGNOSTIC**: the Claude Code session running this
plan predates the `flake.nix` edit, so its own PATH is frozen and carries no shim (orchestrator note
3). Every GREEN transcript below therefore goes through `nix develop . --command …` rather than an
inherited session PATH. That is not the D-09 session-inheritance shape — see the closing
"Session relaunch required before wave 2" section.

## Worktree and provisioning

```
$ test -f .git && echo IS_WORKTREE
IS_WORKTREE

$ git status --short
(empty)

$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
... (tail)
 + typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab7ba88fa3bf417f2)
 + typst==0.15.0
 + urllib3==2.7.0
 + virtualenv==21.5.1

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab7ba88fa3bf417f2

$ git rev-parse HEAD
3e6df794dd001e37a103a664e48ef1b5369cbc12

$ git rev-parse --abbrev-ref HEAD
worktree-agent-ab7ba88fa3bf417f2
```

This is a freshly created git worktree, never the main tree — the D-04 verification locus. `.git`
is a file (a `gitdir:` pointer), confirming isolation.

## Pre-edit session PATH

The Claude Code session's own PATH was frozen at launch and can carry no shim before the edit lands
(orchestrator note 3, D-09's first half):

```
$ command -v ruff
(no output)
$ echo "exit: $?"
exit: 1

$ command -v uv
/nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv
$ echo "exit: $?"
exit: 0

$ echo "DIRENV_DIR=$DIRENV_DIR"
DIRENV_DIR=-/home/yuta/Documents/typsphinx
```

No `ruff` is on this session's PATH; `uv` resolves to the plain nix-store build. Both match the
planning-time measurements exactly.

## RED

The D-04 locus: measured in this freshly provisioned worktree, never the main tree.

```
$ file .venv/bin/ruff
.venv/bin/ruff: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=ca2c631a338418e6129fa7e04e290477442b8489, stripped

$ .venv/bin/ruff --version
Could not start dynamically linked executable: .venv/bin/ruff
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
$ echo "exit: $?"
exit: 127
```

RED reproduced exactly as D-04 predicted: `.venv/bin/ruff` is a generic-linux ELF the stub loader
rejects, exit 127, before any `flake.nix` edit landed.

## Pre-edit baselines

Taken with the git flake ref `.` from the worktree root — never a `path:` ref, which would copy the
whole directory including the untracked `.venv` (~312 MB) and `.tox` (~599 MB) (orchestrator note 4).

```
$ nix eval --raw .#devShells.x86_64-linux.default.drvPath
/nix/store/xbhqkzmnak21qk9j8ph0f00b8w65jr9l-nix-shell.drv

$ nix eval --raw .#devShells.aarch64-linux.default.drvPath
/nix/store/z9yf853g0b6yfk5zf0x0jzvankdn9l34-nix-shell.drv

$ nix eval --raw .#devShells.x86_64-darwin.default.drvPath
evaluation warning: Nixpkgs 26.05 will be the last release to support x86_64-darwin; see https://nixos.org/manual/nixpkgs/unstable/release-notes#x86_64-darwin-26.05
/nix/store/fclfls55m9lp06679x7zrw0qzjya834j-nix-shell.drv

$ nix eval --raw .#devShells.aarch64-darwin.default.drvPath
/nix/store/2m6y6pshri0vyw3jb5agczjnz9a92sxc-nix-shell.drv
```

The x86_64-darwin deprecation warning arrives on stderr and is a warning, not an error. All four
drvPaths match the planning-time values exactly.

```
$ nix eval --json .#devShells.x86_64-linux.default.nativeBuildInputs --apply 'map (p: p.name)'
["nodejs-24.16.0","pnpm-11.9.0","git-2.54.0","python3-3.13.13","uv-0.11.25"]

$ nix eval --json .#devShells.aarch64-darwin.default.nativeBuildInputs --apply 'map (p: p.name)'
["nodejs-24.16.0","pnpm-11.9.0","git-2.54.0","python3-3.13.13","uv-0.11.25"]
```

Both package censuses match the planning-time measurements exactly, cross-checked against the
values recorded in `64-01-PLAN.md`.

## Tracer GREEN (DIAGNOSTIC)

`flake.nix` was edited inside the per-system `let` block, after `pkgs = pkgsFor system;`, adding:
`fhsRun` (a `pkgs.buildFHSEnv` named `typsphinx-fhs-run` whose `runScript` is the `typsphinx-fhs-passthrough`
script, body `exec "$@"`), `venvWalk` (the bounded upward `.venv` walk taking a tool name and an
on-stop fragment), `venvShimOnStop` (the D-03 not-found fragment: a `typsphinx-shim:` stderr line
naming the tool and the walk's start/stop directories, then `exit 127`), and one tracer shim,
`ruffShim = pkgs.writeShellScriptBin "ruff"`. `packages` became the four common entries, `++
pkgs.lib.optionals pkgs.stdenv.hostPlatform.isLinux [ ruffShim ]`, `++ [ pkgs.uv ]` — darwin's list
stays `nodejs, pnpm, git, python3, uv` in today's order.

```
$ nix develop . --command bash -c 'command -v ruff; ruff --version'
(building fhsRun's derivations, first invocation only)
/nix/store/vp86ji36v1nyp4q8d85i49hpyz43zszq-ruff/bin/ruff
ruff 0.15.20
```

Exactly `ruff 0.15.20`, matching `uv.lock:1209-1210`'s pin.

```
$ nix develop . --command bash /tmp/.../xtrace_ruff.sh
# (script body: bash -x "$(command -v ruff)" --version 2>&1)
+ set -eu
+ start=/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab7ba88fa3bf417f2
+ dir=/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab7ba88fa3bf417f2
+ :
+ '[' -x /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab7ba88fa3bf417f2/.venv/bin/ruff ']'
+ exec /nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab7ba88fa3bf417f2/.venv/bin/ruff --version
ruff 0.15.20
```

The `+ exec …/typsphinx-fhs-run <path> --version` line names
`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab7ba88fa3bf417f2/.venv/bin/ruff` — this
worktree's own `.venv/bin/ruff`, under `pwd -P`. No bare-name lookup, no self-recursion: the resolved
target is an absolute path constructed by the upward walk.

```
$ WT="$(git rev-parse --show-toplevel)"
$ cd docs
$ nix develop "$WT" --command ruff --version
ruff 0.15.20
```

The walk survives `tox.ini`'s `changedir = docs` — invoked from `docs/`, the shim still climbs to
the checkout root and finds `.venv/bin/ruff` there.

```
$ .venv/bin/ruff --version
Could not start dynamically linked executable: .venv/bin/ruff
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
$ echo "exit: $?"
exit: 127
```

Outside-sandbox control: still fails at rc 127, exactly as before the edit — proving the shim, not
a repair of the file itself, is what makes `ruff` run.

```
$ grep -c 'buildFHSEnvChroot' flake.nix
0
$ git diff --quiet HEAD -- flake.lock
$ echo "exit: $?"
exit: 0
```

`flake.lock` is unchanged and no reference to the removed `buildFHSEnvChroot` alias exists.
