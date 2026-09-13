---
phase: 72-tox-e-linkcheck-and-root-toctree-deduplication
reviewed: 2026-09-13T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - tox.ini
  - CLAUDE.md
  - README.md
  - docs/source/index.rst
  - docs/source/contributing.rst
findings:
  critical: 0
  warning: 0
  info: 1
  total: 1
status: clean
---

# Phase 72: Code Review Report

**Reviewed:** 2026-09-13T00:00:00Z
**Depth:** standard
**Files Reviewed:** 5
**Status:** clean

## Summary

This phase makes two small, mechanically verifiable changes: (1) adds a `[testenv:linkcheck]` section to `tox.ini` plus one matching `tox -e linkcheck` command-listing line in each of `CLAUDE.md`, `README.md`, and `docs/source/contributing.rst`; (2) removes five duplicate child-page entries (`user_guide/configuration`, `user_guide/builders`, `user_guide/templates`, `examples/basic`, `examples/advanced`) from the root `docs/source/index.rst` toctrees.

Verification performed:

- **`[testenv:linkcheck]` correctness:** Matches the shape of the neighbouring `[testenv:docs-html]`/`[testenv:docs-pdf]`/`[testenv:docs]` sections exactly (`runner = uv-venv-lock-runner`, `extras = docs`, `changedir = docs`), differing only in the `sphinx-build -b linkcheck source _build/linkcheck` command and an accurate `description`. Correctly left out of `env_list` (line 2), so `tox` with no `-e` flag still runs `py312, py313, lint, type, cov, docs` only — consistent with the project's documented intent that `linkcheck` needs network access and must be opt-in.
- **Comment-column alignment:** Verified programmatically (`index($0,"#")`) that the new `tox -e linkcheck` line's `#` lands in the same column as its sibling lines in all three files (CLAUDE.md col 30, README.md col 29, contributing.rst col 32) — alignment is correct in each file.
- **Wording accuracy:** "needs network; not run by plain tox" is accurate given `env_list` doesn't include `linkcheck`. No pre-existing mention of `linkcheck` elsewhere in these files that this could conflict or duplicate with. Cross-checked against `.github/workflows/links.yml` (a separate, complementary repo-wide `lychee` link check for files Sphinx's `linkcheck` builder can't reach, e.g. `README.md`, `pyproject.toml`) — no overlap or contradiction.
- **Toctree deduplication reachability:** Confirmed `docs/source/user_guide/index.rst` still has its own nested toctree listing `configuration`, `builders`, `templates`, `output_layout`, and `docs/source/examples/index.rst` still lists `basic`, `advanced`. All five files removed from the root toctree remain reachable via `user_guide/index` → children and `examples/index` → children, which are both still present in the root toctree. No page becomes orphaned.

No Critical or Warning findings. One Info-level observation below.

## Info

### IN-01: `[testenv:linkcheck]` has no failure-tolerance override, unlike an advisory CI-only check

**File:** `tox.ini:92-98`
**Issue:** `sphinx-build -b linkcheck` exits non-zero on any broken/unknown link by default, and this new `tox -e linkcheck` env doesn't pass `-W` or any accept-list, meaning a single flaky external URL fails the whole env locally with no visibility into which links are being tolerated (unlike `.github/workflows/links.yml`'s `lychee` job, which is explicitly advisory and has an accept-list for redirect ranges). This isn't a correctness bug — it matches the phase's literal scope — but a contributor running `tox -e linkcheck` locally may be surprised by transient failures with no guidance in the surrounding docs about that.
**Fix:** Optional follow-up, not required for this phase: consider noting in the `description` or a comment that the env can fail on transient network issues, e.g. `description = Check external links and anchors in the documentation (needs network; may fail transiently)`.

---

_Reviewed: 2026-09-13T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
