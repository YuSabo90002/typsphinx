# Phase 8: API & Test Compatibility (Sphinx 9 / docutils 0.22) - Pattern Map

**Mapped:** 2026-07-11
**Files analyzed:** 6 (1 source, 4 test, 1 config); translator.py optional hardening not counted as required
**Analogs found:** 6 / 6 (all sites have an in-repo or in-stdlib-doc analog; this is a pure modernization phase — every "analog" is either an existing modern call already in the tree, or the library's own documented replacement API)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|-----------------|----------------|
| `typsphinx/template_engine.py` (line 239) | service / doctree-transform | transform (traversal) | `typsphinx/builder.py` line 151 (`doctree.findall(image)`) | exact — same repo, same `findall()` call shape |
| `tests/test_translator.py` (lines 1606-1607, 1647; 1698-1699, 1725; 1819-1820, 1845) | test | request-response (parse-and-assert) | docutils' own documented replacement `frontend.get_default_settings()` (no in-repo analog exists yet — this introduces the first usage) | role-match (API substitution, not a different pattern family) |
| `tests/test_builder.py` (line 64) | test | request-response (assert) | `tests/test_pdf_generation.py` line 80 (identical `builder.app == app` assertion, same fix) | exact — sibling test file, same bug/fix pattern |
| `tests/test_pdf_generation.py` (line 80) | test | request-response (assert) | `tests/test_builder.py` line 64 (same pattern, mirrored) | exact |
| `tests/test_documentation_configuration.py` (line 106) | test | file-I/O + transform (rST validation) | `tests/test_documentation_usage.py` line 103 (identical `publish_string(writer_name=...)` call, same fix) | exact — sibling test file |
| `tests/test_documentation_usage.py` (line 103) | test | file-I/O + transform | `tests/test_documentation_configuration.py` line 106 (mirrored) | exact |
| `pyproject.toml` `[tool.pytest.ini_options]` | config | config | existing `[tool.pytest.ini_options]` block itself (same file, lines 72-81) | exact — additive to existing structure |
| `typsphinx/translator.py` (visit_term/depart_term/visit_definition, lines ~1047-1113) — **optional hardening only** | translator (node-visit, buffering) | transform (event-driven visitor) | same file's `visit_definition`/`depart_definition` buffering pattern (lines ~1088-1113) — sibling buffer-swap idiom already in place | exact (self-analog; no cross-file pattern needed) |

## Pattern Assignments

### `typsphinx/template_engine.py` (service, transform) — API-01, locked

**Analog:** `typsphinx/builder.py` lines 145-153

**Current (deprecated) call, `template_engine.py` line 239:**
```python
from sphinx import addnodes

# Try to find toctree node in doctree
toctree_nodes = list(doctree.traverse(addnodes.toctree))
```

**Analog call to mirror, `builder.py` lines 149-151:**
```python
from docutils.nodes import image

for node in doctree.findall(image):
```

**Fix — replace `traverse()` with `findall()`, keep the `list(...)` wrapper (downstream code does `toctree_nodes[0]` indexing, so the eager list is still required at this call site, unlike `builder.py`'s direct-iterate `for` loop):**
```python
toctree_nodes = list(doctree.findall(addnodes.toctree))
```

No other lines in `template_engine.py` change. `findall()` is a drop-in generator replacement — same order, same node-matching semantics.

---

### `tests/test_translator.py` (test, request-response) — 3 sites, docutils 0.22 `OptionParser` deprecation

**Analog:** docutils' own blessed replacement API (`docutils.frontend.get_default_settings`); no existing in-repo usage predates this fix, so this pattern is introduced fresh but is a pure 1:1 substitution at each of the 3 identical call shapes.

**Current pattern, repeated 3× (import at 1606/1698/1819, call at 1647/1725/1845):**
```python
from docutils.frontend import OptionParser
...
settings = OptionParser(components=(RstParser,)).get_default_values()
```

**Fix — apply identically at all 3 sites:**
```python
from docutils import frontend
...
settings = frontend.get_default_settings(RstParser)
```

Note: `RstParser` is already imported as `from docutils.parsers.rst import Parser as RstParser` at each site — that import stays unchanged; only the `OptionParser` import and the settings-construction line change.

---

### `tests/test_builder.py` / `tests/test_pdf_generation.py` (test, request-response) — Sphinx 9 `builder.app` deprecation

**Analog:** the two files are exact mirrors of each other — fix one, apply the identical edit to the other.

**Current, `tests/test_builder.py` line 64:**
```python
assert builder.app == app
```

**Current, `tests/test_pdf_generation.py` line 80:**
```python
assert builder.app == temp_sphinx_app
```

**Fix (same substitution, preserve each file's existing right-hand-side variable name):**
```python
# test_builder.py
assert builder._app == app

# test_pdf_generation.py
assert builder._app == temp_sphinx_app
```

`typsphinx/builder.py` itself never accesses `self.app` — this is test-assertion-only; `_app` is the underlying non-deprecated attribute the deprecated `.app` property returns.

---

### `tests/test_documentation_configuration.py` / `tests/test_documentation_usage.py` (test, file-I/O + transform) — docutils 0.22 `writer_name` deprecation

**Analog:** the two files are exact mirrors — same `publish_string(...)` call shape, same fix.

**Current, `tests/test_documentation_configuration.py` lines 102-107:**
```python
from docutils.core import publish_string
...
publish_string(
    source=content,
    writer_name="html",
    settings_overrides={"report_level": 2},  # Only report errors
)
```

**`tests/test_documentation_usage.py` line 103 has the identical `writer_name="html",` line in the same call shape.**

**Fix (apply identically at both sites):**
```python
from docutils.core import publish_string
from docutils.writers import get_writer_class
...
publish_string(
    source=content,
    writer=get_writer_class("html")(),
    settings_overrides={"report_level": 2},  # Only report errors
)
```

---

### `pyproject.toml` `[tool.pytest.ini_options]` (config) — D-02 permanent deprecation guard

**Analog:** the existing block itself (lines 72-81) — additive edit, same table.

**Current, lines 72-81:**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --strict-markers"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
]
```

**Fix — add a `filterwarnings` key. Per RESEARCH.md's empirically-verified finding, escalate both `DeprecationWarning` and `PendingDeprecationWarning` (the latter catches Sphinx's `RemovedInSphinxNNWarning` family, e.g. the `builder.app` warning, which subclasses `PendingDeprecationWarning` not `DeprecationWarning`). RESEARCH.md found zero third-party warnings on this stack, so no `ignore::` entries are currently required — but leave a comment noting the escape-hatch pattern for future third-party warnings:**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --strict-markers"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
]
filterwarnings = [
    "error::DeprecationWarning",
    # Escalated beyond CONTEXT.md's literal "DeprecationWarning" text: Sphinx's own
    # RemovedInSphinxNNWarning family (e.g. builder.app) subclasses
    # PendingDeprecationWarning, not DeprecationWarning — without this line, future
    # Sphinx deprecations would pass through un-gated. See 08-RESEARCH.md Pitfall 2.
    "error::PendingDeprecationWarning",
    # No third-party ignore:: entries needed as of Sphinx 9.1.0/docutils 0.22.4/
    # typst-py 0.15.0 (verified zero third-party warnings in 08-RESEARCH.md). If a
    # future dependency bump introduces one, add a targeted
    # ignore::DeprecationWarning:<module> entry here — do not weaken the two `error`
    # lines above.
]
```

---

### `typsphinx/translator.py` (translator, event-driven) — optional defensive hardening, NOT required for SC2/SC3

**Analog (self-file):** the sibling `visit_definition`/`depart_definition` buffer-swap pattern already in the same file, immediately below `visit_term`/`depart_term` (lines ~1080-1113) — same save/restore-`self.body` idiom, so any hardening should follow the exact same buffering shape already established in this file, not introduce a new mechanism.

**Current — single-term overwrite, `translator.py` lines 1047-1084:**
```python
def visit_term(self, node: nodes.term) -> None:
    # Start buffering term content
    self.saved_body = self.body
    self.current_term_buffer = []
    self.body = self.current_term_buffer

def depart_term(self, node: nodes.term) -> None:
    # Get buffered term content
    if isinstance(self.current_term_buffer, list):
        term_content = "".join(self.current_term_buffer).strip()
    else:
        term_content = ""

    # Restore original body
    if self.saved_body is not None:
        self.body = self.saved_body
    self.saved_body = None

    # Store term for later (will be paired with definition)
    self.current_term_buffer = term_content   # OVERWRITES if depart_term fires twice
```

**Optional fix (per RESEARCH.md Pitfall 4 — append-then-join instead of overwrite; only worth doing if the wave has spare capacity, and must ship with a hand-built-doctree regression test since the rST parser cannot currently produce this shape):**
```python
# In visit_definition_list_item (new): self._term_strings = []
# In depart_term: append rather than overwrite
self._term_strings.append(term_content)
# In depart_definition: join before pairing with the definition
joined_term = ", ".join(self._term_strings)
```

RESEARCH.md confirms **no current rST syntax on docutils 0.22.4 triggers multi-`<term>` nodes** — this is forward-looking only, does not block SC2/SC3, and should not be treated as a required fix site.

## Shared Patterns

### `traverse()` → `findall()` (single locked rule, one call site)
**Source:** `typsphinx/builder.py:151`
**Apply to:** `typsphinx/template_engine.py:239` only — grep confirms this is the only `traverse()` call anywhere in `typsphinx/`. No other files need this pattern.
```python
doctree.findall(NodeClass)   # generator, same order/semantics as traverse()
```

### docutils/Sphinx deprecated-API substitution (mechanical, no design)
**Source:** docutils/Sphinx's own documented replacement APIs (see RESEARCH.md "Standard Stack"/"Architecture Patterns" Patterns 2-4)
**Apply to:** the 4 test files above — each substitution is a 1-2 line drop-in with no behavior change; do not add try/except or compatibility shims since this is a latest-only forward-port (no Sphinx-8/docutils-0.21 branching).

### `filterwarnings` guard interaction
**Source:** `pyproject.toml` `[tool.pytest.ini_options]`
**Apply to:** all test files globally — this is why all 4 test-file fixes must land in the same wave as the guard addition (RESEARCH.md Pitfall 1): landing the guard first without the fixes turns every one of the 7 test-level warnings into a hard failure across the whole suite, not just the affected files.

## No Analog Found

None. Every modification site in this phase has either an exact in-repo analog (`builder.py:151` for the `findall()` swap; sibling test files for the 4 test fixes; the existing `pyproject.toml` block for the config addition; the file's own `visit_definition` buffering idiom for the optional translator hardening) or a documented library-blessed replacement API cited in RESEARCH.md. This is expected for a pure API-modernization phase with zero net-new files.

## Metadata

**Analog search scope:** `typsphinx/` (4 files), `tests/` (5 files touched: `test_translator.py`, `test_builder.py`, `test_pdf_generation.py`, `test_documentation_configuration.py`, `test_documentation_usage.py`), `pyproject.toml`
**Files scanned:** 6 modification-site files + `typsphinx/builder.py` (analog source) + RESEARCH.md's empirically-verified fix catalogue (5 confirmed sites + 1 optional)
**Pattern extraction date:** 2026-07-11
**Verification:** all line numbers in this document were re-confirmed against the live tree via `grep`/`sed` (not copied blindly from RESEARCH.md) — `builder.py:151`, `template_engine.py:239`, `test_translator.py:1606-1607/1647, 1698-1699/1725, 1819-1820/1845`, `test_builder.py:64`, `test_pdf_generation.py:80`, `test_documentation_configuration.py:106`, `test_documentation_usage.py:103`, `pyproject.toml:72-81`, `translator.py:1047-1113` all match RESEARCH.md's claims exactly.
</content>
</invoke>
