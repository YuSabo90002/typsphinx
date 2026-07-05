# Phase 5: Durability Guardrails - Pattern Map

**Mapped:** 2026-07-05
**Files analyzed:** 6 (3 modify-only workflows + 1 new workflow + 1 config + 1 doc)
**Analogs found:** 6 / 6 (self-analogous — modify files are their own best analog; drift.yml's analog is ci.yml's job-step skeleton)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `.github/workflows/ci.yml` | CI config (workflow) | batch (mechanical text substitution) | itself (existing file, in-place edit) | exact |
| `.github/workflows/docs.yml` | CI config (workflow) | batch (mechanical text substitution) | itself (existing file, in-place edit) | exact |
| `.github/workflows/release.yml` | CI config (workflow) | batch (mechanical text substitution) | itself (existing file, in-place edit) | exact |
| `.github/workflows/drift.yml` | CI config (workflow), event-driven (schedule/dispatch) | event-driven + batch | `.github/workflows/ci.yml` (checkout/setup-uv/python-install step skeleton) + `docs.yml` (`--extra dev --extra docs` install pattern + `docs-pdf` tox target) | role-match (structural skeleton reused; failure-reporting step is genuinely new) |
| `.github/dependabot.yml` | config | CRUD (declarative config, GitHub-hosted service reads it) | itself (existing `pip` ecosystem block, append `groups:`) | exact |
| `README.md` | doc/config (badge row) | transform (static markdown insert) | itself (existing badge row, lines 3-7) | exact |

## Pattern Assignments

### `.github/workflows/ci.yml` (CI config, batch edit)

**Analog:** itself — 6 in-place `uv sync` line edits, no structural change.

**Exact before/after per site** (verified against current file 2026-07-05):

```yaml
# line 41 (test job) — before:
      - name: Install dependencies
        run: uv sync --extra dev
# after:
      - name: Install dependencies
        run: uv sync --extra dev --locked

# line 71 (lint job) — same pattern
# line 92 (type-check job) — same pattern
# line 113 (coverage job) — same pattern

# lines 150-152 (build job "Check package" step) — before:
      - name: Check package
        run: |
          uv sync --extra dev
          uv run twine check dist/*
# after:
      - name: Check package
        run: |
          uv sync --extra dev --locked
          uv run twine check dist/*

# line 179 (integration job — THE BARE ONE, no --extra) — before:
      - name: Install package and dependencies
        run: uv sync
# after:
      - name: Install package and dependencies
        run: uv sync --locked
```

**Verification command** (run before considering DUR-01 complete):
```bash
grep -n "uv sync" .github/workflows/ci.yml .github/workflows/docs.yml .github/workflows/release.yml \
  | grep -v -- "--locked"
# Expected: empty output after all edits
```

---

### `.github/workflows/docs.yml` (CI config, batch edit)

**Analog:** itself.

**uv sync edit** (lines 29-32):
```yaml
# before:
      - name: Install dependencies
        run: |
          uv sync --extra dev --extra docs
          uv pip install -e .
# after:
      - name: Install dependencies
        run: |
          uv sync --extra dev --extra docs --locked
          uv pip install -e .
```

**softprops bump** (line 67):
```yaml
# before:
      - name: Upload PDF to Release
        if: startsWith(github.ref, 'refs/tags/v')
        uses: softprops/action-gh-release@v2
# after:
        uses: softprops/action-gh-release@v3
```
Note (Pitfall 3): this step only fires on `refs/tags/v*` — a normal PR push→observe run will NOT exercise it. Needs either a manual tag/`workflow_dispatch` test or explicit human sign-off deferred to next real release tag.

---

### `.github/workflows/release.yml` (CI config, batch edit)

**Analog:** itself.

**uv sync edits** (line 36, `validate` job):
```yaml
# before:
      - name: Install dependencies
        run: uv sync --extra dev
# after:
        run: uv sync --extra dev --locked
```

(lines 92-94, `build` job "Check package" step — identical pattern to ci.yml's build job):
```yaml
# before:
      - name: Check package
        run: |
          uv sync --extra dev
          uv run twine check dist/*
# after:
      - name: Check package
        run: |
          uv sync --extra dev --locked
          uv run twine check dist/*
```

**softprops bump** (line 177, `create-release` job):
```yaml
# before:
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ steps.version.outputs.tag }}
          ...
# after:
        uses: softprops/action-gh-release@v3
```
Note (Pitfall 3): this step only fires on tag push or `workflow_dispatch` — not exercised by a normal PR. `release.yml`'s `workflow_dispatch` supports a manual `tag` input, so this one CAN be smoke-tested via manual dispatch if desired, unlike docs.yml's tag-only trigger.

---

### `.github/workflows/drift.yml` (NEW, event-driven)

**Analog for job-skeleton (checkout / setup-uv / python-install):** `.github/workflows/ci.yml`'s `lint`/`type-check`/`coverage` jobs (lines 55-95) — each follows the identical 4-step opener:

```yaml
# ci.yml lines 59-68 (lint job) — the skeleton to mirror verbatim:
    steps:
      - uses: actions/checkout@v6

      - name: Install uv
        uses: astral-sh/setup-uv@v7
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install 3.10

      - name: Install dependencies
        run: uv sync --extra dev
```

**Analog for the docs-pdf install pattern (if drift.yml exercises docs-pdf):** `.github/workflows/docs.yml` lines 26-38:
```yaml
      - name: Install uv
        uses: astral-sh/setup-uv@v7

      - name: Install dependencies
        run: |
          uv sync --extra dev --extra docs
          uv pip install -e .

      - name: Build PDF documentation (English only)
        run: uv run tox -e docs-pdf
```

**Analog for `permissions:` block declaration style:** `.github/workflows/docs.yml` lines 10-13 and `.github/workflows/release.yml` lines 13-15 — both existing workflows already declare an explicit minimal `permissions:` block at the workflow root (not job-level), matching the security posture drift.yml must follow:
```yaml
# docs.yml
permissions:
  contents: write
  pages: write
  id-token: write

# release.yml
permissions:
  contents: write  # Required for creating releases
  id-token: write  # Required for PyPI trusted publishing
```
drift.yml should follow this exact same top-level `permissions:` placement, scoped to `contents: read` + `issues: write` (per RESEARCH.md Pattern 2 / Security Domain).

**Trigger analog:** none of the 3 existing workflows use `schedule:` — this is the one genuinely novel trigger surface. `ci.yml`'s `workflow_dispatch:` (line 8, no inputs) is the closest analog for the manual-trigger half:
```yaml
# ci.yml lines 3-8
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:
```

**No analog exists for:** the `gh issue list`/`create`/`comment` dedup-reporting step — this is new to the repo. RESEARCH.md's Pattern 2 code block (sourced from GitHub's own docs) is the reference to implement directly; there is no in-repo precedent to copy from instead.

**Full synthesized skeleton** (combining the above analogs — see RESEARCH.md Pattern 2 for the complete, ready-to-use version):
```yaml
name: Dependency Drift Check

on:
  schedule:
    - cron: '0 0 * * 1'
  workflow_dispatch:

permissions:
  contents: read
  issues: write

jobs:
  drift-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6          # ← ci.yml pattern
      - name: Install uv
        uses: astral-sh/setup-uv@v7        # ← ci.yml pattern
        with:
          version: "latest"
      - name: Set up Python
        run: uv python install 3.10        # ← ci.yml pattern (single-version jobs)
      - name: Resolve latest allowed dependency versions
        run: uv lock --upgrade             # ← NEW, no in-repo analog
      - name: Install from freshly-resolved lock
        run: uv sync --extra dev --extra docs --locked   # ← docs.yml's --extra pattern
      - name: Exercise the resolved dependency set
        run: uv run tox -e cov,docs-pdf    # ← docs.yml's docs-pdf tox target
      - name: Report drift via deduplicated issue
        if: failure()
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GH_REPO: ${{ github.repository }}
        run: |
          # ← NEW, no in-repo analog; verbatim from GitHub Docs pattern (RESEARCH.md Pattern 2)
          existing=$(gh issue list --label drift --state open --json number --jq '.[0].number')
          ...
```

---

### `.github/dependabot.yml` (config, append)

**Analog:** itself — existing `pip` ecosystem block (lines 3-13).

**Before:**
```yaml
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "00:00"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "automated"
```

**After (append `groups:` block, keep all existing keys unchanged):**
```yaml
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "00:00"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "automated"
    groups:
      sphinx-typst-stack:
        patterns:
          - "sphinx*"
          - "docutils*"
          - "typst*"
```

The `github-actions` ecosystem block (lines 15-23) is untouched — do not add `groups:` there (D-08 explicit constraint).

---

### `README.md` (doc, insert)

**Analog:** itself — existing badge row (lines 3-7).

**Before:**
```markdown
[![PyPI version](https://badge.fury.io/py/typsphinx.svg)](https://badge.fury.io/py/typsphinx)
[![Python Support](https://img.shields.io/pypi/pyversions/typsphinx.svg)](https://pypi.org/project/typsphinx/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://yusabo90002.github.io/typsphinx/)
```

**After (insert new badge line, position at Claude's discretion per D-09; leading position recommended to foreground build-health signal):**
```markdown
[![CI](https://github.com/YuSabo90002/typsphinx/actions/workflows/ci.yml/badge.svg)](https://github.com/YuSabo90002/typsphinx/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/typsphinx.svg)](https://badge.fury.io/py/typsphinx)
[![Python Support](https://img.shields.io/pypi/pyversions/typsphinx.svg)](https://pypi.org/project/typsphinx/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://yusabo90002.github.io/typsphinx/)
```
Follows existing convention exactly: `[![alt](badge-image-url)](link-target-url)`, one line per badge, no blank lines between them.

---

## Shared Patterns

### uv setup step trio (checkout → install uv → set up Python)
**Source:** `.github/workflows/ci.yml` lines 59-68 (any single-Python job: lint/type-check/coverage), also present identically in `docs.yml` lines 19-27 (using `actions/setup-python@v6` variant) and `release.yml` lines 23-33.
**Apply to:** `drift.yml` (new file) — use the `ci.yml` 3-step form (`actions/checkout@v6` → `astral-sh/setup-uv@v7` with `version: "latest"` → `uv python install 3.10`), which is the more common of the two variants in this repo (used in ci.yml and release.yml; docs.yml's `actions/setup-python@v6` variant is the outlier).

### `--locked` append, preserving `--extra` flags
**Source:** RESEARCH.md Pattern 1 (mechanical, already fully enumerated per call site above).
**Apply to:** all 9 sites across ci.yml/docs.yml/release.yml.

### Explicit top-level `permissions:` block
**Source:** `.github/workflows/docs.yml` lines 10-13, `.github/workflows/release.yml` lines 13-15.
**Apply to:** `drift.yml` — declare `permissions: contents: read / issues: write` at workflow root, matching this repo's existing minimal-permissions convention (ci.yml has no `permissions:` block declared — it is the one workflow file without it, so do NOT use ci.yml as the permissions analog).

### Moving-major-tag Action pinning convention
**Source:** repo-wide — `actions/checkout@v6`, `astral-sh/setup-uv@v7`, `actions/upload-artifact@v7`, `actions/download-artifact@v8`.
**Apply to:** the `softprops/action-gh-release@v2 → @v3` bump — consistent with existing convention (moving major tags, not SHA-pinned; SHA-pinning is explicitly deferred per D-12).

## No Analog Found

| File/Section | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `drift.yml` — `schedule:` trigger block | config (trigger) | event-driven | No existing workflow in this repo uses `schedule:` — ci.yml/docs.yml/release.yml are push/PR/tag/dispatch-triggered only. Use RESEARCH.md's cron syntax (`'0 0 * * 1'`) directly; no in-repo precedent exists to copy. |
| `drift.yml` — `gh issue list/create/comment` dedup step | utility (event-driven side-effect) | event-driven | No existing workflow interacts with the GitHub Issues API. Copy verbatim from RESEARCH.md Pattern 2 (sourced from GitHub's own official docs), not from any in-repo file. |

## Metadata

**Analog search scope:** `.github/workflows/*.yml`, `.github/dependabot.yml`, `README.md` (entire in-scope surface for this phase — no broader codebase search needed since this is a pure CI-config phase with no application code involved).
**Files scanned:** 5 existing files (ci.yml, docs.yml, release.yml, dependabot.yml, README.md) — all read in full (all well under 2,000 lines).
**Pattern extraction date:** 2026-07-05
