# Phase 41: v0.7.0 Release Automation + Release Prep - Pattern Map

**Mapped:** 2026-08-02
**Files analyzed:** 9 (new/modified, excluding one-off hand-run evidence artifacts)
**Analogs found:** 8 / 9 (the CHANGELOG entry itself is prose authored fresh from a structural
model, not code copied from an analog — recorded under "No Analog Found")

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `scripts/extract_changelog_section.py` | utility (CLI script) | file-I/O (text extraction) | `scripts/render_admonition_greyscale.py` | exact (only other file under `scripts/`) |
| `tests/test_changelog_extraction.py` | test | subprocess/request-response | `tests/test_admonition_greyscale_pipeline.py` | exact (subprocess-invokes a `scripts/` module) |
| `.github/workflows/release.yml` (validate job change) | config (CI workflow) | request-response (fail-loud gate) | same file, `validate` job's existing version check (lines 50-59) | exact (in-file precedent) |
| `.github/workflows/release.yml` (create-release job change) | config (CI workflow) | transform (commit dump → curated body) | same file, `Generate release notes` step (lines 152-174) | exact (in-file precedent, being replaced) |
| `CHANGELOG.md` (`## [0.7.0]` entry + tail rollover) | config/docs (structured text) | transform | `CHANGELOG.md`'s own `## [0.6.5]` entry + tail link block | exact (same file, prior entry) |
| `pyproject.toml`, `uv.lock`, `README.md` (version bump) | config | CRUD (literal update) | `tests/test_readme_version_sync.py` (verifies, doesn't write) + Phase 35's version-bump plan | role-match |
| `typsphinx/translator.py` `visit_desc_sig_name` docstring (D-12) | controller (translator visitor method) | transform | same method, same file — docstring-only edit | exact (in-file, no behavior change) |
| `41-HANDOFF.md` | docs (handoff checklist) | — | `35-HANDOFF.md` | exact (explicit named precedent) |
| `41-RELEASE-EVIDENCE.md` | docs (evidence transcript) | — | `35-RELEASE-EVIDENCE.md` | exact (explicit named precedent) |

## Pattern Assignments

### `scripts/extract_changelog_section.py` (utility, file-I/O)

**Analog:** `scripts/render_admonition_greyscale.py` (the only other committed script under
`scripts/`, added this milestone — this is the shape to copy, not a template library).

**Module docstring pattern** (lines 1-53): a long, motivated module docstring explaining *why* the
script exists, referencing the requirement/todo it satisfies, and calling out non-obvious pitfalls
inline (e.g. the BT.601/BT.709 aside, the single-page-PNG caveat). The new script's docstring should
similarly name D-06/D-09/D-10 and the two-`## [Unreleased]`-heading quirk (RESEARCH.md's Pitfall 1)
as the load-bearing gotcha readers must not "fix" by special-casing "Unreleased" by name.

**Imports pattern** (lines 55-63):
```python
from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

import typst
from PIL import Image
```
For the new script, this becomes stdlib-only (`from __future__ import annotations`, `re`,
`sys`, `argparse` inside the `__main__` guard, `pathlib.Path`) — no third-party import at all,
since the extraction is pure text processing (RESEARCH.md's Pattern 2: raw-regex, not a markdown
library).

**Core function + explicit failure-mode raise pattern** (lines 70-117): a top-level function that
takes explicit `Path` args, does the work, and raises a descriptive `RuntimeError` (not a bare
assert) on the one identified failure mode, with a message that names *why* and points at the
mitigation:
```python
def render_admonition_greyscale(typ_path: Path, ppi: float, out_png: Path) -> Path:
    ...
    if not isinstance(result, bytes):
        raise RuntimeError(
            f"{typ_path} compiled to more than one page "
            ...
        )
```
The new script's analogous function — e.g. `extract_section(changelog_text: str, version: str) ->
str` — should raise (not silently return `""`) when the target `## [<version>]` header is not
found, matching D-10's "absent version exits non-zero" requirement. Exit-code plumbing happens in
the `__main__` guard (see below), not inside the core function, exactly as
`render_admonition_greyscale` raises and lets the caller decide exit behavior.

**`__main__` / argparse / exit-code pattern** (lines 155-183):
```python
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=(...))
    parser.add_argument("source_dir", type=Path, help="...")
    parser.add_argument("output_png", type=Path, help="Output PNG path.")
    parser.add_argument("--ppi", type=float, default=DEFAULT_PPI, help="...")
    args = parser.parse_args()
    ...
    out = render_admonition_greyscale(typ_path, args.ppi, args.output_png)
    print(f"Wrote {out}")
```
Note this precedent does NOT wrap the call in try/except to convert exceptions to
`sys.exit(1)` — an uncaught `RuntimeError` propagating out of `__main__` already produces a
non-zero exit with a traceback on stderr, which is sufficient for D-10's "exits non-zero" case.
The new script should follow the same shape: a `version` positional arg, a `--changelog-path`
optional override (default: repo-root `CHANGELOG.md`, computed via `Path(__file__).resolve()
.parents[1] / "CHANGELOG.md"` — mirroring `REPO_ROOT` computation in the version-sync tests
below), print the extracted section body to stdout on success, let an uncaught `RuntimeError`
(or an explicit `sys.exit(1)` after printing to stderr — either satisfies D-10, but an explicit
`print(..., file=sys.stderr); sys.exit(1)` gives CI a clean one-line message rather than a
Python traceback, and is preferable for a script two CI jobs shell out to) handle the failure
path.

**Constants-at-module-level pattern**: `DEFAULT_PPI = 150` sits at module scope with a comment
pointing back at the docstring's rationale. The new script's regex should follow the same shape as
a named, documented, module-level constant (see Pattern 2 below), not inlined into the function.

---

### `tests/test_changelog_extraction.py` (test, subprocess-invoked)

**Analog:** `tests/test_admonition_greyscale_pipeline.py`.

**Subprocess-invocation pattern, not import** (lines 41-44, 85-93):
```python
SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "render_admonition_greyscale.py"
)
...
result = subprocess.run(
    [sys.executable, str(SCRIPT_PATH), str(PROBE_DIR), str(out_png)],
    capture_output=True,
    text=True,
)
assert result.returncode == 0, (
    f"render_admonition_greyscale.py failed:\n"
    f"stdout: {result.stdout}\nstderr: {result.stderr}"
)
```
This is the exact shape D-06/D-09 require: the same script is exercised by pytest via
`subprocess.run([sys.executable, str(SCRIPT_PATH), ...])`, never via `import
extract_changelog_section; extract_changelog_section.extract_section(...)`. Copy this verbatim
for both directions D-10 requires:
- a real version (e.g. `"0.6.5"`, already released and static per RESEARCH.md's Pitfall 3 —
  do NOT use a version that depends on `main..HEAD`'s moving commit count) → assert
  `result.returncode == 0` and `result.stdout` is non-empty and contains expected fixed substrings
  from that entry.
- an absent version (e.g. `"9.9.9"`) → assert `result.returncode != 0`.

**Skip-guard convention**: this precedent uses per-test `@pytest.mark.skipif(not
(PILLOW_AVAILABLE and TYPST_AVAILABLE), reason=...)` rather than a class-level skip, with the
explicit comment that a class-level skip "would let both pass silently by never running." The new
test needs no optional-dependency skip at all (stdlib-only script), so this pattern does not carry
over directly, but the *principle* — never let a test silently no-op — should inform not adding an
unnecessary skip condition.

**Fixture-directory convention**: `PROBE_DIR = Path(__file__).parent / "fixtures" /
"admonition_greyscale_probe"` — a dedicated fixture under `tests/fixtures/`. The new test does not
need a fixture directory since it reads the real repo-root `CHANGELOG.md` directly (matching
`test_preview_version_sync.py`'s and `test_readme_version_sync.py`'s convention of asserting
against the actual repo file, not a synthetic fixture) — but if a case needs a malformed/absent
CHANGELOG to test path-override behavior, follow `tmp_path`-based synthesis (this precedent uses
`tmp_path` for its output artifact, not its input).

---

### `.github/workflows/release.yml` — `validate` job (D-09's new check)

**Analog:** the same job's existing "Verify version matches pyproject.toml" step, `release.yml:50-59`
(measured — CONTEXT.md's line numbers 50-59 confirmed exact against the live tree):

```yaml
      - name: Verify version matches pyproject.toml
        run: |
          PYPROJECT_VERSION=$(uv run python -c "import sys, importlib; tomllib = importlib.import_module('tomllib' if sys.version_info >= (3, 11) else 'tomli'); print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
          TAG_VERSION="${{ steps.version.outputs.version }}"
          echo "pyproject.toml version: $PYPROJECT_VERSION"
          echo "Tag version: $TAG_VERSION"
          if [ "$PYPROJECT_VERSION" != "$TAG_VERSION" ]; then
            echo "::error::Version mismatch: pyproject.toml has $PYPROJECT_VERSION but tag is $TAG_VERSION"
            exit 1
          fi
```

D-09's new step goes immediately beside this one (same job, same "verify before publishing"
position, before the `Run tests` / `Run linters` / `Type check` steps that follow at
`release.yml:61-70`). Copy the shape exactly: a named step, a shell block, an `::error::`-prefixed
message on failure, and `exit 1`. The new step's body should call the extractor for
existence-only, e.g.:
```yaml
      - name: Verify CHANGELOG has a section for this version
        run: |
          uv run python scripts/extract_changelog_section.py "${{ steps.version.outputs.version }}" >/dev/null
```
— relying on the script's own non-zero exit (no need to duplicate the `::error::` echo if the
script's own stderr message is already descriptive; but matching the existing step's convention of
an explicit `::error::` annotation before `exit 1` is preferable for GitHub Actions' inline
annotation UI).

### `.github/workflows/release.yml` — `create-release` job (REL-04's body swap)

**Analog:** the same job's "Generate release notes" step being replaced, `release.yml:152-174`
(measured exact against the live tree):

```yaml
      - name: Generate release notes
        id: notes
        run: |
          TAG="${{ steps.version.outputs.tag }}"

          # Get previous tag
          PREV_TAG=$(git describe --tags --abbrev=0 $TAG^ 2>/dev/null || echo "")

          # Generate changelog
          if [ -n "$PREV_TAG" ]; then
            echo "## Changes since $PREV_TAG" > release_notes.md
            echo "" >> release_notes.md
            git log $PREV_TAG..$TAG --pretty=format:"- %s (%h)" >> release_notes.md
          else
            echo "## Initial Release" > release_notes.md
          fi

          echo "" >> release_notes.md
          echo "## Installation" >> release_notes.md
          echo "" >> release_notes.md
          echo '```bash' >> release_notes.md
          echo "pip install typsphinx==${TAG#v}" >> release_notes.md
          echo '```' >> release_notes.md
```
followed immediately by:
```yaml
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v3
        with:
          tag_name: ${{ steps.version.outputs.tag }}
          name: Release ${{ steps.version.outputs.tag }}
          body_path: release_notes.md
          files: dist/*
          draft: false
          prerelease: ${{ contains(steps.version.outputs.tag, 'a') || contains(steps.version.outputs.tag, 'b') || contains(steps.version.outputs.tag, 'rc') }}
          generate_release_notes: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
Per D-06/D-08: the `git log $PREV_TAG..$TAG --pretty=format:"- %s (%h)"` line (and the
`## Changes since $PREV_TAG` / `## Initial Release` branch around it) is fully removed, replaced
by a call to the committed script writing to the same `release_notes.md` path the
`Installation` block already appends to and `body_path: release_notes.md` already consumes — e.g.:
```yaml
          uv run python scripts/extract_changelog_section.py "${TAG#v}" > release_notes.md
```
The `Installation` block (lines 170-174) is kept verbatim per D-08. `body_path` +
`generate_release_notes: true` staying together on `softprops/action-gh-release` (D-08) requires
no change to the `Create GitHub Release` step at all — only the step that populates
`release_notes.md` changes.

---

### `CHANGELOG.md` — `## [0.7.0]` entry (structural model, not code)

**Analog:** the file's own `## [0.6.5]` entry (lines 10-20+) as the structural shape:
```
## [0.6.5] - 2026-07-29

Fixes a compile-blocking defect where a document mixing prose and math could abort the Typst
compile: inline and display math no longer emit without a valid separator from surrounding text.
The runtime change is confined to the math handlers in `typsphinx/translator.py` — both the inline
and the display-math visitor gained separator participation — with no other file under `typsphinx/`
touched. Zero new runtime dependencies; the bundled `@preview` version-sync surface is untouched.

### Fixed

- **Inline math immediately after text no longer aborts the `typstpdf` compile (MATH-01)** — ...
```
The section-heading skeleton per entry is: lead paragraph → `### Added` / `### Changed` /
`### Fixed` (per D-02's split: `### Added` for CIT, `### Changed` for SIG/IND/FLD/ADM, `### Fixed`
for MATH-02) → `### Verified` → (blank line, next `## [` entry). Bullets use the
`- **Title (REQ-ID)** — description` shape shown above, matching D-01's "requirement IDs in
trailing parentheses" instruction.

**Tail link-block rollover** — the file's tail (measured, current last 20 lines):
```
[0.6.5]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.5
[0.6.4]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.4
...
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.6.5...HEAD
```
Add `[0.7.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.7.0` immediately above the
`[0.6.5]:` line, and change the last line's compare range from `v0.6.5...HEAD` to `v0.7.0...HEAD`.
Note the file's *two* `## [Unreleased]` headings (top, line 8, empty; tail, "Planned for Future
Releases" scratch area) — the new `## [0.7.0]` entry is inserted directly below the top one, ahead
of `## [0.6.5]`; the tail `## [Unreleased]` block is untouched by this phase (it is not a release
entry).

---

### `pyproject.toml` / `uv.lock` / `README.md` version bump

**Analog:** `tests/test_readme_version_sync.py` (verification side) — the sole literal sites this
test guards:
```python
REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"

_STATUS_LINE_RE = re.compile(
    r"\*\*Status\*\*:\s*Stable \(v(?P<version>\d+\.\d+\.\d+)\)"
)
```
This confirms the two edit sites the bump must land in lockstep: `pyproject.toml`'s
`version = "0.6.5"` (bare `[project]` table field, no code copy needed — a direct string literal
edit to `"0.7.0"`) and `README.md`'s `**Status**: Stable (v0.6.5) - Production ready` line (edit to
`v0.7.0`). `uv.lock` is never hand-edited — regenerate via `uv lock` / `uv sync --extra dev
--locked` per RESEARCH.md's own instruction; there is no code pattern to copy for it.

---

### `typsphinx/translator.py` `visit_desc_sig_name` docstring (D-12)

**Analog:** none needed — this is a same-file, same-method docstring text edit at line 6605
(measured: `unresolved-C-domain-type measurement (PyTypeObject *type, no` — the unbalanced `*`
inside `PyTypeObject *type` is the defect). The method itself is at line 6564
(`def visit_desc_sig_name(self, node: addnodes.desc_sig_name) -> None:`). Fix shape: escape or
rephrase so the docstring's inline example does not contain an odd number of `*` characters
(e.g. wrap `*type` in double backtick or rephrase to `PyTypeObject* type` / `PyTypeObject \*type`)
— no code path or emitted-`.typ` shape changes, matching CONTEXT.md's own characterization
("docstring escape... the emitted `.typ` shape does not change").

---

### `41-HANDOFF.md`

**Analog:** `35-HANDOFF.md` (explicit named precedent, full file read above). Structural shape to
copy: an opening "What this phase satisfied, and what it did not" section restating the
requirement text verbatim and mapping each ROADMAP success criterion to the plan/evidence-file
section that satisfies it; a numbered "Checklist" section where each item states **Owner** (always
`/gsd-complete-milestone` or **human** for RTD-console-only steps) and **Ordering** (explicit
dependency on prior items); a "Not done in this phase, by design" bullet list restating every
excluded destructive action; and a closing "Proof the fence held" section with verbatim
`git tag -l v0.7.0` / `git ls-remote --tags origin v0.7.0` output (expected empty), executed twice
independently per 35's own convention ("two independent observations at two separate moments").
Phase 41's version must additionally note the standing second-tag cost on
`typsphinx-doc-translations` (per SC#5's own wording in 41-CONTEXT.md) as its own checklist item,
mirroring 35-HANDOFF.md's item 3.

---

### `41-RELEASE-EVIDENCE.md`

**Analog:** `35-RELEASE-EVIDENCE.md` (explicit named precedent; headings-only structure
confirmed: `## SC#1: ...` through `## SC#5: ...`, each with numbered `### Step N — ...`
subsections and a closing `### SC#N verdict`). Copy this exact per-SC heading shape: one `##`
section per ROADMAP success criterion, each containing verbatim-transcribed command + output
blocks (never paraphrased), and a one-paragraph verdict subsection at the end of each SC section.
Per D-07, this is where the "hand-run, transcribed verbatim" extraction-script demonstration
(SC#1) belongs, and per Pitfall 3 in RESEARCH.md, any commit-count claim ("would otherwise be an
N-line dump") must be re-measured fresh at the moment of writing, not copied from CONTEXT.md's
already-stale 328/369 figures.

## Shared Patterns

### Raw-text regex parsing over a repo file (not a parsing library)
**Source:** `tests/test_preview_version_sync.py` lines 38-43 (`_PREVIEW_IMPORT_RE`) and
`tests/test_readme_version_sync.py` lines 27-29 (`_STATUS_LINE_RE`).
**Apply to:** `scripts/extract_changelog_section.py` and `tests/test_changelog_extraction.py`.
```python
_PREVIEW_IMPORT_RE = re.compile(
    r'#import\s+"@preview/(?P<name>[A-Za-z0-9_-]+):(?P<version>\d+\.\d+\.\d+)"'
)
```
The house convention: a module-level, named, documented `re.compile(...)` constant with a
docstring/comment explaining exactly what it does and does NOT match (e.g. "not a bare mention in
a comment or docstring example"). The CHANGELOG extractor's equivalent anchor is
`r'^## \[(?P<version>[^\]]+)\]'` per RESEARCH.md's Pattern 2 — applied positionally ("take
everything to the next `^## \[` line or EOF"), never special-casing the literal string
"Unreleased" (Pitfall 1).

### `REPO_ROOT`-relative path construction
**Source:** `tests/test_preview_version_sync.py` line 28, `tests/test_readme_version_sync.py`
line 18, `tests/test_admonition_greyscale_pipeline.py` line 42.
**Apply to:** all new/modified files that need the repo root.
```python
REPO_ROOT = Path(__file__).resolve().parents[1]
```
(For a script under `scripts/` rather than `tests/`, this is still `.parents[1]` — one level up
from the file's own directory — since both `scripts/` and `tests/` sit directly under repo root.)

### Comparing parsed values against each other, never against a hardcoded expected string
**Source:** `tests/test_readme_version_sync.py`'s docstring (lines 8-11) and
`tests/test_preview_version_sync.py`'s `test_preview_versions_identical_across_declaration_sites`
docstring (lines 64-67) — both explicitly state this design choice.
**Apply to:** any new assertion comparing two release-surface facts (e.g. if a test wants to
assert `pyproject.toml`'s version matches the newly inserted `CHANGELOG.md` `## [X.Y.Z]` heading,
compare the two parsed values to each other, not against a literal `"0.7.0"` string, so the test
survives the next version bump unmodified).

### Descriptive `AssertionError`/`RuntimeError` messages naming the fix
**Source:** every analog above — e.g. `test_readme_version_sync.py` lines 71-75:
```python
assert readme_version == pyproject_version, (
    f"README.md Status line says v{readme_version} but pyproject.toml "
    f"says {pyproject_version} -- update README.md's Status line "
    "in lockstep with any version bump."
)
```
**Apply to:** the new script's failure path and the new test's assertions — always state what
was found, what was expected, and what to do about it, not a bare `assert x == y`.

### `black`/`ruff` cover `scripts/`; `mypy typsphinx/` does not
**Source:** RESEARCH.md's Pitfall 2, confirmed against `tox.ini`'s `[testenv:type]` (scoped to
`mypy typsphinx/`) versus `[testenv:lint]` (`black --check .` / `ruff check .`, repo-root scoped,
no narrower `exclude`/`include` in `pyproject.toml`'s `[tool.black]`/`[tool.ruff]` tables).
**Apply to:** `scripts/extract_changelog_section.py`. Write clean type hints as good practice
(`render_admonition_greyscale.py` itself does, despite not being mypy-gated), but do not add a
`mypy scripts/` step or treat a hypothetical mypy failure there as a release blocker — it
structurally cannot fail CI's `type` job. Do treat any `black --check .` / `ruff check .` failure
in the new script as a real, CI-failing blocker, since both DO run repo-wide.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `## [0.7.0]` CHANGELOG entry body text (the prose itself, as opposed to its structural shape) | docs | — | Authored fresh per D-01/D-04's requirement-granularity and lead-paragraph rules; the `## [0.6.5]` entry supplies the *shape* to copy (documented above under Pattern Assignments) but the content is new prose, not a code excerpt to transplant |
| SC#4 handler census / `ja` glyph-bar comparison scripts | — (explicitly NOT committed) | — | D-07/RESEARCH.md's Pitfall/Anti-Pattern section explicitly forbids committing these as permanent scripts (Phase 29 D-15 / Phase 30.1 D-03 precedent) — they are one-off hand-run investigations whose *output* goes into `41-RELEASE-EVIDENCE.md`, not new files under `scripts/` or `tests/` |

## Metadata

**Analog search scope:** `scripts/`, `tests/` (version-sync and pipeline test modules),
`.github/workflows/release.yml`, `CHANGELOG.md`, `typsphinx/translator.py`,
`.planning/milestones/v0.6.5-phases/35-v0-6-5-release-prep/` (HANDOFF + RELEASE-EVIDENCE).
**Files scanned:** 9 analog candidates read in full; all matched or exceeded the "3-5 strong
matches" threshold before this document was written.
**Pattern extraction date:** 2026-08-02
