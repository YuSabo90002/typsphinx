# Phase 68 Plan 03 — `flake.nix` Evidence

Comment-only edits to `flake.nix` (DOC-21). Every command below was run inside this
plan's own worktree; the derivation-identity gate proves no script body moved.

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-12T15:48:28Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a85e86a327c1b7e0e

$ test -f .git; echo "exit:$?"
exit:0

$ command -v uv
/nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2

$ nix --version
nix (Nix) 2.34.8
```

NIX_VERSION = nix (Nix) 2.34.8

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
(tail)
 + typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a85e86a327c1b7e0e)
 + typst==0.15.0
 + urllib3==2.7.0
 + uv==0.12.13
 + virtualenv==21.5.1
```

BASE_68_03 = 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a

(Measured via `git rev-parse HEAD` before any commit in this plan; equal to
`git merge-base HEAD gsd/v0.9.3-toolchain-and-dependency-update-repair`.)

## Baseline

For each system, `nix eval --raw ".#devShells.<sys>.default.drvPath"` (no dirty-tree
warning was printed — the tree was clean at this measurement, taken before the edit):

```
DRV_BEFORE_x86_64_linux = /nix/store/jnbia2810h255l78mn8k26sic5xqvb9p-nix-shell.drv
DRV_BEFORE_aarch64_linux = /nix/store/8qqw29d5k2jp4w9pcc4zyhk418fmdv4m-nix-shell.drv
DRV_BEFORE_x86_64_darwin = /nix/store/fclfls55m9lp06679x7zrw0qzjya834j-nix-shell.drv
DRV_BEFORE_aarch64_darwin = /nix/store/2m6y6pshri0vyw3jb5agczjnz9a92sxc-nix-shell.drv
```

All four match `64-FLAKE-EVIDENCE.md`'s recorded values byte-for-byte (no `flake.nix`
Nix code has changed since Phase 64).

```
$ nix flake check --all-systems --no-build; echo "exit:$?"
evaluating flake...
checking flake output 'devShells'...
checking derivation devShells.x86_64-linux.default...
derivation evaluated to /nix/store/jnbia2810h255l78mn8k26sic5xqvb9p-nix-shell.drv
checking derivation devShells.aarch64-linux.default...
derivation evaluated to /nix/store/8qqw29d5k2jp4w9pcc4zyhk418fmdv4m-nix-shell.drv
checking derivation devShells.x86_64-darwin.default...
evaluation warning: Nixpkgs 26.05 will be the last release to support x86_64-darwin; see https://nixos.org/manual/nixpkgs/unstable/release-notes#x86_64-darwin-26.05
derivation evaluated to /nix/store/fclfls55m9lp06679x7zrw0qzjya834j-nix-shell.drv
checking derivation devShells.aarch64-darwin.default...
derivation evaluated to /nix/store/2m6y6pshri0vyw3jb5agczjnz9a92sxc-nix-shell.drv
all checks passed!
exit:0
```

FLAKE_CHECK_BEFORE_EXIT = 0

```
$ grep -vE '^[[:space:]]*(#|$)' flake.nix | sha256sum
2a4570f3029206394711fc81b4e94964361c1b7ba81fc94d19a033db8099cd6b  -
```

```
$ sed -n 's/^home = //p;s/^version_info = //p' .venv/pyvenv.cfg
/home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
3.14
```

PYVENV_HOME_68_03 = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
PYVENV_VERSION_68_03 = 3.14

```
$ uv run pytest --collect-only -q -p no:cacheprovider
...
======================== 1548 tests collected in 1.26s =========================
```

COLLECT_BEFORE_68_03 = 1548

No system failed to evaluate; no HALT.

## uvShim note rewrite

D-12 rewrite: the six-line comment block directly above
`uvShim = pkgs.writeShellScriptBin "uv"` was replaced. The decision-ID prefix (`D-02:`)
and the sentence tying `.venv/bin/uv`'s existence to the Phase 65 revert are removed.
No version number (no digit-dot-digit sequence) appears anywhere in the new block.

New block (quoted via the `cb` helper applied to the `uvShim` line):

```
          # `uv` resolves in two legs, described here by role rather than by
          # version. Leg 1 is the same bounded upward walk used by the strict
          # shims above, ending at the tree's own .venv/bin/uv -- the uv that
          # uv.lock pins, present once `uv sync` has provisioned the tree.
          # Leg 2, the on-stop fragment, resolves to nixpkgs' own uv at a
          # store path fixed at evaluation time, which is why it cannot be
          # shadowed. It is the bootstrap for a fresh clone or worktree that
          # has no .venv yet, before its first uv sync -- without it such a
          # tree could not provision itself, so it must not be removed as
          # cleanup. Both legs enter the sandbox, which is what makes
          # `uv run <tool>` carry FHS into every downstream process. This is
          # the only fallback in this file, deliberately: the six strict
          # shims above must never gain one.
```

Drv paths after the edit, for each of the four systems (`nix eval --raw
".#devShells.<sys>.default.drvPath"`), each equal to its `DRV_BEFORE_` value:

```
DRV_AFTER_x86_64_linux = /nix/store/jnbia2810h255l78mn8k26sic5xqvb9p-nix-shell.drv
DRV_AFTER_aarch64_linux = /nix/store/8qqw29d5k2jp4w9pcc4zyhk418fmdv4m-nix-shell.drv
DRV_AFTER_x86_64_darwin = /nix/store/fclfls55m9lp06679x7zrw0qzjya834j-nix-shell.drv
DRV_AFTER_aarch64_darwin = /nix/store/2m6y6pshri0vyw3jb5agczjnz9a92sxc-nix-shell.drv
```

Comment-stripped hash after the edit, equal to base:

```
$ grep -vE '^[[:space:]]*(#|$)' flake.nix | sha256sum
2a4570f3029206394711fc81b4e94964361c1b7ba81fc94d19a033db8099cd6b  -
```

`git diff -U0 "$BASE_68_03" -- flake.nix`, every changed line a comment or blank line:

```
diff --git a/flake.nix b/flake.nix
index fe227023..fe37d01c 100644
--- a/flake.nix
+++ b/flake.nix
@@ -92,6 +92,13 @@
-          # D-02: `uv` resolves in two legs. Leg 1 is the same bounded upward
-          # walk for .venv/bin/uv (it does not exist until Phase 65's tox-uv
-          # revert installs it). Leg 2, the on-stop fragment, is the fixed
-          # nixpkgs store path -- fixed at flake-evaluation time and therefore
-          # un-shadowable. Both legs enter the sandbox, which is what makes
-          # `uv run <tool>` carry FHS into every downstream process.
+          # `uv` resolves in two legs, described here by role rather than by
+          # version. Leg 1 is the same bounded upward walk used by the strict
+          # shims above, ending at the tree's own .venv/bin/uv -- the uv that
+          # uv.lock pins, present once `uv sync` has provisioned the tree.
+          # Leg 2, the on-stop fragment, resolves to nixpkgs' own uv at a
+          # store path fixed at evaluation time, which is why it cannot be
+          # shadowed. It is the bootstrap for a fresh clone or worktree that
+          # has no .venv yet, before its first uv sync -- without it such a
+          # tree could not provision itself, so it must not be removed as
+          # cleanup. Both legs enter the sandbox, which is what makes
+          # `uv run <tool>` carry FHS into every downstream process. This is
+          # the only fallback in this file, deliberately: the six strict
+          # shims above must never gain one.
```

No drvPath changed. No `## HALT` heading was written.

<!-- gsd:write-continue -->
