# Phase 31: Published-URL Cutover + Repo-Wide Link Guard - Pattern Map

**Mapped:** 2026-07-26
**Files analyzed:** 6 (2 rewrite targets, 1 new workflow, 1 new test, 1 full-refresh doc, plus 1 draft artifact)
**Analogs found:** 5 / 6

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `.github/workflows/links.yml` (new) | CI workflow / config | event-driven (push/PR trigger → external HTTP fetch) | `.github/workflows/drift.yml` | exact (advisory standalone workflow shape) |
| `README.md` (edit) | config/content (published metadata) | transform (string rewrite, in-place) | `README.md` itself (prior edits) / `tests/test_readme_version_sync.py`'s regex-parse model | role-match |
| `pyproject.toml` (edit, `[project.urls]` only) | config | transform (string rewrite) | `pyproject.toml` itself | role-match |
| `tests/test_no_stale_github_io_links.py` (new, recommended) | test (hermetic regression guard) | request-response (none — pure text assertion) | `tests/test_readme_version_sync.py` | exact |
| `.planning/codebase/INTEGRATIONS.md` (full refresh) | doc / config | transform (content rewrite) | itself (existing structure retained, sections updated) | n/a — no other analog needed, it's a self-rewrite |
| Issue #119 close-reply draft | non-code artifact | request-response (GitHub Issues) | prior PR#98 reply precedent (per CONTEXT.md D-16) — not a file in this repo | no analog (external artifact) |

## Pattern Assignments

### `.github/workflows/links.yml` (CI workflow, event-driven)

**Analog:** `.github/workflows/drift.yml` (full file read, 53 lines)

**Full structure to mirror** (`.github/workflows/drift.yml:1-18`):
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
    name: Resolve latest deps and exercise them
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v7
```

**Deviations required for links.yml** (per CONTEXT.md D-02/D-04/D-05):
- `on:` becomes `push:` + `pull_request:` (no `schedule:`, no `workflow_dispatch` requirement — D-02).
- `permissions:` becomes `contents: read` ONLY — drop `issues: write` (research Assumption A3: no auto-filed issue behavior is decided for this phase; do not copy drift.yml's issue-creation step).
- Do NOT copy drift.yml's "Report drift via a single deduplicated issue" step (lines 37-53) — that whole failure-handling block is drift-specific and out of scope here. links.yml's failure signal is just the job going red (D-04).
- Add the scope-documentation comment block at the top of the file (SC#3 requirement) — see RESEARCH.md's Code Examples skeleton for exact wording pattern (a `#`-prefixed block above `name:`, explaining this job — not sphinx linkcheck — covers README.md/pyproject.toml).
- Same `actions/checkout@v7` pin convention (drift.yml:18) — matches this repo's existing major-version-tag pinning convention across `ci.yml`, `docs.yml`, `release.yml`.

**Full target skeleton** (already fully specified in RESEARCH.md Code Examples — copy near-verbatim, this is the primary deliverable):
```yaml
name: Link Check

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  link-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - name: Check links
        uses: lycheeverse/lychee-action@v2
        with:
          args: >-
            --verbose --no-progress
            --extensions md,html,rst,txt,toml
            --exclude-path '.planning'
            --exclude-path 'CHANGELOG.md'
            --exclude-path 'tests/fixtures'
            --accept '100..=103,200..=299,429'
            --max-retries 3
            --timeout 20
            .
          fail: true
          jobSummary: true
```
Note: RESEARCH.md's Pitfall 3 / Open Question flags that `examples/**/README.md` and `examples/**/*.rst` likely also need `--exclude-path` entries (unrelated pre-existing placeholder 404s) — planner must decide and add corresponding lines; not present in the skeleton above.

---

### `README.md` (config/content, transform)

**Analog:** the file's own current state (`README.md:1-30`, `:260-284` — both ranges read this session)

**Current pattern to replace** (`README.md:8`):
```markdown
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://yusabo90002.github.io/typsphinx/)
```
→ becomes (D-12) RTD's official build-status badge, e.g.:
```markdown
[![Documentation Status](https://app.readthedocs.org/projects/typsphinx/badge/?version=latest)](https://typsphinx.readthedocs.io/)
```

**Current pattern to replace** (`README.md:12`):
```markdown
**[📖 Documentation](https://yusabo90002.github.io/typsphinx/)** | **[🐛 Issue Tracker](https://github.com/YuSabo90002/typsphinx/issues)** | **[📦 PyPI](https://pypi.org/project/typsphinx/)**
```
→ `https://yusabo90002.github.io/typsphinx/` becomes `https://typsphinx.readthedocs.io/` (D-11 bare root); the Issue Tracker/PyPI links are untouched (they already point correctly).

**Current pattern to replace** (`README.md:267-277`, the Documentation section, full block already read):
```markdown
**📖 Full documentation is available at [yusabo90002.github.io/typsphinx](https://yusabo90002.github.io/typsphinx/)**

Quick links:

- [Installation Guide](https://yusabo90002.github.io/typsphinx/installation.html)
- [Quick Start](https://yusabo90002.github.io/typsphinx/quickstart.html)
- [User Guide](https://yusabo90002.github.io/typsphinx/user_guide/)
- [Configuration Reference](https://yusabo90002.github.io/typsphinx/user_guide/configuration.html)
- [Examples](https://yusabo90002.github.io/typsphinx/examples/)
- [API Reference](https://yusabo90002.github.io/typsphinx/api/)
- [Contributing Guide](https://yusabo90002.github.io/typsphinx/contributing.html)
```
→ each `https://yusabo90002.github.io/typsphinx/<suffix>` becomes `https://typsphinx.readthedocs.io/en/latest/<suffix>` (D-10; suffixes unchanged — all 7 curl-verified 200 in RESEARCH.md). `:267`'s bare-root sentence link becomes `https://typsphinx.readthedocs.io/` (D-11, no `/en/latest/`, per the top-level-link rule). Add D-13's one-line ja-docs link somewhere in this section (placement/wording is Claude's discretion) pointing at `https://typsphinx.readthedocs.io/ja/latest/`.

**Regression-guard analog** (`tests/test_readme_version_sync.py:14-45`) — the recommended new test file should follow this exact structure (module docstring explaining the hazard being guarded, `REPO_ROOT`-relative `Path` constants, a compiled regex or plain substring check, a helper function with an assertion that fails loudly with an explanatory message if the pattern is absent/changed). Do not import via `importlib.metadata`; parse raw text directly (established convention, also used by `test_preview_version_sync.py`).

---

### `pyproject.toml` (config, transform)

**Analog:** the file's own current state (`pyproject.toml:1-70`, read this session)

**Current pattern to replace** (`pyproject.toml:56`, inside `[project.urls]`, lines 54-58):
```toml
[project.urls]
Homepage = "https://github.com/YuSabo90002/typsphinx"
Documentation = "https://github.com/YuSabo90002/typsphinx#readme"
Repository = "https://github.com/YuSabo90002/typsphinx"
Issues = "https://github.com/YuSabo90002/typsphinx/issues"
```
→ only the `Documentation` line changes, to `Documentation = "https://typsphinx.readthedocs.io/"` (D-11 bare root). `Homepage`/`Repository`/`Issues` are explicitly NOT rewrite targets (CONTEXT.md D-11 / "Files this phase touches" list) — leave untouched.

---

### `tests/test_no_stale_github_io_links.py` (new, test/hermetic)

**Analog:** `tests/test_readme_version_sync.py` (full file, 76 lines, read this session)

**Structure to copy wholesale** — module docstring naming the hazard, `REPO_ROOT = Path(__file__).resolve().parents[1]`, `README_PATH`/`PYPROJECT_PATH` constants, one `test_*` function per assertion, plain substring or regex checks (no network calls — this is the hermetic regression guard, distinct from the real-HTTP curl checks which are not pytest tests). RESEARCH.md's Code Examples section already gives the exact recommended body:
```python
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

def test_readme_has_no_github_io_links():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "github.io" not in text, (
        "README.md still references a github.io URL -- Phase 31 rewrote these to "
        "typsphinx.readthedocs.io; a github.io link here is a regression."
    )

def test_pyproject_documentation_url_is_not_readme_anchor():
    text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "typsphinx#readme" not in text
```
Note this file's own `import re` is unused by the shown body — drop it or use it, per whichever assertion form the planner actually implements (regex vs substring); `test_readme_version_sync.py`'s pattern favors named regex constants when matching structured prose (see `_STATUS_LINE_RE`), plain substring `in`/`not in` when checking mere absence (simpler, matches the RESEARCH.md skeleton above).

---

### `.planning/codebase/INTEGRATIONS.md` (full refresh, doc)

**Analog:** itself — no external analog needed; this is a content refresh of an existing 140-line doc, not a new-file pattern-copy. Read the current file in full during planning/execution (not done in this pass — out of scope for pattern-mapping since it's a self-rewrite, not modeled on another file). Known staleness points to fix (from CONTEXT.md D-18 / RESEARCH.md State of the Art): zero RTD content in Hosting section; "CI only: SPHINX_LANGUAGE" line must become the `READTHEDOCS_LANGUAGE > SPHINX_LANGUAGE > "en"` precedence (Phase 29); `actions/checkout@v6` claim is stale — every workflow in this repo (`ci.yml`, `docs.yml`, `drift.yml`, `release.yml`) now uses `@v7` (confirmed this session via `drift.yml:18` read above); the `typsphinx-doc-translations` submodule/repo (Phase 30.1) is undocumented; `links.yml` (this phase's new workflow) needs to be added to whatever section enumerates workflow files.

---

## Shared Patterns

### Advisory CI workflow shape
**Source:** `.github/workflows/drift.yml:1-18` (structure) — see full analog block above.
**Apply to:** `.github/workflows/links.yml`.
Key invariant: never register the job name in branch protection's required checks (D-04); never add `continue-on-error: true` (would mask real failures); `permissions:` scoped to only what's needed (`contents: read` for links.yml vs drift.yml's added `issues: write`, which links.yml does not need).

### Regression-guard test shape
**Source:** `tests/test_readme_version_sync.py` (full file) — see full analog block above.
**Apply to:** `tests/test_no_stale_github_io_links.py`.
Key invariant: parse raw file text directly (never `importlib.metadata` or a live import), assert with an explanatory failure message, no network I/O (network verification is a separate curl-based manual step per D-08, not a pytest test).

### URL-shape conventions (not code, but a repeatable pattern across both edited files)
**Source:** CONTEXT.md D-10/D-11/D-12/D-13; verified via curl in RESEARCH.md Code Examples.
**Apply to:** `README.md` and `pyproject.toml`.
- Deep links (7 of them): `https://typsphinx.readthedocs.io/en/latest/<suffix>` — suffix unchanged from the current github.io suffix.
- Top-level/root links (README:12, README:267, pyproject Documentation, GitHub About→Website): bare `https://typsphinx.readthedocs.io/` — no `/en/latest/` segment, so Phase 33's `latest`→`stable` Default Version flip auto-propagates with zero re-editing.
- Badge (README:8): `https://app.readthedocs.org/projects/typsphinx/badge/?version=latest` (note the `app.readthedocs.org` host, distinct from `typsphinx.readthedocs.io` — do not conflate the two hosts).
- New ja-docs link (README, D-13): `https://typsphinx.readthedocs.io/ja/latest/`.

## No Analog Found

| File/Artifact | Role | Data Flow | Reason |
|---|---|---|---|
| Issue #119 close-reply draft | non-code artifact (GitHub Issues comment) | request-response (GitHub API/UI) | Not a repository file; no code analog applies. CONTEXT.md D-16 points to the PR#98 reply precedent as the stylistic model (English, terse, whole-thread-read) — that precedent is a past GitHub comment, not something retrievable via Read/Grep in this codebase. Planner/executor should follow D-16/D-17's content rules directly (fulfillment report only, no migration narrative) rather than a code pattern. |

## Metadata

**Analog search scope:** `.github/workflows/` (drift.yml, ci.yml, docs.yml, release.yml headers checked for checkout-version convention), `tests/` (test_readme_version_sync.py, test_preview_version_sync.py, test_readthedocs_config.py located), `README.md` (full badge block + full Documentation section read), `pyproject.toml` (full `[project]`/`[project.urls]` block read), `.planning/codebase/INTEGRATIONS.md` (length-checked, not fully re-read — self-rewrite, no analog needed).
**Files scanned:** 6 read in full or targeted ranges; 4 additional workflow files referenced by name for the checkout-version convention cross-check (not fully read — the version string was already visible in drift.yml plus CONTEXT.md/RESEARCH.md's own verified claims).
**Pattern extraction date:** 2026-07-26
