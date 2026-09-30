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

## Header and per-element notes

Re-ran the head check and `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`
(quick resync, 91 packages resolved, 81 checked, no changes). Header block (D-10 a/b/c,
D-11, D-09) inserted directly above `  outputs =`, no blank line intervening, quoted via
the `cb` helper applied to the `outputs =` line:

```
  # The devShell here is a plain mkShell. On Linux it adds one buildFHSEnv
  # passthrough (`typsphinx-fhs-run`, a pure exec) and PATH command shims
  # that enter it. Two more obvious designs were tried and falsified: using
  # buildFHSEnv's own `.env` attribute as the devShell does not put the
  # shell inside FHS under either `nix develop` or direnv, because
  # `/lib64/ld-linux-x86-64.so.2` still resolves to NixOS's stub-ld either
  # way. A `shellHook` that execs into the wrapper fares no better: `nix
  # develop` never runs the hook at all, and under direnv the exec only
  # replaces nix-direnv's own environment-capture subshell, leaving the
  # real interactive shell outside FHS. So the devShell stays `mkShell`,
  # and `.envrc`'s `use flake` keeps working unchanged.
  #
  # Exactly the seven bare commands CLAUDE.md documents are shimmed: `uv`,
  # plus the six names in `venvShimNames` (`tox`, `ruff`, `black`, `mypy`,
  # `pytest`, `sphinx-build`). A Linux sandbox's mount namespace is
  # inherited across `fork` and `exec` by every descendant process, so
  # only these top-level entrypoints need a shim -- everything tox or uv
  # spawns underneath, including the tree's own `.venv/bin/uv`, a
  # downloaded interpreter, or a `.tox/<env>/bin` tool, already runs
  # inside the sandbox it was forked from. Every shimmed command keeps
  # the exact string CLAUDE.md documents.
  #
  # `buildFHSEnv` is Linux-only, so the wrapper and its shims are added
  # only when the host platform is Linux; on darwin the shell instead
  # carries nixpkgs' own `uv`, unshimmed. Darwin is unverified by
  # construction: no maintainer machine can exercise that branch, and no
  # CI lane evaluates this file at all. The only check ever performed
  # here is a `nix eval` of all four declared systems' devShells, run on
  # a Linux evaluator; the darwin shell itself has never been built or
  # entered. A darwin contributor who hits breakage here should report
  # it directly as a GitHub issue, rather than assume CI would have
  # caught it.
  #
  # Measurement sources:
  # `.planning/PROJECT.md`, "Binding measurements taken during scoping", for the two falsified devShell designs above.
  # v0.9.3 Phase 64 `64-NIX05-WORKTREE-EVIDENCE.md`, for PATH inheritance reaching a worktree.
  # v0.9.3 Phase 64 `64-FLAKE-EVIDENCE.md`, for the four-system `nix eval` check.
  # v0.9.3 Phase 64 `64-LIBZ-FIX-EVIDENCE.md`, for the `zlib` entry below.
  # v0.9.3 Phase 65 `65-REVERT-EVIDENCE.md`, for tox-uv's bundled uv resolving `.venv/bin/uv` inside FHS.
```

`fhsRun` per-element note (`cb` applied to `targetPkgs = `), citation restated to name
milestone and phase:

```
            # Pillow's `_imaging` extension carries a bare `NEEDED libz.so.1`, and
            # uv-managed CPython links zlib statically, so nothing in the sandboxed
            # process ever maps it without this entry. See v0.9.3 Phase 64 `64-LIBZ-FIX-EVIDENCE.md`.
```

`venvWalk` per-element note (`cb` applied to `venvWalk =`) — content unchanged, no decision
ID was present, D-09-compliant already:

```
          # Bounded upward walk from $PWD looking for .venv/bin/<tool>, stopping
          # at the first ancestor holding a .git entry (a file in a worktree, a
          # directory in the main checkout) or at /. This survives tox's own
          # `changedir = docs` (docs-html/docs-pdf) and never leaves the
          # checkout it started in, so a nested executor worktree can never
          # resolve the main checkout's .venv.
```

Strict-shims per-element note (`cb` applied to `venvShimOnStop =`), decision-ID prefix
dropped, `fallback` and `127` retained:

```
          # The six venv shims have no fallback. A missing .venv/bin/<tool>
          # is a hard, loud failure -- naming the tool and the directory the
          # walk started from, then exiting non-zero (127, the shell's own
          # command-not-found status). A shim that quietly ran some other
          # binary instead would turn "does not run" into "runs but lies",
          # which is exactly what this fallback-free design avoids.
```

Roster per-element note (`cb` applied to `venvShimNames = [`), both decision IDs dropped:

```
          # The full seven-name roster is these six strict venv shims plus
          # `uv` (`uvShim` below, the one exception).
```

Darwin guard, optional one-line pointer above `default = pkgs.mkShell {`:

```
          # See the header note above `outputs` for the darwin guard this branch implements.
```

`uvShim` note is unchanged from the Task 1 rewrite above.

## Gates after the edit

Four drvPaths, unchanged:

```
DRV_AFTER_x86_64_linux = /nix/store/jnbia2810h255l78mn8k26sic5xqvb9p-nix-shell.drv
DRV_AFTER_aarch64_linux = /nix/store/8qqw29d5k2jp4w9pcc4zyhk418fmdv4m-nix-shell.drv
DRV_AFTER_x86_64_darwin = /nix/store/fclfls55m9lp06679x7zrw0qzjya834j-nix-shell.drv
DRV_AFTER_aarch64_darwin = /nix/store/2m6y6pshri0vyw3jb5agczjnz9a92sxc-nix-shell.drv
```

```
$ nix flake check --all-systems --no-build; echo "exit:$?"
warning: Git tree '/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a85e86a327c1b7e0e' is dirty
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

FLAKE_CHECK_AFTER_EXIT = 0

```
$ grep -vE '^[[:space:]]*(#|$)' flake.nix | sha256sum
2a4570f3029206394711fc81b4e94964361c1b7ba81fc94d19a033db8099cd6b  -
```

Comment-stripped hash pair equal (before and after both `2a4570f3...8099cd6b`).

`git diff -U0 "$BASE_68_03" -- flake.nix` (full, this task's additional hunks; every
changed line a comment or blank line):

```
@@ -7,0 +8,39 @@
+  # (header block, see "## Header and per-element notes" above)
@@ -29,2 +68,2 @@
-            # uv-managed CPython links zlib statically, so nothing in the process
-            # ever maps it without this entry. See 64-LIBZ-FIX-EVIDENCE.md.
+            # uv-managed CPython links zlib statically, so nothing in the sandboxed
+            # process ever maps it without this entry. See v0.9.3 Phase 64 `64-LIBZ-FIX-EVIDENCE.md`.
@@ -63,4 +102,6 @@
-          # D-03: the six venv shims have no fallback. A missing
-          # .venv/bin/<tool> is a hard, loud failure -- naming the tool and the
-          # directory the walk started from, then exiting non-zero (127, the
-          # shell's own command-not-found status).
+          # (rewritten, see strict-shims note above)
@@ -74,2 +115,2 @@
-          # D-01: the full seven-name roster is these six strict venv shims
-          # plus `uv` (uvShim below, D-02's sole documented exception).
+          # (rewritten, see roster note above)
@@ -92,6 +133,13 @@
-          # (Task 1's uvShim rewrite, see above)
@@ -103,0 +152 @@
+          # See the header note above `outputs` for the darwin guard this branch implements.
```

```
$ grep -nE 'D-[0-9]' flake.nix
(no output)
```

```
$ grep -nE 'until Phase|exist until' flake.nix
(no output)
```

```
$ grep -nF '.planning/phases' flake.nix
(no output)
```

```
$ uv run pytest --collect-only -q -p no:cacheprovider
...
======================== 1548 tests collected in 0.27s =========================
```

COLLECT_AFTER_68_03 = 1548

No `## HALT` heading was written. flake.nix and this evidence file are the only files
this plan modified, aside from the SUMMARY committed alongside them.

## Note on the plan's automated `<verify>` pytest-collect-count check

`68-03-PLAN.md`'s Task 2 automated `<verify>` re-derives the live collect count with
`sed -n 's/^\([0-9][0-9]*\) tests\{0,1\} collected.*/\1/p'`, which anchors to the start
of the line. This project's `pytest --collect-only -q` summary line is always padded
with `=` characters to the terminal width (`======================== 1548 tests
collected in 0.27s =========================`), even when stdout is not a tty, so the
digit is never at column 1 and that literal sed pattern never matches on this tree —
independent of this plan's edit. Verified directly with the same command: `uv run
pytest --collect-only -q -p no:cacheprovider 2>/dev/null | sed -n
's/^\([0-9][0-9]*\) tests\{0,1\} collected.*/\1/p'` produces empty output both before
and after the flake.nix edit. The underlying invariant this check exists to prove
(collected count unchanged) was confirmed with an equivalent, non-anchored extraction:
`grep -oE '[0-9]+ tests? collected' | grep -oE '^[0-9]+'` returns `1548` both before and
after. See `## Deviations from Plan` in `68-03-SUMMARY.md`.
