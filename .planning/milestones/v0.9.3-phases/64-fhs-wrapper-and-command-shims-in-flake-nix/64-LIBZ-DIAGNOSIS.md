# Phase 64 — `libz.so.1` Gap Diagnosis (orchestrator, pre-planning)

**Status: DIAGNOSTIC.** Measured by the plan-phase orchestrator on 2026-09-12, before the
gap-closure plans were written, to test the verifier's and reviewer's prescription ("add `zlib` to
`fhsRun`'s `targetPkgs`", `64-VERIFICATION.md` gaps, `64-REVIEW.md` CR-01) rather than hand it to the
planner untested. Nothing here closes a requirement:

- the "fixed" sandbox below is a scratch `buildFHSEnv`, not an edited `flake.nix`
- no shim and no full-suite run was involved
- nothing ran in the genuine D-09 shape

The gap-closure plans re-measure everything they rely on.

## Probe sandboxes

| Label | Store path | How it was obtained |
|-------|------------|---------------------|
| OLD | `/nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run` | The `fhsRun` embedded in this session's `ruff` shim (`flake.nix` at `4e130c80`, no `targetPkgs`) |
| NEW | `/nix/store/dld9ah7ndlfrhklv2qsjljkx9wv42wb4-typsphinx-fhs-run-zlib-probe` | A scratch `buildFHSEnv` with `targetPkgs = p: [ p.zlib ]`, built from the flake's own locked nixpkgs (`65179426c83bb3f6bc14898b42ea1c6f01d374b0`). Its `zlib` is `zlib-1.3.2` |

## 1. The sandbox root

```
$ OLD /bin/sh -c 'ls -la /usr/lib/libz.so* /usr/lib64/libz.so* /lib/libz.so* /lib64/libz.so*'
ls: cannot access '/usr/lib/libz.so*': No such file or directory      (all four patterns)
$ OLD /bin/sh -c 'ldconfig -p | grep -E "libz\.|libstdc|libgcc_s"'
	libstdc++.so.6 (libc6,x86-64) => /lib/libstdc++.so.6
	libstdc++.so (libc6,x86-64) => /lib/libstdc++.so
	libgcc_s.so.1 (libc6,x86-64) => /lib/libgcc_s.so.1

$ NEW /bin/sh -c 'ls -la /usr/lib/libz.so*; ldconfig -p | grep "libz\.so"'
/usr/lib/libz.so -> /nix/store/dbz6pb9g67kpgpl95k8d85kzpxm1c32p-zlib-1.3.2/lib/libz.so
/usr/lib/libz.so.1 -> /nix/store/dbz6pb9g67kpgpl95k8d85kzpxm1c32p-zlib-1.3.2/lib/libz.so.1
/usr/lib/libz.so.1.3.2 -> /nix/store/dbz6pb9g67kpgpl95k8d85kzpxm1c32p-zlib-1.3.2/lib/libz.so.1.3.2
	libz.so.1 (libc6,x86-64) => /lib/libz.so.1
	libz.so (libc6,x86-64) => /lib/libz.so
```

## 2. What needs `libz.so.1`

Pillow 12.3.0 (the `uv.lock` pin) does not vendor zlib. Its `_imaging` extension carries a bare
`libz.so.1` `NEEDED` entry next to its vendored libraries:

```
$ readelf -d .venv/lib/python3.13/site-packages/PIL/_imaging.cpython-313-x86_64-linux-gnu.so
 (RPATH)   [$ORIGIN/../pillow.libs]
 (NEEDED)  [libtiff-fc87e79d.so.6.2.0]
 (NEEDED)  [libjpeg-31e2ca52.so.62.4.0]
 (NEEDED)  [libopenjp2-b07f72ad.so.2.5.4]
 (NEEDED)  [libz.so.1]
 (NEEDED)  [libxcb-ad31f5a3.so.1.1.0]
 (NEEDED)  [libpthread.so.0]
 (NEEDED)  [libc.so.6]
```

`pillow.libs/` holds 18 vendored libraries, none of them zlib. The `ldd` audit in § 5 finds five more
objects that need `libz.so.1`:

- `PIL/_imagingft`
- the vendored `libfreetype`, `libharfbuzz`, `libpng16` and `libtiff`

## 3. Why the interpreter build decides the outcome

| Interpreter | `NEEDED` of the binary | `zlib` module | Consequence |
|-------------|------------------------|---------------|-------------|
| uv-managed `cpython-3.12.13` (python-build-standalone) | `libpthread`, `libdl`, `libutil`, `librt`, `libm`, `libc`; no `libz` | no `zlib*.so` in `lib-dynload` (built in, statically linked) | nothing in the process ever maps `libz.so.1` |
| uv-managed `cpython-3.14.4` (python-build-standalone) | same set; no `libz` | none in `lib-dynload` (built in) | same |
| nix `python3-3.13.13` | `libpython3.13.so.1.0`, `libdl`, `libm`, `libgcc_s`, `libc` | `zlib.cpython-313-x86_64-linux-gnu.so`, `NEEDED libz.so.1`, `RUNPATH /nix/store/dbz6pb9g…-zlib-1.3.2/lib` | an earlier `import zlib` maps `libz.so.1` from the store, and Pillow's `NEEDED` is then satisfied by soname |

## 4. Import-order probe matrix

Every probe runs with `-S` and inserts the site-packages or unpacked-wheel directory into
`sys.path` by hand. That way no `site` hook can import `zlib` first. The pythons were:

- **cp3.13:** the main checkout's `.venv/bin/python` (nix)
- **cp3.12 / cp3.14:** scratch venvs over the uv-managed interpreters. They load the Pillow 12.3.0
  wheel trees uv already unpacked (`~/.cache/uv/archive-v0/YK3SvbNUbbVkGhtD` for cp312,
  `…/oKlWfE6ejswxwVWT` for cp314). `uv pip install --offline` could not install them because the
  network is disabled in this session.

| Interpreter | Sandbox | `PIL._imaging` as first import | `import zlib`, then `PIL._imaging` | PNG encode + decode |
|-------------|---------|--------------------------------|-----------------------------------|---------------------|
| nix cp3.13.13 | host (no sandbox) | `ImportError: libz.so.1` | OK | — |
| nix cp3.13.13 | OLD | `ImportError: libz.so.1` | OK | — |
| nix cp3.13.13 | NEW | OK | OK | — |
| uv cp3.12.13 | OLD | `ImportError: libz.so.1` | `ImportError: libz.so.1` | `ImportError: libz.so.1` |
| uv cp3.12.13 | NEW | OK | OK | OK, `(7, 5)` |
| uv cp3.14.4 | OLD | `ImportError: libz.so.1` | `ImportError: libz.so.1` | `ImportError: libz.so.1` |
| uv cp3.14.4 | NEW | OK | OK | OK, `(7, 5)` |

**What this explains.** 64-02 recorded that the uv-managed cp312 and cp314 builds fail while
`tox -e py313` passes. That split comes from how each interpreter links zlib: statically in the uv
builds, dynamically in the nix build. The Pillow wheel is not the cause.

`tox -e py313` resolves the nix interpreter (`--python-preference system`) and passes only because
something imports `zlib` before PIL. It is therefore **not a clean control for sandbox health**.
The host main tree carries the same latent order dependence.

## 5. `DT_NEEDED` closure audit

`ldd` ran inside each sandbox over every ELF shared object (`*.so`, `*.so.*`) under three roots:

- the main checkout's `.venv/lib/python3.13/site-packages` (the cp313 wheel set)
- both uv-managed interpreter trees

That is 321 objects per sandbox. The audit script is `probe/ldd-audit.sh`, reproduced in the
appendix.

| Unresolved soname | Objects needing it | OLD | NEW |
|-------------------|--------------------|-----|-----|
| `libz.so.1` | `PIL/_imaging`, `PIL/_imagingft`, `pillow.libs/libfreetype`, `libharfbuzz`, `libpng16`, `libtiff` (6) | not found | resolved |
| `libcrypt.so.1` | cp3.12.13 `lib-dynload/_crypt` | not found | not found |
| `libtcl9.0.so`, `libtcl9tk9.0.so` | `lib-dynload/_tkinter` (cp3.12.13 and cp3.14.4) | not found | not found |

The residuals left in NEW are standard-library modules that the project and its dependencies do not
import: `crypt` was removed in Python 3.13, and nothing uses `tkinter`. CONTEXT § Claude's Discretion
says to add "only what a failing measurement demands", so they are recorded here and not fixed.

**Caveat:** this audit covered the main checkout's cp313 wheel set. It did not cover the cp3.14
worktree `.venv` or the `.tox/*` environments a fresh provisioning creates, so the gap plans re-run
it over the environments they actually provision.

## 6. What this establishes, and what it does not

**Establishes:**

- `targetPkgs = [ zlib ]` resolves every `libz.so.1` edge in the audited set.
- It fixes the exact failing import for all three interpreter builds, whatever the import order.
- No other soname in the audited set is both unresolved and reachable.

**Does not establish:**

- the suite, `tox -e py312` or `tox -e cov` results after the fix, since none of them was run
- NIX-06 evaluation of an edited `flake.nix`
- anything observed through a shim or in a relaunched session

## Appendix — reproduction

The scratch sandbox was built in 1.4 s, with `zlib-1.3.2` already in the store:

```
nix build --no-link --print-out-paths --impure --expr '
let
  flake = builtins.getFlake "git+file:///home/yuta/Documents/typsphinx";
  pkgs = flake.inputs.nixpkgs.legacyPackages.x86_64-linux;
in pkgs.buildFHSEnv {
  name = "typsphinx-fhs-run-zlib-probe";
  targetPkgs = p: [ p.zlib ];
  runScript = "${pkgs.writeShellScript "zlib-probe-passthrough" "exec \"$@\""}";
}'
```

The audit script ran inside the sandbox as `"$FHS" ldd-audit.sh <root>...`:

```
#!/bin/sh
n=0
for root in "$@"; do
  for f in $(find "$root" -type f \( -name '*.so' -o -name '*.so.*' \) 2>/dev/null); do
    n=$((n+1))
    miss=$(ldd "$f" 2>/dev/null | grep 'not found' | sed 's/^[[:space:]]*//' | tr '\n' ';')
    [ -n "$miss" ] && echo "UNRESOLVED $f :: $miss"
  done
done
echo "scanned=$n"
```

The import-order probes, where `<dir>` is the site-packages or unpacked-wheel directory:

```
"$FHS" <python> -S -c "import sys; sys.path.insert(0, '<dir>'); import PIL._imaging"
"$FHS" <python> -S -c "import sys, zlib; sys.path.insert(0, '<dir>'); import PIL._imaging"
"$FHS" <python> -S -c "import sys, io; sys.path.insert(0, '<dir>'); from PIL import Image; b=io.BytesIO(); Image.new('RGB',(7,5),(1,2,3)).save(b,'PNG'); b.seek(0); im=Image.open(b); im.load(); print(im.size)"
```

For the host row, the `"$FHS"` prefix was dropped.
