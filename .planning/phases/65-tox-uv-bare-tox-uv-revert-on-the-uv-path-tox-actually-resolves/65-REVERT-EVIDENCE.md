Measured shape: executor worktree, Phase 64 shims inherited from the session PATH; no nix develop, no direnv exec, never the main checkout.

## Head check

```
$ date -u +%FT%TZ
2026-09-12T07:29:47Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ca8472e956ebe27

$ test -f .git; echo "exit:$?"
exit:0

$ test ! -e .venv; echo "exit:$?"
exit:0

$ test ! -e .tox; echo "exit:$?"
exit:0

$ grep -c 'tox-uv-bare>=1.35,<2' pyproject.toml
1

$ grep -c '^name = "uv"$' uv.lock
0
```

Precondition met: the pre-revert pin is present and no `uv` lock block exists yet.

```
$ command -v uv
/nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv
$ grep -c typsphinx-fhs-run /nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv
2

$ command -v tox
/nix/store/r70g13f57bbrw66k56dlqk9bbbcpch33-tox/bin/tox
$ grep -c typsphinx-fhs-run /nix/store/r70g13f57bbrw66k56dlqk9bbbcpch33-tox/bin/tox
1

$ command -v pytest
/nix/store/7q7lwxpw3xlz4h5rwka4nq0rjk1191yh-pytest/bin/pytest
$ grep -c typsphinx-fhs-run /nix/store/7q7lwxpw3xlz4h5rwka4nq0rjk1191yh-pytest/bin/pytest
1

$ command -v ruff
/nix/store/vxcr1f2x7ywkyvwli0sykhgwsmkg800k-ruff/bin/ruff
$ grep -c typsphinx-fhs-run /nix/store/vxcr1f2x7ywkyvwli0sykhgwsmkg800k-ruff/bin/ruff
1

$ command -v black
/nix/store/axxz4wqgrh8dwvv1qd3j3v9668qp8l4a-black/bin/black
$ grep -c typsphinx-fhs-run /nix/store/axxz4wqgrh8dwvv1qd3j3v9668qp8l4a-black/bin/black
1
```

All five shim bodies name `typsphinx-fhs-run`, at least once.

```
$ grep -o '/nix/store/[a-zA-Z0-9._-]*typsphinx-fhs-run[a-zA-Z0-9._/-]*' /nix/store/vxcr1f2x7ywkyvwli0sykhgwsmkg800k-ruff/bin/ruff | head -5
/nix/store/99fm4lqkp4kab20d3blfbwajnprmlbfx-typsphinx-fhs-run/bin/typsphinx-fhs-run

$ FSH=/nix/store/99fm4lqkp4kab20d3blfbwajnprmlbfx-typsphinx-fhs-run/bin/typsphinx-fhs-run
$ "$FSH" /bin/sh -c 'test -e /usr/lib/libz.so.1'; echo "exit:$?"
exit:0

$ printenv TOX_UV_PATH; echo "exit:$?"
exit:1
```

The FHS rootfs carries `/usr/lib/libz.so.1` and `TOX_UV_PATH` is unset (`exit:1`).

## Provisioning on the pre-revert tree

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
Using CPython 3.14.4
Creating virtual environment at: .venv
Resolved 89 packages in 0.58ms
   Building typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ca8472e956ebe27
      Built typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ca8472e956ebe27
Prepared 1 package in 478ms
Installed 79 packages in 48ms
 ... (79 packages, including tox-uv-bare==1.35.2, tox==4.56.1, pytest==9.1.1)

$ cat .venv/pyvenv.cfg
home = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
implementation = CPython
uv = 0.11.25
version_info = 3.14
include-system-site-packages = false
prompt = typsphinx

$ uv run python -c 'import typsphinx,os;print(os.path.realpath(typsphinx.__file__))'
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ca8472e956ebe27/typsphinx/__init__.py

$ test ! -e .venv/bin/uv; echo "exit:$?"
exit:0

$ uv --version
uv 0.11.25 (x86_64-unknown-linux-gnu)
```

The provisioning command was exactly `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, with no interpreter flag. `pyvenv.cfg`'s `home` names the uv-managed cp3.14 interpreter and `version_info = 3.14`. `typsphinx.__file__` resolves inside this worktree, matching `pwd -P` above. `.venv/bin/uv` is absent (tox-uv-bare pulls in no `uv` package). This is the D-05 **before** value: `uv 0.11.25`, taken through the shim's second leg (nixpkgs uv).

## Gate inversion RED

`tests/test_toolchain_config_gate.py::test_dev_extra_pins_tox_uv_bare_not_tox_uv` was renamed to
`test_dev_extra_pins_tox_uv_not_tox_uv_bare`, its two `canonicalize_name(...)` assertions swapped
(now requiring `tox-uv` present and `tox-uv-bare` absent, both on the normalized distribution
name), and its function docstring / the module docstring's G5 paragraph rewritten to describe the
Phase 65 revert. The `Requirement` parse loop, its `raise AssertionError(...) from e` chaining, and
`canonicalize_name` mechanism are untouched. This was done BEFORE the pin moved:

```
$ uv run pytest tests/test_toolchain_config_gate.py -q
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ca8472e956ebe27
configfile: pyproject.toml
plugins: cov-7.1.0
collected 4 items

tests/test_toolchain_config_gate.py ..F.                                 [100%]

=================================== FAILURES ===================================
__________________ test_dev_extra_pins_tox_uv_not_tox_uv_bare __________________
...
E       AssertionError: dev extra does not contain 'tox-uv' (on normalized distribution name) -- ...
E       assert 'tox-uv' in {'black', 'build', 'mypy', 'pillow', 'pre-commit', 'pypdf', ...}
E        +  where 'tox-uv' = canonicalize_name('tox-uv')

tests/test_toolchain_config_gate.py:344: AssertionError
=========================== short test summary info ============================
FAILED tests/test_toolchain_config_gate.py::test_dev_extra_pins_tox_uv_not_tox_uv_bare
========================= 1 failed, 3 passed in 0.04s ==========================
```

RED confirmed: `1 failed, 3 passed`, the failing node is `test_dev_extra_pins_tox_uv_not_tox_uv_bare`. The pin had not moved yet, so this `uv run`'s implicit lock is a no-op (the failure is purely the inverted assertion against the still-`tox-uv-bare` pyproject.toml).

## TOX-01 lock regeneration

The pin swap (one token in each file):

```
pyproject.toml:38   "tox-uv-bare>=1.35,<2",  ->  "tox-uv>=1.35,<2",
tox.ini:11           requires = tox-uv-bare~=1.35  ->  requires = tox-uv~=1.35
```

No other byte of either file changed. `tox.ini` lines 4-10 keep naming `tox-uv-bare` (DOC-20's, Phase 68, per D-06).

Lock regeneration, with no `uv run`, no `uv sync` and no `tox` run between the pin swap and this step:

```
$ test ! -e .venv/bin/uv; echo "exit:$?"
exit:0

$ uv --version
uv 0.11.25 (x86_64-unknown-linux-gnu)

$ sha256sum uv.lock
2fbb8794c4770b46cbfc96bc367e6658471d5fb9517f62cb7054a7e7e6d65850  uv.lock

$ uv lock
Resolved 91 packages in 711ms
Added tox-uv v1.36.0
Updated tox-uv-bare v1.35.2 -> v1.36.0
Added uv v0.12.13
```

LOCK_REGENERATED_BY = uv 0.11.25 (x86_64-unknown-linux-gnu)

```
$ sed -n 1,3p uv.lock
version = 1
revision = 3
requires-python = ">=3.12"

$ grep -A1 '^name = "tox-uv"$' uv.lock
name = "tox-uv"
version = "1.36.0"

$ grep -A1 '^name = "tox-uv-bare"$' uv.lock
name = "tox-uv-bare"
version = "1.36.0"

$ grep -A1 '^name = "uv"$' uv.lock
name = "uv"
version = "0.12.13"

$ git diff --stat uv.lock
 uv.lock | 48 +++++++++++++++++++++++++++++++++++++++++++-----
 1 file changed, 43 insertions(+), 5 deletions(-)
```

`Added tox-uv v1.36.0` / `Updated tox-uv-bare v1.35.2 -> v1.36.0` / `Added uv v0.12.13`, recorded
verbatim. Header stays `version = 1` / `revision = 3`. `tox-uv` and `tox-uv-bare` carry the same
version (`1.36.0`). No `--upgrade`, no `--upgrade-package`, no pin, no hand edit — plain `uv lock`.

## D-05 uv before and after

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --locked
Resolved 91 packages in 0.66ms
   Building typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ca8472e956ebe27
      Built typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ca8472e956ebe27
Prepared 1 package in 382ms
Uninstalled 2 packages in 0.58ms
Installed 4 packages in 1ms
 + tox-uv==1.36.0
 - tox-uv-bare==1.35.2
 + tox-uv-bare==1.36.0
 ~ typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ca8472e956ebe27)
 + uv==0.12.13
$ echo "exit:$?"
exit:0

$ test -x .venv/bin/uv; echo "exit:$?"
exit:0

$ uv --version
uv 0.12.13 (x86_64-unknown-linux-gnu)

$ uv lock --check
Resolved 91 packages in 3ms
$ echo "exit:$?"
exit:0

$ sha256sum uv.lock
dcf1b1c6d5c4f52584aac72870264f3bb100f202e10a1e1764dab25aa3608ed6  uv.lock
```

Before the sync, `uv --version` named the nixpkgs uv (`0.11.25`). After it, `.venv/bin/uv` exists
and `uv --version` names exactly the `uv.lock` `uv` version (`0.12.13`): the shim's first leg now
resolves `.venv/bin/uv`. `uv sync --extra dev --locked` and `uv lock --check` both exited 0. The
lock's sha256 (`dcf1b1c6…`) is unchanged from the digest immediately after `uv lock` ran through the
locked sync — `uv sync --locked` never rewrites the lock file, which is the adjacency of two uv
versions over one lock.

## Gate GREEN and lint

```
$ uv run pytest tests/test_toolchain_config_gate.py -q
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ca8472e956ebe27
configfile: pyproject.toml
plugins: cov-7.1.0
collected 4 items

tests/test_toolchain_config_gate.py ....                                 [100%]

============================== 4 passed in 0.03s ===============================

$ ruff check .
All checks passed!

$ black --check .
All done! ✨ 🍰 ✨
355 files would be left unchanged.
```

`4 passed`, `ruff check .` clean, `black --check .` clean (no reformat needed).

## TOX-02 tox starts

```
$ tox --showconfig -e py312 > /dev/null; echo "exit:$?"
exit:0

$ tox config -e py312 --core -k requires
[testenv:py312]

[tox]
requires =
  tox-uv~=1.35
  tox
```

`tox --showconfig -e py312` exits 0. `tox config -e py312 --core -k requires` lists
`  tox-uv~=1.35` (the one-entry, comma-free form, alongside tox's implicit own `tox` requirement).

Negative control (scratch copy, never committed, never in the tree):

```
$ cp tox.ini <scratch>/tox-comma.ini
$ sed -i 's/requires = tox-uv~=1.35/requires = tox-uv>=1.35,<2/' <scratch>/tox-comma.ini
$ grep -n '^requires' <scratch>/tox-comma.ini
11:requires = tox-uv>=1.35,<2

$ tox -c <scratch>/tox-comma.ini --showconfig -e py312 > <scratch>/comma-control.log 2>&1
$ echo "exit:$?"
exit:1
$ tail -n 4 <scratch>/comma-control.log
    raise InvalidRequirement(str(e)) from e
packaging.requirements.InvalidRequirement: Expected package name at the start of dependency specifier
    <2
    ^
```

The comma form exits 1 with `InvalidRequirement`, as expected (TOX-02 empty edge — one entry, no
comma, split into exactly one tox-uv requirement beside tox's own implicit entry; the comma form is
parsed as two bogus requirements and rejected).

Encoding edge (`packaging` definitions, not raw strings):

```
$ uv run python -c "
from packaging.utils import canonicalize_name
from packaging.specifiers import SpecifierSet
print('canonicalize:', canonicalize_name('Tox_UV'))
s1 = SpecifierSet('~=1.35')
s2 = SpecifierSet('>=1.35,<2')
for v in ['1.34.9', '1.35.0', '1.36.0', '1.99.0', '2.0.0']:
    print(v, v in s1, v in s2, (v in s1) == (v in s2))
"
canonicalize: tox-uv
1.34.9 False False True
1.35.0 True True True
1.36.0 True True True
1.99.0 True True True
2.0.0 False False True
```

`canonicalize_name('Tox_UV') == 'tox-uv'`. `SpecifierSet('~=1.35')` and `SpecifierSet('>=1.35,<2')`
agree on all five probe versions.

## Tracer tox-uv end to end

```
$ tox -e py312 -- tests/test_toolchain_config_gate.py
py312: venv> .venv/bin/uv venv -p cpython3.12 --allow-existing '--prompt=agent-a3ca8472e956ebe27[py312]' --python-preference system /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ca8472e956ebe27/.tox/py312
py312: uv-sync> .venv/bin/uv sync --locked --python-preference system --extra dev -p cpython3.12
py312: commands[0]> pytest tests/test_toolchain_config_gate.py
platform linux -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0 -- .../.tox/py312/bin/python3
collected 4 items

tests/test_toolchain_config_gate.py::test_uv_venv_lock_runner_requires_extras_forbids_deps PASSED [ 25%]
tests/test_toolchain_config_gate.py::test_testenv_package_is_editable_not_wheel PASSED [ 50%]
tests/test_toolchain_config_gate.py::test_dev_extra_pins_tox_uv_not_tox_uv_bare PASSED [ 75%]
tests/test_toolchain_config_gate.py::test_runtime_dependencies_carry_no_toolchain_package PASSED [100%]

============================== 4 passed in 0.04s ===============================
  py312: OK (0.64=setup[0.10]+cmd[0.53] seconds)
  congratulations :) (0.66 seconds)
```

`py312: OK`. The `venv>` and `uv-sync>` lines both name `.venv/bin/uv` — resolved relative to this
worktree's own root (`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ca8472e956ebe27`),
i.e. `$(pwd -P)/.venv/bin/uv`, the bundled branch. The pre-revert run named the nixpkgs uv through
the PATH branch (`64-GAP-REMEASURE-EVIDENCE.md:255`); this run names the tree's own bundled uv
instead — the mechanism the revert restores.

## Revert commit

```
$ git add pyproject.toml tox.ini uv.lock tests/test_toolchain_config_gate.py
$ git commit -F <msg-file>
[worktree-agent-a3ca8472e956ebe27 d32eb5db] fix(65-01): revert tox-uv-bare to tox-uv now that the Phase 64 FHS shims dissolve QUA-04
 4 files changed, 114 insertions(+), 69 deletions(-)

$ git show --name-only --format='%H %s' HEAD
d32eb5db6219bf4917ab820a44562ba479e5fe71 fix(65-01): revert tox-uv-bare to tox-uv now that the Phase 64 FHS shims dissolve QUA-04

pyproject.toml
tests/test_toolchain_config_gate.py
tox.ini
uv.lock
```

REVERT_SHA = d32eb5db6219bf4917ab820a44562ba479e5fe71

`git show --name-only` lists exactly the four files: `pyproject.toml`, `tests/test_toolchain_config_gate.py`, `tox.ini`, `uv.lock`. `git diff --diff-filter=D --name-only HEAD~1 HEAD` is empty — no deletions.

## TOX-03 D-02 observation inside FHS

```
$ printenv TOX_UV_PATH; echo "exit:$?"
exit:1

$ P="$(pwd -P)"
$ echo "$P"
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ca8472e956ebe27

$ V="$(grep -A1 '^name = "uv"$' uv.lock | sed -n 's/^version = "\(.*\)"$/\1/p')"
$ echo "$V"
0.12.13

$ ls .tox 2>&1
CACHEDIR.TAG
py312
```

One cold `tox -vv -e py312 -r` was run through the shim, in the foreground, timeout 600000ms,
output redirected to a scratchpad log (never inside the tree):

```
$ tox -vv -e py312 -r > "$LOG" 2>&1; echo "exit:$?"
exit:0
$ wc -l "$LOG"
2021 /tmp/claude-1000/-home-yuta-Documents-typsphinx/61c1d12e-cf56-434d-829e-1f7fb406a3a1/scratchpad/tox-vv-py312-cold.log
$ sha256sum "$LOG"
9fa39170f58c764939d57b78168ac206ab3bfb5f47fb6b2372dfae75b2ec9ce4  /tmp/claude-1000/-home-yuta-Documents-typsphinx/61c1d12e-cf56-434d-829e-1f7fb406a3a1/scratchpad/tox-vv-py312-cold.log
```

Decisive lines, grepped verbatim from the log:

```
py312: 87 D using bundled uv from: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ca8472e956ebe27/.venv/bin/uv [tox_uv/_venv.py:237]
py312: 165 W venv> .venv/bin/uv venv -p cpython3.12 --allow-existing '--prompt=agent-a3ca8472e956ebe27[py312]' -v --python-preference system /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ca8472e956ebe27/.tox/py312 [tox/tox_env/api.py:485]
DEBUG uv 0.12.13 (x86_64-unknown-linux-gnu)
py312: 185 W uv-sync> .venv/bin/uv sync --locked --python-preference system --extra dev --reinstall -v -p cpython3.12 [tox/tox_env/api.py:485]
DEBUG uv 0.12.13 (x86_64-unknown-linux-gnu)
platform linux -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ca8472e956ebe27/.tox/py312/bin/python3
collecting ... collected 1548 items
================= 1543 passed, 5 skipped in 108.34s (0:01:48) ==================
  py312: OK (109.46=setup[0.57]+cmd[108.89] seconds)
```

```
$ grep -oE 'DEBUG uv [0-9]+\.[0-9]+\.[0-9]+' "$LOG" | sort -u
DEBUG uv 0.12.13

$ cat .tox/py312/pyvenv.cfg
home = /home/yuta/.local/share/uv/python/cpython-3.12-linux-x86_64-gnu/bin
implementation = CPython
uv = 0.12.13
version_info = 3.12
include-system-site-packages = false
prompt = agent-a3ca8472e956ebe27[py312]
```

Judgment against D-02:
- (a) The bundled-branch discovery line for `py312` names `$P/.venv/bin/uv` exactly
  (`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ca8472e956ebe27/.venv/bin/uv`) — MET.
- (b) Zero lines for the `py312` environment matching either of the two non-bundled discovery
  branches or tox's own self-provisioning path — MET (the log's other environments, e.g.
  `.tox/lint`, are out of scope for this observation, but py312's own lines carry none of those
  branches).
- (c) The unique DEBUG banner set for this run is exactly `DEBUG uv 0.12.13`, equal to `$V` — MET.
- (d) `py312: OK`, Python 3.12 pytest header, `collected 1548 items`, `1543 passed, 5 skipped` — MET.

**CONFIRMED — no DIVERGENT result.** Contrast with the pre-revert run (`64-GAP-REMEASURE-EVIDENCE.md:255`), whose `venv>` line named the nixpkgs uv through the non-bundled PATH-fallback discovery branch (`tox-uv-bare` pulls in no bundled `uv` package, so `find_uv_bin()` failed and tox fell back to `shutil.which()` resolution on PATH); this run's `venv>`/`uv-sync>` lines instead name this worktree's own `.venv/bin/uv` through the bundled branch, at exactly the `uv.lock` version — the mechanism this revert restores.

## TOX-03 D-03 isolated control outside FHS

CTRL_VENV = /tmp/claude-1000/-home-yuta-Documents-typsphinx/61c1d12e-cf56-434d-829e-1f7fb406a3a1/scratchpad/ctrl-venv

```
$ case "$CTRL" in "$(pwd -P)"/*) echo INSIDE ;; *) echo OUTSIDE ;; esac
OUTSIDE
```

### Interpreter provenance

```
$ PY="$(command -v python3)"
$ echo "$PY"
/nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin/python3
$ readlink -f "$PY"
/nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin/python3.13

$ "$PY" -m venv "$CTRL"
$ echo "exit:$?"
exit:0

$ cat "$CTRL/pyvenv.cfg"
home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
include-system-site-packages = false
version = 3.13.13
executable = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin/python3.13
command = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin/python3 -m venv /tmp/claude-1000/-home-yuta-Documents-typsphinx/61c1d12e-cf56-434d-829e-1f7fb406a3a1/scratchpad/ctrl-venv
```

The interpreter is a nix store path (not this worktree's `.venv`, not a uv-managed CPython), and
`pyvenv.cfg`'s `home` is under `/nix/store/` — the control is valid.

### Lock-pinned installs

```
$ grep -A1 '^name = "tox"$' uv.lock
name = "tox"
version = "4.56.1"
$ grep -A1 '^name = "tox-uv"$' uv.lock
name = "tox-uv"
version = "1.36.0"
$ grep -A1 '^name = "tox-uv-bare"$' uv.lock
name = "tox-uv-bare"
version = "1.36.0"
$ grep -A1 '^name = "uv"$' uv.lock
name = "uv"
version = "0.12.13"

$ uv pip install --python "$CTRL/bin/python" "tox==4.56.1" "tox-uv==1.36.0" "tox-uv-bare==1.36.0" "uv==0.12.13"
Using Python 3.13.13 environment at: /tmp/claude-1000/-home-yuta-Documents-typsphinx/61c1d12e-cf56-434d-829e-1f7fb406a3a1/scratchpad/ctrl-venv
Resolved 15 packages in 258ms
Installed 15 packages in 6ms
 + tox==4.56.1
 + tox-uv==1.36.0
 + tox-uv-bare==1.36.0
 + uv==0.12.13
 ... (11 more transitive packages)

$ uv pip list --python "$CTRL/bin/python" | grep -E '^(tox|tox-uv|tox-uv-bare|uv) '
tox              4.56.1
tox-uv           1.36.0
tox-uv-bare      1.36.0
uv               0.12.13

$ file "$CTRL/bin/uv"
/tmp/claude-1000/-home-yuta-Documents-typsphinx/61c1d12e-cf56-434d-829e-1f7fb406a3a1/scratchpad/ctrl-venv/bin/uv: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=26e8aa879683dd1454dd519591fbbc7fa4b91357, stripped
```

All four packages installed at exactly their `uv.lock` versions. `$CTRL/bin/uv` is a
dynamically-linked generic-linux ELF.

### Outside-FHS proof, same shell as the run

```
$ test -e /usr/lib/libz.so.1; echo "fhs-probe exit:$?"
fhs-probe exit:1

$ "$CTRL/bin/python" -c 'import sys;print(sys.executable, sys.version.split()[0])'
/tmp/claude-1000/-home-yuta-Documents-typsphinx/61c1d12e-cf56-434d-829e-1f7fb406a3a1/scratchpad/ctrl-venv/bin/python 3.13.13
```

The shell lacks `/usr/lib/libz.so.1` (outside FHS), and the control interpreter itself runs
successfully there — this is exactly what the earlier (invalid) control failed on
(`.venv/bin/python3`, a uv-managed generic-linux CPython), so it is proven not to fail here.

### The control run, by absolute path, no shim

```
$ grep -n '^requires' tox.ini
11:requires = tox-uv~=1.35

$ env -u TOX_UV_PATH PATH=/usr/bin:/bin "$CTRL/bin/python" -m tox -vv -e py312 --workdir "$CW" -r > "$S/ctrl.log" 2>&1
$ echo "exit:$?"
exit:127

$ head -n 5 "$S/ctrl.log"
ROOT: 306 D setup logging to DEBUG on pid 933992 [tox/report.py:229]
py312: 329 D using bundled uv from: /tmp/claude-1000/-home-yuta-Documents-typsphinx/61c1d12e-cf56-434d-829e-1f7fb406a3a1/scratchpad/ctrl-venv/bin/uv [tox_uv/_venv.py:237]
py313: 329 D using bundled uv from: /tmp/claude-1000/-home-yuta-Documents-typsphinx/61c1d12e-cf56-434d-829e-1f7fb406a3a1/scratchpad/ctrl-venv/bin/uv [tox_uv/_venv.py:237]
lint: 330 D using bundled uv from: /tmp/claude-1000/-home-yuta-Documents-typsphinx/61c1d12e-cf56-434d-829e-1f7fb406a3a1/scratchpad/ctrl-venv/bin/uv [tox_uv/_venv.py:237]
type: 330 D using bundled uv from: /tmp/claude-1000/-home-yuta-Documents-typsphinx/61c1d12e-cf56-434d-829e-1f7fb406a3a1/scratchpad/ctrl-venv/bin/uv [tox_uv/_venv.py:237]

$ grep -nE 'using bundled uv from|using system uv from PATH|using uv from TOX_UV_PATH|automatically provisioned|venv> |Could not start dynamically linked executable|exit [0-9]+ \(|py312: (OK|FAIL)' "$S/ctrl.log"
2:py312: 329 D using bundled uv from: /tmp/claude-1000/-home-yuta-Documents-typsphinx/61c1d12e-cf56-434d-829e-1f7fb406a3a1/scratchpad/ctrl-venv/bin/uv [tox_uv/_venv.py:237]
...
10:py312: 334 W venv> /tmp/claude-1000/-home-yuta-Documents-typsphinx/61c1d12e-cf56-434d-829e-1f7fb406a3a1/scratchpad/ctrl-venv/bin/uv venv -p cpython3.12 --allow-existing '--prompt=agent-a3ca8472e956ebe27[py312]' -v --python-preference system /tmp/claude-1000/-home-yuta-Documents-typsphinx/61c1d12e-cf56-434d-829e-1f7fb406a3a1/scratchpad/ctrl-tox-workdir/py312 [tox/tox_env/api.py:485]
11:Could not start dynamically linked executable: /tmp/claude-1000/-home-yuta-Documents-typsphinx/61c1d12e-cf56-434d-829e-1f7fb406a3a1/scratchpad/ctrl-venv/bin/uv
15:py312: 335 C exit 127 (0.00 seconds) /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ca8472e956ebe27> /tmp/claude-1000/-home-yuta-Documents-typsphinx/61c1d12e-cf56-434d-829e-1f7fb406a3a1/scratchpad/ctrl-venv/bin/uv venv ... pid=934024 [tox/execute/api.py:308]
17:  py312: FAIL code 127 (0.00 seconds)

$ ls "$CW"
CACHEDIR.TAG
py312

$ git status --porcelain
(empty)
```

### Judgment against D-03

- tox started — the bundled discovery line appears at all (line 2 onward) — MET.
- The bundled line names `$CTRL/bin/uv` exactly — MET.
- The first `exit [0-9]+ (` line (line 15) is the `$CTRL/bin/uv venv …` call — MET.
- `Could not start dynamically linked executable: $CTRL/bin/uv` is present (line 11), and
  `py312: FAIL code 127` (line 17) — MET.
- No non-bundled discovery branch or self-provisioning line appears anywhere in the `py312`
  transcript — MET.

**CLOSED — the control isolated the uv path.** Nothing failed before the `uv venv` exec: the
interpreter ran, tox started, environment resolution completed, and the FIRST subprocess
execution — `uv venv` — is what failed, immediately, on the binary itself. The tree is untouched
(`git status --porcelain` empty; `$CW` holds only the control's own side-car files).

## SC#3 literal and amended readings

**Literal reading (D-01).** SC#3's original text holds that `uv.find_uv_bin()` is "a different
function on a different code path" from the shimmed/`.venv` binary, and that the "bundled wheel"
and the "shimmed/`.venv` binary" compete for which `uv` a tox run resolves. Both clauses are
falsified by this file's own observations: `tox_uv/_venv.py`'s bundled step is literally
`from uv import find_uv_bin; return find_uv_bin()` — no binary ships inside the `tox-uv` wheel;
"bundled" means the PyPI `uv` dependency's own script. `find_uv_bin()` returns the CALLING
interpreter's own `bin/uv` — inside this worktree that is `.venv/bin/uv`, the exact same file the
Phase 64 `uv` shim's first leg resolves. There is no second, competing "shimmed/`.venv`" binary;
both mechanisms name one file. The dichotomy the literal text poses does not exist.

**Amended reading (D-01, per `65-CONTEXT.md`'s AMENDED block).** What separates a shell-level
`find_uv_bin()` probe from a real tox run is only the calling process — the substantive
requirement is to observe the branch, path and version from **inside** a real tox run, plus an
isolated outside-FHS control proving the failure is the uv path and nothing earlier. Under this
reading:
- **Branch fired:** the bundled branch (`tox_uv/_venv.py:237`'s `using bundled uv from:` line), in
  both the D-02 observation and the D-03 control — never the `TOX_UV_PATH` branch, never the
  PATH-fallback branch.
- **Resolved path:** `<this worktree>/.venv/bin/uv` inside FHS (D-02); `/tmp/claude-1000/-home-yuta-Documents-typsphinx/61c1d12e-cf56-434d-829e-1f7fb406a3a1/scratchpad/ctrl-venv/bin/uv` outside FHS
  (D-03) — each the calling interpreter's own `bin/uv`, per `find_uv_bin()`'s contract.
- **Version:** `uv 0.12.13`, exactly the `uv.lock` `uv` version, observed from uv's own `-v` banner
  inside the `tox -vv` transcript (D-02).
- **Environment outcome:** inside FHS, `py312: OK`, `1543 passed, 5 skipped` at the established
  baseline (D-02). Outside FHS, `py312: FAIL code 127` on the `uv venv` exec itself, with nothing
  earlier failing (D-03).
- **Control isolation:** the D-03 control resolves the SAME bundled branch to a generic-linux ELF
  the host cannot start — isolating exactly the uv-exec failure, unlike the earlier (invalid)
  control that died on the interpreter itself.

**Verdict (amended reading): SC#3 is MET.** No `TOX_UV_PATH` was set anywhere in this plan
(`git grep` over tracked files outside `.planning/` finds no match; `printenv TOX_UV_PATH` was
unset throughout). No DIVERGENT result occurred at either D-02 or D-03.

## Requirement closure

| Requirement | Status | Deciding section |
|---|---|---|
| TOX-01 | MET | `## TOX-01 lock regeneration`, `## D-05 uv before and after`, `## Revert commit` |
| TOX-02 | MET | `## TOX-02 tox starts` |
| TOX-03 | MET | `## TOX-03 D-02 observation inside FHS`, `## TOX-03 D-03 isolated control outside FHS`, `## SC#3 literal and amended readings` |

TOX-04 belongs to plan 65-02 and carries no row here.
