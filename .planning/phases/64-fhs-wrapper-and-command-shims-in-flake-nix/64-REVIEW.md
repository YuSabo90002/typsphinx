---
phase: 64-fhs-wrapper-and-command-shims-in-flake-nix
reviewed: 2026-09-11T16:11:10Z
depth: standard
files_reviewed: 1
files_reviewed_list:
  - flake.nix
findings:
  critical: 1
  warning: 1
  info: 2
  total: 4
status: issues_found
---

# Phase 64: Code Review Report

**Reviewed:** 2026-09-11T16:11:10Z
**Depth:** standard
**Files Reviewed:** 1
**Status:** issues_found

## Summary

`flake.nix` is the only file this phase changed. It adds a Linux-guarded `pkgs.buildFHSEnv`
passthrough (`typsphinx-fhs-run`) and seven `writeShellScriptBin` command shims (`uv`, `tox`,
`ruff`, `black`, `mypy`, `pytest`, `sphinx-build`) that walk upward from `$PWD` to the nearest
ancestor holding `.git`, looking for `.venv/bin/<tool>`. Six shims fail loudly (exit 127) when no
target is found; `uv` alone falls back to a fixed `pkgs.uv` store path. The shell logic itself
(bounded-walk termination, quoting, `exec`-based tail calls, environment passthrough, PATH
ordering vs. the dropped `pkgs.uv` package) is sound and matches the phase's own decision record
(D-01 through D-09) and its own measured evidence (`64-FLAKE-EVIDENCE.md`, `64-NIX05-WORKTREE-EVIDENCE.md`).

The one substantive defect is not a logic bug in the shell script but a completeness gap in the
sandbox's own package closure: `fhsRun`'s `buildFHSEnv` call declares no `targetPkgs` at all
(defaults to the empty set), and the phase's own Plan 02 measurement reproduced a real
`ImportError: libz.so.1` inside the sandbox for `uv`-downloaded CPython builds, failing three of
seven verification gates (`tox -e py312`, `tox -e cov`, the bare `pytest` shim / NIX-04). That
measurement was taken against this exact file and is not environmental noise — it reproduced three
times with an identical first traceback frame, and a non-failing control (`tox -e py313`, whose
interpreter matches the CI baseline) ruled out a blanket "sandbox always broken" explanation. This
is called out below as CR-01 per the review brief's explicit instruction to assess it.

## Critical Issues

### CR-01: FHS sandbox ships with no `targetPkgs`, causing a reproduced `ImportError: libz.so.1` that fails three of seven verification gates

**File:** `flake.nix:26-31`
**Issue:** `fhsRun = pkgs.buildFHSEnv { name = "typsphinx-fhs-run"; runScript = ...; };` sets no
`targetPkgs`, so `buildFHSEnv`'s default (`pkgs: []`) applies — the sandbox's root filesystem
carries no shared libraries beyond glibc's own baseline. Phase 64's own Plan 02 measurement
(`64-02-SUMMARY.md`, `64-NIX05-WORKTREE-EVIDENCE.md`) ran the full verification procedure through
this exact `flake.nix` and found:
- bare `pytest` shim (NIX-04): `1 failed, 1541 passed, 6 skipped` vs. the `1543 passed, 5 skipped`
  baseline
- `tox -e py312`: `FAIL code 1`
- `tox -e cov`: `FAIL code 1`

All three failures share the identical root cause: `pypdf`'s lazy `PIL` import raises
`ImportError: libz.so.1: cannot open shared object file: No such file or directory` inside the
sandbox. The failure correlates with which CPython build `uv` resolved Pillow's wheel against —
`cp312` and `cp314` (both `uv`-downloaded interpreter builds) fail; `cp313` (the nix-provided
interpreter that matches the CI baseline exactly) passes clean in the *identical* sandbox. This
rules out "the sandbox is missing zlib for everyone" as too broad a diagnosis, but does not change
the outcome: as shipped, invoking the documented bare-command shims (`pytest`, and by extension
any `tox` environment that resolves a `uv`-downloaded non-3.13 interpreter) produces incorrect,
environment-caused test failures rather than the CI-matching baseline this phase exists to
reproduce. This is a real functional regression class introduced by the sandbox's own package
closure, not by the shell logic, and it directly affects the FHS wrapper's stated purpose (make the
documented bare commands behave like CI).
**Fix:** Add `zlib` (and, per D-07's own anticipated case, `cacert` — see WR-01 below) to
`targetPkgs`:
```nix
fhsRun = pkgs.buildFHSEnv {
  name = "typsphinx-fhs-run";
  targetPkgs = pkgs': [ pkgs'.zlib ];
  runScript = "${pkgs.writeShellScript "typsphinx-fhs-passthrough" ''
    exec "$@"
  ''}";
};
```
Re-run `tox -e py312`, `tox -e cov`, and the bare `pytest` shim afterward to confirm the
`libz.so.1` `ImportError` is gone and the 1543/5 baseline is restored before treating NIX-02/
NIX-03/NIX-04 as closed.

## Warnings

### WR-01: Cold-`@preview`-cache / cold-TLS path through the sandbox is unverified, and no `cacert` was added despite D-07 anticipating the need

**File:** `flake.nix:26-31`
**Issue:** D-07 (`64-CONTEXT.md`) explicitly names `cacert` as the package to add to `targetPkgs`
"if a cold cache turns out to need TLS." The phase's own measurement (`64-FLAKE-EVIDENCE.md`, § D-07)
ran `tox -e docs-pdf` only against a *warm* `~/.cache/typst/packages/preview` (nine packages already
present, unchanged before/after) and concluded "the cold-cache TLS path stayed unexercised." No
`cacert` (or any other TLS trust store) is present in `targetPkgs` because `targetPkgs` is entirely
absent from this derivation. If the maintainer's cache is ever cleared, or a new package version is
referenced that isn't already cached, `docs-pdf` run through this sandbox has no verified path to
fetch it — Typst's package fetcher would need to resolve TLS certificates that the sandbox's
minimal rootfs may not provide. This is not a defect that has manifested yet, but it's a foreseeable
gap directly acknowledged and then left unaddressed by the same phase's own decision record.
**Fix:** Either add `pkgs.cacert` (and set `SSL_CERT_FILE`/`NIX_SSL_CERT_FILE` appropriately) to
`targetPkgs` proactively, or explicitly track "verify cold-cache `docs-pdf` behavior" as a follow-up
so it isn't silently forgotten once the warm-cache measurement is read as "D-07 closed."

## Info

### IN-01: `venvWalk`'s upward walk depends on ambient `dirname`/coreutils without declaring that dependency

**File:** `flake.nix:39-57` (specifically the `dir="$(dirname "$dir")"` call at line 54)
**Issue:** The six strict shims and the `uv` shim all run `venvWalk` *before* entering the FHS
sandbox — this portion of the script executes directly on the host shell, using whatever `dirname`
binary is first on the ambient `PATH` at devShell-entry time. `flake.nix` never adds `coreutils` (or
any package providing `dirname`) to the Linux devShell's `packages`, so the script's correctness
relies entirely on the host environment already having it (true in practice on the maintainer's
NixOS system and virtually every Linux/macOS system, which is presumably why it was never
measured as a gap). This is a latent, undeclared dependency rather than a reproduced failure.
**Fix:** No action required unless the devShell's package list is ever pared down aggressively; if
so, add `pkgs.coreutils` explicitly rather than relying on ambient PATH.

### IN-02: The strict-shim not-found message assumes a `.git` ancestor was found, but the walk can also stop at `/` with none

**File:** `flake.nix:63-68`
**Issue:** `venvShimOnStop`'s message ("no executable .venv/bin/<tool> found walking up from
$start (stopped at $dir); provision with: env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync
--extra dev") is accurate when the walk stops at a `.git` boundary, but the same code path also
fires when the walk reaches `/` without ever finding a `.git` ancestor (i.e., the shim was invoked
from outside any git checkout). In that case the suggested remedy is misleading — there's no
project root at `$dir` to provision, and running the suggested command there would either fail or
create an unwanted `.venv` at an arbitrary location. Low likelihood in normal use (the shims are
only reachable via the project's own devShell, invoked from inside the checkout), but the message
doesn't distinguish the two stop conditions even though the loop already does (`.git` check vs. the
root check).
**Fix:** Track *why* the loop stopped (`.git` found vs. hit `/`) and tailor the message, e.g. only
suggest the `uv sync` remedy when a `.git` ancestor was actually found.

---

_Reviewed: 2026-09-11T16:11:10Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
