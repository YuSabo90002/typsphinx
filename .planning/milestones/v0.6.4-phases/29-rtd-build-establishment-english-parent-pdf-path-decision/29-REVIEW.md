---
phase: 29-rtd-build-establishment-english-parent-pdf-path-decision
reviewed: 2026-07-26T00:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - .readthedocs.yaml
  - docs/source/conf.py
  - tests/test_readthedocs_config.py
findings:
  critical: 0
  warning: 3
  info: 1
  total: 4
status: issues_found
---

# Phase 29: Code Review Report

**Reviewed:** 2026-07-26T00:00:00Z
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Summary

Reviewed the three non-`.planning/` files this phase touched: the new `.readthedocs.yaml` manifest, the
`_resolve_language()` seam added to `docs/source/conf.py`, and the new `tests/test_readthedocs_config.py`
suite. All five domain-flagged hazards from the review brief are correctly handled in the YAML:
`formats: [pdf]` is paired with a `build.jobs.build.pdf` override (avoiding RTD's own LaTeX pipeline), the
override targets a temp directory and copies only `*.pdf` into `$READTHEDOCS_OUTPUT/pdf/`, that
subdirectory is `mkdir -p`'d before the copy, no secrets or credentials appear anywhere in the
(publicly-logged) `build.jobs` commands, and no command delegates to this repo's `tox`. The
`_resolve_language()` precedence chain (`READTHEDOCS_LANGUAGE` → `SPHINX_LANGUAGE` → `"en"`) is correctly
implemented and covered by all four combinations in `test_language_seam_precedence`. `ruff`, `black`, and
the new test module all pass locally.

The remaining concerns are: (1) an edge case in `_resolve_language()` around an env var explicitly set to
the empty string, (2) a load-bearing schema assumption (`python.install[].method: uv` /
`command: sync`) that this phase's own test suite cannot actually verify against RTD's live config
validator — if it's wrong, the entire manifest is rejected and no build (HTML or PDF) ever runs, silently,
until a live RTD build is attempted, and (3) a minor hardening note on the predictable `/tmp` path used by
the PDF override script. None of these rise to a proven BLOCKER from static review of these three files
alone, but (2) in particular deserves a live-build confirmation before this is treated as done, since it
is the single point of failure for the whole phase's goal.

## Warnings

### WR-01: `python.install[].method: uv` schema correctness is unverified by any test in this suite

**File:** `.readthedocs.yaml:47-57`, `tests/test_readthedocs_config.py:110-119`
**Issue:** The manifest's entire dependency-installation story rests on `method: uv` /
`command: sync` / `extras: [docs]` being accepted by Read the Docs' real config-file-v2 validator. The only
test coverage (`test_readthedocs_yaml_shape`) asserts that the parsed YAML matches the literal values the
author put there (`entry.get("method") == "uv"`, etc.) — it is entirely self-referential and provides zero
protection against `method: uv` (or the `command`/`extras` sub-keys) being an invalid or misremembered
schema key. If RTD's validator rejects any of these keys, RTD refuses the *entire* config file, and no
build — HTML or PDF — ever runs. That failure mode is silent from this repo's perspective: `pytest`, `ruff`,
`black`, and `mypy` all stay green, and the only way to discover the break is an actual RTD build attempt.
Given the review brief calls this exact risk out as the crux of the phase, and the phase's own
`29-RESEARCH.md` cites this as "confirmed" against RTD's docs, this is not asserted here as definitely wrong
— but the local test suite cannot distinguish "correct" from "confidently wrong" on this point, so it should
not be treated as verified until an actual RTD build (or RTD's remote config-validation feedback) confirms
it.
**Fix:** Before marking this phase's RTD-01 requirement fully satisfied, trigger one real RTD build (the
phase's own verification plan already calls for this) and read the raw build log for either a successful
`uv sync` install-provenance line or a top-level "invalid configuration" rejection. If it fails, the correct
alternative shape (per RTD's currently-documented schema) is likely a `pip`-based fallback:
```yaml
python:
  install:
    - method: pip
      path: .
      extra_requirements:
        - docs
```

### WR-02: `_resolve_language()` treats an env var explicitly set to `""` as a real value, not "unset"

**File:** `docs/source/conf.py:51-52`
**Issue:**
```python
def _resolve_language():
    return os.getenv("READTHEDOCS_LANGUAGE", os.getenv("SPHINX_LANGUAGE", "en"))
```
`os.getenv(name, default)` only returns `default` when the variable is *absent* from the environment — if
`READTHEDOCS_LANGUAGE` (or `SPHINX_LANGUAGE`) is present but set to the empty string (e.g. a misconfigured
CI/local shell doing `export READTHEDOCS_LANGUAGE=` with nothing after the `=`), this function returns `""`
rather than falling through to the next layer or to `"en"`. Sphinx's `language = ""` is not a valid locale
and would break the build (or `gettext`-based localization lookups) in a way that is not obviously connected
to this line. This exact edge case is not exercised by any of the four cases in
`test_language_seam_precedence` (all four either set a non-empty value or delete the var entirely).
**Fix:**
```python
def _resolve_language():
    return (
        os.getenv("READTHEDOCS_LANGUAGE")
        or os.getenv("SPHINX_LANGUAGE")
        or "en"
    )
```

### WR-03: Predictable, fixed `/tmp` directory name in the PDF build override

**File:** `.readthedocs.yaml:27-28`
**Issue:** `mkdir -p /tmp/typst-pdf-build/doctrees` and the subsequent `sphinx-build` output directory both
use a fixed, predictable path under `/tmp` rather than a uniquely-generated temp directory (`mktemp -d`).
In a genuinely single-tenant, ephemeral RTD build container this is low risk, but it's still an avoidable
deviation from the standard hardening practice of never `mkdir`-ing into a shared, world-writable directory
by a guessable name (symlink pre-creation races, TOCTOU). It also means a second concurrent process in the
same container (unlikely here, but not something this file can guarantee) would silently share the
directory.
**Fix:**
```yaml
- PDF_TMPDIR=$(mktemp -d)
- mkdir -p "$PDF_TMPDIR/doctrees"
- sphinx-build -b typstpdf -d "$PDF_TMPDIR/doctrees" docs/source "$PDF_TMPDIR/out"
- mkdir -p "$READTHEDOCS_OUTPUT/pdf/"
- cp "$PDF_TMPDIR"/out/*.pdf "$READTHEDOCS_OUTPUT/pdf/"
```
(Note RTD executes each `build.jobs.build.pdf` entry as a separate shell invocation by default, so a shell
variable set in one line may not survive to the next without confirming RTD executes the whole list in one
persistent shell — verify this before adopting the above verbatim.)

## Info

### IN-01: Loose substring matching in `test_readthedocs_yaml_pdf_override` command-shape assertions

**File:** `tests/test_readthedocs_config.py:210-243`
**Issue:** The `mkdir_indices` and `copy_indices` checks use `"mkdir" in cmd and "READTHEDOCS_OUTPUT" in cmd
and "pdf" in cmd` / `"cp " ... and "*.pdf" in cmd and "READTHEDOCS_OUTPUT" in cmd` substring tests rather than
a more structural check (e.g. splitting into argv-like tokens). This is adequate for the current 4-line
command list, but a future edit that adds a decoy command containing all three substrings incidentally (e.g.
an echoed diagnostic string) would satisfy the assertion without actually performing the required
`mkdir`/`cp`, silently weakening the guarantee this test is meant to provide.
**Fix:** Low priority given the current small, stable command list; if `build.jobs.build.pdf` grows,
consider tokenizing each command (e.g. `shlex.split(cmd)`) and asserting on the leading token (`argv[0] ==
"mkdir"` / `"cp"`) rather than membership-testing the whole string.

---

_Reviewed: 2026-07-26T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
