---
phase: 76-the-password-free-publish-pypi-rehearsed-against-the-publish
reviewed: 2026-09-27T00:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - .github/workflows/release.yml
  - tests/test_translator_path_quoting_gate.py
  - typsphinx/translator.py
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---

# Phase 76: Code Review Report

**Reviewed:** 2026-09-27T00:00:00Z
**Depth:** standard
**Files Reviewed:** 3
**Status:** clean

## Summary

Two independent changes were reviewed against `diff_base`:

1. **`.github/workflows/release.yml`** — the `Publish to PyPI` step's
   `with: password: ${{ secrets.PYPI_API_TOKEN }}` block was deleted so the
   job authenticates to PyPI via OIDC Trusted Publishing instead of a static
   token. The job already carried the two prerequisites Trusted Publishing
   needs — top-level `permissions: id-token: write` and an `environment:
   name: pypi` block matching a configured PyPI trusted-publisher entry —
   and neither was touched by this diff, so the change is a correct,
   minimal deletion. The sibling `publish-testpypi` job still authenticates
   via `secrets.TEST_PYPI_API_TOKEN`; per the phase's explicit scope note
   this is intentionally left as-is and is not reported as a finding.
   `attestations:`, `skip-existing:`, action SHA-pinning, and job-level
   `permissions:` narrowing are likewise explicitly out of scope per
   REQUIREMENTS.md and are not reported.

2. **`typsphinx/translator.py`** (MSG-06) — the two cross-directory DEBUG
   `logger.debug()` f-strings in `_compute_relative_include_path()` and
   `_compute_relative_image_path()` were changed from hardcoded
   `up_path='{up_path}'` / `down_path='{down_path}'` apostrophe-delimited
   interpolation to `up_path={quote_path(up_path)}` /
   `down_path={quote_path(down_path)}`, using the existing
   `typsphinx.pathfmt.quote_path()` helper (added in an earlier phase, not
   part of this diff) to select a delimiter that can't be closed early by
   an apostrophe embedded in a path component (e.g. `o'brien`). Traced
   `quote_path()`'s implementation: `up_path` here is always `""` or a
   run of `"../"` so it can never itself contain a quote character, and
   `down_path` is built by `"/".join()` of raw docname/URI segments so it
   can legitimately contain an apostrophe — exactly the case this change
   fixes. Both call sites are pure logging statements with no effect on
   the returned `relative_path`, so there is no behavior change to
   production output, only to the debug log's escaping.

3. **`tests/test_translator_path_quoting_gate.py`** — new gate test
   asserting the exact rendered DEBUG message for both methods, for both
   an apostrophe-carrying `down_path` and an empty `down_path`. Ran the
   file directly (`pytest tests/test_translator_path_quoting_gate.py`):
   4 passed. Confirmed by reading the two target methods that neither
   touches anything on `self` besides the module-level `logger`, so the
   minimal `mock_document`/`mock_builder` fixtures (mirroring
   `tests/test_nested_toctree_paths.py`) are sufficient — the test's own
   docstring claim holds.

Verified `black --check` and `mypy typsphinx/` both pass on the touched
files; `ruff` could not be exec'd in this sandbox (NixOS generic-linux ELF
issue documented in this repo's own CLAUDE.md, not a code defect) but a
manual 88-column check of the changed lines found no violations.

All reviewed files meet quality standards. No issues found.
