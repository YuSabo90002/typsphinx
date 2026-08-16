---
created: 2026-08-15
title: "`_track_image()` uses bare `path.isabs()`, not the project's own `posixpath.isabs()` + `_is_drive_qualified()` idiom -- a driveless-absolute Windows image URI is silently not rehomed under CPython 3.13"
area: builder
resolves_phase: 55
severity: minor
source: Phase 52 plan 52-09, surfaced by CI run 31856929828 (Test Python 3.13 on windows-latest), root-caused by direct log read plus CPython source cross-reference; Broken Windows ledger entry 6
files:
  - typsphinx/builder.py:910  # _track_image() -- `if path.isabs(resolved_uri):`
  - typsphinx/builder.py:105-112  # _escapes_outdir() -- the sibling that already avoids this trap
  - tests/test_builder.py  # test_post_process_images_rehome_escape_relocates_with_warning (52-09 fixed the test-side symptom only)
---

## Problem

CPython 3.13 changed `ntpath.isabs()`: a driveless path beginning with a single leading
separator is no longer treated as absolute on Windows. Measured on this machine
(Python 3.13.13):

```
>>> ntpath.isabs('\typsphinx_test_50_03_escape_root\chart.png')
False
>>> ntpath.isabs('C:\typsphinx_test\chart.png')
True
```

`typsphinx/builder.py:910`'s `_track_image()` gates its entire rehome/relocate/warn branch on
`path.isabs(resolved_uri)`, where `path` is the OS-native module (`ntpath` on Windows). Under
CPython 3.13 on Windows, a driveless-absolute image URI (e.g. one planted by a third-party
Sphinx extension outside `<doctreedir>`) now evaluates `False` here, so the whole rehome branch
is skipped, `img["uri"]` is left completely unrewritten, and the image is neither relocated into
the reserved namespace nor warned about.

This is not a new problem this milestone introduced -- `_track_image()` has used bare
`path.isabs()` since Phase 50. It became visible only because CPython 3.13 narrowed what counts
as absolute on Windows, and only `windows-latest` + `py3.13` CI lanes exercise that combination.
`py3.12.14` on the identical `windows-latest` runner, same commit, is unaffected.

The same module already knows about exactly this trap, in a sibling function.
`_escapes_outdir()`, around `typsphinx/builder.py:105-112`, quotes the reasoning verbatim:

```python
segments = stem.replace("\\", "/").split("/")
# posixpath.isabs(), not path.isabs(): this function's own contract is
# platform-independent (D-05) -- the OS-native `path` (== ntpath on a
# Windows CI runner) disagrees with posixpath on which of these shapes
# count as absolute (e.g. ntpath.isabs("/abs/manual") is False, since
# ntpath requires a drive letter or a UNC-style leading "//"), which
# would let a POSIX-shaped escape target through unrefused on Windows.
# Measured on the windows-latest CI lane, 47-10/T2.
return ".." in segments or posixpath.isabs(stem) or _is_drive_qualified(stem)
```

`_escapes_outdir()` deliberately pairs `posixpath.isabs()` with `_is_drive_qualified()` instead
of trusting the OS-native `path.isabs()`, precisely because `ntpath.isabs()`'s notion of
"absolute" does not match a platform-independent one. `_track_image()` at line 910 does not
follow the same idiom -- it is the one caller in this module still trusting bare `path.isabs()`
for a decision that needs to be platform-independent.

**Real behavioural consequence:** on Windows under Python 3.13, a driveless-absolute image URI
(e.g. `\some\path\chart.png`, no drive letter -- reachable if a third-party Sphinx extension
writes an image URI outside `<doctreedir>` in that shape) is silently NOT rehomed, where the
identical input was correctly rehomed under Python 3.12 on the same OS. No warning is emitted
either, because the warning lives inside the same skipped branch. This degrades to the pre-Phase-50
failure mode Phase 50's own IMG-01/IMG-02 review named as a regression class: a silent wrong or
missing image rather than a loud compile abort.

## Why this is still open

Plan 52-09 (Phase 52, v0.8.0 release prep) measured this defect while chasing the last red CI
lane and deliberately fixed only the TEST side -- drive-qualifying the fixture in
`tests/test_builder.py` so it stays absolute on Windows under CPython 3.13 too. The owner's
explicit decision, recorded in `52-09-PLAN.md`'s `<context>`, was: **fix the test, file the
product issue, keep Phase 52's zero-product-lines fence intact for the release.** Phase 52 is
prep-only by design (REL-07); touching `typsphinx/builder.py` here would have broken that fence
for the sake of a narrow, low-reachability Windows+3.13-only gap.

**The product-side fix is therefore still OUTSTANDING.** This todo exists so that fact survives
independently of the test fix -- the test going green must not be read as "the underlying
inconsistency was resolved," because it was not.

## Candidate repair (not attempted here)

Mirror `_escapes_outdir()`'s own idiom at line 910:

```python
if posixpath.isabs(resolved_uri) or _is_drive_qualified(resolved_uri):
```

instead of the current:

```python
if path.isabs(resolved_uri):
```

This would also cover the exact fixture shape the 52-09 test previously exercised (a driveless
leading-separator path) without requiring drive-qualification, on every platform and Python
version -- closing the gap at its source rather than only proving it green in CI. Needs its own
RED-first fixture per this project's standing GATE-01 discipline, run against the unfixed code,
before any fix lands.

## Reachability

Low, same shape as the Phase 50 IMG-01/IMG-02 escape-branch findings: requires a third-party
Sphinx extension to write an absolute image URI outside `<doctreedir>` (Sphinx's own three
post-transforms -- `ImageConverter` / `ImageDownloader` / `DataURIExtractor` -- all write under
`<doctreedir>/images/`), in the specific driveless-absolute Windows shape, running under Python
3.13 specifically.

## Related

- `.planning/phases/52-v0-8-0-release-prep-prep-only/52-CI-EVIDENCE.md` -- both measurements
  (`ntpath.isabs()` behaviour change) and the full CI job-log excerpt this todo is built from.
- `.planning/WINDOWS.md` ledger entry 6 -- the cross-phase defect register entry for this finding,
  marked `fixed` by plan 52-09 (the ledger tracks the CI symptom being discharged; this todo
  tracks the underlying product-side inconsistency, which is a separate, still-open fact).
- `typsphinx/builder.py:105-112` (`_escapes_outdir()`) and `typsphinx/builder.py:36-68`
  (`_is_drive_qualified()`) -- the existing platform-independent idiom this fix would reuse.
