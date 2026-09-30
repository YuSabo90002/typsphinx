# Phase 59: Path-Shape Predicate and Image-URI Correctness - Pattern Map

**Mapped:** 2026-08-29
**Files analyzed:** 4 new test modules + 1 new fixture project + 2 modified product files (6 total)
**Analogs found:** 6 / 6

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `typsphinx/builder.py` (`_escapes_outdir`, `_track_image` escape branch, `copy_image_files`) | utility / service (path predicate + key construction) | transform (pure string → string) | `typsphinx/builder.py` `_is_absolute_image_uri()` (in-file sibling, lines 121-194) | exact — same file, same idiom family |
| `typsphinx/translator.py` (`visit_image`) | component/translator (node → emitted string) | transform | `typsphinx/translator.py` `escape_typst_string()` (line 156) + its existing call sites | exact — routing change onto an already-shipped helper |
| `tests/test_path_shape_predicate_gate.py` (new) | test (unit, direct-call + characterization) | request-response (pure function call) | `tests/test_out02_escape_target_gate.py` (predicate/warning-shape gate) + in-file docstring pattern of `_is_absolute_image_uri()` | role-match |
| `tests/test_track_image_key_construction.py` (new) | test (unit, pure-string, no filesystem) | transform | `tests/test_builder.py:512-598` `test_post_process_images_rehome_escape_relocates_with_warning` (key-construction assertions) | role-match |
| `tests/test_windows_image_uri_render_gate.py` (new) | test (integration: `-b typst` string-shape + `-b typstpdf` real-compile) | request-response (subprocess) | `tests/test_absolute_image_render_gate.py` (compile-gate template) + `tests/test_templates_path_collision_gate.py:411-470` `TestWindowsPathEscapingRegressionGuard` (string-shape template) + `tests/test_package_template_routing.py:48-89` (`-b typst` build helper) | exact (both halves have exact analogs) |
| `tests/test_copy_image_files_name_too_long.py` (new) | test (integration, `caplog`-based) | event-driven (logged warning capture) | `tests/test_builder.py:512-598` (`caplog.at_level("WARNING")` idiom) | exact |
| `tests/fixtures/<new>/conf.py` (new fixture project) | config (Sphinx `conf.py` + post-transform) | file-I/O | `tests/fixtures/absolute_image_render_gate/conf.py` | exact — template names itself as the model in CONTEXT.md |

## Pattern Assignments

### `typsphinx/builder.py` — PATH-01 (`_escapes_outdir`)

**Analog:** `_is_absolute_image_uri()`, same file, lines 121-194 (already-shipped sibling implementing the exact idiom PATH-01 must copy).

**The idiom to copy** (`typsphinx/builder.py:193-194`):
```python
def _is_absolute_image_uri(resolved_uri: str) -> bool:
    normalized = resolved_uri.replace("\\", "/")
    return posixpath.isabs(normalized) or _is_drive_qualified(normalized)
```

**Current (pre-fix) `_escapes_outdir()` body** (`typsphinx/builder.py:230-238`, read live this session — note: line numbers in this live tree differ slightly from CONTEXT.md's citation, which cites `builder.py:197-238` for the whole function including its docstring):
```python
def _escapes_outdir(stem: str) -> bool:
    segments = stem.replace("\\", "/").split("/")
    # posixpath.isabs(), not path.isabs(): ...
    return ".." in segments or posixpath.isabs(stem) or _is_drive_qualified(stem)
```
The `..`-segment check already normalizes (`stem.replace("\\", "/").split("/")`); only the `posixpath.isabs(stem)` and `_is_drive_qualified(stem)` terms read the RAW `stem` — those two calls are what PATH-01 must repoint at the already-computed `segments`-source normalized string (mirroring `_is_absolute_image_uri`'s single `normalized` variable, reused for both terms).

**Docstring convention to follow:** this module's predicates (`_is_drive_qualified`, `_is_absolute_image_uri`, `_escapes_outdir`) all carry an `Examples:` doctest block with `>>>` transcripts (see `_escapes_outdir`'s own current docstring, lines 197-229) — PATH-01's docstring update should add the two newly-`True` shapes (`\manuals\guide`, `\\srv\share\g`) as doctest lines, matching house style.

---

### `typsphinx/builder.py` — IMG-04 / IMG-06 (`_track_image()` escape branch + `copy_image_files()`)

**Analog:** the surrounding, unmodified code in the same function (`typsphinx/builder.py` `_track_image`, escape branch located just after the `if escaped:` block — grep-located this session; the docstring block precedes it, and `digest`/`key` construction plus the `logger.warning` follow it in this order):

```python
digest = hashlib.sha1(resolved_uri.encode("utf-8")).hexdigest()[:8]
key = (
    f"{RESERVED_IMAGE_NAMESPACE}/{digest}-"
    f"{path.basename(resolved_uri)}"
)
logger.warning(
    f"could not rehome image URI {resolved_uri!r} relative "
    f"to the doctree directory -- relocated to {key!r}"
)
```
`path.basename(resolved_uri)` is the exact defect IMG-04 fixes — `path` is `os.path`, which on a POSIX build host resolves to `posixpath`, which does not split on `\`, so the whole raw URI (backslashes intact) becomes the "basename". **Pitfall 2 (RESEARCH.md):** the `digest = hashlib.sha1(resolved_uri.encode(...))` line must keep reading the RAW `resolved_uri` unchanged — only the basename-extraction half gets a new, separately-named normalized variable (e.g. `basename_source`), never a shared `normalized = resolved_uri.replace(...)` reused for both. `!r` interpolation in the `logger.warning` call is explicitly out of scope this phase (CONTEXT.md Phase Boundary) — do not touch that f-string.

**`copy_image_files()`'s swallow site** (`typsphinx/builder.py`, `copy_image_files`, near the end):
```python
try:
    shutil.copy2(src, dest)
    logger.debug(f"Copied image: {imguri}")
except Exception as e:
    logger.warning(f"Failed to copy image {imguri}: {e}")
```
This is the `except Exception` that swallows `ENAMETOOLONG` (D-08) — IMG-06(b)'s integration gate asserts this exact log line fires pre-fix (`Failed to copy image …: [Errno 36] File name too long`, verbatim per specifics #5) and is absent post-fix, via `caplog` (see Pitfall 4 below — NOT `pytest.warns`).

---

### `typsphinx/translator.py` — IMG-05 (`visit_image()`)

**Analog:** `escape_typst_string()` itself (`typsphinx/translator.py:156-183`) plus `visit_image()`'s current unescaped call sites.

**`escape_typst_string()`** (`typsphinx/translator.py:156-182`, already shipped, single source of truth):
```python
def escape_typst_string(text: str) -> str:
    text = text.replace("\\", "\\\\")  # Backslash (FIRST, avoids double-escaping)
    text = text.replace('"', '\\"')  # Quote
    # ... newline/CR/tab escapes follow
```

**Current `visit_image()` body to change** (`typsphinx/translator.py`, in `visit_image`):
```python
adjusted_uri = self._compute_relative_image_path(uri, current_docname)

if self.in_figure:
    self.add_text(f'  image("{adjusted_uri}"')
else:
    self.add_text(f'image("{adjusted_uri}"')
```
IMG-05/D-13's fix inserts exactly one line after `adjusted_uri = ...`:
```python
escaped_uri = escape_typst_string(adjusted_uri)
```
and both `add_text` sites interpolate `escaped_uri` instead of `adjusted_uri`. This is a **routing change onto an existing helper**, not a new escaper — look at any other `add_text(f'...("{escape_typst_string(...)}"...')`-shaped call site elsewhere in `translator.py` for the established call convention (the helper is already used at multiple text/raw emission sites in this file; grep `escape_typst_string(` for siblings before writing the diff).

---

### `tests/test_path_shape_predicate_gate.py` (new) — PATH-01's direct-call RED gate + characterization pin

**Analog 1 (docstring/doctest convention + direct predicate call):** `typsphinx/builder.py` `_escapes_outdir()`'s own `Examples:` doctest block — a plan/executor should call `_escapes_outdir(...)` directly, exactly as the doctest does, for the RED gate (ROADMAP constraint 8 — the gate must NOT route through either call site).

**Analog 2 (parametrized characterization-through-call-sites shape):** `tests/test_out02_escape_target_gate.py`'s docstring discipline — "drive real product code with a Windows-SHAPED string... never a copy of the f-string pasted into this test module" (mirrored from `TestWindowsPathEscapingRegressionGuard`, quoted below) is the same discipline the characterization pin needs when calling `_resolve_target_stem()` and `_track_image()` — go through the real function, not a re-derived boolean table.

**Analog 3 (parametrize pattern in this suite):** files matching `pytest.mark.parametrize` in `tests/` (e.g. `tests/test_default_typst_documents_derivation.py`, `tests/test_include_edge_derivation_unit.py`, `tests/test_path_naming_predicate.py`) show the house convention of one `@pytest.mark.parametrize("shape,expected", [...])` table driving one assertion body — use this shape for the full shape table (driveless-absolute, drive-qualified, posix-absolute, unc, ordinary-relative) at both `_resolve_target_stem()` (builder.py, `_resolve_target_stem`) and `_track_image()` call sites.

---

### `tests/test_track_image_key_construction.py` (new) — IMG-04's no-backslash gate + IMG-06(a)'s pure-string length-bound gate

**Analog:** `tests/test_builder.py:512-598` `test_post_process_images_rehome_escape_relocates_with_warning` — shows the house pattern for asserting on a COMPUTED key (not a hardcoded literal, since fixture URIs/digests are unstable across runs/machines):

```python
import hashlib
from typsphinx.builder import RESERVED_IMAGE_NAMESPACE, TypstBuilder
# ... build app/builder via temp_sphinx_app fixture, call the escape branch,
# then compute the SAME digest/key construction independently in the test
# and assert equality — never assert against a hardcoded hash string.
```
Per RESEARCH.md's Open Question #1 (recommended: extract), if `_track_image()`'s key-construction logic is pulled into a module-level helper (e.g. `_build_relocation_key(resolved_uri) -> str`), this test module should call that helper DIRECTLY — a pure function, no `TypstBuilder`/`temp_sphinx_app` fixture needed, no filesystem — which is the shape D-08(a) requires ("pure-string unit gate, all lanes, no filesystem"). If the logic stays inline, fall back to `test_builder.py`'s pattern above (drive `_track_image()` through a minimal builder instance and inspect `self.images`/`node["uri"]`).

**Boundary-safety / truncation code to gate (from RESEARCH.md, verified this session):**
```python
def _bound_relocation_component(digest: str, raw_basename: str, limit: int = 255) -> str:
    prefix = f"{digest}-"
    budget = limit - len(prefix.encode("utf-8"))  # D-06: 255 - 9 = 246
    stem, ext = os.path.splitext(raw_basename)
    # ... encode/decode-walk truncation, digest whole, extension preserved,
    # stem never empty, UTF-8 boundary safe (D-07)
```
Test assertions: `len(component.encode("utf-8")) <= 255`; `component.startswith(f"{digest}-")`; `component.endswith(ext)`; stem segment non-empty; `component.encode("utf-8").decode("utf-8")` round-trips without error; and (SC#3 collision re-proof) two long URIs sharing a basename still produce two DISTINCT bounded keys.

---

### `tests/test_windows_image_uri_render_gate.py` (new) — D-04's `-b typst` string-shape sibling + D-01..D-03's real-compile gate

**Analog A (string-shape, no filesystem, `-b typst`):** `tests/test_templates_path_collision_gate.py:411-470` `TestWindowsPathEscapingRegressionGuard`:

```python
class TestWindowsPathEscapingRegressionGuard:
    """... Each test below calls the ACTUAL message-construction function
    ... never a copy of their f-strings pasted into this test module. A
    re-pasted format string would keep passing even if the product
    regressed ... calling the real function is what makes reverting any
    one site turn its own test RED ..."""

    WINDOWS_SHAPED_PATH = "C:\\Users\\runner\\project\\_templates\\nested"

    @staticmethod
    def _assert_no_doubled_separator(message: str) -> None:
        doubled = re.findall(r"\\\\+", message)
        assert not doubled, (...)
```
D-04's sibling must build a Windows-shaped absolute image URI (backslash + double-quote basename, per D-01's four-combination table), drive it through a REAL `-b typst` build (not a hand-written `.typ`), and assert on the emitted `image("...")` literal: no raw backslash present, and the `"` appears escaped as `\"`.

**`-b typst` (not `typstpdf`) subprocess helper to copy:** `tests/test_package_template_routing.py:48-54`:
```python
def _run_sphinx_build_typst(srcdir: Path, outdir: Path) -> subprocess.CompletedProcess:
    """Run ``sphinx-build -b typst`` as a subprocess and return the result."""
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typst", str(srcdir), str(outdir)],
        capture_output=True,
        text=True,
    )
```
Note `tests/test_out02_escape_target_gate.py` has a richer version of the same helper (parametrized `builder` argument, optional `env` merge) — prefer that shape if the same module also needs the `-b typstpdf` compile gate, so one helper serves both builders.

**Analog B (real-compile gate, `-b typstpdf`, full structural template):** `tests/test_absolute_image_render_gate.py` (entire file) + `tests/fixtures/absolute_image_render_gate/` (entire fixture). Concretely reuse:
- The `TYPST_AVAILABLE` import guard:
  ```python
  try:
      import typst  # noqa: F401
      TYPST_AVAILABLE = True
  except ImportError:
      TYPST_AVAILABLE = False
  ```
  applied via `@pytest.mark.skipif(not TYPST_AVAILABLE, reason="...")` on the compile-gate class.
- The `_run_sphinx_build_typstpdf()` helper (identical shape to the `_run_sphinx_build_typst` above, `-b typstpdf`).
- The fixture `conf.py` post-transform pattern (`FakeImageConverter(SphinxTransform)`, `default_priority = 200`, rewriting `node["uri"]` to an absolute path under `<doctreedir>/...` for a matched node, registered via `def setup(app): app.add_post_transform(FakeImageConverter)`) — D-02's fixture changes only WHICH absolute path (and basename shape: `dir\we"ird.png`-style) the post-transform writes, and the transform must copy/create a REAL file at that absolute destination (`shutil.copyfile(standin, destpath)` in the analog) so `copy_image_files()` does not skip it with "Image file not found" (specifics #3).
- Assertion shape: `result.returncode == 0`; absence of the pre-fix `TypstError` substring in `stderr`/build log; presence of `.pdf` output; `.exists()` + non-empty + `%PDF` magic-byte check on the output file, exactly as `test_typstpdf_handles_absolute_image_uri_and_produces_pdf` does at its tail (lines beyond 180, not re-read here — same PDF-assertion idiom other compile gates in this suite already use).

**D-03's probe-and-skip (must be inside the test body, per Pitfall 1 — NOT a `skipif` decorator referencing `tmp_path`):**
```python
def test_windows_shaped_uri_compiles(tmp_path):
    probe_path = tmp_path / 'dir\\we"ird.png'
    try:
        probe_path.parent.mkdir(parents=True, exist_ok=True)
        probe_path.write_bytes(b"probe")
    except OSError as e:
        pytest.skip(f"filesystem cannot hold a backslash+quote filename: {e}")
    # ... build the real fixture from here
```
(RESEARCH.md § Code Examples, verified live this session — no existing analog in this suite performs a fixture-dependent runtime probe-skip; this idiom must be written fresh but is fully specified.)

---

### `tests/test_copy_image_files_name_too_long.py` (new) — IMG-06(b)'s integration gate

**Analog:** `tests/test_builder.py:512-598` region's `caplog.at_level("WARNING")` idiom (used at lines 503, 574, 650, 745, 788, 875 throughout that file — the house convention for this whole test module):
```python
with caplog.at_level("WARNING"):
    # ... call the builder method under test ...

warning_records = [r for r in caplog.records if r.levelname == "WARNING"]
```
**Do not use `pytest.warns(...)`** — RESEARCH.md Pitfall 4: `copy_image_files()`'s `except Exception as e: logger.warning(...)` uses `sphinx.util.logging`, not `warnings.warn()`; `pytest.warns()` will not intercept it and the test will falsely report "did not raise" even when the log line fires.

Gate shape: assert the pre-fix run logs `Failed to copy image …: [Errno 36] File name too long` (verbatim, per specifics #5) and the destination file is absent; assert both are gone (no such warning record, destination file present) post-fix. This needs a real long-basename image URI reaching `copy_image_files()` — build a minimal doctree/builder fixture the way `test_builder.py`'s own `_track_image()`/`post_process_images()` tests do (see `temp_sphinx_app` fixture usage throughout that file), or drive it via a `-b typst`/`-b typstpdf` subprocess build with a long-named source image, whichever the executor's plan decomposition prefers.

---

### `tests/fixtures/<new windows-shaped fixture>/conf.py` (new) — D-02's fixture project

**Analog:** `tests/fixtures/absolute_image_render_gate/conf.py` (full file, read above). Reusable verbatim structure:
```python
project = "..."
author = "Test Author"
release = "1.0.0"
extensions = ["typsphinx"]
html_static_path = ["_static"]
typst_documents = [
    ("index", "master.typ", "...", "Test Author"),
]

class FakeImageConverter(SphinxTransform):
    default_priority = 200
    def apply(self, **kwargs):
        # rewrite node["uri"] to an absolute path outside doctreedir
        # (D-01's basename must carry BOTH a backslash and a double quote,
        # e.g. an absolute path ending in "sub\we\"ird.png")
        ...

def setup(app):
    app.add_post_transform(FakeImageConverter)
```
Two changes from the analog: (1) target path (`"master.typ"`, avoiding the same self-collision the analog's own comment explains — target stem must differ from docname `"index"`); (2) the destination basename shape must be D-01's `sub\we"ird.png`-style string with a real backslash AND a real double quote, and the transform must actually create that file on disk (via `shutil.copyfile` from a `_static/` stand-in PNG, matching the analog) — `\` and `"` are both illegal in NTFS filenames, so this fixture can only be built/run where D-03's probe succeeds (POSIX CI lanes; `windows-latest` will skip via the in-body probe, never via `skipif(os.name == "nt")`).

## Shared Patterns

### Normalize-then-decide (path-shape classification)
**Source:** `typsphinx/builder.py` `_is_absolute_image_uri()` (lines 121-194, esp. 193-194)
**Apply to:** `_escapes_outdir()` (PATH-01)
```python
normalized = resolved_uri.replace("\\", "/")
return posixpath.isabs(normalized) or _is_drive_qualified(normalized)
```
Never `os.path`/`ntpath` for this decision — `posixpath` only, per this module's own documented CPython 3.12/3.13 `ntpath.isabs()` divergence.

### Escape-last (Typst string-literal safety)
**Source:** `typsphinx/translator.py:156` `escape_typst_string()`
**Apply to:** `visit_image()` (IMG-05) — compute once, immediately after `_compute_relative_image_path()`, use at both `add_text` sites (D-13).

### `caplog`, never `pytest.warns`, for `sphinx.util.logging` output
**Source:** `tests/test_builder.py` (six existing usages, e.g. lines 503-509, 574-589)
**Apply to:** `tests/test_copy_image_files_name_too_long.py` (IMG-06(b)); any other new gate asserting on a `logger.warning(...)` call in `builder.py`.

### `sys.executable -m sphinx` subprocess invocation (never `uv run sphinx-build` or a resolved binary)
**Source:** `tests/test_absolute_image_render_gate.py::_run_sphinx_build_typstpdf`; `tests/test_package_template_routing.py::_run_sphinx_build_typst`; `tests/test_out02_escape_target_gate.py::_run_sphinx_build`
**Apply to:** all integration gates in the four new test modules that shell out to `sphinx-build` — each existing gate module in this suite carries its OWN copy of this helper rather than importing a sibling's; follow that convention (do not introduce a shared test-utility import across new modules unless the planner explicitly decides otherwise).

### `TYPST_AVAILABLE` import-guard skip
**Source:** `tests/test_absolute_image_render_gate.py` (top of file) and `tests/test_out02_escape_target_gate.py` (identical block)
**Apply to:** `tests/test_windows_image_uri_render_gate.py`'s compile-gate class only (its string-shape sibling needs no such guard — it never calls `typst.compile()`).

### Parametrized characterization/shape tables
**Source:** house convention across `tests/test_default_typst_documents_derivation.py`, `tests/test_include_edge_derivation_unit.py`, `tests/test_path_naming_predicate.py` (all use `@pytest.mark.parametrize`)
**Apply to:** `tests/test_path_shape_predicate_gate.py`'s characterization pin (D-09/D-10) over the five documented shapes (driveless-absolute, drive-qualified, posix-absolute, unc, ordinary-relative).

## No Analog Found

None — all six new/modified files have a concrete, verified analog in the live tree.

## Metadata

**Analog search scope:** `typsphinx/builder.py`, `typsphinx/translator.py`, `tests/` (grep across all `*.py`), `tests/fixtures/absolute_image_render_gate/`
**Files scanned:** `typsphinx/builder.py`, `typsphinx/translator.py`, `tests/test_absolute_image_render_gate.py`, `tests/fixtures/absolute_image_render_gate/conf.py`, `tests/test_templates_path_collision_gate.py`, `tests/test_out02_escape_target_gate.py`, `tests/test_package_template_routing.py`, `tests/test_builder.py`
**Pattern extraction date:** 2026-08-29
