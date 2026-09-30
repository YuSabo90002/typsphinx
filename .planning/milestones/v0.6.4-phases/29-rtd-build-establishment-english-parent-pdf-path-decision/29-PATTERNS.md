# Phase 29: RTD Build Establishment (English Parent) + PDF Path Decision - Pattern Map

**Mapped:** 2026-07-25
**Files analyzed:** 3 (1 new build manifest, 1 modified config seam, 1 new test file)
**Analogs found:** 3 / 3 (one is style-only, explicitly not a code-shape analog)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `.readthedocs.yaml` | config (build manifest) | batch (CI/build) | `.github/workflows/docs.yml` (style only — different engine, do not copy invocation shape) | partial — style-only |
| `docs/source/conf.py` (language seam, ~2 lines at line 51) | config | transform (env-var precedence chain) | `docs/source/conf.py` itself, lines 21-30 (pyproject-version read) and line 51 (existing seam) | exact (self-analog; no separate helper-function precedent exists) |
| `tests/test_readthedocs_config.py` | test | transform / file-I/O (parse+assert) | `tests/test_readme_version_sync.py` (best) + `tests/test_preview_version_sync.py` (secondary) | exact |

## Pattern Assignments

### `.readthedocs.yaml` (config, batch)

**Analog:** `.github/workflows/docs.yml` (style reference only) and `tox.ini:53-84` (§`docs-html`/`docs-pdf`, content reference only for *what* commands do, not *how* to invoke them)

**IMPORTANT — explicit non-pattern:** RTD's `build.jobs.build.pdf` runs directly inside RTD's own
provisioned build container (`build.tools.python` + `python.install`). It does **not** go through this
repo's `tox` at all. `docs.yml:32` (`uv run tox -e docs-pdf`) and `tox.ini:61-67`
(`[testenv:docs-pdf]` → `sphinx-build -b typstpdf source _build/pdf`) show *what* the PDF build
logically does (an `sphinx-build -b typstpdf` invocation against `docs/source`), but copying the
`tox -e docs-*` wrapper shape into `.readthedocs.yaml`'s `build.jobs` would be wrong — RTD's
`python.install` step already provisions the equivalent environment; nesting tox creates a redundant
second venv with no working `uv sync --locked` wiring in RTD's sandbox. RESEARCH.md's Common Pitfalls
and CLAUDE.md both call this out explicitly. Copy only:
- the `source docs/source` (not `docs/` + `changedir`) path convention — RTD's `sphinx.configuration`
  key takes the full path from repo root, unlike tox's `changedir = docs` + relative `source`.
- the extras name (`docs`) from `docs.yml:27` (`uv sync --extra dev --extra docs --locked`) →
  `.readthedocs.yaml`'s `python.install: extras: [docs]` uses the same optional-dependency group name
  (`pyproject.toml:48-52`).
- `.github/workflows/ci.yml`'s YAML indentation/comment style (2-space, sparse comments except where a
  non-obvious constraint needs explaining — mirrors `tox.ini:4-10`'s comment density model for
  explaining *why*, not *what*) as the house style baseline for the new file's own comments.

**No copy of:** job/step keys (`jobs:`, `runs-on:`, `uses:`) — those are GitHub Actions syntax, not RTD
config-file-v2 syntax. `.readthedocs.yaml`'s schema (`version: 2`, `build:`, `sphinx:`, `python:`,
`formats:`) is unrelated to both files' key vocabulary; only indentation/comment conventions transfer.

**Concrete content is already fully specified** in RESEARCH.md § "Code Examples" → "Recommended
`.readthedocs.yaml`" and § "Pattern 1: Two-Commit Sequencing (D-06)" — both commits' exact YAML are
given there and should be used verbatim (with D-04's temp-dir-then-copy and D-10's `apt_packages`
already folded in for Commit 2). This PATTERNS.md does not re-derive that content; it only confirms the
house-style conventions to apply to it.

---

### `docs/source/conf.py` (config, transform — language seam)

**Analog:** the file's own existing conventions (no separate helper-function file exists in this
codebase to imitate).

**Existing seam** (`docs/source/conf.py:47-51`):
```python
# -- Internationalization (i18n) configuration -------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-locale_dirs

# Language can be set via SPHINX_LANGUAGE environment variable
language = os.getenv("SPHINX_LANGUAGE", "en")
```

**Comment-style convention to preserve:** a one-line `#` comment immediately above the assignment,
stating which env var controls the value — not a docstring, not a block comment. The new seam should
read:
```python
# Language can be set via READTHEDOCS_LANGUAGE (RTD's per-project Language
# setting) or SPHINX_LANGUAGE (existing local/CI override); defaults to "en".
language = os.getenv("READTHEDOCS_LANGUAGE", os.getenv("SPHINX_LANGUAGE", "en"))
```
This matches RESEARCH.md's Code Examples § "`conf.py:51` seam" verbatim.

**Every other config value in this file is a top-level inline assignment** (`project`, `copyright`,
`author`, `release` at lines 27-30; `typst_documents` at line 93-95) — there is **no** existing
helper-function precedent anywhere in `conf.py` (no `def` at module scope other than none found). This
confirms RESEARCH.md's Wave 0 Gap note: there is nothing in this file's own style to imitate for "factor
the seam into a tiny testable expression" — that recommendation, if taken, introduces a *new* pattern
(a small `_resolve_language()` helper or similar) rather than following an existing one. Planning should
treat this as a deliberate deviation from the surrounding inline-assignment style, justified purely by
testability (see next section), not as "matching an existing pattern."

**`conf.py` is not importable via plain `import` in the pytest path** — confirmed no test file anywhere
under `tests/` does `import conf` or `from docs.source import conf`. The two existing consumption
mechanisms in this suite are (a) `sphinx.testing.fixtures`' `SphinxTestApp`, which builds a full app
against a *different*, test-fixture `conf.py` under `tests/roots/` (see `conftest.py`'s
`temp_sphinx_app` fixture, which **writes its own minimal `conf.py`** rather than reading the real one),
and (b) direct raw-text parsing via regex/tomllib against the file's *source text*, exactly as
`test_readme_version_sync.py` and `test_preview_version_sync.py` do for their respective target files.
Neither mechanism gives a cheap way to assert an `os.getenv` chain's *runtime* precedence behavior
against the real `conf.py`.

---

### `tests/test_readthedocs_config.py` (test, transform/file-I/O)

**Primary analog:** `tests/test_readme_version_sync.py` (full file read above — 68 lines, plain-function
style, no test class, no Sphinx fixtures)

**Secondary analog:** `tests/test_preview_version_sync.py` (raw-text-regex-parsing idiom for a
non-Python target file; same no-class, no-fixture style)

**Class-vs-function convention:** These two closest analogs — both config/file-shape assertion tests
disconnected from doctree rendering — use **plain top-level `def test_*()` functions, no test class**.
This differs from `tests/test_translator.py`'s per-CLAUDE.md class-based convention, which is used for
node-visitor behavioral tests, not file-shape tests. **`test_readthedocs_config.py` should follow the
plain-function convention** (matching `test_readme_version_sync.py`/`test_preview_version_sync.py`),
not the class-based one — this is the config-oriented sub-style, confirmed by direct inspection.

**Module docstring pattern** (`test_readme_version_sync.py:1-13`):
```python
"""
Test guarding the README/pyproject.toml version-sync hazard (D-13).

README.md's Status line (...) has drifted stale relative to
pyproject.toml's `version` field across two prior releases -- ... This
module asserts the two stay in lockstep, mirroring the existing
`test_preview_version_sync.py` pattern: parse each file's raw text/
structured data directly (never via `importlib.metadata`), and compare
the two parsed values against each other rather than against a hardcoded
expected version string.
"""
```
Copy this shape: a module docstring naming the CONTEXT.md decision ID it guards (here, likely D-06/RTD-01
for the YAML-shape test, RTD-01/the seam decision for the precedence test), explaining *why* the test
exists (what silently drifted or could silently drift), and stating the parsing approach up front.

**Module-level path constants** (`test_readme_version_sync.py:16-19`):
```python
REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
```
Copy this exact idiom for `READTHEDOCS_YAML_PATH = REPO_ROOT / ".readthedocs.yaml"` and
`CONF_PY_PATH = REPO_ROOT / "docs" / "source" / "conf.py"`.

**Extraction-helper + assertion-in-test-body split** (`test_readme_version_sync.py:33-58`): a private
`_extract_*()` helper does the parsing and raises an assertive `assert match, "..."` if the expected
shape isn't found (guards against a vacuous pass), and the `test_*()` function calls the helper(s) and
does the final comparison assertion with a descriptive f-string message. Apply this same split to
`test_readthedocs_yaml_shape`: a `_load_readthedocs_yaml()` helper (via `yaml.safe_load`) plus a test
function asserting the required nested keys exist (`version`, `build.os`, `build.tools.python`,
`sphinx.configuration`, `python.install`) with descriptive failure messages, e.g.
`assert "os" in data["build"], ".readthedocs.yaml build: block is missing required key 'os'"`.

**PyYAML availability — confirmed this session:**
- `import yaml` **fails** under a bare `python3` invocation in this environment (`ModuleNotFoundError`).
- `import yaml` **succeeds** under `uv run python3 -c "import yaml; print(yaml.__version__)"` →
  `6.0.3`. PyYAML is present as a transitive dependency (via `sphinx`'s own dependency chain, per
  RESEARCH.md), not a directly-declared one anywhere in `pyproject.toml` — grep of
  `pyproject.toml`/`tests/`/`typsphinx/` found zero direct `import yaml`/`pyyaml` references anywhere
  in this codebase today.
- **Consequence for the plan:** `import yaml` is safe to use in the new test file **only** because this
  suite is always run via `uv run pytest` (worktree-isolated execution, per CLAUDE.md's standing
  execution mode) — a bare-`python3` invocation would fail. This is consistent with the rest of the
  suite's environment assumptions (nothing here is runnable outside `uv run`). Do not add `PyYAML` as a
  new explicit `dev`/`docs` extra dependency — it is already transitively guaranteed by `sphinx>=9.1,<10`
  being a hard dependency (`pyproject.toml:29`), and adding an explicit pin would be an unnecessary new
  direct-dependency edit this phase doesn't need. If the plan prefers zero reliance on an undeclared
  transitive package, the fallback is `test_preview_version_sync.py`'s manual-regex-parsing idiom
  instead of `yaml.safe_load` — but given the confirmed availability under `uv run`, `yaml.safe_load` is
  the cheaper, more robust choice for asserting nested-key structure (`build.os`, `build.tools.python`,
  etc.) than a regex would be.

**`monkeypatch` idiom — none exists in this suite today.** Grep of `tests/*.py` for `monkeypatch` found
zero matches anywhere in the codebase. `test_language_seam_precedence` will be this suite's **first**
use of `monkeypatch.setenv`/`monkeypatch.delenv`. There is no existing idiom to copy for the mechanics
of env-var manipulation itself; use pytest's standard `monkeypatch` fixture directly
(`monkeypatch.setenv("READTHEDOCS_LANGUAGE", "ja")`, `monkeypatch.delenv("SPHINX_LANGUAGE", raising=False)`),
following this file's own module-docstring/helper-split conventions for everything else (docstring
explaining the precedence rule under test, a small helper if the seam is factored per RESEARCH.md's
recommendation, and a table-style or parametrized set of assertions covering: both unset → `"en"`;
only `SPHINX_LANGUAGE` set → that value; only `READTHEDOCS_LANGUAGE` set → that value; both set →
`READTHEDOCS_LANGUAGE` wins).

**How to test the seam without a full Sphinx app fixture:** Per the `conf.py`-not-importable finding
above, the cheapest correct approach is **not** `conftest.py`'s `temp_sphinx_app` (that fixture writes
its own separate, minimal `conf.py` with none of the language seam in it — standing up a full
`SphinxTestApp` just to read one `os.getenv` chain would be paying for machinery this test doesn't need
and wouldn't even exercise the real file). Two options, in order of cost:
1. **(Recommended, matches RESEARCH.md's Wave 0 Gap note)** Factor the one-line seam into a tiny
   testable expression — e.g. a module-level function in `conf.py` itself,
   `def _resolve_language(): return os.getenv("READTHEDOCS_LANGUAGE", os.getenv("SPHINX_LANGUAGE", "en"))`
   — then import *only that function* from `conf.py` via `importlib.util.spec_from_file_location` (since
   `docs/source/conf.py` is not on `sys.path` as an importable package) or via a `sys.path.insert` +
   `import conf` scoped to the test using `CONF_PY_PATH`'s parent directory. This is a **new** pattern
   for this codebase (no precedent found) — flag it in the plan as such rather than presenting it as an
   existing convention.
2. **Fallback (no `conf.py` factoring):** parse `conf.py`'s raw text with a regex for the `language = ...`
   line (mirroring `test_preview_version_sync.py`'s `_PREVIEW_IMPORT_RE` raw-text-regex idiom) purely to
   assert the *literal source line* contains the right `os.getenv(...)` nesting — this proves the edit
   landed correctly but does **not** exercise actual runtime precedence behavior the way `monkeypatch` +
   a live call would. RESEARCH.md's own Wave 0 Gap text prefers option 1 ("Recommend factoring the
   one-line seam into a tiny testable expression... keep this test cheap") — this PATTERNS.md confirms
   there is no cheaper existing-precedent alternative, since neither of this suite's two current `conf.py`
   consumption mechanisms (full `SphinxTestApp`, or raw-text regex against an unrelated file) gives cheap
   *behavioral* coverage of an `os.getenv` chain.

**`conftest.py` — confirmed no change needed.** Read in full (`tests/conftest.py`, 80+ lines): the two
existing fixtures (`rootdir`, `sample_doctree`, `temp_sphinx_app`) are unrelated to `.readthedocs.yaml`
or the language seam — `temp_sphinx_app` writes its own separate throwaway `conf.py` with no `language`
seam of its own. RESEARCH.md's Wave 0 Gap note ("No `conftest.py` changes needed... this phase adds no
new fixture requirements beyond what `tests/roots/` already provides") is confirmed correct by this
direct read.

## Shared Patterns

### File-shape/version-sync test style
**Source:** `tests/test_readme_version_sync.py`, `tests/test_preview_version_sync.py`
**Apply to:** `tests/test_readthedocs_config.py` in full — module docstring naming the guarded hazard,
`REPO_ROOT`-relative path constants, `_extract_*`/`_load_*` private helper + assertive `assert ..., "..."`
guard-against-vacuous-pass idiom, plain top-level functions (no test class), descriptive f-string failure
messages on the final comparison assertion.

### RTD-vs-tox non-wrapping
**Source:** `tox.ini:53-84`, `.github/workflows/docs.yml:31-33`, CLAUDE.md's own explicit line
**Apply to:** `.readthedocs.yaml`'s `build.jobs.build.pdf` block — never invoke `tox -e docs-*` from
inside it; call `sphinx-build` directly, exactly as RESEARCH.md's Pattern 1 Commit 2 example already
does.

### Env-var-optional-fallback-chain style
**Source:** `docs/source/conf.py:51` (existing single-layer form)
**Apply to:** the new two-layer form at the same line — preserve the one-line explanatory `#` comment
directly above the assignment; do not introduce a block comment or docstring for this one-line change.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `.readthedocs.yaml` | config | batch | No prior RTD (or any non-GitHub-Actions, non-tox) build manifest exists anywhere in this repo — its *content* is fully specified by RESEARCH.md's Code Examples instead, and only house-style conventions (indentation, comment density) are borrowed from `.github/workflows/*.yml`/`tox.ini`. |
| `test_language_seam_precedence`'s `monkeypatch` mechanics | test | event-driven (env-var) | Zero existing use of pytest's `monkeypatch` fixture anywhere in this suite (confirmed by repo-wide grep) — this test introduces the idiom fresh, following pytest's standard API rather than an in-repo precedent. |

## Metadata

**Analog search scope:** `tests/` (68 files listed via `ls`; read `conftest.py` in full,
`test_readme_version_sync.py` in full, `test_preview_version_sync.py` head, grepped all for
`monkeypatch`/`import yaml`/`os.environ`), `docs/source/conf.py` (first 100 lines, full config surface
for this phase), `tox.ini` (full file), `.github/workflows/docs.yml` (full file), `pyproject.toml`
(first 60 lines, dependency declarations).
**Files scanned:** ~8 read in full or targeted range; ~70 listed/grepped.
**Pattern extraction date:** 2026-07-25
