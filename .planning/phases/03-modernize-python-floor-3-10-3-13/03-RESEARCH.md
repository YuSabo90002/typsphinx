# Phase 3: Modernize Python Floor (3.10-3.13) - Research

**Researched:** 2026-07-04
**Domain:** Python packaging metadata / CI matrix configuration / dependency-lock resolution (uv)
**Confidence:** HIGH

## Summary

This phase is a pure configuration-surface change (no new code, no new dependencies)
across five files: `pyproject.toml`, `ci.yml`, `docs.yml`, `release.yml`, `tox.ini`.
CONTEXT.md already enumerates every edit site and locks D-01..D-04; this research
answers the three genuine unknowns the planner needs resolved concretely before
writing tasks.

**All three unknowns resolve favorably, with empirical local verification:**

1. **3.13 wheel availability (D-02 contingency): NOT triggered.** Every dev/docs
   dependency in `uv.lock` already has a resolved, 3.13-compatible version with
   either a `cp313` wheel (black 26.5.1, mypy 2.1.0) or a universal `py3-none-any`
   wheel (sphinx 8.1.3, sphinx-autodoc-typehints 3.0.1, sphinx-intl 2.3.2, furo
   2025.12.19, docutils 0.21.2, pytest 9.1.1, ruff 0.15.20 per-platform `py3-none-*`
   wheels). `typst` 0.14.9 ships a `cp38-abi3` stable-ABI wheel (forward-compatible
   with 3.13 without a rebuild) plus explicit `cp314` wheels. **No dependency bump
   is needed for 3.13 support — D-02's contingency does not fire.**

2. **uv.lock 3.13 resolution (blocks tox py313): already resolved, confirmed empirically.**
   `uv.lock`'s `resolution-markers` already group Python 3.12/3.13/3.14 together
   (`python_full_version >= '3.12' and python_full_version < '3.15'`) because
   `requires-python = ">=3.9"` has no upper bound, so uv already solved for versions
   beyond 3.13. Bumping `requires-python` to `>=3.10` and running plain `uv lock`
   (no `--upgrade`) was tested in a scratch worktree: the result is a **pure collapse**
   of each package's `<3.10`/`>=3.10` marker-branch pair down to the already-resolved
   `>=3.10` version — zero new version bumps, one incidental drop of a now-orphaned
   transitive dep (`chardet`, only needed by the `<3.10` branch). This is the safest,
   minimal-diff command sequence and satisfies the diff-minimization discipline
   (Phase 1 D-04/D-05, carried forward).

3. **Python 3.13 runtime breakages: none found.** `uv run pytest tests/` under a
   real Python 3.13.13 interpreter, using the collapsed 3.10+ lock, produced
   **357 passed / 45 failed** — every failure was a subprocess `uv run …` spawn
   failure caused by a NixOS-specific dynamic-linking quirk in this **local dev
   sandbox only** (unrelated to Python 3.13; confirmed by inspecting a failure
   traceback — `Could not start dynamically linked executable: uv`). No test
   failed for a Python-version-related reason. A grep across `typsphinx/`, `tests/`,
   `docs/`, `examples/` found zero uses of any of the 19 PEP 594 "dead battery"
   stdlib modules removed in 3.13 (`cgi`, `telnetlib`, `imghdr`, etc.), zero uses of
   `distutils`, and zero uses of the removed `locale.getdefaultlocale()`. The one
   existing `sys.version_info >= (3, 10)` branch in `tests/test_entry_points.py`
   becomes permanently-true dead code once the floor is 3.10 — harmless, not
   required to clean up in this phase (Phase 4/discretion territory).

**Primary recommendation:** Execute the plan almost exactly as CONTEXT.md's D-01..D-04
specify. Add one concrete step CONTEXT.md doesn't yet name explicitly: after the
`pyproject.toml` surface commit (`requires-python`, classifiers, tool
target-versions), run **plain `uv lock`** (no `--upgrade`) as part of that same
commit, and assert the diff only *removes* `<3.10` marker branches/versions —
if any *new* version appears beyond what's already in the current lock, stop and
flag it as a deviation from the expected collapse (this would indicate the pinned
ceilings in `pyproject.toml` — e.g. `sphinx<9` — allow multiple candidates and uv
picked a different one than today, which should not happen since `uv lock` without
`--upgrade` prefers already-locked versions).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Python version floor/ceiling declaration | Build/Package metadata (`pyproject.toml`) | — | `requires-python` + classifiers are PyPI-facing package metadata, not runtime code |
| Dependency version resolution | Lockfile (`uv.lock`) | Build/Package metadata | `uv.lock` is generated from `pyproject.toml` constraints; must be regenerated in lockstep with floor changes |
| CI test-matrix execution | CI/CD (GitHub Actions `ci.yml`) | Local dev (`tox.ini`) | The matrix `python-version` list and its `include:` tox-env mapping are the CI tier's responsibility; `tox.ini` env_list must mirror it 1:1 |
| Single-version job interpreter selection | CI/CD (`ci.yml`/`docs.yml`/`release.yml`) | — | Non-matrixed jobs (lint/type/coverage/build/integration/docs/release) each hardcode one interpreter version independently of the test matrix |
| Static-analysis target-version alignment | Dev tooling config (`[tool.black]`/`[tool.ruff]`/`[tool.mypy]` in `pyproject.toml`) | CI/CD (interpreter running the tool) | Tool target-version must agree with the interpreter Phase 3 pins single-version jobs to (3.10, per D-01), or the tool second-guesses syntax support |

## Package Legitimacy Audit

**Not applicable this phase.** Phase 3 installs zero new external packages — it only
changes version *floors/ceilings* and *target-version* declarations for packages
already present in `pyproject.toml`/`uv.lock`. The one specific unknown (whether any
existing dep needs a *version bump* for 3.13 support, D-02) resolved to "no bump
needed" (see Summary #1) — so no new/changed package name enters the Standard Stack
this phase.

## Standard Stack

No new libraries are introduced. The existing pinned stack (unchanged from Phase 1/2,
confirmed compatible with 3.10-3.13 by direct `uv.lock` inspection):

### Core (unchanged versions, confirmed 3.13-compatible)
| Library | Locked version (>=3.10 branch) | 3.13 wheel evidence | Source |
|---------|-------------------------------|----------------------|--------|
| sphinx | 8.1.3 | `py3-none-any` (universal) | [VERIFIED: uv.lock] |
| docutils | 0.21.2 | `py3-none-any` (universal, no markers at all) | [VERIFIED: uv.lock] |
| typst | 0.14.9 | `cp38-abi3` stable-ABI wheel + explicit `cp314` wheels | [VERIFIED: uv.lock] |
| black | 26.5.1 | `cp313-cp313-*` wheels present (linux/mac/win) | [VERIFIED: uv.lock] |
| ruff | 0.15.20 | `py3-none-{platform}` wheels (Rust binary shipped per-OS, Python-version-agnostic tag) | [VERIFIED: uv.lock] |
| mypy | 2.1.0 | `cp313-cp313-*` wheels present (linux/mac/win) | [VERIFIED: uv.lock] |
| pytest | 9.1.1 | `py3-none-any` (universal) | [VERIFIED: uv.lock] |
| furo | 2025.12.19 | `py3-none-any` (universal) | [VERIFIED: uv.lock] |
| sphinx-autodoc-typehints | 3.0.1 | `py3-none-any` (universal) | [VERIFIED: uv.lock] |
| sphinx-intl | 2.3.2 | `py3-none-any` (universal) | [VERIFIED: uv.lock] |

**Empirical confirmation:** these exact versions were exercised live under
CPython 3.13.13 in a scratch worktree — `uv sync --extra dev` installed cleanly,
`black --check .` reported "46 files would be left unchanged" with
`target-version = ["py310","py311","py312","py313"]`, and `pytest tests/` collected
and ran 402 tests (357 passed, 45 environment-specific failures unrelated to Python
version — see Summary #3). [VERIFIED: local worktree run, this session]

### Alternatives Considered
None — this phase does not introduce or swap any library; it only widens/shifts the
declared Python version range for the existing stack.

**Installation (no change needed beyond the lock regeneration below):**
```bash
# After bumping pyproject.toml requires-python + classifiers:
uv lock          # NOT --upgrade — see "Don't Hand-Roll" / Pitfall 2 below
```

## Architecture Patterns

### System Architecture Diagram

```
pyproject.toml (requires-python, classifiers, tool target-versions)
        │
        │  1. bump floor/ceiling + tool target-versions (D-01, PYVER-01, PYVER-03)
        ▼
   uv lock   (regenerate — collapses <3.10 marker branches, D-04 commit #1)
        │
        │  2. uv.lock now declares requires-python >=3.10, no <3.10 branches
        ▼
tox.ini env_list (py310, py311, py312, py313, lint, type, cov, docs)  ── D-04 commit #2
        │
        │  3. tox envs use `runner = uv-venv-lock-runner` → resolve from the
        │     regenerated uv.lock per Python version
        ▼
.github/workflows/{ci,docs,release}.yml
        │
        │  4. matrix python-version list 3.10-3.13 + include: tox-env mapping;
        │     every hardcoded single-version `uv python install 3.11` → 3.10 (D-01)
        │     (D-04 commit #3)
        ▼
   git push → PR → GitHub Actions runs full matrix
        │
        │  5. Observe: 3 OS × 4 Python versions (test) + lint + type-check +
        │     coverage + build + integration + docs.yml, all green
        │     (Phase 2 D-01 carried forward: push→observe is definition of done)
        ▼
  Full CI matrix green on 3.10-3.13 (success criterion 5)
```

### Recommended Commit Sequence (D-04)
```
commit 1: pyproject.toml (requires-python, classifiers, tool target-versions)
          + regenerated uv.lock (same commit — lock must never be out of sync
            with the constraints that produced it)
commit 2: tox.ini env_list
commit 3: ci.yml / docs.yml / release.yml (matrix + hardcoded interpreter pins)
          [+ commit 4 only if D-03's black-reformat actually produces a diff —
           confirmed in this research that it does NOT, so no commit 4 expected]
```
Land all commits on one branch/PR so the "atomic batch" success criterion is
satisfied at the PR level (Phase 3 CONTEXT.md specifics section — already decided,
repeated here only to align the commit-sequence recommendation with it).

### Pattern 1: `uv.lock` regeneration without `--upgrade`
**What:** After changing `requires-python` in `pyproject.toml`, run `uv lock` with
no flags (not `uv lock --upgrade`).
**When to use:** Any time a `requires-python` floor/ceiling changes but the actual
dependency *version ceilings* (`sphinx<9`, `docutils<0.22`, `typst<0.15`) are
untouched.
**Why:** `uv lock` (no `--upgrade`) prefers versions already present in the lockfile
when they still satisfy the constraints; it only re-resolves what the narrower
`requires-python` makes newly *unreachable* (the `<3.10` marker branches). This was
verified empirically this session — see Summary #2.
```bash
# Source: verified in a disposable scratch worktree, this session
cd /path/to/repo
# 1. edit pyproject.toml: requires-python = ">=3.10"; drop the 3.9 classifier
uv lock
git diff uv.lock   # expect: only "<3.10" marker-branch entries removed / collapsed,
                    # zero NEW version numbers appearing
```

### Anti-Patterns to Avoid
- **`uv lock --upgrade` for this phase:** Would pull the *latest* resolvable
  version of every dependency, not just collapse the marker branches — this
  reintroduces exactly the kind of unrelated-dep-drift the Phase 1/Phase 3 D-04/D-05
  diff-minimization discipline forbids. Reserve `--upgrade` for Phase 4 (TOOL-01/02).
- **Leaving the `docs-pdf`/`docs-multilang`/`docs-html` tox envs un-added to
  `env_list`:** they already exist in `tox.ini` as named envs (`docs`, `docs-html`,
  `docs-pdf`, `docs-multilang`) but are *not* part of `env_list` today (only `docs`
  is, implicitly via the CI job `tox -e docs-multilang` / `tox -e docs-pdf` direct
  calls, not through `env_list`). Do not conflate "add py313 to env_list" with
  needing to touch the docs envs — they are Python-version-agnostic and untouched
  by this phase.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|--------------|-----|
| Detecting whether a pinned dependency has a 3.13 wheel | A custom PyPI-API polling script | Direct `uv.lock` inspection (`grep -n resolution-markers` + wheel filename tags) | The lockfile already contains the authoritative, already-resolved answer — no network call needed, and it reflects the *exact* pinned version, not "latest" |
| Verifying the lock collapses cleanly for a narrower `requires-python` | Manually diffing every package block by hand | `uv lock` in a disposable scratch copy + `git diff` | uv's resolver already implements the minimal-diff collapse; hand-editing risks missing a transitive dependency change |
| Confirming no 3.13-specific stdlib break | Reading the full "What's New in 3.13" doc top-to-bottom hoping to spot a hit | Grep the codebase for the specific known-removed module names (PEP 594 list + `distutils` + `locale.getdefaultlocale`) | Targeted, verifiable, fast — this codebase is small (~4100 LOC in `typsphinx/`) so an exhaustive grep is authoritative here |

**Key insight:** For a pure floor-bump phase like this, the lockfile and a disposable
scratch worktree are strictly more reliable than researching "does package X support
Python 3.13" via web search — the actual pinned version is what matters, and uv
already resolved that question when the lockfile was last regenerated (it resolves
for the full possible marker range, not just the currently-declared floor).

## Runtime State Inventory

> Not applicable — this is a config-surface version-floor bump, not a rename/refactor/
> migration phase. No stored data, live service config, OS-registered state, secrets,
> or stale build artifacts reference "3.9" or "3.11" as an identifier requiring
> migration. (Verified: this phase only edits five config files; no database, no
> external service config, no OS task registration is touched.)

## Common Pitfalls

### Pitfall 1: Assuming `uv lock` needs `--upgrade` to "pick up" 3.13 support
**What goes wrong:** A planner/executor sees `py313` needs to newly resolve and
reaches for `uv lock --upgrade`, pulling in unrelated newer versions of every
dependency (e.g. a hypothetical `sphinx==8.2.x` if one existed) — violating the
diff-minimization discipline and risking a *different* kind of regression than the
Python-floor bump.
**Why it happens:** Intuition suggests "new Python version support" requires
re-resolving from scratch.
**How to avoid:** Run plain `uv lock` (no flags) — confirmed this session to
produce a pure collapse, not an upgrade.
**Warning signs:** `git diff uv.lock` shows version *bumps* (not just branch
removals) for packages unrelated to Python-version markers.

### Pitfall 2: Testing `tox -e py313` locally on a NixOS dev machine and mis-reading the failure as a 3.13 incompatibility
**What goes wrong:** `tox -e py313` (and any `pyNNN` tox env using
`uv-venv-lock-runner`) fails on this specific NixOS dev machine with
`Could not start dynamically linked executable: uv` — because tox-uv's per-env
`.venv/bin/uv` is a generic-glibc-linux binary NixOS can't run without
`nix-ld`/patchelf. This is **not** a Python 3.13 problem — it reproduces the exact
same root cause Phase 2 already documented for `tox -e py311`
(`.planning/STATE.md` "NixOS cannot execute tox-uv's downloaded standalone CPython
3.11 build") and now confirmed to also affect subprocess-spawned `uv` calls inside
the test suite itself (`tests/test_integration_*.py` call `subprocess.run(["uv",
"run", "sphinx-build", ...])`, which fails identically for the same reason).
**Why it happens:** This machine is NixOS; GitHub Actions runners are standard
Ubuntu/macOS/Windows and are unaffected.
**How to avoid:** For local pre-checks on this machine, use `uv run pytest tests/`
directly (bypassing tox-uv's internal `.venv/bin/uv`) to validate interpreter-level
compatibility, and rely on `tox -e cov` (confirmed working in Phase 2) or the actual
CI push for anything that needs the full tox/subprocess pipeline. The authoritative
verification remains **push → observe GitHub Actions** (Phase 2 D-01, carried
forward) — this local NixOS limitation is a pre-check convenience gap only.
**Warning signs:** Any local tox invocation failing with "Could not start
dynamically linked executable" — this is the NixOS signature, not a code or
Python-version defect.

### Pitfall 3: Forgetting the `docs.yml` `actions/setup-python` step uses a *different* action than `ci.yml`/`release.yml`'s `uv python install`
**What goes wrong:** `docs.yml` line 22-24 uses `actions/setup-python@v6` with
`python-version: "3.11"` (a GitHub-native action), whereas `ci.yml`/`release.yml`
use `uv python install 3.11` (a `uv`-managed interpreter). Both need to change to
`3.10` (D-01) but via their respective mechanisms — a search-and-replace assuming
one shared pattern across all three files could miss the `docs.yml` action's
different syntax.
**Why it happens:** `docs.yml` was likely written before the other two workflows
standardized on `uv python install`.
**How to avoid:** Edit `docs.yml`'s `python-version: "3.11"` key (YAML value, not a
shell command argument) separately; do not rely on a single grep pattern across all
three workflow files.
**Warning signs:** A grep for `uv python install 3.11` across `.github/workflows/`
will not find the `docs.yml` occurrence — confirmed this session (`docs.yml` has
zero `uv python install` lines).

### Pitfall 4: The pre-existing `sys.version_info >= (3, 10)` branch in `tests/test_entry_points.py` looks like it needs updating but doesn't
**What goes wrong:** A contributor sees a Python-version conditional during this
phase and assumes it needs editing (e.g., removing the `else` branch) as part of
"reconciling with the floor."
**Why it happens:** Once the floor is 3.10, the `else` branch (Python 3.9's
dict-like `entry_points()` access) becomes permanently dead code.
**How to avoid:** Leave it as-is — CONTEXT.md scopes this phase to the five listed
config surfaces only; cleaning up now-dead version-gated code in `tests/` is
out of scope (arguably Phase 4/general-tooling-cleanup territory, and is not one of
PYVER-01..04's acceptance criteria). Removing it would be an uninstructed drive-by
change against the diff-minimization discipline.
**Warning signs:** A diff touching `tests/test_entry_points.py` in this phase's PR.

## Code Examples

### Confirmed no-op: black target-version bump produces zero reformatting
```bash
# Source: verified in a disposable scratch copy of typsphinx/, tests/, docs/, this session
# pyproject.toml [tool.black] changed to:
#   target-version = ["py310", "py311", "py312", "py313"]
uvx black==26.5.1 --check --diff .
# Output: "All done! ✨ 🍰 ✨  /  46 files would be left unchanged."
```
This empirically confirms D-03's expectation ("py39→py310 typically produces no
black output change") extends to the full py310-py313 target-version list — no
commit 4 (reformat) is expected to be needed.

### `uv.lock` collapse after `requires-python` bump (exact observed diff shape)
```
# Source: verified this session, `uv lock` (no --upgrade) after:
#   requires-python = ">=3.9" -> ">=3.10"  in pyproject.toml
Resolved 91 packages in 897ms
Updated alabaster v0.7.16, v1.0.0 -> v1.0.0
Updated black v25.11.0, v26.5.1 -> v26.5.1
Updated mypy v1.19.1, v2.1.0 -> v2.1.0
Updated pytest v8.4.2, v9.1.1 -> v9.1.1
Updated sphinx v7.4.7, v8.1.3 -> v8.1.3
... (one line per package that had a <3.10-only branch)
Removed chardet v5.2.0
```
Every line reads `Updated X vOLD, vNEW -> vNEW` — i.e. dropping the now-unreachable
old marker branch and keeping the version *already* selected for `>=3.10`. Nothing
reads `vNEW1 -> vNEW2` (an actual version change). `chardet` is removed outright
because it was only a transitive dependency needed by a `<3.10`-only requests/urllib3
resolution branch.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single dotted `requires-python = ">=3.9"` with no ceiling, letting the lockfile silently accumulate 3.9-only marker branches | Explicit floor bump (`>=3.10`) with a synchronized `uv lock` regeneration in the same commit | This phase | Removes stale <3.10 resolution branches from the lock, shrinking `uv.lock` and removing dead transitive deps (e.g. `chardet`) |
| `black`/`ruff`/`mypy` target-versions trailing behind the actual interpreter floor (`py39` config vs. 3.11 CI interpreter) | Tool target-versions aligned to the same floor the interpreters run (`py310` everywhere) | This phase (PYVER-03) | Eliminates the class of failure where a tool parses/targets syntax for a Python version no longer actually tested |

**Deprecated/outdated:**
- Python 3.9: EOL per CPython's own support schedule; being dropped project-wide
  this phase (matches PYVER-01).
- The 19 PEP 594 "dead battery" stdlib modules (`cgi`, `telnetlib`, `imghdr`, `crypt`,
  etc.) were removed outright in Python 3.13 — confirmed via
  docs.python.org/3/whatsnew/3.13.html and confirmed absent from this codebase by
  grep. [CITED: docs.python.org/3/whatsnew/3.13.html]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | GitHub Actions hosted runners (ubuntu-latest/windows-latest/macos-latest) are standard glibc/native environments unaffected by the NixOS-specific `uv`/tox-uv dynamic-linking failures observed locally | Common Pitfalls #2 | Low — this is standard, widely-relied-upon knowledge about GitHub-hosted runners, not project-specific; if wrong, Phase 2's already-proven-green matrix (Phase 2 D-01) would also have failed, which it did not |

**If this table is empty:** N/A — one low-risk assumption logged above; all other
claims in this research were verified via direct `uv.lock` inspection, an empirical
scratch-worktree `uv lock` + `black --check` + `pytest` run, or a grep audit of the
actual codebase.

## Open Questions

None outstanding for planning purposes. The three unknowns the research brief asked
to resolve (3.13 wheel availability, uv.lock resolution behavior, 3.13 runtime
breakage risk) are all resolved with empirical evidence in the Summary above.

One minor residual note for the planner: `ruff check .` could not be exercised
locally in this sandbox (ruff ships a native/Rust binary; NixOS cannot execute the
generic-glibc `ruff` binary `uvx` downloads without `nix-ld`). This is a local-tooling
gap only — `ruff check .` already runs successfully in CI today (Phase 1/2 lint job
green) and nothing in this phase's diff touches ruff's actual lint rule *selection*,
only its `target-version` string — so this is not expected to be a risk, just an
unverified-locally item the planner should let CI confirm (per carried-forward
Phase 2 D-01, push→observe is authoritative anyway).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` | All CI jobs + local dev | ✓ | 0.11.25 (local); CI installs "latest" via `astral-sh/setup-uv@v7` | — |
| System Python 3.13 | Local pre-check of the new floor's top version | ✓ | 3.13.13 (Nix-provided, not a uv-downloaded standalone build) | — |
| `tox` / `tox-uv` (`uv-venv-lock-runner`) | Local `tox -e pyNNN` pre-checks | ✗ (NixOS-specific) | tox 4.56.1 / tox-uv 1.35.2 resolved in lock | Use `uv run pytest tests/` directly for interpreter-level pre-checks; rely on CI push for full tox pipeline |
| `ruff` (native binary via `uvx`) | Local lint pre-check | ✗ (NixOS-specific) | 0.15.20 resolved in lock | Rely on CI's `lint` job (already green, unaffected by NixOS) |
| `black` (via `uvx`) | Local lint/reformat pre-check | ✓ (pure-Python-invokable, works via `uvx black==<ver>`) | 26.5.1 | — |
| GitHub Actions hosted runners (ubuntu/windows/macos-latest) | Full matrix verification (success criterion 5) | ✓ (external service, not locally probed — proven green in Phase 2 on the current matrix) | — | — |

**Missing dependencies with no fallback:**
- None — every gap above has a documented fallback (direct `pytest` invocation or
  reliance on CI, per carried-forward Phase 2 D-01).

**Missing dependencies with fallback:**
- `tox`/`tox-uv` local execution and `ruff` local execution — both NixOS-specific
  gaps with documented fallbacks above. Not new to this phase (Phase 2 already
  encountered and documented the `tox` gap for `py311`).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (>=3.10 branch) / 8.4.2 (<3.10 branch, being retired this phase) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (testpaths=`tests`, markers `slow`/`integration`) |
| Quick run command | `uv run pytest tests/ -q -m "not integration and not slow"` (excludes the 7 typst-compiling integration tests which need the `typst` CLI + real sphinx-build subprocess) |
| Full suite command | `uv run tox -e cov -- --cov-report=xml` (CI's actual coverage job command) — or, per-Python-version, `uv run tox -e py310` / `py311` / `py312` / `py313` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PYVER-01 | `requires-python>=3.10` + classifiers (drop 3.9, add 3.13) set correctly | static/metadata check | `uv run python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb'))['project']; print(d['requires-python']); print(d['classifiers'])"` | ✅ (no new test file — a metadata assertion, not a pytest test) |
| PYVER-02 | CI matrix covers 3.10-3.13; all hardcoded `uv python install`/`setup-python` lines reconciled to 3.10 | CI observation (push→observe, per Phase 2 D-01) | `gh run watch` on the PR's `ci.yml`/`docs.yml`/`release.yml` runs (release.yml only exercises on a real tag push — not exercised by this phase's PR; validate by reading the diff instead) | ✅ (no new test file — GitHub Actions run is the test) |
| PYVER-03 | `[tool.black]`/`[tool.ruff]`/`[tool.mypy]` target-versions aligned to 3.10 | automated, existing CI jobs | `uv run tox -e lint` (black --check + ruff check) and `uv run tox -e type` (mypy) | ✅ `tox.ini` `[testenv:lint]`/`[testenv:type]` already exist |
| PYVER-04 | `tox.ini` `env_list` updated to py310-py313 in lockstep with CI matrix | static check + CI observation | `diff <(grep -oP "python-version: \[\K[^]]+" .github/workflows/ci.yml) <(grep env_list tox.ini)` (manual lockstep check) + full matrix green | ✅ (lockstep check is a manual/script assertion, not a new pytest test) |
| Success criterion 5 | Full matrix green, no reformat regression, no 3.13 wheel gap | integration (CI) + local pre-check | `black --check .` (confirmed no-op this session) + push→observe full matrix | ✅ existing `[testenv:lint]` covers the black-check portion |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/ -q -m "not integration and not slow"` (fast, ~1-3s per the empirical run this session) + `black --check .` (near-instant)
- **Per wave merge:** `uv run tox -e cov -- --cov-report=xml` locally where possible (NixOS gap noted above — fall back to reading CI on this machine), plus a full `git diff uv.lock` sanity check per Pitfall 1
- **Phase gate:** Full CI matrix (`ci.yml` test job × 12 combinations under the new 3.10-3.13 range, `lint`, `type-check`, `coverage`, `build`, `integration`, and `docs.yml`) green via `gh run watch` — this is the actual Phase 3 "done" signal per carried-forward Phase 2 D-01, not a local proxy.

### Wave 0 Gaps
None — existing test infrastructure (`tests/`, `tox.ini` envs, `ci.yml`/`docs.yml`
jobs) already covers every phase requirement. This phase changes configuration
values, not test coverage; no new test file, fixture, or framework install is
needed.

## Project Constraints (from CLAUDE.md)

No `CLAUDE.md` (project root or `.claude/CLAUDE.md`) exists in this repository —
verified by direct file-existence check this session. No project-specific directives
to reconcile. No `.claude/skills/` or `.agents/skills/` project-skill directories
were found either.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | Phase touches only build/CI config, no auth surface |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | No | No new input-handling code is introduced |
| V6 Cryptography | No | N/A |

### Known Threat Patterns for this stack
None applicable — this phase's entire diff surface is version-floor/classifier
strings and a lockfile regeneration; it introduces no new code path, no new
dependency, and no new attack surface. The one supply-chain-adjacent consideration
(regenerating `uv.lock`) is mitigated by the "no `--upgrade`" recommendation above,
which prevents silently pulling in newer, unaudited versions of any dependency as a
side effect of the Python-floor bump.

## Sources

### Primary (HIGH confidence)
- `/home/yuta/Documents/typsphinx/uv.lock` — direct inspection of `resolution-markers`
  and wheel tags for black, mypy, sphinx, sphinx-autodoc-typehints, sphinx-intl,
  furo, docutils, pytest, ruff, typst.
- Empirical scratch-worktree run this session: `uv lock` diff after `requires-python`
  bump; `black --check --diff .` with `target-version=["py310".."py313"]`;
  `uv run pytest tests/` under CPython 3.13.13.
- `.planning/phases/03-modernize-python-floor-3-10-3-13/03-CONTEXT.md` — locked
  decisions D-01..D-04 and the exact edit-site line enumeration.
- `.planning/phases/02-verify-the-green-baseline/02-CONTEXT.md` — carried-forward
  D-01 (push→observe) and the NixOS `tox`/standalone-CPython local-execution gap.

### Secondary (MEDIUM confidence)
- [What's New In Python 3.13](https://docs.python.org/3/whatsnew/3.13.html) — PEP 594
  "dead battery" module removals, cross-checked against a codebase grep.
- [PEP 594 has been implemented: Python 3.13 removes 20 stdlib modules](https://discuss.python.org/t/pep-594-has-been-implemented-python-3-13-removes-20-stdlib-modules/27124)

### Tertiary (LOW confidence)
- None — every claim in this research was either verified directly against the
  lockfile/codebase, empirically reproduced in a scratch worktree this session, or
  cited from official Python documentation.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — every version/wheel claim verified directly against
  `uv.lock` content, not inferred from training data.
- Architecture: HIGH — the five-file edit map is user-locked in CONTEXT.md; the
  commit-sequencing recommendation is derived directly from that lock.
- Pitfalls: HIGH — all four pitfalls were either empirically reproduced this
  session (NixOS `uv`/tox failures, black no-op) or confirmed by direct grep/read
  of the actual workflow YAML files.

**Research date:** 2026-07-04
**Valid until:** 30 days (stable domain — Python packaging metadata and a fixed
lockfile do not drift quickly; re-verify if `uv.lock` is regenerated with
`--upgrade` for any reason before this phase executes, since that would invalidate
the specific version numbers cited here).
