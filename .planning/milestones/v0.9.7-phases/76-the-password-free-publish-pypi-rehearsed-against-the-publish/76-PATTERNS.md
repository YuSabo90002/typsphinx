# Phase 76: The `password:`-Free `publish-pypi`, Rehearsed — Pattern Map

**Mapped:** 2026-09-27
**Files analyzed:** 4 (1 modified workflow, 1 modified module, 1 new test module, 1 new evidence doc)
**Analogs found:** 4 / 4

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|-----------------|---------------|
| `.github/workflows/release.yml` (2-line deletion) | config (CI/CD workflow) | request-response (external OIDC/PyPI call) | `.github/workflows/release.yml`'s own `publish-testpypi` job (same file, sibling step) | exact (same file, same shape, keep as reference for what NOT to touch) |
| `typsphinx/translator.py` (import + 2 f-string sites) | utility call-site (translator internals) | transform (string formatting for a diagnostic log) | `typsphinx/writer.py:511-515` (MSG-04's `quote_path()` call site) | exact — same helper, same call shape, only site count/plurality differs |
| `tests/test_translator_path_quoting_gate.py` (new) | test | request-response (caplog observable on a private method) | `tests/test_nested_toctree_paths.py` (construction) + `tests/test_writer_path_quoting_gate.py` (caplog/DEBUG assertion shape) | exact — construction from one analog, assertion shape from the other |
| `76-ATT-EVIDENCE.md` (new) | test (evidence/verification doc) | batch (RED→GREEN evidence record) | `.planning/milestones/v0.9.1-phases/60-.../60-PATH-QUOTING-EVIDENCE.md` and `60-03-EVIDENCE.md` | exact — same "single fixed-name evidence file, not `*-VERIFICATION.md`" convention |

## Pattern Assignments

### `.github/workflows/release.yml` (config, request-response) — ATT-01

**Analog:** the same file's own `publish-testpypi` job, which must stay byte-identical (do NOT copy its `password:` line into the edited job — it is the negative reference, showing what the *unedited* shape looks like so the diff stays a clean 2-line deletion).

**Current site, measured this session** (re-measure again before editing — lines drift):
```yaml
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```
Orchestrator re-measurement (2026-09-27, `grep -n`): `with:` at `:143`, `password: ${{ secrets.PYPI_API_TOKEN }}` at `:144` — CONTEXT.md/RESEARCH.md's `:143-144` is correct; the pattern mapper's earlier `:140-143` claim was a mis-read and is withdrawn. Re-measure with `grep -n "Publish to PyPI\|password: \${{ secrets.PYPI_API_TOKEN }}" .github/workflows/release.yml` immediately before editing; every document that cites a line number for this edit (ROADMAP, REQUIREMENTS, CONTEXT, RESEARCH) has been wrong at least once already.

**The edit:** delete exactly the `with:` line and the `password:` line, keeping `- name: Publish to PyPI` and `uses: pypa/gh-action-pypi-publish@release/v1`. Nothing is added in their place — no `attestations:`, no `skip-existing:`, no SHA pin (all explicitly out of scope).

**Sibling job that must stay untouched** (negative reference, confirms scope boundary):
```yaml
      - name: Publish to TestPyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.TEST_PYPI_API_TOKEN }}
          repository-url: https://test.pypi.org/legacy/
```

**Verification greps** (pre/post):
```bash
grep -c 'PYPI_API_TOKEN' .github/workflows/release.yml   # 2 -> 1 (remaining is TEST_PYPI_API_TOKEN)
grep -c 'attestations' .github/workflows/release.yml     # 0 -> 0
grep -c 'skip-existing' .github/workflows/release.yml    # 0 -> 0
uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))"  # YAML OK, both before and after
```

---

### `typsphinx/translator.py` (utility call-site, transform) — MSG-06

**Analog:** `typsphinx/writer.py:511-515` (MSG-04, Phase 60) — the identical `quote_path()` substitution pattern, already live.

**Import pattern to add** (new line; `translator.py` currently has zero `typsphinx`-internal imports):
```python
# typsphinx/writer.py:15 (sibling precedent, same import line shape)
from typsphinx.pathfmt import quote_path
```
Add this alongside `translator.py`'s existing import block (`:8-16`, currently `re`, `typing`, `docutils`, `sphinx.*` only).

**Analog core pattern** (`typsphinx/writer.py:511-515`, read this session):
```python
logger.debug(
    f"Rendering wrapper for docname {docname!r} at "
    f"wrapper_relative_dir={quote_path(wrapper_relative_dir)}, "
    f"include_path={quote_path(include_path)}, template_file={quote_path(template_file)}"
)
```

**Both target sites in `translator.py`** (byte-identical, at `:5119-5123` and `:5224-5228` — line numbers re-confirmed this session; f-string bodies sit at `:5121` and `:5226`):
```python
# BEFORE (both sites, identical text)
logger.debug(
    f"Cross-directory path calculation: up_count={up_count}, "
    f"up_path='{up_path}', down_path='{down_path}', "
    f"result: {relative_path}"
)

# AFTER
logger.debug(
    f"Cross-directory path calculation: up_count={up_count}, "
    f"up_path={quote_path(up_path)}, down_path={quote_path(down_path)}, "
    f"result: {relative_path}"
)
```

**Scope boundary (confirmed by grep this session):** these are the *only* two hardcoded-`'...'`-delimiter path fragments in either `_compute_relative_include_path()` or `_compute_relative_image_path()`. Every other `logger.debug()` call in both functions interpolates unquoted identifiers/paths — do not touch them.
```bash
grep -n "logger.debug\|f\"up_path" typsphinx/translator.py
# 5121 and 5226 are the only lines with the hardcoded 'up_path='/'down_path=' quoting
```

---

### `tests/test_translator_path_quoting_gate.py` (test, request-response) — MSG-06's gate

**Analog 1 (construction — direct instantiation, no Sphinx app):** `tests/test_nested_toctree_paths.py:1-51`

```python
from docutils import nodes
from docutils.parsers.rst import states
from docutils.utils import Reporter

from typsphinx.translator import TypstTranslator


@pytest.fixture
def mock_document():
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False
    return doc


@pytest.fixture
def mock_builder():
    class MockConfig:
        typst_use_mitex = True

    class MockDomains:
        pass

    class MockEnv:
        domains = MockDomains()

    class MockBuilder:
        name = "typst"
        current_docname = None
        config = MockConfig()
        env = MockEnv()

    return MockBuilder()
```
Call shape used elsewhere in that same file:
```python
translator = TypstTranslator(mock_document, mock_builder)
result = translator._compute_relative_include_path(
    target_docname="chapter2/doc2", current_docname="chapter1/doc1"
)
```
Do NOT use `SphinxTestApp`/`temp_sphinx_app` for this gate — neither `_compute_relative_include_path` nor `_compute_relative_image_path` touches `self` in its body, so the sibling gates' `temp_sphinx_app`-driven pattern (used for `builder.py`/`writer.py`/`template_registry.py`, which DO need a real app) is the wrong analog here despite being in the same `*_path_quoting_gate.py` family.

**Analog 2 (caplog/DEBUG assertion shape):** `tests/test_writer_path_quoting_gate.py:1-11,40-46,60-76` (module docstring + `caplog.at_level("DEBUG")` usage):
```python
"""MSG-04: `typsphinx/writer.py`'s wrapper-render debug log routes its
...path-valued interpolations... through `typsphinx.pathfmt.quote_path()`.

The site is a `logger.debug()` call, so the only observable is `caplog` at
DEBUG level (D-12) -- no existing test drives this log at all...
It asserts ONLY on strings `typsphinx/writer.py` itself emits -- never on
a string emitted by [a sibling module], which belong to the sibling ... plans.
"""

with caplog.at_level("DEBUG"):
    writer.render_wrapper(...)

debug_records = [r for r in caplog.records if r.levelname == "DEBUG"]
```
Adapt: filter to the one record by message prefix (`"Cross-directory path calculation:"`), assert exactly one was emitted, then assert on its exact text.

**Fixture values to drive the cross-directory + apostrophe branch** (computed this session by hand-tracing the actual function body):
```python
current_docname = "chapter1/doc1"
target_docname = "chapter2/o'brien"
# -> up_path = "../", down_path = "chapter2/o'brien"
# Pre-fix (RED) message:
#   "Cross-directory path calculation: up_count=1, up_path='../', down_path='chapter2/o'brien', result: ../chapter2/o'brien"
# Post-fix (GREEN) message (quote_path: no apostrophe -> '...'; apostrophe present, no " -> "..."):
#   "Cross-directory path calculation: up_count=1, up_path='../', down_path=\"chapter2/o'brien\", result: ../chapter2/o'brien"
```
**Do not** drive the RED assertion off the `up_path == ""` shape (`up_count == 0`): `quote_path("")` returns `''`, byte-identical to the pre-fix hardcoded output for that case — it stays green before and after the fix and proves nothing. The apostrophe must land in `down_path`.

**Module-naming convention** (sibling family, all git-tracked): `tests/test_writer_path_quoting_gate.py`, `tests/test_builder_path_quoting_gate.py`, `tests/test_template_registry_path_quoting_gate.py` — the new file follows `tests/test_translator_path_quoting_gate.py` naming, completing the family's fourth member. Do not modify the three siblings (SC #5 pins them byte-identical).

---

### `76-ATT-EVIDENCE.md` (evidence document) — ATT-01/ATT-02

**Analog:** `.planning/milestones/v0.9.1-phases/60-one-delimiter-aware-path-quoting-helper-routed-everywhere/60-PATH-QUOTING-EVIDENCE.md` (consolidated single evidence file, D-10 precedent for "one fixed-name file, not per-plan `*-VERIFICATION.md`") and `60-03-EVIDENCE.md` (RED→GREEN recording shape):

```
Command: `uv run pytest tests/test_writer_path_quoting_gate.py -q` (plan base SHA <sha>,
before `typsphinx/writer.py` was edited).
<pytest FAILED output, showing the AssertionError with the actual message vs. expected>
```
Followed by the green re-run after the fix landed. `76-ATT-EVIDENCE.md` should record MSG-06's RED (test run against phase-base SHA, before `translator.py` is edited) and GREEN (after) in this same shape, in addition to all of D-08's ATT-01/ATT-02 items (pre/post PyPI captures, dispatch command + ref + SHA, `gh run list` before/after diff, run id + job conclusions, and the two corrected evidence greps below).

**Corrected evidence greps (per D-08 AMENDED block — use these, not the original `'attestations input ignored'`):**
```bash
gh run view <run-id> --log | LC_ALL=C grep -c 'disabling Trusted Publishing'      # rehearsal: 0, control 35730551619: 1
gh run view <run-id> --log | LC_ALL=C grep -c 'the attestations input is ignored' # rehearsal: 0, control 35730551619: 1
```
These are the two greps confirmed to actually discriminate the control run in this session's research; do not use the original `'attestations input ignored'` (three-word form) as a discriminating control — it reads 0 on both rehearsal and control because that literal exists only in the GitHub Actions annotation's `title=` attribute, which `gh run view --log` never renders.

## Shared Patterns

### `quote_path()` leaf-module import
**Source:** `typsphinx/pathfmt.py` (module docstring, D-01/D-01a/D-03/D-04 contract) + three existing call sites (`typsphinx/builder.py:22`, `typsphinx/writer.py:15`, `typsphinx/template_registry.py:33`)
**Apply to:** `typsphinx/translator.py` (MSG-06's new fourth call site — same import line shape, no cycle risk since `pathfmt.py` has zero `typsphinx`-internal imports)

### `*_path_quoting_gate.py` test family conventions
**Source:** `tests/test_writer_path_quoting_gate.py`, `tests/test_builder_path_quoting_gate.py`, `tests/test_template_registry_path_quoting_gate.py`
**Apply to:** `tests/test_translator_path_quoting_gate.py` (new) — module docstring stating the MSG-ID, what observable is used (caplog DEBUG), and an explicit "asserts ONLY on strings this module itself emits" scoping statement.

### Single fixed-name phase evidence document (not `*-VERIFICATION.md`)
**Source:** `.planning/milestones/v0.9.1-phases/60-.../60-PATH-QUOTING-EVIDENCE.md`
**Apply to:** `76-ATT-EVIDENCE.md` — `gsd-verifier` reserves and overwrites `76-VERIFICATION.md` wholesale, so evidence that must survive belongs in a differently-named file.

## No Analog Found

None — all four files have a strong, git-tracked analog in the codebase.

## Metadata

**Analog search scope:** `.github/workflows/`, `typsphinx/`, `tests/`, `.planning/milestones/v0.9.1-phases/60-*/`
**Files scanned:** `.github/workflows/release.yml`, `typsphinx/translator.py`, `typsphinx/writer.py`, `typsphinx/pathfmt.py`, `tests/test_writer_path_quoting_gate.py`, `tests/test_nested_toctree_paths.py`, `tests/test_builder_path_quoting_gate.py` (name only), `tests/test_template_registry_path_quoting_gate.py` (name only), `.planning/milestones/v0.9.1-phases/60-.../60-PATH-QUOTING-EVIDENCE.md`, `.../60-03-EVIDENCE.md`
**Pattern extraction date:** 2026-09-27
**Tracked-source gate:** confirmed via `git ls-files` for all six analog source paths and the two evidence analog paths — all tracked, none are gitignored mirrors.
