---
phase: 64-fhs-wrapper-and-command-shims-in-flake-nix
reviewed: 2026-09-12T00:00:00Z
depth: standard
files_reviewed: 1
files_reviewed_list:
  - flake.nix
findings:
  critical: 0
  warning: 1
  info: 3
  total: 4
status: issues_found
---

# Phase 64: Code Review Report (re-review after 64-05)

**Reviewed:** 2026-09-12T00:00:00Z
**Depth:** standard
**Files Reviewed:** 1
**Status:** issues_found

## Summary

This is a re-review of `flake.nix` after plan 64-05 (commit `6beae3af`) added
`targetPkgs = p: [ p.zlib ];` to the `fhsRun` FHS sandbox derivation, closing the prior review's
sole Critical finding (CR-01: missing `libz.so.1` causing `ImportError` inside Pillow's `_imaging`
extension for `uv`-managed CPython builds). The remainder of the file — the bounded `venvWalk`
upward search, the strict six-name venv shim roster, the two-leg `uv` shim, and the Linux/darwin
`packages` split — is byte-identical to what the prior review already assessed as sound, and no
new defect was found in that logic.

**CR-01 is resolved.** `64-LIBZ-FIX-EVIDENCE.md` documents a full RED (old rootfs fails
`import PIL._imaging` for all three interpreter builds) → GREEN (new rootfs succeeds for all
three) → AFTER-audit (the `libz.so.1` unresolved-soname entry is gone, no new unresolved soname
appeared) cycle, plus re-runs of the three previously failing gates (`pytest`, `tox -e py312`,
`tox -e cov`) all passing at the 1543/5 baseline. This matches what is visible in the file itself:
`targetPkgs = p: [ p.zlib ];` at `flake.nix:31`, scoped to the Linux-only `fhsRun` derivation, with
nothing else in the shim logic touched.

**WR-01 remains open** — no `cacert`/TLS trust store was added, and the underlying condition
(cold `@preview` cache needing TLS) is explicitly acknowledged as untested, not disproven. This is
a tracked, deliberate deferral per the phase's own decision record, not an oversight, but the gap
itself is unchanged from the prior review and is kept as a Warning here for that reason.

**IN-01 and IN-02 remain open, unactioned**, exactly as the prior review left them, for the same
reasons the fix plan itself gave (both are info-level with no failing gate forcing a change, and
both would perturb evidence — the NIX-06 package census for IN-01, the NIX-07 rename-carry-over
diffs for IN-02 — that this same plan just finished re-proving unchanged).

One new observation surfaced in this pass: the comment justifying the `targetPkgs` addition names
a specific phase-scoped planning artifact by filename (`64-LIBZ-FIX-EVIDENCE.md`), which is
expected to be archived away once this milestone completes — unlike this file's other planning
references, which cite durable decision IDs (`D-01`..`D-09`) rather than filenames. See IN-03.

## Warnings

### WR-01: Cold-`@preview`-cache / cold-TLS path through the sandbox is still unverified — `cacert` was still not added (STILL OPEN, unchanged from prior review)

**File:** `flake.nix:26-35`
**Issue:** D-07 (`64-CONTEXT.md`) named `cacert` as the package to add to `targetPkgs` "if a cold
cache turns out to need TLS." Plan 64-05 only added `zlib`; no `cacert` (or `SSL_CERT_FILE`/
`NIX_SSL_CERT_FILE` wiring) is present. Per `64-LIBZ-FIX-EVIDENCE.md`'s own disposition table, this
was deliberately deferred because no gate in that plan exercised a cold `@preview` cache — the
condition that would force the addition never fired, so per the project's own "add only what a
failing measurement demands" rule, `cacert` correctly stays out for now. That said, the underlying
risk described in the prior review is completely unchanged: if the maintainer's `~/.cache/typst/
packages/preview` is ever cleared, or a new package version not already cached is referenced,
`docs-pdf` run through this sandbox still has no verified path to fetch it over TLS.
**Fix:** No code change is required unless/until a cold-cache failure is actually measured. Keep
tracking "verify cold-cache `docs-pdf` behavior through the sandbox" as an explicit follow-up so it
isn't silently forgotten once the warm-cache measurement is read as "D-07 fully closed" — the two
are not the same claim.

## Info

### IN-01: `venvWalk`'s upward walk still depends on ambient `dirname`/coreutils without declaring that dependency (STILL OPEN, unchanged from prior review)

**File:** `flake.nix:44-62` (specifically `dir="$(dirname "$dir")"`)
**Issue:** Unchanged since the prior review. The venv-walk portion of every shim (all seven) runs
on the host shell before entering the FHS sandbox, using whatever `dirname` is first on the ambient
`PATH`. `flake.nix` still does not add `pkgs.coreutils` (or equivalent) to the devShell's
`packages`, so correctness still depends on the host already providing it.
**Fix:** No action required unless the devShell's package list is ever pared down aggressively; if
so, add `pkgs.coreutils` explicitly rather than relying on ambient `PATH`.

### IN-02: The strict-shim not-found message still assumes a `.git` ancestor was found, but the walk can also stop at `/` with none (STILL OPEN, unchanged from prior review)

**File:** `flake.nix:63-72`
**Issue:** Unchanged since the prior review. `venvShimOnStop`'s message ("no executable
.venv/bin/<tool> found walking up from $start (stopped at $dir); provision with: …") does not
distinguish "stopped because a `.git` ancestor was found but had no `.venv`" from "stopped because
the walk reached `/` without ever finding a `.git` ancestor." In the second case the suggested
`uv sync` remedy is misleading — there is no project root at `$dir` to provision.
**Fix:** Track *why* the loop stopped (`.git` found vs. hit `/`) and tailor the message accordingly.

### IN-03 (new): `fhsRun`'s justifying comment names a phase-scoped evidence file that will not survive milestone archival

**File:** `flake.nix:28-30`
**Issue:** The comment added by 64-05 reads: "Pillow's `_imaging` extension carries a bare `NEEDED
libz.so.1`, and uv-managed CPython links zlib statically, so nothing in the process ever maps it
without this entry. See 64-LIBZ-FIX-EVIDENCE.md." This is the only place in `flake.nix` that names
a specific `.planning/phases/.../*.md` file by filename; every other planning-derived comment in
this file cites a durable decision ID instead (`D-01`, `D-02`, `D-03`, `D-07`, etc. — see e.g.
lines 63-64, 74-75, 92-93). Per this project's own milestone lifecycle (phase directories under
`.planning/phases/` get archived once a milestone completes — see the `gsd-cleanup` skill and this
repo's MEMORY notes on milestone archival), `64-LIBZ-FIX-EVIDENCE.md` is a phase-scoped artifact
that is likely to be moved out of its current path or archived entirely once this milestone ships,
at which point this in-code pointer becomes a dangling reference with no way for a future reader to
resolve it via `git blame`/`git log` alone as quickly as a decision-ID citation would allow.
**Fix:** Either fold the load-bearing fact (bare `NEEDED libz.so.1` in Pillow's `_imaging`, no
RPATH/RUNPATH from uv-managed CPython builds) directly into the comment without the filename
pointer, or reference it the same way the rest of the file does — by decision ID — and let the
decision record (not the evidence file's transient path) carry the pointer to supporting detail.

---

_Reviewed: 2026-09-12T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
