# Phase 10: Version-String Fix + v0.5.0 Release - Research

**Researched:** 2026-07-11
**Domain:** Python package version single-sourcing (`importlib.metadata`) + Keep a Changelog release-notes curation
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Release timing (RE-SCOPE — overrides Phase 9 D-03)**
- **D-01:** The release itself is deferred to milestone completion. Phase 10 does NOT tag,
  publish, or merge. It only prepares the branch. The tag + `release.yml` publish + PR #112 merge
  all execute at `/gsd-complete-milestone`.
- **D-02:** This overrides Phase 9's D-03, which had assumed Phase 10 would add the version-bump
  commit to PR #112, merge to `main`, then tag. That assumption is retired by the user's decision.
  PR #112 (`release/v0.5.0 → main`, 13/13 jobs green, observed in Phase 9) remains open/unmerged.
- **D-03:** Tag-on-release-branch is confirmed feasible and is the intended publish mechanism at
  milestone close: git tags can point at any commit (no `main` requirement). `release.yml` fires
  on `v*` push and checks out the tagged commit, so tagging `release/v0.5.0` HEAD publishes
  correctly. The `git describe --tags --abbrev=0 v0.5.0^` in `release.yml`'s notes step resolves
  to `v0.4.4` because `release/v0.5.0` descends from the `v0.4.4` tag (92 commits ahead). Branch
  protection does not apply to tags. Whether the milestone-close step tags the release branch
  directly or merges first is a milestone-close decision, not Phase 10's — Phase 10 just leaves
  the branch ready.

**Version string fix + drift prevention**
- **D-04:** Single-source `__version__` via `importlib.metadata`. Replace the hardcoded
  `__version__ = "0.4.3"` in `typsphinx/__init__.py:14` with
  `__version__ = importlib.metadata.version("typsphinx")` so `pyproject.toml`'s `version` becomes
  the only place a version string lives. This is the root-cause fix — the drift that left `0.4.3`
  stale becomes structurally impossible, not just corrected once.
- **D-05:** `pyproject.toml` MUST be bumped `0.4.4 → 0.5.0`. IMPORTANT correction surfaced during
  scout: the roadmap assumed `pyproject.toml` was already `0.5.0`, but it actually reads `0.4.4`
  (the v0.4.4 release bumped it; the v0.5.0 branch never bumped it). With single-sourcing (D-04),
  bumping `pyproject.toml` to `0.5.0` is what makes `__version__` report `0.5.0`. The
  `release.yml` version-verify gate compares tag vs `pyproject.toml`, so `0.5.0` here is also
  mandatory for the (deferred) publish to pass.

**Release notes & CHANGELOG**
- **D-06:** `CHANGELOG.md` is the single source of truth for the v0.5.0 release notes. Add a
  v0.5.0 entry covering the milestone highlights: Sphinx 9.1 + docutils 0.22 support, typst 0.15 +
  `@preview` bumps (the `kai` fix), the admonition code-mode rendering fix (Phase 8.1), Python
  floor raised to 3.12–3.13, and the CI smoke-gate/guardrail work. At publish time (milestone
  close), the curated v0.5.0 section is passed manually to the GitHub Release body
  (`release.yml`'s `body_path`), avoiding the noisy 92-commit auto-generated `git log`. No
  separate release-notes draft file (avoids double-maintenance with CHANGELOG).

### Claude's Discretion
- Exact `importlib.metadata` implementation detail (e.g., `PackageNotFoundError` fallback for
  uninstalled/source runs) is left to research/planning — see Pattern 1 / Alternatives Considered
  above for the resolved recommendation.
- CHANGELOG entry formatting/section granularity — follow the existing CHANGELOG.md style.

### Deferred Ideas (OUT OF SCOPE)
- Actual v0.5.0 release execution — merge PR #112 (or tag the release branch directly), tag
  `v0.5.0`, run `release.yml` → PyPI + GitHub Release. Deferred to `/gsd-complete-milestone` by
  explicit user decision (D-01). Not lost — it is the milestone-close deliverable.
- ROADMAP/REQUIREMENTS SC reconciliation — Phase 10 SC #2/#3 and REL-01's publish clause should be
  updated to reflect the prepare-vs-publish split. This is bookkeeping for the planner/transition,
  noted so it is not silently dropped (see Open Question 2 below).
</user_constraints>

## Summary

Phase 10 is a small, mechanical, two-deliverable phase: (1) make `typsphinx/__init__.py`'s
`__version__` derive from installed-distribution metadata instead of a hardcoded string, with
`pyproject.toml` as the sole literal version (bumped `0.4.4` → `0.5.0`), and (2) add a curated
`v0.5.0` entry to `CHANGELOG.md`. Everything else (tag, publish, PR #112 merge) is explicitly
deferred to `/gsd-complete-milestone` per CONTEXT.md D-01/D-02.

The highest-value finding from this research is empirical, not theoretical: I directly reproduced
all three `importlib.metadata.version("typsphinx")` runtime scenarios in this exact repo.
`uv sync`-managed dev/CI environments and even a bare `sys.path` insert of the repo root **both
succeed** today only because a stray `typsphinx.egg-info/` directory happens to sit in the repo
root from a prior local install — but `*.egg-info/` is `.gitignore`d (twice), so **a genuinely
fresh `git clone` with no install step raises `PackageNotFoundError`**. This confirms the
`PackageNotFoundError` fallback CONTEXT.md flagged as a discretion item is not optional
defensiveness — it is required, or `import typsphinx` (or at minimum `typsphinx.__version__`)
breaks for anyone who imports the source tree without installing it first (e.g. `sys.path` hacks,
some doc-generation tooling, vendoring). The codebase already has **two internal precedents** for
this exact problem (`typsphinx/pdf.py:97-102` uses `importlib.metadata.version()` with a
try/except and an `"unknown"` string fallback; `docs/source/conf.py:10-25` reads
`pyproject.toml`'s `[project].version` directly via `tomllib` for the Sphinx docs `release`
config) — the planner should follow these existing in-repo conventions rather than invent a new
style.

The second highest-value finding: `tests/test_extension.py::test_setup_version_matches` is
tautological today (`metadata["version"] == __version__`, both trace to the same hardcoded
string) and will **remain tautological** even after D-04's fix, because both sides of that
assertion will still resolve through the identical `importlib.metadata.version()` call. A real
drift guard requires an **independent** second source — `docs/source/conf.py` already shows the
pattern: parse `pyproject.toml` directly with `tomllib` and assert it equals `__version__`. This
is the same technique `.github/workflows/release.yml`'s "Verify version matches pyproject.toml"
step already uses. Recommend adding this as a new test rather than only relying on the existing
tautological one.

Third: bumping `pyproject.toml`'s version has a knock-on effect the CONTEXT.md canonical refs
don't mention — `uv.lock` has its own embedded `version = "0.4.4"` entry for the
`typsphinx` workspace member (`source = { editable = "." }`). `.github/workflows/ci.yml`'s
`examples` job runs `uv sync --locked`, which fails if the lockfile is stale relative to
`pyproject.toml`. The version bump task must include `uv lock` (or `uv sync`, which
regenerates it) so `uv.lock` is back in sync — otherwise a downstream CI leg breaks even though
the two files this phase is scoped to (`__init__.py`, `pyproject.toml`) are individually correct.

**Primary recommendation:** Add `import importlib.metadata` to `typsphinx/__init__.py`, replace
`__version__ = "0.4.3"` with a try/except around `importlib.metadata.version("typsphinx")`
falling back to a non-release-looking sentinel (recommend `"unknown"`, matching the existing
`pdf.py` precedent) on `PackageNotFoundError`; bump `pyproject.toml`'s `version` to `0.5.0`;
regenerate `uv.lock`; add a `tomllib`-based independent drift-guard test; add the curated
`## [0.5.0]` CHANGELOG entry under the correct (top-of-file, line 8) `## [Unreleased]` header.

## Architectural Responsibility Map

This phase is a Python packaging/tooling change, not a multi-tier application feature. The
"tiers" below are this project's packaging/release layers, not client/server/DB tiers.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Version string resolution at runtime (`typsphinx.__version__`) | Package Source (`typsphinx/__init__.py`) | Build/Package Metadata (`pyproject.toml`) | `__init__.py` is where callers read `__version__`; it must derive from, not duplicate, the metadata |
| Canonical version literal | Build/Package Metadata (`pyproject.toml`) | Lockfile (`uv.lock`) | Per D-04/D-05, `pyproject.toml` becomes the *only* place a literal version string is typed; `uv.lock` mirrors it and must be regenerated in lockstep |
| Version drift detection | Test Suite (`tests/test_extension.py`) | CI (`release.yml` validate job) | The test suite is the fast/local gate; `release.yml`'s tag-vs-`pyproject.toml` check is the deferred, release-time gate — both must agree on the same source of truth |
| Release-notes content | Documentation (`CHANGELOG.md`) | CI (`release.yml` create-release job, deferred) | `CHANGELOG.md` is now the sole source per D-06; the deferred `release.yml` step just copies from it (`body_path`) rather than generating notes independently |
| Sphinx extension metadata (`setup()` return `version` key) | Package Source (`typsphinx/__init__.py`) | — | `setup()` just echoes `__version__`; fixing the root (`__version__`) fixes this automatically, no separate edit needed |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|---------------|
| `importlib.metadata` (stdlib) | Python 3.12+ (project floor) | Read the installed distribution's version from `pyproject.toml`-derived metadata at import time | Stdlib since Python 3.8; no dependency to add. This is the standard single-sourcing mechanism when `pyproject.toml` holds a static (non-`dynamic`) version — confirmed via official docs [CITED: docs.python.org/3/library/importlib.metadata.html] and already used elsewhere in this exact codebase (`typsphinx/pdf.py:98`) [VERIFIED: repo inspection] |
| `tomllib` (stdlib) | Python 3.11+ (project floor is 3.12, always available) | Parse `pyproject.toml` directly for an independent drift-guard test | Already used in this exact codebase for the identical purpose — `docs/source/conf.py:10-25` and `.github/workflows/release.yml:52` both parse `pyproject.toml`'s `[project].version` with `tomllib` [VERIFIED: repo inspection] |

No new packages are introduced — both are Python stdlib. **Package Legitimacy Audit: not
applicable** (no external/third-party packages installed this phase).

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| n/a | — | — | This phase touches only stdlib + existing project files |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `importlib.metadata.version()` reading a static `pyproject.toml` version | `setuptools_scm` / `hatch-vcs` (derive version from git tags automatically, no literal string anywhere) | More automated (zero-touch version bumps from tags) but requires switching the version field to `dynamic = ["version"]` and adding a build-time dependency — a build-system change, not a single-line fix. **Out of scope**: CONTEXT.md D-04 already locked the `importlib.metadata` + static-`pyproject.toml` approach; this alternative is noted only so the planner doesn't reconsider it mid-plan |
| `"unknown"` fallback sentinel (matches existing `pdf.py` precedent) | `"0.0.0.dev0"` (PEP 440-compliant sentinel) | `"unknown"` matches in-repo convention and is what a human immediately recognizes as "not really versioned"; `"0.0.0.dev0"` is machine-parseable by PEP 440 tooling if something ever feeds `__version__` into a version comparison. Since `__version__` here is only ever *displayed* (module attribute, Sphinx extension metadata dict) and never version-compared, `"unknown"` is the lower-friction, convention-consistent choice — but this is explicitly a Claude's-discretion item per CONTEXT.md; either is defensible |

**Installation:** None — no new dependencies.

**Version verification:**
```bash
python3 -c "import importlib.metadata as m; print(m.version('typsphinx'))"   # currently reports 0.4.4
```
`importlib.metadata` and `tomllib` are both Python stdlib at the project's 3.12 floor — no
`pip`/`uv` registry check applies.

## Package Legitimacy Audit

**Not applicable.** This phase installs no new external packages (npm/PyPI/crates or otherwise).
Both `importlib.metadata` and `tomllib` are Python standard library modules, already implicitly
available at the project's confirmed `requires-python = ">=3.12"` floor (`pyproject.toml:10`)
[VERIFIED: repo inspection]. No `gsd-tools query package-legitimacy check` run was needed.

## Architecture Patterns

### System Architecture Diagram

```
                         ┌─────────────────────────┐
                         │      pyproject.toml      │
                         │  [project].version =     │
                         │  "0.4.4" → "0.5.0" (D-05) │  <- SOLE literal version (this phase)
                         └────────────┬─────────────┘
                                      │
                   ┌──────────────────┼───────────────────────┐
                   │                  │                       │
        (A) install/build       (B) uv lock                (C) direct file read
        `uv sync` / `uv build`  writes uv.lock's            `tomllib.load()`
                   │             embedded self-version              │
                   ▼                  │                             ▼
     .dist-info / .egg-info    uv.lock "typsphinx"           docs/source/conf.py
     metadata on sys.path      package version entry         (Sphinx docs `release`)
                   │             (must stay in sync,          tests/test_extension.py
                   │              `uv sync --locked`           (NEW drift-guard test,
                   │              gate in ci.yml)               this phase)
                   ▼
     importlib.metadata.version("typsphinx")
                   │
                   ▼
     typsphinx/__init__.py: __version__ =
        importlib.metadata.version("typsphinx")
        except PackageNotFoundError: "unknown"   <- D-04 fix (this phase)
                   │
                   ▼
     setup(app) -> {"version": __version__, ...}   <- Sphinx extension metadata
                   │
                   ▼
     (deferred to milestone close)
     release.yml validate job:
       compares git tag vs pyproject.toml directly
       (NOT __init__.py) -- unaffected by this phase's
       __init__.py implementation detail, only by the
       pyproject.toml literal being correct
```

### Recommended Project Structure

No new files or directories. Edits confined to:
```
typsphinx/__init__.py       # __version__ single-sourcing (D-04)
pyproject.toml               # version bump 0.4.4 -> 0.5.0 (D-05)
uv.lock                      # regenerate (uv lock) to match pyproject.toml bump
tests/test_extension.py      # add/extend drift-guard test
CHANGELOG.md                 # new [0.5.0] entry (D-06)
```

### Pattern 1: `importlib.metadata` version single-sourcing with fallback

**What:** Read the version from installed distribution metadata instead of hardcoding it; catch
the one specific exception `importlib.metadata` raises when the distribution isn't installed.

**When to use:** Any Python package whose `pyproject.toml` holds a static (non-`dynamic`)
`[project].version` and wants a single source of truth without adopting a VCS-based versioning
build backend.

**Example (recommended for `typsphinx/__init__.py`):**
```python
# Source: https://docs.python.org/3/library/importlib.metadata.html (official docs)
#         + existing in-repo precedent typsphinx/pdf.py:97-102 [VERIFIED: repo inspection]
import importlib.metadata

try:
    __version__ = importlib.metadata.version("typsphinx")
except importlib.metadata.PackageNotFoundError:
    # Uninstalled source tree (no .dist-info/.egg-info discoverable on sys.path) --
    # e.g. a fresh `git clone` with no `pip install`/`uv sync` step yet.
    # Sentinel must NOT resemble a real release version (avoids reintroducing the
    # exact drift class this phase fixes). Matches the existing "unknown" convention
    # already used for this same failure mode in typsphinx/pdf.py:105.
    __version__ = "unknown"
```

**Empirical verification performed this session** [VERIFIED: direct execution against this repo]:
```bash
# (1) uv-managed dev env (normal CI/dev flow) -- resolves correctly
$ uv run python -c "import importlib.metadata as m; print(m.version('typsphinx'))"
0.4.4

# (2) bare sys.path insert of repo root, WITH the (gitignored, locally-present)
#     typsphinx.egg-info/ directory still sitting in the repo root -- resolves
#     correctly, but only because of this stray directory, not because it's "installed"
$ python3 -c "
import sys; sys.path.insert(0, '/home/yuta/Documents/typsphinx')
import importlib.metadata as m
print(m.version('typsphinx'))"
0.4.4

# (3) TRUE uninstalled source tree -- copy of typsphinx/ package dir ONLY, no
#     .egg-info/.dist-info anywhere on sys.path -- raises PackageNotFoundError
$ python3 -c "
import sys; sys.path.insert(0, '.')   # cwd = bare copy, no egg-info
import importlib.metadata as m
m.version('typsphinx')"
PackageNotFoundError: No package metadata was found for typsphinx
```
`.gitignore` excludes `*.egg-info/` twice (lines 24 and 77) [VERIFIED: repo inspection], so
scenario (3) is what a genuinely fresh `git clone` experiences until an install step runs. The
`PackageNotFoundError` fallback is therefore load-bearing, not defensive boilerplate.

### Pattern 2: Independent drift-guard test via direct `pyproject.toml` parse

**What:** Assert `__version__` equals the value read directly out of `pyproject.toml`, using a
completely separate code path from the one `__version__` itself uses — this is what makes the
test a genuine regression guard instead of a tautology.

**When to use:** Whenever a "single source of truth" claim needs a test that would actually fail
if the single-sourcing were silently reverted (e.g. someone re-hardcodes a string in
`__init__.py`, or `pyproject.toml` is bumped without re-running `uv sync`/`uv lock` so the
installed metadata goes stale).

**Example (existing in-repo precedent to copy from, adapted for a test):**
```python
# Source: docs/source/conf.py:10-25 [VERIFIED: repo inspection] --
#         same tomllib-parse pattern already used by
#         .github/workflows/release.yml:52 to verify tag vs pyproject.toml
import tomllib
from pathlib import Path


def test_version_matches_pyproject_toml():
    """__version__ must match pyproject.toml's [project].version directly --
    an independent check, not merely re-deriving from the same
    importlib.metadata call __version__ itself uses."""
    import typsphinx

    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)

    assert typsphinx.__version__ == pyproject_data["project"]["version"]
```
Note: `docs/source/conf.py:10-13` still carries a `try: import tomllib / except
ModuleNotFoundError: import tomli as tomllib` fallback for Python <3.11 — this is now dead code
given the project's confirmed 3.12 floor (`requires-python = ">=3.12"`) [VERIFIED: repo
inspection]. It is **not part of this phase's scope** (CONTEXT.md locks the boundary to
`__init__.py` + `pyproject.toml` + `CHANGELOG.md` + the test file); flagging only as an
opportunistic cleanup the planner may choose to fold in or explicitly leave for later — not a
blocking finding.

**Recommendation on the existing `test_setup_version_matches` test
(`tests/test_extension.py:54-68`):** Keep it — it still validates that `setup()`'s returned
metadata dict actually echoes `__version__` (i.e. `setup()` doesn't independently hardcode a
second string). It is not sufficient alone (tautological w.r.t. version *drift*), so **add** the
new `pyproject.toml`-comparison test alongside it rather than replacing it.

### Anti-Patterns to Avoid

- **Fallback sentinel that looks like a real version** (e.g. `"0.5.0"` or the old `"0.4.3"`):
  reintroduces exactly the drift-risk class this phase exists to close — a stale-but-plausible
  version string that nobody notices is wrong. Use an obviously-non-release sentinel.
- **Comparing `__version__` to itself via `importlib.metadata.version()` a second time** in a
  "new" test: this is what makes `test_setup_version_matches` tautological today and will remain
  tautological after the fix if reused as the *only* guard — both sides trace to the identical
  call. The independent guard must read `pyproject.toml` directly (Pattern 2).
- **Bumping `pyproject.toml` without regenerating `uv.lock`**: `ci.yml`'s `examples` job runs
  `uv sync --locked`, which fails on a stale lockfile-vs-pyproject.toml version mismatch.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|--------------|-----|
| Reading the installed package version | A custom `pkg_resources`/regex-on-`pyproject.toml`-at-import-time scheme | `importlib.metadata.version()` (stdlib) | Handles distribution-name normalization, zip-safe installs, and multiple metadata formats correctly; already the standard library's answer to this exact problem since Python 3.8 |
| Parsing `pyproject.toml` for a test/config need | A hand-rolled TOML line-scanner or regex | `tomllib` (stdlib, 3.11+) | Correct TOML parsing (quoting, nested tables) with zero dependency cost; already used twice elsewhere in this codebase for the identical field |

**Key insight:** Both problems this phase touches (read installed version, read a TOML file) have
free, stdlib, already-in-use-in-this-codebase solutions. There is no library gap to fill here —
the fix is entirely "call the existing stdlib function instead of a hardcoded literal."

## Common Pitfalls

### Pitfall 1: Uninstalled source tree breaks `import typsphinx` silently at the version line
**What goes wrong:** Without a `PackageNotFoundError` fallback, `typsphinx/__init__.py` raises an
unhandled exception on line 14 (before even reaching the `sphinx` import) for anyone importing the
package from a checkout that was never `pip install`ed/`uv sync`ed.
**Why it happens:** `*.egg-info/`/`*.dist-info` metadata is generated by an install step and is
`.gitignore`d — a fresh clone has neither until someone runs `uv sync` or `pip install -e .`.
**How to avoid:** try/except `importlib.metadata.PackageNotFoundError` with a non-release-looking
sentinel (see Pattern 1).
**Warning signs:** `ModuleNotFoundError`/`PackageNotFoundError` traceback pointing at the
`__version__` assignment line when running `import typsphinx` from a bare checkout — reproduce
with the exact repro steps under Pattern 1's "Empirical verification" block.

### Pitfall 2: Stale `uv.lock` after the version bump
**What goes wrong:** `pyproject.toml`'s `version` changes to `0.5.0` but `uv.lock`'s own embedded
`version = "0.4.4"` entry for the `typsphinx` package (currently at `uv.lock:1379`) is left
unregenerated; `.github/workflows/ci.yml`'s `examples` job step "Install package and dependencies"
(`uv sync --locked`) then fails because the lockfile no longer matches `pyproject.toml`
[VERIFIED: repo inspection, `ci.yml:175`].
**Why it happens:** `uv.lock` is a generated artifact that must be explicitly regenerated
(`uv lock`) after any `pyproject.toml` metadata change — it does not auto-update on file save.
**How to avoid:** Run `uv lock` (or `uv sync`, which also updates the lock) as part of the same
task/commit that bumps `pyproject.toml`'s version, then confirm with `uv sync --locked` locally
before considering the task done.
**Warning signs:** `uv sync --locked` (or CI's `examples` job) failing with a lockfile-out-of-date
error immediately after the version-bump commit.

### Pitfall 3: Inserting the CHANGELOG entry under the wrong `## [Unreleased]` header
**What goes wrong:** `CHANGELOG.md` has **two** `## [Unreleased]` headings — the canonical one at
line 8 (top, Keep a Changelog convention, immediately followed by `## [0.4.3]` at line 10) and a
stray second one at line 517 (near end-of-file, under a `### Planned for Future Releases` bullet
list, apparently a leftover from an earlier changelog format/merge) [VERIFIED: repo inspection].
Inserting the new `## [0.5.0]` entry near the wrong one either buries it or creates a confusing
duplicate-looking structure.
**Why it happens:** The file has accumulated structural drift from earlier in the project's
history; not obvious without reading the whole file.
**How to avoid:** Insert `## [0.5.0]` directly under line 8's `## [Unreleased]` header (between it
and the current `## [0.4.3]` at line 10) — the standard Keep a Changelog position for the newest
release. Add a `[0.5.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.5.0` link
reference near the bottom's existing link list, and update the `[Unreleased]:` compare-link
(currently `.../compare/v0.4.3...HEAD` at line 537) to `.../compare/v0.5.0...HEAD`.
**Warning signs:** `grep -n "## \[" CHANGELOG.md` shows the entry landed after line 500+ instead
of near line 8-10.

### Pitfall 4: Assuming CHANGELOG needs a backfilled `[0.4.4]` entry too
**What goes wrong:** Noticing `CHANGELOG.md` jumps from `[0.4.3]` straight to no `[0.4.4]` entry
at all (confirmed: `v0.4.4` was tagged via commit `7aca57c chore: bump version to 0.4.4 for
release` with no corresponding CHANGELOG edit) [VERIFIED: `git log v0.4.3..v0.4.4`] might prompt
an unnecessary attempt to backfill a `[0.4.4]` section.
**Why it happens:** It looks like a gap, but v0.4.4's changes were entirely internal
CI/packaging/tooling work (Dependabot grouping, drift-detection workflow, softprops/action-gh-release
v3, a tomllib/tomli release-workflow fix) with no user-facing behavior change — consistent with
Keep a Changelog's convention of only documenting user-facing changes.
**How to avoid:** Do not backfill `[0.4.4]`; CONTEXT.md D-06 already scopes the new entry to
"v0.5.0 entry covering the milestone highlights" (Phases 6-9 + 8.1) — this correctly subsumes the
period since 0.4.3 without a separate 0.4.4 section.
**Warning signs:** N/A — informational only, prevents scope creep in the CHANGELOG task.

### Pitfall 5: `release.yml`'s version-verify gate is unaffected by `__init__.py`'s implementation — don't over-engineer around it
**What goes wrong:** Spending planning effort making `__init__.py`'s fallback/implementation
detail "release.yml-aware" in some way.
**Why it happens:** Easy to over-scope once you've read `release.yml` and see it does version
checking.
**How to avoid:** `release.yml`'s "Verify version matches pyproject.toml" step
(`.github/workflows/release.yml:50-59`) parses `pyproject.toml` directly via `tomllib`/`tomli` and
compares against the git tag — it **never reads `__init__.py` or `__version__` at all**
[VERIFIED: repo inspection]. As long as `pyproject.toml`'s literal is correctly `0.5.0`, this
(deferred, out-of-scope-for-Phase-10) gate is satisfied regardless of `__init__.py`'s
implementation detail. No coupling to design around.
**Warning signs:** N/A — this is purely a scope-boundary reminder for the planner.

## Code Examples

### Full recommended `typsphinx/__init__.py` diff shape
```python
# Source: pattern synthesized from docs.python.org/3/library/importlib.metadata.html
# [CITED] + typsphinx/pdf.py:97-102 in-repo precedent [VERIFIED: repo inspection]
"""
Sphinx Typst Extension
=======================
...
"""

import importlib.metadata
from typing import Any, Dict

from sphinx.application import Sphinx

from typsphinx.builder import TypstBuilder, TypstPDFBuilder

try:
    __version__ = importlib.metadata.version("typsphinx")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"
__author__ = "YuSabo"


def setup(app: Sphinx) -> Dict[str, Any]:
    ...
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
```
Note: moving `import importlib.metadata` above the `__version__` assignment (which itself now sits
after the `from sphinx.application import Sphinx` import) has no observable behavior change for
callers — `import typsphinx` already fails as a whole (not partially) if `sphinx` isn't installed,
regardless of statement order within the module, since Python only binds a module into
`sys.modules` after the entire top-level body executes successfully. [VERIFIED: Python import
semantics + confirmed no `dynamic = ["version"]` in `pyproject.toml`, i.e. no reverse dependency
from build metadata back onto `__init__.py`'s source text]

### `pyproject.toml` version bump
```toml
# Source: pyproject.toml:7 [VERIFIED: repo inspection]
[project]
name = "typsphinx"
version = "0.5.0"   # was "0.4.4"
```

### CHANGELOG.md v0.5.0 entry skeleton (content per CONTEXT.md D-06/Specific Ideas)
```markdown
## [Unreleased]

## [0.5.0] - 2026-07-11

### Changed

- **Forward-ecosystem port**: Sphinx re-pinned to `>=9.1,<10`, `typst` to `>=0.15.0,<0.16`,
  `docutils` to `>=0.21,<0.23`; Python floor raised to 3.12-3.13 (3.10/3.11 dropped)
- Bundled `@preview` packages bumped: `mitex` 0.2.4->0.2.7 (fixes `unknown variable: kai` under
  typst 0.15), `gentle-clues` 1.2.0->1.3.1, `codly-languages` 0.1.1->0.1.10

### Fixed

- Admonition rendering: fixed a markup/code-mode mismatch in the translator that caused
  `.. note::`-style admonitions to render literal unevaluated Typst source instead of typeset prose

### Added

- CI: `typst compile` smoke test catching `kai`-class `@preview` breaks before release;
  `drift.yml`/Dependabot guardrails updated to the new major-version ceilings

[0.5.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.5.0
```
(Exact wording/section granularity is the planner's/implementer's call per CONTEXT.md discretion
— follow existing CHANGELOG.md style, this is a shape example not literal required text.)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|-------------------|---------------|--------|
| `__version__ = "0.4.3"` hardcoded, independent of `pyproject.toml` | `__version__` derived from `importlib.metadata.version("typsphinx")`, `pyproject.toml` sole literal | This phase (D-04) | Version drift between the two files becomes structurally impossible instead of a one-time fix |
| `pyproject.toml` version bumped manually at release time with no CHANGELOG discipline (v0.4.4 precedent — no `[0.4.4]` entry exists) | `CHANGELOG.md` v0.5.0 entry curated as the sole source for the eventual GitHub Release body | This phase (D-06) | Avoids maintaining release notes in two places (a separate draft file + CHANGELOG); `release.yml`'s `body_path` will consume this directly at milestone close |

**Deprecated/outdated:** None — no library APIs are being deprecated by this change; it's a
project-internal convention fix.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|----------------|
| A1 | `"unknown"` is the recommended fallback sentinel (vs. a PEP 440-style sentinel like `"0.0.0.dev0"`) | Standard Stack / Alternatives Considered, Pattern 1 | Low — this is explicitly a Claude's-discretion item per CONTEXT.md; either choice satisfies the requirement. If the planner picks the PEP-440 sentinel instead, no rework needed, just a different literal |
| A2 | The `docs/source/conf.py:10-13` dead `tomli` fallback for Python <3.11 is out of scope for this phase and safe to leave as-is | Pattern 2, note | Low — purely a style/dead-code observation, not load-bearing for REL-01; leaving it does not block the phase's deliverables |

Both assumptions are low-risk discretion items, not compliance/security/retention-policy claims —
neither requires a user-confirmation gate before planning proceeds, but the planner should still
make an explicit choice on A1 rather than silently deciding.

## Open Questions

1. **Should `docs/source/conf.py`'s dead Python-<3.11 `tomli` fallback be cleaned up in this
   phase?**
   - What we know: It's dead code given the confirmed 3.12 floor; it doesn't affect REL-01's
     acceptance criteria.
   - What's unclear: Whether the planner wants to fold this trivial cleanup in opportunistically
     (touches an adjacent, related file) or leave it for a separate housekeeping pass.
   - Recommendation: Leave out of Phase 10's task list by default (CONTEXT.md's boundary is
     explicit: `__init__.py` + `pyproject.toml` + `CHANGELOG.md` + the test file) — mention it in
     the plan's "not in scope" notes so it isn't silently lost, consistent with how CONTEXT.md
     itself flags SC reconciliation as a bookkeeping item.

2. **ROADMAP.md / REQUIREMENTS.md Phase 10 success-criteria reconciliation** (flagged explicitly
   by the orchestrator's additional_context and CONTEXT.md's Deferred Ideas section).
   - What we know: `.planning/REQUIREMENTS.md` REL-01 text (line 44) already reads as re-scoped
     (it explicitly separates "the version-fix half" from "release execution ... deferred to
     milestone completion") — this was already updated. `.planning/ROADMAP.md`'s Phase 10 success
     criteria were **not** verified in this research pass (out of the required-files list) and per
     CONTEXT.md may still describe SC #2/#3 (release.yml green / published to PyPI) as Phase 10
     acceptance criteria.
   - What's unclear: Exact current wording of ROADMAP.md's Phase 10 SC block.
   - Recommendation: Planner should read `.planning/ROADMAP.md`'s Phase 10 section directly before
     finalizing PLAN.md's own success criteria, and explicitly exclude "release.yml green" /
     "published to PyPI" from Phase 10's verification checklist — those belong to
     `/gsd-complete-milestone`, not this phase, per CONTEXT.md D-01.

## Project Constraints (from CLAUDE.md)

- **Commands must match CI exactly**: `black --check .`, `ruff check .`, `mypy typsphinx/`,
  `pytest` (config lives in `pyproject.toml`). The plan's verification steps should use these
  exact invocations.
- **`N802` ruff exception** exists for docutils visitor PascalCase methods — not relevant to this
  phase's diff (no `visit_*`/`depart_*` methods touched).
- **Python 3.10+ typing-compat note in CLAUDE.md** (`ruff` ignores `UP006`/`UP035` to keep
  `Dict`/`List` importable) is **stale relative to the Phase-6-confirmed 3.12 floor**
  (`pyproject.toml requires-python = ">=3.12"`, `ruff.target-version = "py312"`,
  `black.target-version = ["py312", "py313"]` — all already raised) [VERIFIED: repo inspection].
  This is moot for Phase 10's actual diff (`typsphinx/__init__.py`'s edit adds no new
  `Dict`/`List` typing usage — the existing `from typing import Any, Dict` import in `setup()`'s
  signature is untouched), but flagged per the orchestrator's explicit instruction to verify which
  guidance applies. CLAUDE.md itself appears not to have been updated after Phase 6 landed —
  outside Phase 10's scope to fix.
- **Line length 88 (black-owned, `E501` ignored in ruff)**: applies normally to any new lines
  added (the try/except block, the new test function).
- **`tox.ini` `tox-uv~=1.35` pin** and CI job matrix are unaffected by this phase.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|--------------|--------------------|
| REL-01 (version-fix half only; publish half deferred to milestone close) | Version string single-sourced at `0.5.0` — `pyproject.toml` bumped `0.4.4`->`0.5.0` as sole source, `typsphinx/__init__.py` `__version__` derived from `importlib.metadata` (retiring stale `0.4.3`), curated `CHANGELOG.md` v0.5.0 entry prepared | Pattern 1 (single-sourcing implementation + empirically-verified fallback necessity), Pattern 2 (independent drift-guard test replacing the tautological existing one), Pitfall 2 (uv.lock regeneration), Pitfalls 3-4 (CHANGELOG insertion correctness), Code Examples section gives concrete diffs for all three touched files |
</phase_requirements>

## Runtime State Inventory

Phase 10 is not a rename/refactor/migration phase (it's a targeted bug fix + docs addition) — but
because it touches a *version identifier* that could plausibly be cached/registered somewhere,
the canonical question was checked explicitly:

| Category | Items Found | Action Required |
|----------|--------------|-------------------|
| Stored data | None — no database/datastore keys the version string | None |
| Live service config | None — no external service (PyPI, GitHub Release) is touched by Phase 10; those are deferred to milestone close | None |
| OS-registered state | None | None |
| Secrets/env vars | None — no env var or secret encodes the version | None |
| Build artifacts / installed packages | **Yes** — the local dev environment's `.venv` editable install (`typsphinx-0.4.4.dist-info`) and the repo-root `typsphinx.egg-info/` (both gitignored, both locally present in this sandbox) still report `0.4.4` until the environment is re-synced (`uv sync`) after the `pyproject.toml` bump. This is expected/normal (not a migration concern) — just note that `uv sync` (or equivalent) must run **after** the version bump, in the same task, before any test asserting `__version__ == "0.5.0"` will pass locally | Re-run `uv sync` (or `uv lock` + `uv sync`) after bumping `pyproject.toml`, before running the new drift-guard test or any manual `import typsphinx; print(typsphinx.__version__)` check |

**Nothing else found in any category** — verified by direct repo inspection (`git grep` for
`0.4.3`/`0.4.4` across `*.py`/`*.toml`/`*.md`/`*.rst`/`*.cfg`/`*.ini`, and `grep` for
`typsphinx.__version__`/`import typsphinx` across `.github/workflows/` and `tests/`); the only
non-planning, non-CHANGELOG hits were `pyproject.toml` itself and `typsphinx/__init__.py` itself
— no other file encodes the version literal.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|--------------|-----------|---------|----------|
| Python | Runtime | check | 3.13.13 (this sandbox; project floor is 3.12) [VERIFIED] | — |
| `uv` | Dev workflow / lockfile regeneration | check | 0.11.25 [VERIFIED] | — |
| `importlib.metadata` (stdlib) | `__version__` resolution | check | Bundled with Python 3.12+ | — |
| `tomllib` (stdlib) | New drift-guard test, `conf.py`, `release.yml` | check | Bundled with Python 3.11+ (always present at 3.12 floor) | — |

**Missing dependencies with no fallback:** None.
**Missing dependencies with fallback:** None — this phase has no external service or optional-tool
dependency; everything needed is either already in the repo or Python stdlib.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.4+ (`pyproject.toml [tool.pytest.ini_options]`) [VERIFIED: repo inspection] |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`, testpaths `["tests"]`) |
| Quick run command | `pytest tests/test_extension.py -v` |
| Full suite command | `pytest` (or `tox` for the full matrix incl. lint/type/cov/docs) |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|----------------------|---------------|
| REL-01 | `typsphinx.__version__` reports `0.5.0` after install/sync | unit | `python -c "import typsphinx; assert typsphinx.__version__ == '0.5.0'"` (also formalized as a pytest assertion) | Extend existing ✅ `tests/test_extension.py` |
| REL-01 | `__version__` independently matches `pyproject.toml`'s literal `[project].version` (real drift guard, not the existing tautological one) | unit | `pytest tests/test_extension.py::test_version_matches_pyproject_toml -v` | ❌ Wave 0 gap — new test to add |
| REL-01 | `setup(app)` returns `metadata["version"] == "0.5.0"` | unit | `pytest tests/test_extension.py::test_setup_version_matches -v` | ✅ Exists (`tests/test_extension.py:54-68`), keep as-is (validates `setup()` wiring, not drift) |
| REL-01 | `pyproject.toml [project].version == "0.5.0"` | manual/smoke | `python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])"` | N/A — direct file check, no test file needed |
| REL-01 | `uv.lock` stays in sync with the bumped `pyproject.toml` | smoke | `uv sync --locked` (exit 0) | N/A — CI already gates this (`ci.yml:175`); local pre-check recommended before commit |
| REL-01 | `CHANGELOG.md` has a `## [0.5.0]` entry under the correct (top) `## [Unreleased]` header | manual | `grep -n "## \[0.5.0\]" CHANGELOG.md` (should appear near line 8-10, not near line 500+) | N/A — content/prose check, not automatable meaningfully |
| REL-01 (regression) | Full suite + lint/type stay green after the edit | smoke | `pytest && black --check . && ruff check . && mypy typsphinx/` | ✅ Existing suite covers this |

### Sampling Rate

- **Per task commit:** `pytest tests/test_extension.py -v` (fast — the directly-touched test file)
- **Per wave merge:** `pytest && black --check . && ruff check . && mypy typsphinx/`
- **Phase gate:** Full suite green (`pytest`) + `uv sync --locked` succeeds before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] New test `tests/test_extension.py::test_version_matches_pyproject_toml` — independent
      `tomllib`-based drift guard (Pattern 2 above); this is the only genuinely new test file
      content needed. No new test *file* or fixture is required — extends the existing,
      already-covering `tests/test_extension.py`.

*(No framework install needed — pytest is already configured and used project-wide; no new test
directories or `conftest.py` fixtures required for this phase's narrow scope.)*

## Security Domain

`security_enforcement` is enabled (`.planning/config.json` `workflow.security_enforcement: true`,
`security_asvs_level: 1`), so this section is included per protocol, but scoped honestly to what
actually applies.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|-----------------|---------|----------------------|
| V2 Authentication | No | This phase touches no auth surface |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | No (narrow) | `tomllib.load()` on `pyproject.toml` is parsing a trusted, repo-local, developer-authored config file, not untrusted external input — no validation gap introduced |
| V6 Cryptography | No | N/A |
| V14 Configuration (dependency/supply-chain) | Marginally | No new third-party dependency is added (stdlib only, see Package Legitimacy Audit above) — the one supply-chain-relevant fact is that `release.yml` uses PyPI Trusted Publishing (`id-token: write` permission, no long-lived API token in the repo) for the eventual (deferred) publish, which is already the secure baseline and unaffected by this phase |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|------------------------|
| Version-string spoofing / confusion (a package reporting a version it isn't) | Tampering | Exactly what this phase fixes at the root — single-sourcing via `importlib.metadata` means the reported version is always the actually-installed distribution's real version, not an independently-editable literal that can drift out of truthfulness |

No `checkpoint:human-verify` gates are needed for this phase — no new packages, no auth/crypto
surface, no untrusted input path.

## Sources

### Primary (HIGH confidence)
- Direct repo inspection via `Read`/`Bash` (grep, git log, git tag, empirical Python execution)
  of: `typsphinx/__init__.py`, `pyproject.toml`, `uv.lock`, `tests/test_extension.py`,
  `tests/test_entry_points.py`, `typsphinx/pdf.py`, `docs/source/conf.py`, `CHANGELOG.md`,
  `.github/workflows/release.yml`, `.github/workflows/ci.yml`, `.gitignore` — all claims tagged
  `[VERIFIED: repo inspection]` above trace to these direct reads.
- Empirical execution of `importlib.metadata.version("typsphinx")` under three distinct
  filesystem/install scenarios in this exact sandbox (see Pattern 1) — direct tool-confirmed
  ground truth, not inference.

### Secondary (MEDIUM confidence)
- `docs.python.org/3/library/importlib.metadata.html` via WebFetch — confirms `version()`/
  `PackageNotFoundError` official semantics [CITED].
- Keep a Changelog 1.0.0 format conventions (already self-declared in `CHANGELOG.md`'s own
  preamble; cross-checked via web search) [CITED].

### Tertiary (LOW confidence)
- None used as load-bearing for any recommendation in this document.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — stdlib-only, both modules already precedented elsewhere in this exact
  codebase, versions/behavior empirically confirmed against this repo
- Architecture: HIGH — three-file edit surface fully read and cross-referenced; no architectural
  ambiguity for a change this narrow
- Pitfalls: HIGH — all five pitfalls are grounded in direct repo/CI-config inspection or empirical
  reproduction, not speculation

**Research date:** 2026-07-11
**Valid until:** 2026-08-10 (30 days — stable stdlib APIs and a static, already-merged CI/release
configuration; re-verify sooner only if `pyproject.toml`, `uv.lock`, or `.github/workflows/*.yml`
change again before this phase executes)
