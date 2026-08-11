# Phase 45: Documentation Currency + Carried Hygiene - Pattern Map

**Mapped:** 2026-08-09
**Files analyzed:** 8 (+ `uv.lock`, regenerated not hand-edited)
**Analogs found:** 8 / 8 (2 are "no direct analog exists — use structural placeholder + reference pattern")

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `docs/source/changelog.rst` | docs-page (Sphinx source, myst include) | transform (Markdown→doctree→Typst/HTML) | No existing `.. include::`/myst analog in this repo. Structural analog: `docs/source/conf.py`'s `extensions` list (for registering `myst_parser`) + `docs/source/changelog.rst` itself (existing prose framing to keep/trim) | no-direct-analog |
| `README.md` (Quick Start 63-126, Config Options 203) | docs-page (Markdown, hand-authored) | transform (prose) | Same file, adjacent untouched sections (self-analog) — no cross-file pattern needed, this is prose editing | self-analog |
| `docs/source/quickstart.rst:60-67,71-90` | docs-page (rST) | transform (prose) | Same file / `docs/source/user_guide/configuration.rst` (sibling rST page with the same Sphinx-doc directive conventions) | role-match |
| `docs/source/user_guide/configuration.rst:23-33` | docs-page (rST) | transform (prose) | `typsphinx/builder.py:28-47` (`_default_typst_documents`, the source of truth the prose must describe accurately) | role-match (source-of-truth, not a doc-analog) |
| `CHANGELOG.md` (D-03/D-04/D-05) | data file (Keep-a-Changelog Markdown) | batch (structured text edit) | The file's own neighboring, well-formed sections (e.g. `## [0.4.3]` at line 404 as the shape template for the reconstructed `## [0.4.4]`) | self-analog |
| `pyproject.toml` (`docs` extra) | config | CRUD (dependency-list edit) | `pyproject.toml:49-53` — the existing `docs` extra itself (verbatim, quoted below) | exact |
| `typsphinx/template_engine.py:131-150` (`derive_typst_lang`) | utility (pure function, single-site refactor) | transform (validation + logging) | The function itself — no cross-file analog needed; refactor shape confirmed compatible with `tests/test_template_engine.py::TestDeriveTypstLang` and `tests/test_typst_lang_gate.py::TestMalformedLanguage` | self-refactor |
| `.planning/PROJECT.md` (QUA-03, verification only) | planning-record (verification script target) | batch (scan, no edit expected) | `tests/test_no_stale_github_io_links.py` — established shape for a repo-hygiene check that parses raw file text, no network, avoids self-matching | role-match |
| (test) DOC-11 build-check | test (real-`sphinx-build` gate) | request-response (subprocess) | `tests/test_default_typst_documents_gate.py` | exact |
| (test) DOC-12 changelog-content-coverage check | test (build-check / content regression) | batch (grep rendered output) | `tests/test_no_stale_github_io_links.py` (content-regression shape) + `tests/test_changelog_extraction.py` (subprocess-of-real-script shape) | role-match |

## Pattern Assignments

### `docs/source/changelog.rst` (docs-page, transform)

**No existing include/myst analog in this repo** — this is the first use of `myst-parser` and the
first cross-file `.. include::` of a non-`.rst` source. Two supporting analogs instead:

**1. `docs/source/conf.py:35-42`** — the `extensions` list every new Sphinx extension is registered
in (verbatim, read this session):
```python
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "typsphinx",
]
```
Add `"myst_parser"` to this list (Pattern 1 in RESEARCH.md — defensive registration; the FAQ examples
all show it present even for `include::`-only use).

**2. Current `docs/source/changelog.rst`** (existing prose, read this session) shows the framing
sections to be corrected/deleted per D-06 — e.g. the stale `Migration Guides` section:
```rst
Migration Guides
----------------

Migrating from 0.2.x to 0.3.x
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No breaking changes. Documentation site is a new feature.
```
This is the section shape (H2 `----`, H3 `~~~~`) to extend with 0.6.x/0.7.0 entries per D-06, and
`Development Status` (not shown here but immediately above this block in the file) is the section to
delete outright.

**Include directive to add** (from RESEARCH.md Pattern 1, quoted verbatim from official myst-parser
docs, fetched 2026-08-09):
```rst
.. include:: ../../CHANGELOG.md
   :parser: myst_parser.sphinx_
```
Do the `CHANGELOG.md` edits (D-03/D-04/D-05) **before** finalizing any `:start-line:`/`:start-after:`
offset (Pitfall 1) — measure against the final file.

---

### `pyproject.toml` `docs` extra (config, CRUD)

**Analog:** the extra itself, `pyproject.toml:49-53` (verbatim, read this session):
```toml
docs = [
    "furo>=2024.0",
    "sphinx-autodoc-typehints>=1.0",
    "sphinx-intl>=2.0",
]
```
**Version-pin house style:** lower-bound-only (`>=X.Y`), no upper cap, matching `sphinx-intl>=2.0`
and `furo>=2024.0` — so the new line should read `"myst-parser>=5.0",` (not `>=5.0,<6` or similar; no
existing `docs`-extra entry carries an upper bound). After the edit, regenerate the lock:
```bash
uv lock
```
(per RESEARCH.md Standard Stack — commit the updated `uv.lock` alongside, exactly as the existing
three `docs`-extra packages already are).

---

### `typsphinx/template_engine.py:131-150` (`derive_typst_lang`, utility, transform)

**Before (verbatim, read this session, two byte-identical rejection-branch warnings):**
```python
    if not isinstance(sphinx_language, str) or not sphinx_language:
        logger.warning(
            f"typsphinx: could not derive a Typst 'lang' from Sphinx "
            f"'language' = {sphinx_language!r} -- omitting 'lang' (falling "
            f"back to the template's own default)."
        )
        return None

    head = re.split(r"[_\-@]", sphinx_language, maxsplit=1)[0].lower()

    if re.fullmatch(r"[a-z]{2,3}", head):
        return head

    logger.warning(
        f"typsphinx: could not derive a Typst 'lang' from Sphinx "
        f"'language' = {sphinx_language!r} -- omitting 'lang' (falling "
        f"back to the template's own default)."
    )
    return None
```

**Illustrative after** (RESEARCH.md Pattern 3 — planner/executor picks exact shape; constraint is one
call site + byte-identical wording):
```python
def derive_typst_lang(sphinx_language: str | None) -> str | None:
    if isinstance(sphinx_language, str) and sphinx_language:
        head = re.split(r"[_\-@]", sphinx_language, maxsplit=1)[0].lower()
        if re.fullmatch(r"[a-z]{2,3}", head):
            return head
    logger.warning(
        f"typsphinx: could not derive a Typst 'lang' from Sphinx "
        f"'language' = {sphinx_language!r} -- omitting 'lang' (falling "
        f"back to the template's own default)."
    )
    return None
```
**Identity proof (no new test needed):** run both of the following before/after the refactor —
identical PASS on both sides *is* the identity proof, because both assert on warning presence/content:
```bash
pytest tests/test_template_engine.py::TestDeriveTypstLang -v
pytest tests/test_typst_lang_gate.py::TestMalformedLanguage -v
```
`tests/test_template_engine.py`'s pinning assertion (paraphrased from RESEARCH.md, not re-quoted
verbatim here — see that file's line ~1202-1216): `any(repr(malformed) in record.message for record
in caplog.records)` — a presence check, not a call-count check, so a single-tail restructure is
compatible.

**Structural "exactly one site" check** (Wave 0 gap, optional belt-and-suspenders):
```bash
grep -c "logger.warning" typsphinx/template_engine.py   # scope to derive_typst_lang()'s line range
```

---

### `.planning/PROJECT.md` (QUA-03, verification only — no edit expected)

**Analog:** `tests/test_no_stale_github_io_links.py:1-38` (read this session) — the established shape
for a repo-hygiene check: parses raw file text, no network, splits a literal to avoid self-matching:
```python
import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"

# ... literal split into two fragments to avoid self-matching, e.g.:
_RETIRED_HOST_PREFIX = "yusabo90002.github"
_RETIRED_HOST_SUFFIX = "io"
_RETIRED_HOST = f"{_RETIRED_HOST_PREFIX}.{_RETIRED_HOST_SUFFIX}"
```
**QUA-03's own verification script** (D-09-compliant, run this session — record output as evidence,
do not add to the pytest suite per D-07):
```python
import re
lines = open(".planning/PROJECT.md", encoding="utf-8").read().split("\n")
stack = []
in_fence = False
for idx, line in enumerate(lines, start=1):
    if line.strip().startswith("```") or line.strip().startswith("~~~"):
        in_fence = not in_fence
        continue
    if in_fence:
        continue
    stripped = re.sub(r'`{1,2}[^`\n]*?`{1,2}', '', line)
    for m in re.finditer(r'<!--|-->', stripped):
        if m.group(0) == '<!--':
            stack.append(idx)
        elif stack:
            stack.pop()
# Result this session: len(stack) == 0 (34 openers, 34 closers, all paired)
```
Result already confirmed: zero unterminated openers; D-08 bisect names commit `43a2a78` as the
deliberate closer. No file edit — this task is "run script, record result" only.

---

### DOC-11 build-check test (real-`sphinx-build` gate)

**Analog:** `tests/test_default_typst_documents_gate.py` (read this session) — exact match, same
mechanism the new check should reuse or mirror:
```python
FIXTURES_DIR = Path(__file__).parent / "fixtures"
DEFAULT_GATE_FIXTURE_DIR = FIXTURES_DIR / "default_typst_documents_gate"

def _run_sphinx_build(source_dir, build_dir, builder):
    """Invoked as sys.executable -m sphinx (never `uv run sphinx-build`,
    never a resolved sphinx-build binary) so the exact interpreter/venv
    running this test is reused, sidestepping the NixOS-sandbox PATH-
    shadowing hazard. Every gate module in this suite carries its own copy
    of this helper rather than importing a sibling module's."""
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", builder, str(source_dir), str(build_dir)],
        capture_output=True, text=True,
    )

@pytest.mark.skipif(not TYPST_AVAILABLE, reason="typst-py is required for the default-derivation gate")
class TestDefaultTypstDocumentsDerivationGate:
    def test_unset_typst_documents_produces_pdf(self, tmp_path):
        ...
```
RESEARCH.md's Phase Requirement → Test Map recommends either reusing `DEFAULT_GATE_FIXTURE_DIR`
directly for DOC-11's check, or adding a doc-mirroring fixture whose `project` value matches the
README/quickstart's published example (`"My Project"` / stem `myproject`), then asserting the PDF
filename equals `make_filename_from_project(project) + ".pdf"`, not `index.pdf`.

---

### DOC-12 changelog-content-coverage check (Wave 0 gap — net-new)

**Analog 1 (content-regression shape):** `tests/test_no_stale_github_io_links.py` — parses raw
rendered/source text, asserts presence/absence, no network.

**Analog 2 (subprocess-of-real-script shape):** `tests/test_changelog_extraction.py` +
`scripts/extract_changelog_section.py:59,87-116` (read this session) — the positional extractor
pattern the new check must not disturb:
```python
_SECTION_HEADER_RE = re.compile(r"^## \[(?P<version>[^\]]+)\]")

def extract_section(changelog_text: str, version: str) -> str:
    lines = changelog_text.splitlines()
    start_index: int | None = None
    for index, line in enumerate(lines):
        match = _SECTION_HEADER_RE.match(line)
        if match and match.group("version") == version:
            start_index = index + 1
            break
    ...
```
The new DOC-12 check should: build both `tox -e docs-html` and `tox -e docs-pdf` (or invoke
`sphinx-build` directly per the gate-test pattern above), then grep the rendered HTML / extracted PDF
text (`pypdf`) for each of the 12 previously-missing version strings (`0.4.4`, `0.4.1`…`0.7.0`) and
assert zero `WARNING:` lines mentioning `changelog` (delta against a pre-phase baseline, per Pitfall
2 — neither `tox -e docs-html` nor `tox -e docs-pdf` passes `-W`, verified verbatim below).

---

## Shared Patterns

### `tox.ini` docs envs (verbatim, read this session — no `-W` on either)
```ini
[testenv:docs-html]
description = Build HTML documentation
runner = uv-venv-lock-runner
extras = docs
changedir = docs
commands =
    sphinx-build -b html source _build/html

[testenv:docs-pdf]
description = Build PDF documentation with typstpdf
runner = uv-venv-lock-runner
extras = docs
changedir = docs
commands =
    sphinx-build -b typstpdf source _build/pdf
```
**Apply to:** DOC-12's "build clean" verification — since neither env passes `-W`, exit code 0 does
not mean zero warnings; capture stdout/stderr and grep for `WARNING:` lines instead (Pitfall 2).

### Worktree-isolated execution (from CLAUDE.md)
**Apply to:** every executor in this phase.
```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
uv run pytest   # run ALL subsequent commands via `uv run`
```
Note: the `docs-html`/`docs-pdf` tox envs use `extras = docs` (tox-uv managed), which is separate
from `uv sync --extra dev` — after editing `pyproject.toml`'s `docs` extra, `uv lock` must be run so
tox-uv's `uv-venv-lock-runner` picks up `myst-parser` when it next provisions the `docs` extras env.

### `@preview` version-sync hazard (from CLAUDE.md)
**Not directly touched by this phase** (`codly`, `codly-languages`, `mitex`, `gentle-clues` are
unrelated to `myst-parser`), but flagged because `writer.py`, `template_engine.py`, and
`templates/base.typ` are the three files that hazard applies to — none of them are edited by DOC-12's
myst-parser addition, only `typsphinx/template_engine.py:131-150` is touched, and that edit is
unrelated (QUA-02's logging refactor, not a package-import line).

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `docs/source/changelog.rst`'s `.. include::` directive itself | docs-page | transform | This is the first myst-parser / cross-format include in the repo — no prior `.. include::` or Markdown-parsed directive exists under `docs/source/`. Use RESEARCH.md's Pattern 1 (quoted verbatim from official myst-parser docs) as the authoritative source instead of a codebase analog. |
| DOC-12 warning-delta capture harness | test | batch | No existing test captures a before/after warning-count delta across two `sphinx-build` invocations; RESEARCH.md's Wave 0 Gaps section confirms this is net-new — build it following the subprocess-capture style of `tests/test_default_typst_documents_gate.py`'s `_run_sphinx_build` helper (capture_output=True, text=True) rather than any grep-only precedent. |

## Metadata

**Analog search scope:** `typsphinx/`, `docs/source/`, `tests/`, `scripts/`, `pyproject.toml`,
`tox.ini`, `.planning/PROJECT.md`, `CHANGELOG.md`, `README.md` — all read verbatim this session per
RESEARCH.md's Sources list; no additional Glob/Grep sweep was needed since RESEARCH.md already names
exact files and line numbers for every touched surface.
**Files scanned:** 14 read directly this session (`tests/test_default_typst_documents_gate.py`,
`tests/test_no_stale_github_io_links.py`, `pyproject.toml`, `tox.ini`,
`scripts/extract_changelog_section.py`, `docs/source/conf.py`, `docs/source/changelog.rst`,
`docs/source/quickstart.rst`, `docs/source/user_guide/configuration.rst`, `README.md`,
`typsphinx/template_engine.py`) plus RESEARCH.md/CONTEXT.md as primary sources for line numbers
already measured.
**Pattern extraction date:** 2026-08-09
</content>
