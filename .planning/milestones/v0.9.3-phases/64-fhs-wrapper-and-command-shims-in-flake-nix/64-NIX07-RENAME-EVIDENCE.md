# Phase 64 Plan 03 Task 1 — NIX-07 Rename Proof Evidence

**Measured shape:** the genuine D-09 shape — the inherited session PATH of a Claude Code session
launched after 64-01's `flake.nix` merged, running inside a git worktree nested in the main
checkout. No `nix develop --command` wrapper is used anywhere in this file; every shim invocation
below runs the shim exactly as it is reachable on this session's own `PATH`.

## Head check and provisioning

- Timestamp (UTC): `2026-09-11T15:17:47Z`
- `pwd -P`: `/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa549e5cc51035b0c` — under
  `/home/yuta/Documents/typsphinx/.claude/worktrees/`, confirming this is the nested worktree
  location that makes an escape into the main checkout observable.
- `test -f .git`: true (a worktree `gitdir:` pointer file, not a directory).
- `command -v ruff`: `/nix/store/vp86ji36v1nyp4q8d85i49hpyz43zszq-ruff/bin/ruff`
- `command -v uv`: `/nix/store/f1y7m4b5vxrbwszkrni3yc2lv0x22zcj-uv/bin/uv`
- Both files confirmed (via `grep -l typsphinx-fhs-run`) to contain `typsphinx-fhs-run` in their
  body — the D-09 precondition is met without any `nix develop --command` diagnostic wrapper.

Provisioning: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` ran to completion,
installing this worktree's own `.venv` including `ruff==0.15.20`, `black==26.5.1`, `mypy==2.1.0`,
`pytest==9.1.1`, `tox==4.56.1`, `sphinx==9.1.0`, `tox-uv-bare==1.35.2` — matching `uv.lock`'s pins.

## Shim bodies

All seven shim names resolve to `/nix/store/…` paths (the Nix-store outputs of each
`writeShellScriptBin` derivation). Verbatim bodies, `cat "$(command -v <name>)"`:

### `uv`

```sh
#!/nix/store/zh1ijdhb6gng1509b1zrilb6xlzx60j6-bash-5.3p9/bin/bash
set -eu
start="$PWD"
dir="$PWD"
while :; do
  if [ -x "$dir/.venv/bin/uv" ]; then
    exec "/nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run" "$dir/.venv/bin/uv" "$@"
  fi
  if [ -e "$dir/.git" ]; then
    break
  fi
  if [ "$dir" = / ]; then
    break
  fi
  dir="$(dirname "$dir")"
done
exec "/nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run" "/nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv" "$@"
```

Exec line through `typsphinx-fhs-run` with an absolute target: the walk variable for leg 1
(`$dir/.venv/bin/uv`), the fixed `/nix/store/…-uv-0.11.25/bin/uv` store path for leg 2 (D-02's sole
documented exception). No `command -v`, `which` or bare-name lookup anywhere in the body.

### `tox`

```sh
#!/nix/store/zh1ijdhb6gng1509b1zrilb6xlzx60j6-bash-5.3p9/bin/bash
set -eu
start="$PWD"
dir="$PWD"
while :; do
  if [ -x "$dir/.venv/bin/tox" ]; then
    exec "/nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run" "$dir/.venv/bin/tox" "$@"
  fi
  if [ -e "$dir/.git" ]; then
    break
  fi
  if [ "$dir" = / ]; then
    break
  fi
  dir="$(dirname "$dir")"
done
echo "typsphinx-shim: tox: no executable .venv/bin/tox found walking up from $start (stopped at $dir); provision with: env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev" >&2
exit 127
```

Exec line through `typsphinx-fhs-run` with the absolute `$dir/.venv/bin/tox` walk-variable target;
D-03's no-fallback on-stop fragment (`typsphinx-shim:` message, `exit 127`). No PATH lookup of any
tool name anywhere in the body.

### `ruff`

```sh
#!/nix/store/zh1ijdhb6gng1509b1zrilb6xlzx60j6-bash-5.3p9/bin/bash
set -eu
start="$PWD"
dir="$PWD"
while :; do
  if [ -x "$dir/.venv/bin/ruff" ]; then
    exec "/nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run" "$dir/.venv/bin/ruff" "$@"
  fi
  if [ -e "$dir/.git" ]; then
    break
  fi
  if [ "$dir" = / ]; then
    break
  fi
  dir="$(dirname "$dir")"
done
echo "typsphinx-shim: ruff: no executable .venv/bin/ruff found walking up from $start (stopped at $dir); provision with: env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev" >&2
exit 127
```

Same shape as `tox`, absolute `.venv/bin/ruff` target, D-03 on-stop, no PATH lookup.

### `black`

```sh
#!/nix/store/zh1ijdhb6gng1509b1zrilb6xlzx60j6-bash-5.3p9/bin/bash
set -eu
start="$PWD"
dir="$PWD"
while :; do
  if [ -x "$dir/.venv/bin/black" ]; then
    exec "/nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run" "$dir/.venv/bin/black" "$@"
  fi
  if [ -e "$dir/.git" ]; then
    break
  fi
  if [ "$dir" = / ]; then
    break
  fi
  dir="$(dirname "$dir")"
done
echo "typsphinx-shim: black: no executable .venv/bin/black found walking up from $start (stopped at $dir); provision with: env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev" >&2
exit 127
```

Same shape, absolute `.venv/bin/black` target, D-03 on-stop, no PATH lookup.

### `mypy`

```sh
#!/nix/store/zh1ijdhb6gng1509b1zrilb6xlzx60j6-bash-5.3p9/bin/bash
set -eu
start="$PWD"
dir="$PWD"
while :; do
  if [ -x "$dir/.venv/bin/mypy" ]; then
    exec "/nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run" "$dir/.venv/bin/mypy" "$@"
  fi
  if [ -e "$dir/.git" ]; then
    break
  fi
  if [ "$dir" = / ]; then
    break
  fi
  dir="$(dirname "$dir")"
done
echo "typsphinx-shim: mypy: no executable .venv/bin/mypy found walking up from $start (stopped at $dir); provision with: env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev" >&2
exit 127
```

Same shape, absolute `.venv/bin/mypy` target, D-03 on-stop, no PATH lookup.

### `pytest`

```sh
#!/nix/store/zh1ijdhb6gng1509b1zrilb6xlzx60j6-bash-5.3p9/bin/bash
set -eu
start="$PWD"
dir="$PWD"
while :; do
  if [ -x "$dir/.venv/bin/pytest" ]; then
    exec "/nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run" "$dir/.venv/bin/pytest" "$@"
  fi
  if [ -e "$dir/.git" ]; then
    break
  fi
  if [ "$dir" = / ]; then
    break
  fi
  dir="$(dirname "$dir")"
done
echo "typsphinx-shim: pytest: no executable .venv/bin/pytest found walking up from $start (stopped at $dir); provision with: env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev" >&2
exit 127
```

Same shape, absolute `.venv/bin/pytest` target, D-03 on-stop, no PATH lookup.

### `sphinx-build`

```sh
#!/nix/store/zh1ijdhb6gng1509b1zrilb6xlzx60j6-bash-5.3p9/bin/bash
set -eu
start="$PWD"
dir="$PWD"
while :; do
  if [ -x "$dir/.venv/bin/sphinx-build" ]; then
    exec "/nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run" "$dir/.venv/bin/sphinx-build" "$@"
  fi
  if [ -e "$dir/.git" ]; then
    break
  fi
  if [ "$dir" = / ]; then
    break
  fi
  dir="$(dirname "$dir")"
done
echo "typsphinx-shim: sphinx-build: no executable .venv/bin/sphinx-build found walking up from $start (stopped at $dir); provision with: env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev" >&2
exit 127
```

Same shape, absolute `.venv/bin/sphinx-build` target, D-03 on-stop, no PATH lookup.

**Per-body statement:** all seven bodies `exec` through the absolute
`/nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run` path. Six of
the seven (`tox`, `ruff`, `black`, `mypy`, `pytest`, `sphinx-build`) resolve their own target
exclusively through the upward-walk `$dir` variable (never a bare tool name); `uv` resolves through
the same walk variable for leg 1 and a fixed nixpkgs store path for leg 2. No body contains
`command -v`, `which`, `type -P`, or any other PATH lookup of a tool name.

## Escape positive control

The main checkout's own runnable `.venv/bin/ruff` — the binary an unbounded walk would reach if the
`.git`-boundary stop did not exist — is a real, executable ELF:

```
$ ls -l /home/yuta/Documents/typsphinx/.venv/bin/ruff
-rwxr-xr-x 1 yuta users 27906360  7月 11 20:01 /home/yuta/Documents/typsphinx/.venv/bin/ruff

$ /home/yuta/Documents/typsphinx/.venv/bin/ruff --version
ruff 0.15.20
exit=0
```

This is the discriminating control: an escape past this worktree's own `.git` boundary into the
main checkout WOULD print `ruff 0.15.20` and exit 0 — indistinguishable from a correct in-worktree
resolution by version string alone. The rename test below is therefore run from *this* worktree
(nested under the main checkout), where a bounded walk stops at the worktree's own `.git` file and
an unbounded walk would silently reach this main-checkout binary instead of failing.

## Rename test

Procedure per tool: `mv .venv/bin/<t> .venv/bin/<t>.nix07-bak`, `timeout 30 <t> --version` (stdout
and stderr captured separately, rc recorded), then unconditional restore via a `trap` on the shell
script's `EXIT` (T-64-11 — the restore always fires even if the timed command's own exit status is
nonzero), followed by a fresh `<t> --version` confirming the restored version.

| Tool | Start dir | rc | stderr line | stdout bytes | Wall (s) | Restored version |
|------|-----------|----|--------------|---------------|----------|-------------------|
| `tox` | worktree root | 127 | `typsphinx-shim: tox: no executable .venv/bin/tox found walking up from <worktree root> (stopped at <worktree root>); provision with: env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` | 0 (empty) | 0.00 | `4.56.1` (+ `tox-uv-bare-1.35.2` plugin line) |
| `ruff` | worktree root | 127 | `typsphinx-shim: ruff: no executable .venv/bin/ruff found walking up from <worktree root> (stopped at <worktree root>); provision with: env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` | 0 (empty) | 0.00 | `ruff 0.15.20` |
| `black` | worktree root | 127 | `typsphinx-shim: black: no executable .venv/bin/black found walking up from <worktree root> (stopped at <worktree root>); provision with: env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` | 0 (empty) | 0.00 | `black, 26.5.1 (compiled: yes)` / `Python (CPython) 3.14.4` |
| `mypy` | worktree root | 127 | `typsphinx-shim: mypy: no executable .venv/bin/mypy found walking up from <worktree root> (stopped at <worktree root>); provision with: env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` | 0 (empty) | 0.00 | `mypy 2.1.0 (compiled: yes)` |
| `pytest` | worktree root | 127 | `typsphinx-shim: pytest: no executable .venv/bin/pytest found walking up from <worktree root> (stopped at <worktree root>); provision with: env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` | 0 (empty) | 0.00 | `pytest 9.1.1` |
| `sphinx-build` | worktree root | 127 | `typsphinx-shim: sphinx-build: no executable .venv/bin/sphinx-build found walking up from <worktree root> (stopped at <worktree root>); provision with: env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` | 0 (empty) | 0.00 | `sphinx-build 9.1.0` |
| `ruff` (from `docs/`) | `<worktree root>/docs` | 127 | `typsphinx-shim: ruff: no executable .venv/bin/ruff found walking up from <worktree root>/docs (stopped at <worktree root>); provision with: env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` | 0 (empty) | 0.00 | `ruff 0.15.20` |

`<worktree root>` = `/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa549e5cc51035b0c`.

All seven rows: rc 127, exactly one `typsphinx-shim: <tool>:` stderr line naming the worktree root
as both start and stop directory (docs/ row: start `<worktree root>/docs`, stop `<worktree root>`
— confirming the walk climbs one level and halts at the worktree's own `.git` file), zero stdout
bytes, well under the 30-second timeout, and the restored `--version` output matches `uv.lock`'s
pinned version in every case. No rc 124 (hang), no version string printed by a renamed run (no
fall-through to the main checkout's runnable `.venv/bin/ruff` recorded above as the positive
control), and no rc other than 127.

`.venv/bin` at the end of this step holds all six targets (`tox`, `ruff`, `black`, `mypy`,
`pytest`, `sphinx-build`), confirmed by `ls -l`.

## uv leg order

With no `.venv/bin/uv` present (confirmed: `test -e .venv/bin/uv` → absent, matching D-02's
"`.venv/bin/uv` does not exist today" measurement), the xtrace of the `uv` shim names the fixed
nixpkgs store path — leg 2:

```
$ bash -x "$(command -v uv)" --version 2>&1 | grep '^+ exec'
+ exec /nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run /nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv --version
```

A `.venv/bin/uv` probe script was created — a two-line `sh` script (`#!/bin/sh` +
`echo nix07-leg1-probe`), **not a link to any binary**:

```sh
#!/bin/sh
echo nix07-leg1-probe
```

`uv --version` from the worktree root:

```
$ uv --version
nix07-leg1-probe
```

`uv --version` from `docs/`:

```
$ cd docs && uv --version
nix07-leg1-probe
```

Leg 1 wins when present, from both the worktree root and from `docs/` (the walk works identically
to the six strict shims). The probe script was then deleted (`rm .venv/bin/uv`), and `uv --version`
re-confirmed the store uv:

```
$ uv --version
uv 0.11.25 (x86_64-unknown-linux-gnu)
```

`.venv/bin/uv` is absent again at the end of this step (`test ! -e .venv/bin/uv` holds).

## Boundary, encoding and ordering probe (outside the repository)

Scratch tree created via `mktemp -d` under `/tmp` (`TMPDIR` unset this session), containing a path
component with a space and a non-ASCII word (`nix07 probe/外側`), entirely outside the repository:

```
SCRATCH_ROOT=/tmp/tmp.AUR7pR85ZM
OUTER=/tmp/tmp.AUR7pR85ZM/nix07 probe/外側
```

Layout created:
- `<OUTER>/.venv/bin/ruff` — executable `sh` script: `echo "OUTER $0"`
- `<OUTER>/inner/.git` — empty file, standing in for a worktree's `.git` pointer
- `<OUTER>/inner/sub/` — empty directory

### a. Boundary (before an inner `.venv` exists)

From `<OUTER>/inner/sub`:

```
rc=127
stdout: []
stderr: [typsphinx-shim: ruff: no executable .venv/bin/ruff found walking up from /tmp/tmp.AUR7pR85ZM/nix07 probe/外側/inner/sub (stopped at /tmp/tmp.AUR7pR85ZM/nix07 probe/外側/inner); provision with: env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev]
```

The walk stops at `inner`'s `.git` file and never reaches `<OUTER>`'s own `.venv/bin/ruff` one
level further up — exactly the boundary NIX-07 requires.

### b. Ordering and encoding

`<OUTER>/inner/.venv/bin/ruff` added — executable `sh` script: `echo "INNER $0"`. From
`<OUTER>/inner/sub`:

```
output: [INNER /tmp/tmp.AUR7pR85ZM/nix07 probe/外側/inner/.venv/bin/ruff]
```

The nearest `.venv` wins (`inner`'s, not `OUTER`'s), and the full path — including the space and
the non-ASCII `外側` component — survives intact through the sandbox's `exec` chain, in `$0`.

### c. From `<OUTER>` itself

```
output: [OUTER /tmp/tmp.AUR7pR85ZM/nix07 probe/外側/.venv/bin/ruff]
```

`<OUTER>`'s own `.venv/bin/ruff` resolves immediately (the walk finds a match at its own starting
directory), again with the space and non-ASCII component intact in `$0`.

### Cleanup

```
CLEANUP OK: test ! -e /tmp/tmp.AUR7pR85ZM confirmed
```

The whole scratch tree was removed, confirmed absent by `test ! -e`. Per D-05, none of these files
ever entered the repository and none became a committed script.

## Final state

- `git status --porcelain` over the scope-fenced paths (`flake.nix flake.lock typsphinx tests
  scripts .github CLAUDE.md tox.ini pyproject.toml uv.lock`) is empty.
- `.venv/bin` holds all six targets (`tox`, `ruff`, `black`, `mypy`, `pytest`, `sphinx-build`) and
  no `uv` (`test ! -e .venv/bin/uv` holds).
- `ruff --version` prints `ruff 0.15.20`.

Every shim is shown to resolve by absolute path, bounded at its checkout root. A missing target
fails loud at 127 rather than hanging, recursing, or escaping to the main checkout's runnable
copy. `uv`'s leg order, quoting and nearest-wins ordering are each proven.
