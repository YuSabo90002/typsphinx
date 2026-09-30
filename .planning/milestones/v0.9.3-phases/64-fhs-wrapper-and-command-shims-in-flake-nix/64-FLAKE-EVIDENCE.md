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

## Roster expansion (DIAGNOSTIC)

The single tracer shim was replaced with `venvShimNames = [ "tox" "ruff" "black" "mypy" "pytest"
"sphinx-build" ]` mapped over `pkgs.writeShellScriptBin`, plus `uvShim` — D-02's sole exception
with a second, fixed-store-path leg. `packages` on Linux became `[ uvShim ] ++ venvShims`; darwin
kept its byte-identical `[ nodejs pnpm git python3 uv ]` list via
`pkgs.lib.optionals (!pkgs.stdenv.hostPlatform.isLinux) [ pkgs.uv ]`.

For each of the seven names, `command -v <name>`, `<name> --version`, and the xtrace `+ exec` line
from `bash -x "$(command -v <name>)" --version 2>&1`:

```
== tox ==
$ command -v tox
/nix/store/s7rlc9zr6p3c03b9498jabqwjrhp13qz-tox/bin/tox
$ tox --version
4.56.1 from .../typsphinx/.claude/worktrees/agent-ab7ba88fa3bf417f2/.venv/lib/python3.13/site-packages/tox/__init__.py
registered plugins:
    tox-uv-bare-1.35.2 at .../tox_uv/plugin.py
+ exec /nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab7ba88fa3bf417f2/.venv/bin/tox --version

== ruff ==
$ command -v ruff
/nix/store/vp86ji36v1nyp4q8d85i49hpyz43zszq-ruff/bin/ruff
$ ruff --version
ruff 0.15.20
+ exec /nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab7ba88fa3bf417f2/.venv/bin/ruff --version

== black ==
$ command -v black
/nix/store/kl05v1f86vm0vwq00csz47rlbyxv1chg-black/bin/black
$ black --version
black, 26.5.1 (compiled: yes)
Python (CPython) 3.13.13
+ exec /nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab7ba88fa3bf417f2/.venv/bin/black --version

== mypy ==
$ command -v mypy
/nix/store/4pwm7pb8jxk68wprgwicyc00mbn7vz4w-mypy/bin/mypy
$ mypy --version
mypy 2.1.0 (compiled: yes)
+ exec /nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab7ba88fa3bf417f2/.venv/bin/mypy --version

== pytest ==
$ command -v pytest
/nix/store/jmwmq21z24kqhbff4b3clpj4agixph5p-pytest/bin/pytest
$ pytest --version
pytest 9.1.1
+ exec /nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab7ba88fa3bf417f2/.venv/bin/pytest --version

== sphinx-build ==
$ command -v sphinx-build
/nix/store/0m5hj81l70ddxzkzjn643zyms08ccggm-sphinx-build/bin/sphinx-build
$ sphinx-build --version
sphinx-build 9.1.0
+ exec /nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab7ba88fa3bf417f2/.venv/bin/sphinx-build --version

== uv ==
$ command -v uv
/nix/store/f1y7m4b5vxrbwszkrni3yc2lv0x22zcj-uv/bin/uv
$ uv --version
uv 0.11.25 (x86_64-unknown-linux-gnu)
+ exec /nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run /nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv --version
```

Six xtrace lines name `<worktree>/.venv/bin/<tool>`; the `uv` line names a `/nix/store/…-uv-0.11.25/bin/uv`
path, because `.venv/bin/uv` does not exist before Phase 65 (D-02) — the walk falls through to leg 2,
the fixed store path.

```
$ nix develop . --command bash -c 'type -P uv'
/nix/store/f1y7m4b5vxrbwszkrni3yc2lv0x22zcj-uv/bin/uv
```

`type -P uv` inside the devShell prints the shim's own unversioned store path
(`/nix/store/f1y7m4b5vxrbwszkrni3yc2lv0x22zcj-uv/bin/uv`, no `-<version>` in the derivation name),
not a `uv-0.11.25`-suffixed nixpkgs store path — this is the NIX-06 ordering edge: the shim is the
first and only `uv` provider on the Linux devShell PATH.

All seven versions match the `uv.lock` pins re-read at run time: `ruff 0.15.20` (`uv.lock:1210`),
`black 26.5.1` (`uv.lock:95`), `mypy 2.1.0` (`uv.lock:727`), `pytest 9.1.1` (`uv.lock:1011`),
`tox 4.56.1` (`uv.lock:1395`), `sphinx-build 9.1.0` (`uv.lock:1266`); `uv 0.11.25` matches the
pinned nixpkgs store build (the session `uv` observed pre-edit).

## tox subprocess tree through the sandbox (DIAGNOSTIC)

Nested-entry and namespace-inheritance shakeout: `tox` runs inside the sandbox; `tox-uv-bare`
resolves `uv` from PATH, which is now the `uv` shim; that shim enters the sandbox again — a nested
entry (the wrapper exec'ing the wrapper).

```
$ test ! -e .tox && echo NO_TOX_DIR
NO_TOX_DIR

$ nix develop . --command tox -e lint
lint: venv> /nix/store/f1y7m4b5vxrbwszkrni3yc2lv0x22zcj-uv/bin/uv venv -p .../.venv/bin/python --allow-existing '--prompt=agent-ab7ba88fa3bf417f2[lint]' --python-preference system .../.tox/lint
lint: uv-sync> /nix/store/f1y7m4b5vxrbwszkrni3yc2lv0x22zcj-uv/bin/uv sync --locked --python-preference system --extra dev -p .../.venv/bin/python
lint: commands[0]> black --check .
All done! ✨ 🍰 ✨
355 files would be left unchanged.
lint: commands[1]> ruff check .
All checks passed!
  lint: OK (1.14=setup[0.18]+cmd[0.94,0.03] seconds)
  congratulations :) (1.26 seconds)
```

`tox -e lint` completed cleanly through the sandbox on the first attempt: `venv>` and `uv-sync>`
show `tox-uv-bare` invoking the `uv` shim's own resolved store path
(`/nix/store/f1y7m4b5vxrbwszkrni3yc2lv0x22zcj-uv/bin/uv`, the same unversioned shim path `type -P
uv` reported earlier) to create and sync `.tox/lint` — a nested entry into `typsphinx-fhs-run`
that worked without any change to `flake.nix`. Both `black --check .` and `ruff check .` ran and
passed, ending in `lint: OK` and `congratulations :)`. No design defect surfaced; no fix was
needed in this task.

## D-07

```
$ ls "$HOME/.cache/typst/packages/preview"
charged-ieee
codly
codly-languages
fontawesome
gentle-clues
linguify
mitex
modern-cv
xarrow

$ rm -rf docs/_build && nix develop . --command tox -e docs-pdf
...
typst: wrote 1 wrapper file(s) -- compile these: typsphinx.typ
Compiling 1 master document(s) to PDF...
Generated PDF: .../docs/_build/pdf/typsphinx.pdf
build succeeded, 5 warnings.
  docs-pdf: OK (4.32=setup[0.10]+cmd[4.22] seconds)
  congratulations :) (4.44 seconds)

$ test -s docs/_build/pdf/typsphinx.pdf && echo NON_EMPTY
NON_EMPTY

$ head -c 4 docs/_build/pdf/typsphinx.pdf
%PDF

$ ls "$HOME/.cache/typst/packages/preview"
charged-ieee
codly
codly-languages
fontawesome
gentle-clues
linguify
mitex
modern-cv
xarrow
```

`docs-pdf` produced a real PDF through the sandbox on the first attempt (nine packages already
warm in `~/.cache/typst/packages/preview`, unchanged before and after — no new fetch occurred).
The warm cache did all the work: the cold-cache TLS path stayed unexercised, so `pkgs.cacert` was
**not** added to `fhsRun`'s `targetPkgs` — D-07's investigation found no gap to fix. `$HOME`
reaching the sandbox is implied by the cache being read from `~/.cache/typst` at all; the build's
own success is the positive proof.

## NIX-06 — all four systems

Run on the FINAL `flake.nix` content (no step-1 or step-2 fix was needed):

```
$ nix flake check --all-systems --no-build
evaluating flake...
checking flake output 'devShells'...
checking derivation devShells.x86_64-linux.default...
derivation evaluated to /nix/store/vd4rms2m5kvjaazd3i78049k0s9a21g0-nix-shell.drv
checking derivation devShells.aarch64-linux.default...
derivation evaluated to /nix/store/gm6k80436paqz5hbr66cph11mrfhlnid-nix-shell.drv
checking derivation devShells.x86_64-darwin.default...
evaluation warning: Nixpkgs 26.05 will be the last release to support x86_64-darwin; see https://nixos.org/manual/nixpkgs/unstable/release-notes#x86_64-darwin-26.05
derivation evaluated to /nix/store/fclfls55m9lp06679x7zrw0qzjya834j-nix-shell.drv
checking derivation devShells.aarch64-darwin.default...
derivation evaluated to /nix/store/2m6y6pshri0vyw3jb5agczjnz9a92sxc-nix-shell.drv
all checks passed!
$ echo "exit: $?"
exit: 0

$ nix flake show --all-systems
git+file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab7ba88fa3bf417f2?ref=refs/heads/worktree-agent-ab7ba88fa3bf417f2&rev=350108b70e0694261bcbd5f67c869247b253fedf
└───devShells
    ├───aarch64-darwin
    │   └───default: development environment 'nix-shell'
    ├───aarch64-linux
    │   └───default: development environment 'nix-shell'
    ├───x86_64-darwin
    │   └───default: development environment 'nix-shell'
    └───x86_64-linux
        └───default: development environment 'nix-shell'
```

Both all-systems commands exit 0 and list all four systems' `devShells`.

```
$ nix eval --raw .#devShells.x86_64-linux.default.drvPath
/nix/store/vd4rms2m5kvjaazd3i78049k0s9a21g0-nix-shell.drv
$ nix eval --raw .#devShells.aarch64-linux.default.drvPath
/nix/store/gm6k80436paqz5hbr66cph11mrfhlnid-nix-shell.drv
$ nix eval --raw .#devShells.x86_64-darwin.default.drvPath
/nix/store/fclfls55m9lp06679x7zrw0qzjya834j-nix-shell.drv
$ nix eval --raw .#devShells.aarch64-darwin.default.drvPath
/nix/store/2m6y6pshri0vyw3jb5agczjnz9a92sxc-nix-shell.drv
```

Both darwin values are byte-identical to Task 1's pre-edit values and to the planning-time values
(`fclfls55m9lp06679x7zrw0qzjya834j-nix-shell.drv`, `2m6y6pshri0vyw3jb5agczjnz9a92sxc-nix-shell.drv`)
— the NIX-06 empty edge: the Linux-only additions are the empty list on darwin. Both Linux values
differ from their pre-edit values (`xbhqkzmnak21qk9j8ph0f00b8w65jr9l` → `vd4rms2m5kvjaazd3i78049k0s9a21g0`
for x86_64-linux; `z9yf853g0b6yfk5zf0x0jzvankdn9l34` → `gm6k80436paqz5hbr66cph11mrfhlnid` for
aarch64-linux) — the shims landed.

```
$ nix eval --json .#devShells.x86_64-linux.default.nativeBuildInputs --apply 'map (p: p.name)'
["nodejs-24.16.0","pnpm-11.9.0","git-2.54.0","python3-3.13.13","uv","tox","ruff","black","mypy","pytest","sphinx-build"]

$ nix eval --json .#devShells.x86_64-darwin.default.nativeBuildInputs --apply 'map (p: p.name)'
["nodejs-24.16.0","pnpm-11.9.0","git-2.54.0","python3-3.13.13","uv-0.11.25"]

$ nix eval --json .#devShells.aarch64-darwin.default.nativeBuildInputs --apply 'map (p: p.name)'
["nodejs-24.16.0","pnpm-11.9.0","git-2.54.0","python3-3.13.13","uv-0.11.25"]
```

`x86_64-linux` reads exactly the eleven-name array `nodejs-24.16.0, pnpm-11.9.0, git-2.54.0,
python3-3.13.13, uv, tox, ruff, black, mypy, pytest, sphinx-build` — one `uv`, no `uv-<version>`
entry (the NIX-06 adjacency edge). Both darwin systems read exactly the pre-edit five-name array,
byte-for-byte.

```
$ grep -c 'LC_ALL' flake.nix
0
$ grep -c 'clearenv' flake.nix
0
$ grep -c 'patchelf' flake.nix
0
$ grep -c 'pkgs.ruff' flake.nix
0
$ git diff --quiet HEAD -- flake.lock
$ echo "exit: $?"
exit: 0
```

No locale variable, env-clearing flag, ELF-patch tool, or nixpkgs' own `ruff` package appears
anywhere in `flake.nix`; `flake.lock` remains unchanged — no flake input was added.

**Darwin verification status, stated plainly:** darwin *evaluation* is proven here — both drvPaths
are byte-identical to the pre-edit baseline and both package censuses are unchanged — but darwin
*execution* (actually running `nix develop` or the shims on a darwin machine) is unverified by
construction, per ROADMAP constraint 8. This repository has zero CI coverage for `nix`/`flake`, and
no darwin machine is available to this phase. Phase 68's DOC-21 writes this up; this plan adds no
documentation comments to `flake.nix` beyond what the code needs.

## Session relaunch required before wave 2

The Claude Code session that ran this plan predates the `flake.nix` edit, and its PATH carries no
shim (orchestrator note 3) — every shim invocation recorded in this evidence file was routed
through `nix develop . --command …` and labelled DIAGNOSTIC for exactly this reason.

After this plan merges into the main checkout, the maintainer should open a terminal in
`/home/yuta/Documents/typsphinx` so direnv re-evaluates the flake. The maintainer then confirms
that `command -v ruff` prints a `/nix/store/…-ruff/bin/ruff` path, launches Claude Code from that
same shell, and re-runs `/gsd-execute-phase 64`.

Plans 64-02 and 64-03 carry a precondition that halts otherwise. No per-worktree `direnv allow` and
no `nix develop --command` wrapper around the provisioning line is involved; D-09 rejects both.

