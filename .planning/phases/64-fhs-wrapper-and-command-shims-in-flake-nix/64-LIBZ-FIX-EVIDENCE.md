# Phase 64 Plan 05 — `libz.so.1` Fix Evidence

**Status paragraph (read before anything below).** The Claude Code session running this plan
predates its own `flake.nix` edit: its PATH was frozen at launch and carries 64-01's shims, which
embed the old rootfs `/nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run` (no
`targetPkgs`, no `libz.so.1`). That old rootfs is exactly what this plan needs for RED and the
BEFORE audit. Every observation recorded **after** the edit lands goes through
`nix develop . --command …` and is labelled **DIAGNOSTIC** for that reason — this session can never
see the edit through its own inherited PATH. Nothing in this file closes NIX-02, NIX-03 or NIX-04;
those close only in plan 64-06, run in a session the maintainer relaunches after this plan merges.

## Worktree and provisioning

```
$ test -f .git && echo IS_WORKTREE
IS_WORKTREE
$ git status --short
(empty)
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-affb732be8707b0ce
$ git rev-parse HEAD
7aa5cefcbf133ee08e8b1eca86b9e13d9877199c
$ git rev-parse --abbrev-ref HEAD
worktree-agent-affb732be8707b0ce

$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
... (tail)
 + typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-affb732be8707b0ce)
 + typst==0.15.0
 + urllib3==2.7.0
 + virtualenv==21.5.1

$ cat .venv/pyvenv.cfg
home = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
implementation = CPython
uv = 0.11.25
version_info = 3.14
include-system-site-packages = false
prompt = typsphinx

$ uv run python -c 'import typsphinx,os;print(os.path.realpath(typsphinx.__file__))'
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-affb732be8707b0ce/typsphinx/__init__.py
```

Exactly one documented provisioning line, no interpreter pin (D-04). The `typsphinx.__file__`
realpath matches `$(pwd -P)/typsphinx/__init__.py` exactly — this worktree's own editable install,
not the main checkout's.

### Seven tox environments, provisioned cold, no commands run

```
$ test ! -e .tox && echo NO_TOX_DIR
NO_TOX_DIR

$ tox run -e lint,type,py312,py313,cov,docs-html,docs-pdf --notest
lint: venv> /nix/store/f1y7m4b5vxrbwszkrni3yc2lv0x22zcj-uv/bin/uv venv -p .../.venv/bin/python --allow-existing '--prompt=agent-affb732be8707b0ce[lint]' --python-preference system .../.tox/lint
lint: uv-sync> /nix/store/f1y7m4b5vxrbwszkrni3yc2lv0x22zcj-uv/bin/uv sync --locked --python-preference system --extra dev -p .../.venv/bin/python
lint: OK ✔ in 0.15 seconds
type: venv> ... type: OK ✔ in 0.13 seconds
py312: venv> /nix/store/f1y7m4b5vxrbwszkrni3yc2lv0x22zcj-uv/bin/uv venv -p cpython3.12 --allow-existing '--prompt=agent-affb732be8707b0ce[py312]' --python-preference system .../.tox/py312
py312: uv-sync> ... py312: OK ✔ in 0.14 seconds
py313: venv> /nix/store/f1y7m4b5vxrbwszkrni3yc2lv0x22zcj-uv/bin/uv venv -p cpython3.13 --allow-existing '--prompt=agent-affb732be8707b0ce[py313]' --python-preference system .../.tox/py313
py313: uv-sync> ... py313: OK ✔ in 0.14 seconds
cov: venv> ... cov: OK ✔ in 0.13 seconds
docs-html: venv> ... docs-html: OK ✔ in 0.11 seconds
docs-pdf: venv> /nix/store/f1y7m4b5vxrbwszkrni3yc2lv0x22zcj-uv/bin/uv venv -p .../.venv/bin/python --allow-existing '--prompt=agent-affb732be8707b0ce[docs-pdf]' --python-preference system .../.tox/docs-pdf
docs-pdf: uv-sync> /nix/store/f1y7m4b5vxrbwszkrni3yc2lv0x22zcj-uv/bin/uv sync --locked --python-preference system --extra docs -p .../.venv/bin/python
  lint: OK (0.15 seconds)
  type: OK (0.13 seconds)
  py312: OK (0.14 seconds)
  py313: OK (0.14 seconds)
  cov: OK (0.13 seconds)
  docs-html: OK (0.11 seconds)
  docs-pdf: OK (0.12 seconds)
  congratulations :) (1.05 seconds)
```

`--notest` was accepted (tox 4.56.1); no environment's own commands ran during provisioning.

```
$ ls .tox
CACHEDIR.TAG  cov  docs-html  docs-pdf  lint  py312  py313  type
```

`pyvenv.cfg` `home` / `version_info` per environment:

| Env | `home` | `version_info` |
|-----|--------|-----------------|
| `.venv` | `/home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin` | `3.14` |
| `.tox/cov` | `/home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin` | `3.14` |
| `.tox/docs-html` | `/home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin` | `3.14` |
| `.tox/docs-pdf` | `/home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin` | `3.14` |
| `.tox/lint` | `/home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin` | `3.14` |
| `.tox/py312` | `/home/yuta/.local/share/uv/python/cpython-3.12-linux-x86_64-gnu/bin` | `3.12` |
| `.tox/py313` | `/nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin` | `3.13.13` |
| `.tox/type` | `/home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin` | `3.14` |

Matches planning's expectation exactly: `py312` resolves a uv-managed cpython-3.12, `py313` the
nix `python3-3.13.13`, everything else the same uv cpython-3.14 as `.venv`.

## Old sandbox and pre-edit baselines

```
$ command -v ruff tox black mypy pytest sphinx-build uv
/nix/store/vp86ji36v1nyp4q8d85i49hpyz43zszq-ruff/bin/ruff
/nix/store/s7rlc9zr6p3c03b9498jabqwjrhp13qz-tox/bin/tox
/nix/store/kl05v1f86vm0vwq00csz47rlbyxv1chg-black/bin/black
/nix/store/4pwm7pb8jxk68wprgwicyc00mbn7vz4w-mypy/bin/mypy
/nix/store/jmwmq21z24kqhbff4b3clpj4agixph5p-pytest/bin/pytest
/nix/store/0m5hj81l70ddxzkzjn643zyms08ccggm-sphinx-build/bin/sphinx-build
/nix/store/f1y7m4b5vxrbwszkrni3yc2lv0x22zcj-uv/bin/uv
```

All seven equal the carried-in table byte for byte.

```
OLD_FHS=/nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run
$ "$OLD_FHS" /bin/sh -c 'ls -la /usr/lib/libz.so*; ldconfig -p | grep -c libz'
ls: cannot access '/usr/lib/libz.so*': No such file or directory
0
```

No `libz.so.1` anywhere in the old rootfs; `ldconfig`'s count is 0.

```
$ nix eval --raw .#devShells.x86_64-linux.default.drvPath
/nix/store/vd4rms2m5kvjaazd3i78049k0s9a21g0-nix-shell.drv
```

```
PRE_X86_LINUX: /nix/store/vd4rms2m5kvjaazd3i78049k0s9a21g0-nix-shell.drv
```

Matches the carried-in value exactly (`64-FLAKE-EVIDENCE.md` § NIX-06, post-64-01).

```
$ nix eval --raw .#devShells.aarch64-linux.default.drvPath
/nix/store/gm6k80436paqz5hbr66cph11mrfhlnid-nix-shell.drv
$ nix eval --raw .#devShells.x86_64-darwin.default.drvPath
evaluation warning: Nixpkgs 26.05 will be the last release to support x86_64-darwin; ...
/nix/store/fclfls55m9lp06679x7zrw0qzjya834j-nix-shell.drv
$ nix eval --raw .#devShells.aarch64-darwin.default.drvPath
/nix/store/2m6y6pshri0vyw3jb5agczjnz9a92sxc-nix-shell.drv
```

Both darwin values match the carried-in table exactly.

```
$ nix eval --json .#devShells.x86_64-linux.default.nativeBuildInputs --apply 'map (p: p.name)'
["nodejs-24.16.0","pnpm-11.9.0","git-2.54.0","python3-3.13.13","uv","tox","ruff","black","mypy","pytest","sphinx-build"]

$ nix eval --json .#devShells.aarch64-darwin.default.nativeBuildInputs --apply 'map (p: p.name)'
["nodejs-24.16.0","pnpm-11.9.0","git-2.54.0","python3-3.13.13","uv-0.11.25"]
```

Both censuses match the carried-in table exactly (x86_64-linux 11 names, one `uv`; darwin 5 names).

## RED — import probe (old sandbox)

Import-order-independent, `-S` disables the `site` hook so nothing imports `zlib` before Pillow:

```
== .venv (uv cp3.14.4) ==
$ "$OLD_FHS" .venv/bin/python -S -c "import sys; sys.path.insert(0, '<site-packages>'); import PIL._imaging"
ImportError: libz.so.1: cannot open shared object file: No such file or directory
exit=1

== .tox/py312 (uv cp3.12.13) ==
$ "$OLD_FHS" .tox/py312/bin/python -S -c "import sys; sys.path.insert(0, '<site-packages>'); import PIL._imaging"
ImportError: libz.so.1: cannot open shared object file: No such file or directory
exit=1

== .tox/py313 (nix cp3.13.13) ==
$ "$OLD_FHS" .tox/py313/bin/python -S -c "import sys; sys.path.insert(0, '<site-packages>'); import PIL._imaging"
ImportError: libz.so.1: cannot open shared object file: No such file or directory
exit=1
```

RED reproduced for all three interpreter builds, independent of import order, under the old rootfs.

## BEFORE residual audit

Frame-inversion audit script (POSIX `sh`, kept in the session scratchpad, never a tracked file —
D-05), reproduced verbatim:

```sh
#!/bin/sh
# Frame-inversion audit: visits every regular file named *.so or *.so.*
# or carrying the owner-execute bit, keeps only ELF (magic 7f 45 4c 46),
# runs ldd, and reports unresolved sonames plus a scanned count.
n=0
for root in "$@"; do
  for f in $(find "$root" \( -type f -o -type l \) \( -name '*.so' -o -name '*.so.*' -o -perm -u+x \) 2>/dev/null); do
    [ -f "$f" ] || continue
    magic=$(head -c 4 "$f" 2>/dev/null | od -An -tx1 | tr -d ' \n')
    [ "$magic" = "7f454c46" ] || continue
    n=$((n+1))
    miss=$(ldd "$f" 2>/dev/null | grep 'not found' | sed 's/^[[:space:]]*//' | tr '\n' ';')
    [ -n "$miss" ] && echo "UNRESOLVED $f :: $miss"
  done
done
echo "scanned=$n"
```

Roots (this plan's frame-inversion set — derived from the code, not the symptom text):

```
$(pwd)/.venv
$(pwd)/.tox/cov
$(pwd)/.tox/docs-html
$(pwd)/.tox/docs-pdf
$(pwd)/.tox/lint
$(pwd)/.tox/py312
$(pwd)/.tox/py313
$(pwd)/.tox/type
/home/yuta/.local/share/uv/python/cpython-3.14.4-linux-x86_64-gnu   (realpath of .venv/.tox/{cov,docs-html,docs-pdf,lint,type}'s pyvenv.cfg home's parent)
/home/yuta/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu  (realpath of .tox/py312's pyvenv.cfg home's parent)
/nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13         (realpath of .tox/py313's pyvenv.cfg home's parent)
```

Run inside the old sandbox: `"$OLD_FHS" /bin/sh <script> <roots…>`. Full output (35 UNRESOLVED
lines, elided here to one representative line per distinct object class; the full transcript was
inspected line by line during the plan run):

```
UNRESOLVED <root>/lib/python3.*/site-packages/PIL/_imaging.cpython-*-x86_64-linux-gnu.so :: libz.so.1 => not found;libz.so.1 => not found;
UNRESOLVED <root>/lib/python3.*/site-packages/PIL/_imagingft.cpython-*-x86_64-linux-gnu.so :: libz.so.1 => not found;libz.so.1 => not found;
UNRESOLVED <root>/lib/python3.*/site-packages/pillow.libs/libfreetype-9fc94c80.so.6.20.6 :: libz.so.1 => not found;libz.so.1 => not found;
UNRESOLVED <root>/lib/python3.*/site-packages/pillow.libs/libharfbuzz-172d1f63.so.0.61421.0 :: libz.so.1 => not found;libz.so.1 => not found;
UNRESOLVED <root>/lib/python3.*/site-packages/pillow.libs/libpng16-abb096d5.so.16.58.0 :: libz.so.1 => not found;
UNRESOLVED <root>/lib/python3.*/site-packages/pillow.libs/libtiff-fc87e79d.so.6.2.0 :: libz.so.1 => not found;
```

(occurring once per `<root>` in `{.venv, .tox/cov, .tox/lint, .tox/py312, .tox/py313, .tox/type}` —
`.tox/docs-html` and `.tox/docs-pdf` carry no Pillow install, since the `docs` extra does not
depend on it, so they contribute zero UNRESOLVED lines for these objects)

```
UNRESOLVED /home/yuta/.local/share/uv/python/cpython-3.14.4-linux-x86_64-gnu/lib/python3.14/lib-dynload/_tkinter.cpython-314-x86_64-linux-gnu.so :: libtcl9.0.so => not found;libtcl9tk9.0.so => not found;
UNRESOLVED /home/yuta/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/lib-dynload/_crypt.cpython-312-x86_64-linux-gnu.so :: libcrypt.so.1 => not found;
UNRESOLVED /home/yuta/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/lib-dynload/_tkinter.cpython-312-x86_64-linux-gnu.so :: libtcl9.0.so => not found;libtcl9tk9.0.so => not found;

scanned=1974
```

```
BEFORE = {libz.so.1, libcrypt.so.1, libtcl9.0.so, libtcl9tk9.0.so}
```

The nix `python3-3.13.13` interpreter tree contributes no UNRESOLVED lines: its own extension
modules carry `RUNPATH`/`RPATH` entries pointing directly at nix store paths for their
dependencies (e.g. its `zlib` module's own `RUNPATH` to `/nix/store/…-zlib-1.3.2/lib`), independent
of the FHS sandbox's `ld.so.cache` — confirmed by `64-LIBZ-DIAGNOSIS.md` § 3.

## The edit

```diff
diff --git a/flake.nix b/flake.nix
index 973f745a..fe227023 100644
--- a/flake.nix
+++ b/flake.nix
@@ -25,6 +25,10 @@

           fhsRun = pkgs.buildFHSEnv {
             name = "typsphinx-fhs-run";
+            # Pillow's `_imaging` extension carries a bare `NEEDED libz.so.1`, and
+            # uv-managed CPython links zlib statically, so nothing in the process
+            # ever maps it without this entry. See 64-LIBZ-FIX-EVIDENCE.md.
+            targetPkgs = p: [ p.zlib ];
             runScript = "${pkgs.writeShellScript "typsphinx-fhs-passthrough" ''
               exec "$@"
             ''}";
```

Exactly one `targetPkgs = p: [ p.zlib ];` line plus one comment. No `multiPkgs`, `venvWalk`,
`venvShimOnStop`, `venvShimNames`, `venvShims`, `uvShim` or `packages` line touched. `runScript`
stays a pure `exec "$@"` (D-06); no locale variable is set anywhere (D-08). This is the exact
expression `64-LIBZ-DIAGNOSIS.md` built and measured at this flake's locked nixpkgs (`zlib-1.3.2`).

## GREEN — tracer (DIAGNOSTIC)

```
$ nix develop . --command bash -c 'command -v pytest'
(building fhsRun's derivations, first invocation only)
/nix/store/7q7lwxpw3xlz4h5rwka4nq0rjk1191yh-pytest/bin/pytest

$ grep -oE '/nix/store/[a-z0-9]{32}-typsphinx-fhs-run/bin/typsphinx-fhs-run' /nix/store/7q7lwxpw3xlz4h5rwka4nq0rjk1191yh-pytest/bin/pytest | head -1
/nix/store/99fm4lqkp4kab20d3blfbwajnprmlbfx-typsphinx-fhs-run/bin/typsphinx-fhs-run
```

New rootfs (tracer value; Task 3 re-confirms this is still the final value once the whole task set
has been through the sandbox): `/nix/store/99fm4lqkp4kab20d3blfbwajnprmlbfx-typsphinx-fhs-run`.

`NEW_FHS` differs from `OLD_FHS` (`dgddrdfkvigqsv48k563szqc8w7xlw2g` → `99fm4lqkp4kab20d3blfbwajnprmlbfx`).

```
$ "$NEW_FHS" /bin/sh -c 'test -e /usr/lib/libz.so.1'; echo "exit=$?"
exit=0
$ "$OLD_FHS" /bin/sh -c 'test -e /usr/lib/libz.so.1'; echo "exit=$?"
exit=1

$ "$NEW_FHS" /bin/sh -c 'ls -la /usr/lib/libz.so*; ldconfig -p | grep libz'
lrwxrwxrwx 1 nobody nogroup 66  1月  1  1970 /usr/lib/libz.so -> /nix/store/dbz6pb9g67kpgpl95k8d85kzpxm1c32p-zlib-1.3.2/lib/libz.so
lrwxrwxrwx 1 nobody nogroup 68  1月  1  1970 /usr/lib/libz.so.1 -> /nix/store/dbz6pb9g67kpgpl95k8d85kzpxm1c32p-zlib-1.3.2/lib/libz.so.1
lrwxrwxrwx 1 nobody nogroup 72  1月  1  1970 /usr/lib/libz.so.1.3.2 -> /nix/store/dbz6pb9g67kpgpl95k8d85kzpxm1c32p-zlib-1.3.2/lib/libz.so.1.3.2
	libz.so.1 (libc6,x86-64) => /lib/libz.so.1
	libz.so (libc6,x86-64) => /lib/libz.so
```

New rootfs holds `/usr/lib/libz.so.1`; old rootfs does not. `zlib-1.3.2`, matching the diagnosis's
scratch probe exactly.

```
== .venv (uv cp3.14.4) ==
$ "$NEW_FHS" .venv/bin/python -S -c "import sys; sys.path.insert(0, '<site-packages>'); import PIL._imaging; print('OK')"
OK
exit=0

== .tox/py312 (uv cp3.12.13) ==
$ "$NEW_FHS" .tox/py312/bin/python -S -c "import sys; sys.path.insert(0, '<site-packages>'); import PIL._imaging; print('OK')"
OK
exit=0

== .tox/py313 (nix cp3.13.13) ==
$ "$NEW_FHS" .tox/py313/bin/python -S -c "import sys; sys.path.insert(0, '<site-packages>'); import PIL._imaging; print('OK')"
OK
exit=0
```

All three probes succeed under NEW_FHS — RED under OLD, GREEN under NEW, for every interpreter
build, independent of import order.

```
$ nix develop . --command pytest tests/test_converted_image_collision_render_gate.py -q -rs
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
collected 3 items
tests/test_converted_image_collision_render_gate.py ...                  [100%]
============================== 3 passed in 1.43s ===============================
```

The previously failing node passes cleanly through the new rootfs: 3 passed, 0 failed.

```
$ nix develop . --command pytest tests/test_admonition_greyscale_pipeline.py -q -rs
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
collected 2 items
tests/test_admonition_greyscale_pipeline.py ..                           [100%]
============================== 2 passed in 0.63s ===============================
```

The Pillow-gated skip recorded in `64-NIX05-WORKTREE-EVIDENCE.md`'s six-skip table is gone: 2
passed, 0 skipped, 0 failed.

```
$ git diff --quiet 4e130c80 HEAD -- flake.lock; echo "exit=$?"
exit=0
$ git diff --quiet -- flake.lock; echo "exit=$?"
exit=0
```

`flake.lock` is unchanged, both against the phase base and against the working tree.
