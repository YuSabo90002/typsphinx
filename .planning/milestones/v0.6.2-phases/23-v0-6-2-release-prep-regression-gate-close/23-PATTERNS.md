# Phase 23: v0.6.2 Release Prep + Regression-Gate Close - Pattern Map

**Mapped:** 2026-07-23
**Files analyzed:** 5 (4 modified, 1 created)
**Analogs found:** 5 / 5

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `tests/test_readme_version_sync.py` | test | request-response (pure-function read/compare) | `tests/test_preview_version_sync.py` | exact (named by CONTEXT D-13/RESEARCH) |
| `pyproject.toml` | config | CRUD (single field edit) | itself (`:7`, prior version bumps) | exact |
| `uv.lock` | config (generated) | batch (regenerate) | itself (`typsphinx` self-entry `:1379`) | exact |
| `CHANGELOG.md` | documentation | CRUD (insert entry) | itself, `## [0.6.1]` entry (`:10-`) | exact |
| `README.md` | documentation | CRUD (single-line edit) | itself, Status line (`:316`) | exact |

## Pattern Assignments

### `tests/test_readme_version_sync.py` (test, request-response / pure read-compare)

**Analog:** `tests/test_preview_version_sync.py` (full file, 106 lines — read in full, no re-reads needed)

**Module docstring style** (analog lines 1-12):
```python
"""
Tests guarding the 3-way `@preview` version-sync hazard.

typsphinx declares the same four Typst Universe `@preview` package versions
(codly, codly-languages, mitex, gentle-clues) in three separate places:
`typsphinx/writer.py`, `typsphinx/template_engine.py`, and
`typsphinx/templates/base.typ`. These must stay in lockstep, or generated
Typst documents can end up importing mismatched package versions depending
on which code path produced them. This module asserts the three declaration
sites agree, so a future single-file edit fails CI loudly instead of
silently (D-03).
"""
```
New file's docstring must follow the same shape: state the hazard (README Status line drifted stale across two prior releases), name the exact files, state what the test asserts and why it prevents recurrence — cite `D-13` the same way the analog cites `D-03`.

**Repo-root path resolution** (analog lines 14-21):
```python
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

WRITER_PATH = REPO_ROOT / "typsphinx" / "writer.py"
TEMPLATE_ENGINE_PATH = REPO_ROOT / "typsphinx" / "template_engine.py"
BASE_TYP_PATH = REPO_ROOT / "typsphinx" / "templates" / "base.typ"
```
New file: `REPO_ROOT = Path(__file__).resolve().parents[1]`, then `README_PATH = REPO_ROOT / "README.md"` and `PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"` — identical `.parents[1]` depth since the new test also lives directly in `tests/`.

**Regex-based raw-text parsing (module-level constant + doc-commented pattern)** (analog lines 23-30):
```python
EXPECTED_PACKAGES = {"codly", "codly-languages", "mitex", "gentle-clues"}

# Matches an actual Typst `#import "@preview/<name>:<version>"` statement
# (not a bare mention in a comment or docstring example). name is
# letters/digits/underscore/hyphen; version is a three-part semver.
_PREVIEW_IMPORT_RE = re.compile(
    r'#import\s+"@preview/(?P<name>[A-Za-z0-9_-]+):(?P<version>\d+\.\d+\.\d+)"'
)
```
Do **not** reuse this exact regex (it targets `#import "@preview/..."` syntax, not README prose — see RESEARCH.md Pitfall 5). New pattern, verified against current exact text `README.md:316` (`**Status**: Stable (v0.6.1) - Production ready`):
```python
_STATUS_LINE_RE = re.compile(r"\*\*Status\*\*:\s*Stable \(v(?P<version>\d+\.\d+\.\d+)\)")
```

**Extraction-helper pattern** (analog lines 33-47, `_extract_preview_versions`):
```python
def _extract_preview_versions(path):
    """Parse a file's raw text for `#import "@preview/<name>:<version>"` lines.
    ...
    """
    text = path.read_text()
    versions = {}
    for match in _PREVIEW_IMPORT_RE.finditer(text):
        versions[match.group("name")] = match.group("version")
    return versions
```
New file needs two small `_extract_*` helpers (one per file), each returning a plain string — not a dict, since there is exactly one version value per file (unlike the 4-package `@preview` case). For `pyproject.toml`, use `tomllib` per the `tests/test_extension.py` precedent below — not a regex.

**`tomllib` parsing precedent** (from `tests/test_extension.py:79-95`, `test_version_matches_pyproject_toml`):
```python
def test_version_matches_pyproject_toml():
    """Test that __version__ matches pyproject.toml [project].version.

    This parses pyproject.toml independently via tomllib, rather than
    relying on the same importlib.metadata call __version__ itself uses,
    so it is a genuine drift guard rather than a tautology.
    """
    import tomllib
    from pathlib import Path

    import typsphinx

    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)

    assert typsphinx.__version__ == pyproject_data["project"]["version"]
```
New file: reuse `tomllib.load(open(PYPROJECT_PATH, "rb"))["project"]["version"]` verbatim as the parse call inside `_extract_pyproject_version()`; do not invent a regex for this value since a stdlib parser is already proven in this repo. Note the analog does `Path(__file__).parent.parent` (equivalent to `.parents[1]`, module-scoped inline) — the new file should instead use the module-level `PYPROJECT_PATH` constant (matching `test_preview_version_sync.py`'s constants-at-top style, not `test_extension.py`'s inline-per-test style), since D-13 explicitly names `test_preview_version_sync.py` as the template file to mirror.

**Assertion + failure-message style** (analog lines 50-84, both test functions):
```python
def test_preview_versions_identical_across_declaration_sites():
    """The three declaration sites must agree on every @preview version.

    This compares the files against each other (not against a hardcoded
    expected mapping) so the test stays correct if the whole set is
    intentionally rebumped in lockstep — it only fails on a *divergence*.
    """
    ...
    assert (
        not divergences
    ), "@preview version desync detected across declaration sites: " + "; ".join(
        f"{package}: {per_file_versions}" for package, per_file_versions in divergences
    )


def test_all_four_packages_declared():
    """Each declaration site must declare all four expected packages.

    Without this, a dropped import in one file could make the identity
    check above vacuously pass (an empty dict equals another empty dict).
    """
    ...
        assert not missing, (
            f"{filename} is missing expected @preview packages: {missing} "
            f"(declared: {declared})"
        )
```
Pattern to copy: (1) plain module-level test functions, no `Test*` class wrapper, full-sentence docstrings explaining *why* the assertion matters, not just *what* it checks; (2) compare parsed values against each other, not a hardcoded literal, so the test survives a legitimate joint bump; (3) a second guard test exists so an empty/missing value on both sides can't vacuously pass — for the new file this is the `assert match, "..."` guard inside `_extract_readme_status_version()` (see RESEARCH.md's skeleton) rather than a second top-level test function, since there's only one value per file (not a 4-item set) so the vacuous-pass risk is smaller and a single assert-with-message suffices; f-string failure messages name the exact file/line context so a failure is immediately actionable.

**Test function naming convention:** plain functions (no class), descriptive full-sentence-style names: `test_preview_versions_identical_across_declaration_sites`, `test_all_four_packages_declared`. New file: `test_readme_status_version_matches_pyproject` (matches RESEARCH.md's skeleton, which is authoritative and ready to use near-verbatim — see RESEARCH.md "Code Examples" § "New sync test skeleton").

**Do not append to the analog file.** Create a new module `tests/test_readme_version_sync.py`, mirroring the naming shape `test_<subject>_version_sync.py`. Rationale (from RESEARCH.md): the analog's own docstring frames its scope narrowly to the `@preview` hazard; the project's convention is one small single-purpose module per drift hazard, not a shared "misc sync tests" file.

---

### `pyproject.toml` (config, CRUD — single-field edit)

**Analog:** itself, `:7` (current state, read this session):
```toml
[project]
name = "typsphinx"
version = "0.6.1"
```
Convention: bump `version = "0.6.1"` → `"0.6.2"` only; no other line in `[project]` changes. This is the sole version literal in the file (confirmed by RESEARCH.md; `typsphinx/__init__.py:20` reads it dynamically via `importlib.metadata.version`, not a duplicate literal).

---

### `uv.lock` (config, generated — batch regenerate)

**Analog:** itself, the `typsphinx` self-entry (`:1378-1381`, read this session):
```
name = "typsphinx"
version = "0.6.1"
source = { editable = "." }
dependencies = [
```
Convention: this is not hand-edited; regenerate via `uv lock` (Claude's Discretion recommends `uv lock` then verify with `uv sync --extra dev --locked`, per RESEARCH.md). Expect only `version = "0.6.1"` → `"0.6.2"` at this self-entry (plus possibly a cosmetic `revision` counter bump) — no dependency-range changes.

---

### `CHANGELOG.md` (documentation, CRUD — insert one version entry)

**Analog:** the file's own `## [0.6.1]` entry (`:10-` onward, excerpt read this session):
```markdown
## [Unreleased]

## [0.6.1] - 2026-07-20

Rendering fidelity: move `typstpdf` output from "compiles fatal-free" (achieved
in v0.6.0) to "renders faithfully to the source". Implements the last two
silently-dropped nodes, unifies length conversion across all figure/table
sites, and — driven by a full human-assisted visual audit of the Sphinx `doc/`
corpus — fixes the sole high-severity mis-render. Zero new runtime dependencies;
the bundled `@preview` version-sync surface is untouched.

### Added
...
### Changed
...
### Fixed
- **Wide-table glyph collision + right-margin clip (FID-01a)** — ...
### Verified
- Full 151/151-docname human-assisted rendering-fidelity audit ...
```
Convention to copy: `## [X.Y.Z] - YYYY-MM-DD` heading (`##`) → 3-5 line present-tense lead paragraph stating the release's overall theme, ending with the standing "Zero new runtime dependencies; the bundled `@preview` version-sync surface is untouched" sentence → `###` subsections in order `Added`/`Changed`/`Fixed`/`Verified` (only sections that have content) → bullet-level bold lead-in for headline items (`- **Short label (ID range)** — description`). Insert the new `## [0.6.2]` entry between `## [Unreleased]` (line 8) and `## [0.6.1]` (line 10), i.e. right after the blank line following `[Unreleased]`. RESEARCH.md already contains a near-final, ready-to-use `[0.6.2]` draft (11 bullets, D-01 through D-15 compliant) — treat it as the primary source, not a re-derivation target.

**First-time-use conventions this entry introduces** (no prior analog in this file, confirmed via full-file grep this session — `git log -L`/`grep "^### "` shows no prior `Removed` section, and `BREAKING` has appeared only as a section-header suffix, e.g. `### Changed (Breaking)` in `[0.4.0]`, never as a bullet-level prefix): use bullet-level bold-prefix style for the single BREAKING item — `- **BREAKING: <label>** — <description>` — inside a new `### Removed` subsection, per RESEARCH.md's analysis (the section-header-suffix style doesn't fit since only one bullet, not the whole section, is breaking).

---

### `README.md` (documentation, CRUD — single-line edit)

**Analog:** itself, the Status line (`:316`, read this session):
```markdown
## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

---

**Status**: Stable (v0.6.1) - Production ready
**Python**: 3.12+ | **Sphinx**: 9.1+ | **Typst**: 0.15+
```
Convention: bump only `Stable (v0.6.1)` → `Stable (v0.6.2)` on line 316. Leave line 317's `**Python**: 3.12+ | **Sphinx**: 9.1+ | **Typst**: 0.15+` untouched (D-14 explicitly excludes it — already verified in sync with `pyproject.toml`'s dependency floors).

## Shared Patterns

### "Read-your-own-precedent" version bump discipline
**Source:** the project's own prior version-bump commits (implicit; no single file)
**Apply to:** `pyproject.toml`, `uv.lock`, `README.md` together
All three must move in lockstep in a single logical change; the new `tests/test_readme_version_sync.py` (README↔pyproject) plus the pre-existing `tests/test_preview_version_sync.py` (unaffected by this phase, used only to confirm SC#4) are the enforcement mechanisms for exactly this kind of drift.

### "Compare parsed values against each other, never a hardcoded literal"
**Source:** `tests/test_preview_version_sync.py:56-84`
**Apply to:** `tests/test_readme_version_sync.py`
Guarantees the test stays correct across future joint version bumps and only fails on genuine divergence — the single most important structural pattern to carry over, called out explicitly in RESEARCH.md's "Version-Sync Test Design" section.

### "No unverifiable numbers in prose documentation"
**Source:** Phase 22.4 principle (D-01/D-02/D-04 there), extended by this phase's D-11
**Apply to:** `CHANGELOG.md`'s new `[0.6.2]` entry
Page counts and other unassert-able numbers are omitted from the CHANGELOG; only test-backed facts (fatal-free, valid `%PDF` magic, empty `unknown_visit` catalogue) are stated, matching the `[0.6.1]` entry's own restraint pattern for anything not directly asserted by a test.

## No Analog Found

None — all five files this phase touches have a direct, in-repo analog (four are edits to their own prior state; the one new file has an explicitly-named template in CONTEXT.md D-13).

## Metadata

**Analog search scope:** `tests/` (test_preview_version_sync.py, test_extension.py, test_corpus_gate.py), repo root (`pyproject.toml`, `uv.lock`, `CHANGELOG.md`, `README.md`)
**Files scanned:** 6 (5 target files + 1 cross-check analog `tests/test_extension.py`)
**Pattern extraction date:** 2026-07-23
</content>
