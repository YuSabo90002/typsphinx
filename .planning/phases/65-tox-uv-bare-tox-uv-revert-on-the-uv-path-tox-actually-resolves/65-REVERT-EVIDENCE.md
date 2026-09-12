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

`LOCK_REGENERATED_BY = uv 0.11.25 (x86_64-unknown-linux-gnu)`

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

`REVERT_SHA = d32eb5db6219bf4917ab820a44562ba479e5fe71`

`git show --name-only` lists exactly the four files: `pyproject.toml`, `tests/test_toolchain_config_gate.py`, `tox.ini`, `uv.lock`. `git diff --diff-filter=D --name-only HEAD~1 HEAD` is empty — no deletions.
