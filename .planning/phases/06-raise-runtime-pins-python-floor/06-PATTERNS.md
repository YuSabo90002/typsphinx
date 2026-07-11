# Phase 6: Raise Runtime Pins + Python Floor - Pattern Map

**Mapped:** 2026-07-09
**Files analyzed:** 6 declaration files (no new source modules — pin/floor edit phase)
**Analogs found:** 21/21 declaration sites mapped to exact current-value excerpts; strong precedent commit found for the whole surface

## Precedent (strongest analog for this entire phase)

This phase is a repeat of a prior pin-raise phase against the **identical declaration
surface**: the v0.4.4 milestone's Python-floor modernization (3.9→3.10-3.13), phase "03".

- `fce2ffb` — `feat(03-01): bump Python floor to 3.10-3.13 in pyproject.toml + regenerate uv.lock`
- `2e285d4` — `feat(03-01): reconcile CI/docs/release workflows to the 3.10-3.13 floor`
- `ee2f9ae` — `docs(03-01): complete modernize-python-floor plan 01`
- `caf779d` — `fix(03-02): backport tomllib via tomli for the 3.10 docs floor`
- `6ce9889` — `docs(04-03): update README Python version references to 3.10`
- `62b01e7` — `docs(04-03): update ruff UP035/UP006 comment text to Python 3.10+ support`
- `d99748d` — `docs(04-03): complete Python 3.9->3.10 leftover cleanup plan`

Use `git show fce2ffb` / `git show 2e285d4` as the concrete precedent for *how* each of the
site categories below (pyproject dependency strings, classifiers, tox `env_list`, CI matrix,
single-runner `uv python install` lines, `uv.lock` regeneration) was edited last time — same
files, same site shapes, just different version numbers. The `d99748d`/`62b01e7`/`6ce9889`
"leftover cleanup" commits are the analog for the **optional hygiene items** noted below
(stale `UP035`/`UP006` comment text, README version mentions, CLAUDE.md line 75) — Phase 6
does NOT need to replicate those unless the planner chooses to fold hygiene in.

**Pattern to copy:** each precedent commit is scoped to one file-group (pyproject+lock in one
commit, CI/docs/release workflows in a second commit) — mirrors this phase's recommended
task sequencing (RESEARCH.md "Recommended Task Sequencing", steps 1-2 vs 3-5).

## File Classification

| File | Role | Data Flow | Edit Type | Sites |
|------|------|-----------|-----------|-------|
| `pyproject.toml` | config (build/packaging manifest) | batch (declarative constant replace) | modify | 7 |
| `tox.ini` | config (CI task-runner manifest) | batch | modify | 3 |
| `.github/workflows/ci.yml` | config (CI workflow) | batch | modify | 7 |
| `.github/workflows/docs.yml` | config (CI workflow) | batch | modify | 1 |
| `.github/workflows/release.yml` | config (CI workflow) | batch | modify | 2 |
| `.github/workflows/drift.yml` | config (CI workflow) | batch | modify | 1 |
| `uv.lock` | config (regenerated lockfile artifact) | batch (regenerated, not hand-edited) | regenerate | 1 (whole-file) |

No new files are created. No `role: controller/component/service/model` classes apply — every
site is a **version-string declaration** inside a config/manifest file.

## Pattern Assignments

### `pyproject.toml` (7 sites) — verified against current repo state (line numbers match RESEARCH.md)

**Analog:** `git show fce2ffb -- pyproject.toml` (same file, same site shapes, prior floor raise)

1. **`requires-python`** (line 10):
```toml
requires-python = ">=3.10"
```
→ `requires-python = ">=3.12"`

2. **Classifiers** (lines 20-24):
```toml
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
```
→ remove the `3.10` and `3.11` lines, keep `3`, `3.12`, `3.13`.

3. **Core dependencies** (lines 29-33):
```toml
dependencies = [
    "sphinx>=5.0,<9",
    "docutils>=0.18,<0.22",
    "typst>=0.14.1,<0.15",
]
```
→ `"sphinx>=9.1,<10"`, `"docutils>=0.21,<0.23"`; **leave `typst>=0.14.1,<0.15` untouched**
(Phase 7 scope fence — do not edit this line).

4. **`dev` extra `types-docutils`** (line 45, within lines 36-48 block):
```toml
    "types-docutils>=0.18",
```
→ `"types-docutils>=0.21"` (per RESEARCH.md A1 recommendation — matches new runtime docutils
floor; the `[dependency-groups].dev` entry at line 136 already reads
`"types-docutils>=0.22.2.20251006"` and is a second, already-current declaration of the same
constraint — do not need to touch line 136, only line 45's stale duplicate).

5. **`[tool.black] target-version`** (line 88):
```toml
target-version = ["py310", "py311", "py312", "py313"]
```
→ `target-version = ["py312", "py313"]`

6. **`[tool.ruff] target-version`** (line 103):
```toml
target-version = "py310"
```
→ `target-version = "py312"`

7. **`[tool.mypy] python_version`** (line 120):
```toml
python_version = "3.10"
```
→ `python_version = "3.12"`

**Explicitly do NOT touch this phase** (flag-only, RESEARCH.md footnote):
- Lines 111-112 `UP035`/`UP006` ruff-ignore comments ("Python 3.10+ support" rationale) —
  becomes stale phrasing but changing it is a `docs(04-03)`-style hygiene commit, not required.
- Line 53 `docs` extra `"tomli>=2.0; python_version < '3.11'"` — becomes permanently-false
  under the new 3.12 floor; harmless to leave, optional to drop.
- `CLAUDE.md` line 75 ("Python 3.10+ compatibility is required...") — stale after this phase,
  optional hygiene fix, not gated by any success criterion.

---

### `tox.ini` (3 sites) — verified against current repo state

**Analog:** `git show 2e285d4 -- tox.ini` (same file edited in the prior floor-raise)

8. **`env_list`** (line 2):
```ini
env_list = py310, py311, py312, py313, lint, type, cov, docs
```
→ `env_list = py312, py313, lint, type, cov, docs`

9. **`[testenv] deps` sphinx pin** (line 21, within lines 18-21 block):
```ini
deps =
    pytest>=8.4,<10
    pytest-cov>=4.0
    sphinx>=5.0,<9
```
→ `sphinx>=9.1,<10` (pytest/pytest-cov lines unchanged)

10. **`[testenv:type] deps`** (lines 40-42, within lines 38-42 block):
```ini
deps =
    mypy>=1.13,<3.0
    sphinx>=5.0,<9
    types-docutils>=0.18
    docutils>=0.18,<0.22
```
→ `sphinx>=9.1,<10`, `types-docutils>=0.21` (match site 4's chosen value exactly — this is the
split-brain hazard Pitfall 2 warns about), `docutils>=0.21,<0.23`

---

### `.github/workflows/ci.yml` (7 sites) — verified against current repo state (grep-confirmed)

**Analog:** `git show 2e285d4 -- .github/workflows/ci.yml`

11. **Matrix** (line 18):
```yaml
        python-version: ['3.10', '3.11', '3.12', '3.13']
```
→ `python-version: ['3.12', '3.13']`

12. **`include:` mapping** (lines 20-26):
```yaml
          - python-version: '3.10'
            tox-env: py310
          - python-version: '3.11'
            tox-env: py311
          - python-version: '3.12'
            ...
          - python-version: '3.13'
```
→ remove the `'3.10'`/`py310` and `'3.11'`/`py311` entries; keep `3.12`/`3.13` mappings intact.

13-17. **Five single-runner `uv python install 3.10` sites** (lines 68, 89, 110, 144, 176 —
in `lint`, `type-check`, `coverage`, `build`, `integration` jobs respectively):
```yaml
        run: uv python install 3.10
```
→ `run: uv python install 3.12` (all five, per CONTEXT.md discretion default: non-matrix jobs
move to the new floor 3.12, not 3.13).

Note: line 38's `uv python install ${{ matrix.python-version }}` is matrix-driven and does
**not** need a literal edit — it inherits from the (now-narrowed) matrix at site 11.

---

### `.github/workflows/docs.yml` (1 site) — verified against current repo state

18. **Line 24** (`actions/setup-python@v6` step):
```yaml
          python-version: "3.10"
```
→ `python-version: "3.12"`

---

### `.github/workflows/release.yml` (2 sites) — verified against current repo state

**Analog:** `git show 2e285d4 -- .github/workflows/release.yml`

19. **Line 33** (`validate` job):
```yaml
        run: uv python install 3.10
```
→ `run: uv python install 3.12`

20. **Line 86** (`build` job):
```yaml
        run: uv python install 3.10
```
→ `run: uv python install 3.12`

---

### `.github/workflows/drift.yml` (1 site) — verified against current repo state

21. **Line 26**:
```yaml
        run: uv python install 3.10
```
→ `run: uv python install 3.12`

---

### `uv.lock` (regenerated artifact, not hand-edited)

**Pattern:** `git show fce2ffb -- uv.lock` shows the prior floor-raise's lock regeneration
(commit message: "bump Python floor to 3.10-3.13 in pyproject.toml + regenerate uv.lock" —
both edits landed in the same commit, confirming the atomicity pattern this phase must repeat).

**Command** (per CONTEXT.md discretion, minimal-diff preferred):
```bash
uv lock --upgrade-package sphinx --upgrade-package docutils
uv sync --locked   # currency gate; if it fails, fall back to full `uv lock` re-resolve
```
The lockfile's own header `requires-python` (currently `">=3.10"`) auto-updates once
`pyproject.toml`'s value changes and `uv lock` runs — never hand-edit `uv.lock`.

## Shared Patterns

### Atomic single-commit landing (cross-cutting, applies to ALL 21 sites)
**Source:** RESEARCH.md "Common Pitfalls" Pitfall 1 + precedent commit `fce2ffb`
**Apply to:** every file above
Raising `sphinx`/`docutils` pins in `pyproject.toml` without simultaneously raising
`requires-python` produces an immediate, loud `uv lock` resolver failure (reproduced live in
RESEARCH.md). All edits across all 6 files plus the lockfile regeneration must land together
(one commit, or a final pre-push state with no partial-edit push in between) — this mirrors
how `fce2ffb` bundled the `pyproject.toml` edit + lockfile regen in one commit and `2e285d4`
bundled all CI/docs/release workflow edits in a second, immediately-following commit.

### Split-brain ceiling sync (types-docutils / docutils / sphinx duplication)
**Source:** RESEARCH.md Pitfall 2; sites 3, 4, 9, 10
**Apply to:** `pyproject.toml` sites 3 & 4, `tox.ini` site 10
The `docutils` ceiling and `types-docutils` floor exist as **duplicate declarations** across
`pyproject.toml` and `tox.ini`'s `[testenv:type]` block with no automated sync-check (unlike
the `@preview` package versions, which have `tests/test_preview_version_sync.py` — that test
is out of scope here per Phase 7 boundary). Edit all four occurrences to the same target
values in the same pass; verify with the grep audit below.

### Post-edit verification grep (from RESEARCH.md Pitfall 2 "How to avoid")
**Source:** RESEARCH.md, verbatim command
**Apply to:** verification step after all 6 files are edited
```bash
grep -rn "sphinx>=5.0,<9\|sphinx<9\|docutils>=0.18,<0.22\|docutils<0.22\|python.*3\.10\|python.*3\.11\|py310\|py311" \
  --include="*.toml" --include="*.ini" --include="*.yml" --include="*.yaml" .
```
Expect zero hits outside historical/planning docs (e.g. `.planning/milestones/v0.4.4-ROADMAP.md`)
after all 21 sites are edited.

### Done-ness smoke gate (registration + full non-PDF build)
**Source:** RESEARCH.md "Code Examples" block 2, live-tested this session against Sphinx 8.1.3
**Apply to:** verification after `uv sync --locked` succeeds, in place of full pytest suite
(Phase 8's gate)
```bash
uv run python -c "
import tempfile, os
from sphinx.application import Sphinx
srcdir = 'tests/roots/test-basic'
with tempfile.TemporaryDirectory() as tmp:
    for name in ('typst', 'typstpdf'):
        outdir = os.path.join(tmp, name)
        doctreedir = os.path.join(tmp, name + '-doctrees')
        app = Sphinx(srcdir, srcdir, outdir, doctreedir, name)
        assert app.builder.name == name, f'{name} builder failed to register'
        print(f'{name}: OK (registered, class={type(app.builder).__name__})')
"
uv run sphinx-build -b typst tests/roots/test-basic /tmp/typst-smoke-out
uv run python -c "import typsphinx; print(typsphinx.__version__)"
```
Do NOT use `-b typstpdf` or `tox -e docs-pdf` as a pass/fail gate — expected red until Phase 7
(`kai` fix), per D-03/Pitfall 3.

## No Analog Found

None — every declaration site has a direct precedent from the v0.4.4 Phase 3 floor-raise
(`fce2ffb`/`2e285d4`) touching the identical file and identical site shape, and every current
value was independently re-verified by direct `Read`/`grep` against the present repo state
during this pattern-mapping pass (matches RESEARCH.md's line numbers exactly).

## Metadata

**Analog search scope:** `pyproject.toml`, `tox.ini`, `.github/workflows/{ci,docs,release,drift}.yml`,
git history (`git log --all --oneline --grep`) for the v0.4.4 Phase 3 precedent commits.
**Files scanned:** 6 declaration files + 1 lockfile (regenerated) + 7 precedent commits inspected via `git log`.
**Pattern extraction date:** 2026-07-09
**Verification note:** All current-value excerpts above were re-read live from the repo in
this pass (not copied uncritically from RESEARCH.md), confirming RESEARCH.md's 21-site
checklist is accurate against the present `main` branch state.
