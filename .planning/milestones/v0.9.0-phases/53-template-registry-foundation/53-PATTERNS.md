# Phase 53: Template Registry Foundation - Pattern Map

**Mapped:** 2026-08-15
**Files analyzed:** 8
**Analogs found:** 8 / 8

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `typsphinx/template_registry.py` (NEW) | validator/resolver (utility-like, config-shape) | transform + batch validate-once | `TypstBuilder._validate_output_path_collisions()` (`builder.py:502-613`) | exact (shape) |
| `typsphinx/__init__.py` (~44-58) | config | CRUD (config registration) | same file's existing `app.add_config_value(...)` calls | exact |
| `typsphinx/builder.py write()` (695-730) | orchestrator (Builder method) | event-driven (build lifecycle) | `self._master_include_edges = self._build_include_edge_map()` (builder.py:730) | exact |
| `typsphinx/builder.py _write_typst_files()` wrapper loop (1074-1092) | controller-like (per-docname dispatch) | request-response (per-entry resolve) | same loop's existing `edge_keys = self._master_include_edges.get(docname, ())` lookup | exact |
| `typsphinx/writer.py render_wrapper()` (322-355) | service (template construction) | transform | its own current body (self-analog; only the input source changes) | exact |
| `typsphinx/template_engine.py` (`TemplateResolution`, `resolve_template()`) | model + service | transform | itself (widen in place; single priority walk) | exact |
| `tests/test_template_registry.py` (NEW) | test | request-response (raise/message assertion) | `tests/test_builder_output_stem.py::test_validate_output_path_collisions_raises_on_docname_collision` (391-416) | exact (in-process `pytest.raises(ExtensionError)` unit style) |
| `tests/test_template_engine.py::TestTemplateResolutionProvenance` | test | transform (additive assertions) | itself (existing class, additive only) | exact |

## Pattern Assignments

### `typsphinx/template_registry.py` (NEW — validator/resolver)

**Primary analog:** `TypstBuilder._validate_output_path_collisions()` (`typsphinx/builder.py:502-613`)

**Accumulate-then-raise-once shape** (builder.py:550-613, the exact idiom D-03 copies):
```python
claims: Dict[str, str] = {}
failures: List[Tuple[str, str]] = []

def _claim(relpath: str, description: str) -> None:
    key = self._collision_key(relpath)
    existing = claims.get(key)
    if existing is not None:
        failures.append(
            (
                relpath,
                f"{existing} and {description} both resolve to "
                f"the same output path {relpath!r}",
            )
        )
        return
    claims[key] = description

# ... populate claims for every relevant item ...

if failures:
    summary = "; ".join(
        f"{relpath!r}: {message}" for relpath, message in failures
    )
    raise ExtensionError(
        f"typst: {len(failures)} output path collision(s): {summary}"
    )
```
D-03 requires the registry validator to mirror this `failures`-list / `"; ".join(...)` / raise-once shape but through an **independent** `ExtensionError` — do not append into `_validate_output_path_collisions()`'s own `failures` list, and do not touch its `"typst: N output path collision(s): …"` message text.

**Case-collision reuse — route through `_collision_key()`, do not re-fold** (`builder.py:422-500`):
```python
@staticmethod
def _collision_key(relative_path: str) -> str:
    folded_separators = relative_path.replace("\\", "/")
    normalized_shape = posixpath.normpath(folded_separators)
    return normalized_shape.casefold()
```
RESEARCH.md Q4 gives the exact CONF-18 case-7 predicate built on top of it:
```python
def _has_case_collision(key: str, other_keys: set[str]) -> bool:
    folded = TypstBuilder._collision_key(key)
    return any(
        other != key and TypstBuilder._collision_key(other) == folded
        for other in other_keys
    )
```

**Fail-loud validate-and-raise precedent** — `derive_typst_lang()`'s `re.fullmatch()` idiom (`template_engine.py:84-104`, called by `template_engine.py:133` for the actual regex line) is the in-repo precedent for "reject a config-shape value, log/raise naming the offending value". D-01 explicitly **declines its allowlist-regex form** (`re.fullmatch(r"[A-Za-z0-9_-]+", key)`, rejected by name in CONTEXT.md D-01/STACK.md) but keeps the fail-loud structure — i.e. copy the "name the offending value via `repr()`" habit, not the regex.

**Package-vs-template routing — reuse, don't re-derive**, `resolve_package_for_engine()` (`template_engine.py:149-173`):
```python
def resolve_package_for_engine(
    typst_package: str | None, raw_template_path: str | None
) -> str | None:
    """... D-01/D-03 routing rule ... This is the SINGLE place that
    decision is made. writer.py and builder.py must not re-derive it
    independently ..."""
    return None if raw_template_path else typst_package
```
The `"typst"` key's synthesis must call this, not re-implement the "template wins over package" rule inline.

**The `"typst"` key's synthesis mirrors, but does not delete, `_write_template_file()`** (`builder.py:1109-1179`, quoted for the planner — NOT deleted this phase):
```python
raw_template_path = getattr(config, "typst_template", None)
template_path = raw_template_path
if template_path:
    template_path = os.path.join(self.srcdir, template_path)

typst_package = getattr(config, "typst_package", None)

if typst_package and raw_template_path:
    logger.warning(
        "Both 'typst_package' and 'typst_template' are configured; "
        "this combination is unsupported. 'typst_template' will be "
        "honoured and 'typst_package' will be ignored."
    )

if typst_package and not raw_template_path:
    return

template_engine = TemplateEngine(
    template_path=template_path,
    search_paths=[self.srcdir],
    parameter_mapping=getattr(config, "typst_template_mapping", None),
    typst_package=resolve_package_for_engine(typst_package, raw_template_path),
    typst_template_function=getattr(config, "typst_template_function", None),
    typst_package_imports=getattr(config, "typst_package_imports", None),
)
```
Per RESEARCH.md Q1, the built-in `"typst"` entry synthesis is exactly:
```python
TemplateRegistryEntry(
    key="typst",
    template=getattr(config, "typst_template", None),
    package=getattr(config, "typst_package", None),
    template_function=getattr(config, "typst_template_function", None),
)
```
— read the same three globals `_write_template_file()` already reads, unmodified, so `resolve_package_for_engine()` and `os.path.join()` see identical inputs and TPL-03's byte-identical-output invariant holds structurally.

**Anti-analog — do NOT reuse for registry-key shape validation:** `_is_drive_qualified()` / `_escapes_outdir()` (`builder.py:36-112`). Quote their docstrings so the planner records why:
```python
def _escapes_outdir(stem: str) -> bool:
    """... Deliberately does NOT test for a path separator alone -- OUT-01
    reverses Phase 44's "any path component is rejected" rule. A
    separator-bearing, non-escaping stem (e.g. "manuals/guide") is
    now a legitimate output path, not a guard trigger; ...

    Examples:
        >>> _escapes_outdir("manuals/guide")
        False
        >>> _escapes_outdir("../escape")
        True
    """
```
`_escapes_outdir("manuals/guide")` is `False` by design — this function's contract is "is this a legal multi-segment OUTPUT path", the opposite question from CONF-18's "is this key legal as a SINGLE path segment" (D-02's case 3 rejects `/` and `\` outright). Registry-key validation needs a **new named predicate set** (Q4's seven functions), not an extension or reuse of `_escapes_outdir()`/`_is_drive_qualified()`.

**"New usability question gets a new predicate" precedent** — `_is_usable_typst_documents_entry()` docstring (`builder.py:115-166`), quoted because D-06 is built directly on this instruction:
```python
def _is_usable_typst_documents_entry(entry: tuple) -> bool:
    """... This is the SINGLE source of truth for "can this entry produce a
    wrapper file", consulted by all FOUR sites that need this answer ...
    A future site needing a genuinely DIFFERENT usability question must
    introduce a second named predicate rather than yet another inline
    check.
    ...
    An entry that fails this predicate is TOLERATED AND SKIPPED at every
    write-phase site -- it never raises there. ...
    """
    return bool(entry) and len(entry) >= 2 and isinstance(entry[0], str)
```
D-06's element-[4]-not-a-`str` case must NOT join this tolerate-and-skip contract; it raises the same CONF-14-class `ExtensionError` as an unregistered key instead — this is "a different usability question", per the docstring's own instruction, so it belongs in a distinct predicate/branch inside the registry lookup helper, never as an extension of `_is_usable_typst_documents_entry()`.

**Reserved-name/CONF-18 predicates (Q4, ready-to-copy):**
```python
_WINDOWS_RESERVED_NAMES = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)


def _is_windows_reserved_name(key: str) -> bool:
    stem = key.split(".", 1)[0]
    return stem.upper() in _WINDOWS_RESERVED_NAMES
```

**CONF-17 path-arithmetic predicate (Q5, ready-to-copy):**
```python
def _violates_conf17(template_abs_path: str, srcdir: str) -> bool:
    parent = os.path.normpath(os.path.dirname(os.path.abspath(template_abs_path)))
    norm_srcdir = os.path.normpath(os.path.abspath(srcdir))
    return os.path.commonpath([norm_srcdir, parent]) == parent
```

---

### `typsphinx/__init__.py` (~44-58) — config registration

**Analog:** the existing block itself.
```python
app.add_config_value("typst_documents", _default_typst_documents, "html", [list])
app.add_config_value("typst_template", None, "html", [str, type(None)])
app.add_config_value("typst_template_mapping", None, "html", [dict, type(None)])
app.add_config_value("typst_use_mitex", True, "html", [bool])
app.add_config_value("typst_elements", {}, "html", [dict])
app.add_config_value("typst_package", None, "html", [str, type(None)])
app.add_config_value("typst_package_imports", None, "html", [list, type(None)])
app.add_config_value(
    "typst_template_function", None, "html", [str, dict, type(None)]
)
app.add_config_value("typst_debug", False, "html", [bool])
app.add_config_value("typst_template_assets", None, "html", [list, type(None)])
```
New line follows the exact same shape: `app.add_config_value("typst_document_templates", {}, "html", [dict])`. `typst_template_assets` at line 58 is **not removed** this phase (Phase 54/CONF-19).

---

### `typsphinx/builder.py write()` (695-730) — insertion point

**Analog:** `self._master_include_edges = self._build_include_edge_map()` (builder.py:719-730), the "derive once in `write()`, thread into the per-docname loop" pattern:
```python
# D-02/D-03: validate BEFORE anything is written -- including
# prepare_writing()'s own _write_template_file() call just below ...
self._validate_output_path_collisions()

logger.info("preparing documents... ", nonl=True)
self.prepare_writing(docnames)
logger.info("done")

# Phase 49 (COMP-05/COMP-06): derive the per-master include-edge
# mapping UNCONDITIONALLY at the same position ...
self._master_include_edges = self._build_include_edge_map()
```
Per ROADMAP's locked placement and RESEARCH.md's recommendation, the registry resolution call goes **after line 713's `_validate_output_path_collisions()`, before line 716's `prepare_writing()`** — i.e. `self._template_registry = resolve_template_registry(self.config)` inserted between those two lines, stored as a builder attribute exactly like `self._master_include_edges` is stored, so `_write_typst_files()` can read it later without re-deriving it (mirrors the lazy-init fallback at builder.py:1071-1072 for direct-call test paths, if the planner wants the same safety net).

---

### `typsphinx/builder.py _write_typst_files()` wrapper loop (1074-1092)

**Analog:** the existing `edge_keys = self._master_include_edges.get(docname, ())` lookup immediately above it:
```python
for entry in typst_documents:
    if not _is_usable_typst_documents_entry(entry) or entry[0] != docname:
        continue
    wrapper_relpath = self._wrapper_output_relpath(entry)
    wrapper_destination = path.normpath(
        path.join(self.outdir, wrapper_relpath + ".typ")
    )
    ensuredir(path.dirname(wrapper_destination))
    wrapper_relative_dir = posixpath.dirname(wrapper_relpath)
    edge_keys = self._master_include_edges.get(docname, ())
    wrapper_output = self.writer.render_wrapper(
        entry,
        doctree,
        wrapper_relative_dir,
        content_relative_path,
        edge_keys=edge_keys,
    )
```
Resolve `entry[4]` (absent → `"typst"`) the same way — a plain dict lookup against `self._template_registry`, raising CONF-14's `ExtensionError` (naming `sorted(registry.keys())`) on a miss — and pass the resolved `TemplateRegistryEntry` into `render_wrapper(..., template_entry=...)` alongside the existing positional args, following the same "thread an already-derived value into an existing call" shape `edge_keys` already demonstrates.

---

### `typsphinx/writer.py render_wrapper()` (322-355)

**Analog:** its own current body (self-analog — only the input source changes).
```python
config = self.builder.config

raw_template_path = getattr(config, "typst_template", None)
typst_package = getattr(config, "typst_package", None)

template_path = raw_template_path
if template_path:
    source_dir = self.builder.srcdir
    template_path = os.path.join(source_dir, template_path)

package_for_engine = resolve_package_for_engine(
    typst_package, raw_template_path
)

template_engine = TemplateEngine(
    template_path=template_path,
    search_paths=[self.builder.srcdir],
    parameter_mapping=getattr(config, "typst_template_mapping", None),
    typst_package=package_for_engine,
    typst_template_function=getattr(config, "typst_template_function", None),
    typst_package_imports=getattr(config, "typst_package_imports", None),
)
```
RESEARCH.md Q1's constructor-argument mapping table (verbatim, this is the concrete diff to make):

| Constructor argument | Today | Phase 53 source | Scope |
|---|---|---|---|
| `template_path` | `os.path.join(srcdir, raw_template_path)` if `typst_template` set | `os.path.join(srcdir, entry.template)` if `entry.template` set, else `None` | Per-key |
| `search_paths` | `[self.builder.srcdir]` | unchanged | Global |
| `parameter_mapping` | `getattr(config, "typst_template_mapping", None)` | same, **only when `entry.key == "typst"`**, else `None` | Per-key (D-11) |
| `typst_package` | `resolve_package_for_engine(typst_package, raw_template_path)` | `resolve_package_for_engine(entry.package, entry.template)` — same helper | Per-key |
| `typst_template_function` | `getattr(config, "typst_template_function", None)` | `entry.template_function` | Per-key (D-10: no inheritance) |
| `typst_package_imports` | `getattr(config, "typst_package_imports", None)` | unchanged | Global |

---

### `typsphinx/template_engine.py` — `TemplateResolution` / `resolve_template()`

**Analog:** itself. Widen `TemplateResolution` (template_engine.py:37-56) in place — verified `grep -n "TemplateResolution(" typsphinx/*.py tests/*.py` returns exactly 3 hits, all inside `resolve_template()` (lines 311/324/336), so this is zero-call-site-migration-cost:
```python
@dataclass(frozen=True)
class TemplateResolution:
    content: str
    source: str
    path: Path | None
```
populated inline at each of the three existing branches:
```python
if self.template_path:
    template_content = self._try_load_file(self.template_path)
    if template_content is not None:
        return TemplateResolution(template_content, "explicit")   # -> add self.template_path
    ...
if self.search_paths:
    for search_dir in self.search_paths:
        candidate_path = Path(search_dir) / self.template_name
        template_content = self._try_load_file(str(candidate_path))
        if template_content is not None:
            return TemplateResolution(template_content, "search")  # -> add candidate_path
...
default_path = self.get_default_template_path()
...
return TemplateResolution(template_content, "default")  # -> add Path(default_path)
```
Do **not** add a separate `resolve_template_path()` method — RESEARCH.md Q2 shows both alternatives collapse into either literal duplication of the priority walk (forbidden by the class's own CONF-07/D-06 docstring at template_engine.py:290-295) or a thin wrapper around the widened dataclass anyway.

**D-08's per-key existence check does NOT live here.** RESEARCH.md Q3: `resolve_template()`'s Priority-1 warn-and-fallback (lines 308-315) stays behaviourally untouched; D-08's `os.path.isfile()` check for user-defined keys belongs in `template_registry.py`'s validator, called as a bare filesystem check, never through `resolve_template()`'s multi-priority walk (which always succeeds via fallback and therefore can never itself signal "not found").

---

### `tests/test_template_registry.py` (NEW)

**Best structural analog:** `tests/test_builder_output_stem.py::test_validate_output_path_collisions_raises_on_docname_collision` / `test_validate_output_path_collisions_raises_on_reserved_template_name` (lines 391-455) — in-process, `temp_sphinx_app` fixture, direct method call, `pytest.raises(ExtensionError)`. This is preferred over the subprocess-based `..._gate.py` modules (`test_typst_documents_collision_gate.py`, `test_collision_predicate_completeness_gate.py`, `test_package_only_config_gate.py`, `test_typst_lang_gate.py`), which spawn `sys.executable -m sphinx` and assert on subprocess stdout/returncode — appropriate for full-build e2e gates but heavier and less suited to per-case `ExtensionError`-message assertions than an in-process unit test.

```python
def test_validate_output_path_collisions_raises_on_docname_collision(
    temp_sphinx_app,
):
    import types

    import pytest
    from sphinx.errors import ExtensionError

    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.env = types.SimpleNamespace(found_docs={"index", "chapter1"})
    builder.config.typst_documents = [("index", "chapter1.typ", "T", "A")]

    with pytest.raises(ExtensionError):
        builder._validate_output_path_collisions()
```

The `temp_sphinx_app` fixture itself (`tests/conftest.py:46-71`) that both this analog and the new test file should use:
```python
@pytest.fixture
def temp_sphinx_app(tmp_path: Path) -> SphinxTestApp:
    srcdir = tmp_path / "source"
    srcdir.mkdir()
    conf_py = srcdir / "conf.py"
    conf_py.write_text(
        "extensions = ['typsphinx']\n"
        "project = 'Test Project'\n"
        "author = 'Test Author'\n"
    )
    index_rst = srcdir / "index.rst"
    index_rst.write_text(
        "Test Document\n=============\n\nThis is a test document.\n"
    )
    # ... (builds and returns a SphinxTestApp)
```
For TPL-01/TPL-04/TPL-05/CONF-14…18, follow the same shape: construct a Sphinx app/config (or a plain `types.SimpleNamespace`-based config stub, as `test_validate_output_path_collisions_raises_on_docname_collision` does for `env`), set `builder.config.typst_document_templates = {...}`, call `resolve_template_registry(builder.config)` (or the builder-attribute equivalent) directly, and assert either the returned dict shape (TPL-01/04/05) or `pytest.raises(ExtensionError, match=...)` with a message-substring check for each CONF-14…18 case — parametrize one case per denylist entry (Q4's seven predicates) using `pytest.mark.parametrize`, matching this suite's established one-assertion-per-named-case granularity (see `test_typst_lang_gate.py`'s per-shape test classes for the parametrization density convention, though that module itself is subprocess-based).

---

### `tests/test_template_engine.py::TestTemplateResolutionProvenance`

**Analog:** itself — the existing class. Modification is **additive only**: add one or two assertions confirming the new `.path` field is populated correctly at each of the three priorities, alongside the existing `.source` assertions. Do not restructure the 3 existing passing tests in this class.

---

## Shared Patterns

### Accumulate-then-raise-once validation
**Source:** `TypstBuilder._validate_output_path_collisions()` (`builder.py:502-613`)
**Apply to:** `template_registry.py`'s `resolve_template_registry()` — same shape, independent `ExtensionError`, never merged into the collision validator's own `failures` list (D-03).

### Comparison-only key folding
**Source:** `TypstBuilder._collision_key()` (`builder.py:422-500`)
**Apply to:** CONF-18's case-7 (differs from another registered key only by case) — route through this static method, do not write a second `.casefold()` call.

### Package-vs-template routing
**Source:** `resolve_package_for_engine()` (`template_engine.py:149-173`)
**Apply to:** the `"typst"` key's synthesis in `template_registry.py`, and `render_wrapper()`'s per-key `typst_package` argument — single source of truth for "template wins over package" (WR-04/D-01/D-03).

### Fail-loud, never `config-inited`
**Source:** `derive_typst_lang()` (`template_engine.py:84-133`); confirmed no `config-inited` handler exists anywhere in `typsphinx/*.py` (RESEARCH.md's own `grep` measurement).
**Apply to:** every new `ExtensionError` raised by `template_registry.py` — raised from inside a `Builder` method (`write()`'s call site), never registered as a `config-inited` event handler.

### "New usability question -> new predicate"
**Source:** `_is_usable_typst_documents_entry()` docstring (`builder.py:115-166`)
**Apply to:** D-06 — an element `[4]` that is present-but-non-`str` is a different question from "is this entry well-formed enough to produce a wrapper" and must NOT extend that predicate's tolerate-and-skip contract.

## No Analog Found

None — every file in scope has a strong (role + data-flow) in-repo analog; no file requires falling back to RESEARCH.md's Q1–Q5 code sketches as the sole source (though those sketches are still the most literal starting point for the wholly-new `template_registry.py` module, since no prior file in this codebase combines "dataclass registry entry" + "resolver function" in one module).

## Metadata

**Analog search scope:** `typsphinx/*.py` (builder.py, writer.py, template_engine.py, __init__.py), `tests/test_builder_output_stem.py`, `tests/test_template_engine.py`, `tests/test_typst_documents_collision_gate.py`, `tests/test_collision_predicate_completeness_gate.py`, `tests/test_package_only_config_gate.py`, `tests/test_typst_lang_gate.py`, `tests/conftest.py`.
**Files scanned:** 12 (read in full or targeted-section reads; no re-reads of already-loaded ranges).
**Pattern extraction date:** 2026-08-15
