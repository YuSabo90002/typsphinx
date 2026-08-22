# Phase 54: One Bundle Rule — Pattern Map

**Mapped:** 2026-08-15
**Files analyzed:** 12 (production) + 6 (test/fixture/CI categories)
**Analogs found:** 11 / 12 production files have a direct in-repo analog (the `config-inited`
handler has none — it is this codebase's first; mapped to the nearest `setup(app)` registration
site instead)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `typsphinx/builder.py` — new `_copy_used_template_bundles()` (replaces `copy_template_assets()`) | builder/service | batch file-I/O | `typsphinx/builder.py:1378-1432` `_copy_template_directory()` (itself, generalized) | exact (self-analog) |
| `typsphinx/builder.py` — `init()` addition (`self._used_template_keys`) | builder state | event-driven accumulator | `typsphinx/builder.py:231` `self.images: dict[str, str] = {}` | exact |
| `typsphinx/builder.py` — `_write_typst_files()` accumulator append | builder/write-loop | event-driven accumulator | `typsphinx/builder.py:1296-1332` `copy_image_files()` consumer side + the (currently separate) `_track_image()` producer side | exact |
| `typsphinx/builder.py` — `finish()` bundle-copy call site | builder/lifecycle | batch | `typsphinx/builder.py:1508-1516` `finish()` (itself) | exact |
| `typsphinx/builder.py` — `_validate_output_path_collisions()` `_template/` prefix reservation | validator | request-response (pre-write validation) | `typsphinx/builder.py:517-628` (itself, `_claim()`/`_collision_key()`) | exact (self-analog) |
| `typsphinx/builder.py` — fatal-vs-warn split in bundle copy (D-05) | builder/service | batch file-I/O with mixed error severity | `typsphinx/builder.py:1408-1429` (`_copy_template_directory()`'s existing per-file `try/except → logger.warning`) for the non-fatal half; `typsphinx/template_registry.py:436-441` (`raise ExtensionError(...)` accumulate-then-raise) for the fatal half | exact / exact |
| `typsphinx/writer.py` — new `compute_template_import_path()` (root-absolute) | utility/transform | pure string transform | `typsphinx/writer.py:69-106` `compute_template_import_path_for_dir()` (itself, being replaced) | exact (self-analog) |
| `typsphinx/writer.py` — `render_wrapper()` call-site update | writer | request-response | `typsphinx/writer.py:267-486` (itself, line ~480 call site) | exact (self-analog) |
| `typsphinx/template_engine.py` — `get_default_template_path()` via `importlib.resources` | service/resolver | file-I/O | `typsphinx/template_engine.py:276-288` (itself, being replaced) | exact (self-analog) — no existing `importlib.resources` usage anywhere in `typsphinx/` |
| `typsphinx/__init__.py` — CONF-19 `config-inited` handler + `app.connect(...)` | event handler | event-driven | **No analog exists** — `grep -n "app.connect\|config-inited" typsphinx/*.py` returns zero hits. Nearest structural precedent is `typsphinx/__init__.py:40-63` `setup(app)`'s own `app.add_config_value(...)` registration block (same file, same function, same "runs once at extension setup" role) | role-match only (no event-handler precedent in this codebase) |
| `pyproject.toml` — `templates/**/*` glob widening | config | batch | `pyproject.toml:72-73` (itself, being widened) | exact (self-analog) |
| `.github/workflows/ci.yml` — wheel-content assertion step | CI config | request-response (build verification) | `.github/workflows/ci.yml:127-151` (`build` job: `uv build` → `twine check`) | role-match (extends an existing job, no prior "open the wheel and grep its contents" step exists) |
| `tests/test_bundle_copy_layout_gate.py` (OUT-04) | test | integration (real `sphinx-build`) | `tests/test_typst_lang_gate.py` (canonical GATE-01 real-compile pattern, see below) | exact |
| `tests/test_user_template_relative_asset_gate.py` (OUT-05) | test | integration (real `sphinx-build` → `typst.compile()`) | `tests/test_typst_lang_gate.py` `TestJapaneseSourceProof` class shape | exact |
| `tests/test_removed_config_deprecation_warning.py` (CONF-19) | test | unit (`caplog`) | No direct `caplog`-based warning test found in a quick grep; nearest is the `logger.warning(...)`-and-continue assertions embedded in `tests/test_collision_predicate_completeness_gate.py` (asserts warning behaviour via subprocess stdout/stderr, not `caplog`) — Claude's discretion on exact mechanism per CONTEXT.md | role-match |
| `tests/test_bundle_copy_exclusion_manifest_gate.py` (BLD-06, manifest-diff shaped) | test | integration (filesystem manifest diff) | **No existing manifest-diff-shaped test found** — see "No Analog Found" below | none |
| `tests/fixtures/template_named_dir_master/` successor (OUT-07 negative case) | fixture | request-response (negative/error path) | `tests/fixtures/template_named_dir_master/conf.py` (itself, relocating per Claude's Discretion) | exact (self-analog) |
| `tests/fixtures/typst_lang_gate/srcdir_shadow_lang/base.typ → _typst/base.typ` (D-14) | fixture | file-I/O relocation | `tests/fixtures/typst_lang_gate/srcdir_shadow_lang/` (itself; contains `base.typ`, `conf.py`, `index.rst` today) | exact (self-analog) |

## Pattern Assignments

### `typsphinx/builder.py` — bundle-copy driver (D-02, generalizing `_copy_template_directory()`)

**Analog:** `typsphinx/builder.py:1378-1432` (`_copy_template_directory()`, current body)

**Current body to generalize** (imports/signature at top of file, `os`/`shutil`/`path` already
imported — see `typsphinx/builder.py:8-19`):
```python
def _copy_template_directory(self, template_path: str) -> None:
    import os

    template_dir = path.dirname(template_path)
    if not template_dir:
        return

    src_dir = path.join(self.srcdir, template_dir)
    dest_dir = path.join(self.outdir, template_dir)

    if not path.exists(src_dir):
        logger.warning(f"Template directory not found: {src_dir}")
        return

    copied_count = 0
    for root, _dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".typ"):        # <-- D-02: THIS skip is removed
                continue
            src_file = path.join(root, file)
            rel_path = path.relpath(src_file, src_dir)
            dest_file = path.join(dest_dir, rel_path)
            ensuredir(path.dirname(dest_file))
            try:
                shutil.copy2(src_file, dest_file)
                logger.debug(f"Copied template asset: {rel_path}")
                copied_count += 1
            except Exception as e:
                logger.warning(f"Failed to copy template asset {rel_path}: {e}")
    if copied_count > 0:
        logger.info(f"Copied {copied_count} template asset(s) from {template_dir}/")
```

**What D-02/D-04/D-05 require changed, concretely:**
1. Signature must accept an ABSOLUTE `src_dir`/`dest_dir` pair (not a srcdir-relative
   `template_path` string) — the bundled `"typst"` key's source lives inside the installed
   package (`importlib.resources`), not under `srcdir`.
2. Remove the `if file.endswith(".typ"): continue` skip entirely (D-02).
3. Add `os.walk(src_dir, followlinks=False)` explicitly — `followlinks=False` is already
   `os.walk`'s own default, so this is a no-behaviour-change explicit-arg addition, per D-02's
   text ("today's `_copy_template_directory()` body … D-02 keeps").
4. Add a name-based exclusion filter for exactly the D-04 four kinds (`.git`, `.DS_Store`,
   `Thumbs.db`, editor backups) applied to `dirs[:]` (to prune `.git` from descent) and to `files`
   — see the `_is_excluded_bundle_entry()` shape in RESEARCH.md's Code Examples section
   (`54-RESEARCH.md` lines 654-678).
5. Split the per-file `except Exception → logger.warning` (kept verbatim for non-template files,
   D-05) from a NEW fatal branch: when the file being copied is the RESOLVED template file itself,
   a copy failure must `raise ExtensionError(...)` naming the registry key and both paths, not
   `logger.warning`-and-continue. Model the `ExtensionError` message shape on
   `typsphinx/template_registry.py:438-441`'s accumulate-then-raise style (`f"typst_document_templates: {len(failures)} invalid definition(s): {summary}"`) —
   i.e. name the registry key, both the source and destination absolute paths, and the underlying
   exception.

**Caller-side accumulator changes:**

**Analog:** `typsphinx/builder.py:231` (`init()`) + `typsphinx/builder.py:1296-1332`
(`copy_image_files()`) — this is ROADMAP constraint #4's explicitly named pattern to mirror.

```python
# builder.py:231 (init()) -- existing precedent, self.images
self.images: dict[str, str] = {}

# NEW, same method, same shape:
self._used_template_keys: set[str] = set()
```

```python
# builder.py:1195-1205 (_write_typst_files(), existing wrapper loop) --
# template_entry is ALREADY resolved here (Phase 53); add ONE line:
template_entry = resolve_registry_key(
    self._document_template_registry, entry
)
self._used_template_keys.add(template_entry.key)   # NEW
wrapper_output = self.writer.render_wrapper(
    entry, doctree, wrapper_relative_dir, content_relative_path,
    edge_keys=edge_keys, template_entry=template_entry,
)
```

```python
# builder.py:1296-1332 (copy_image_files()) -- the CONSUMER shape to mirror
# in finish(): "if not self.<accumulator>: return", then iterate .items()/
# set members, resolve src/dest, ensuredir, try/except shutil.copy2.
def copy_image_files(self) -> None:
    if not self.images:
        return
    logger.info(f"Copying {len(self.images)} image file(s)...")
    for imguri, override_src in self.images.items():
        src = override_src if override_src else path.join(self.srcdir, imguri)
        dest = path.join(self.outdir, imguri)
        if not path.exists(src):
            logger.warning(f"Image file not found: {src}")
            continue
        ensuredir(path.dirname(dest))
        try:
            shutil.copy2(src, dest)
        except Exception as e:
            logger.warning(f"Failed to copy image {imguri}: {e}")
```

```python
# builder.py:1508-1516 (finish()) -- current shape, second line is
# replaced by the new driver:
def finish(self) -> None:
    self.copy_image_files()
    self.copy_template_assets()   # <-- replaced with the accumulator-driven driver
```

---

### `typsphinx/builder.py` — `_validate_output_path_collisions()` `_template/` prefix reservation (OUT-07)

**Analog:** `typsphinx/builder.py:517-628` (itself)

**`_collision_key()` — the normalization primitive to route the new prefix check through**
(`typsphinx/builder.py:513-515`, body only — full docstring at 438-512 explains the
casefold/normpath contract):
```python
folded_separators = relative_path.replace("\\", "/")
normalized_shape = posixpath.normpath(folded_separators)
return normalized_shape.casefold()
```

**`_claim()` — the accumulate-then-raise-once idiom** (`typsphinx/builder.py:568-580`):
```python
def _claim(relpath: str, description: str) -> None:
    key = self._collision_key(relpath)
    existing = claims.get(key)
    if existing is not None:
        failures.append((
            relpath,
            f"{existing} and {description} both resolve to "
            f"the same output path {relpath!r}",
        ))
        return
    claims[key] = description
```

**Current exact-string claim being replaced/widened** (`typsphinx/builder.py:586`):
```python
_claim("_template.typ", "the reserved _template.typ infrastructure file")
```
This must become a PREFIX predicate ("first `/`-segment is `_template`"), which — per
RESEARCH.md's Anti-Patterns section — is a materially different shape from `_claim()`'s existing
exact-match semantics, so it needs its OWN new predicate function routed through
`_collision_key()`'s normalize-then-casefold, not a widened `_claim()` call. The final
`ExtensionError` raise to model the message on (`typsphinx/builder.py:622-628`):
```python
if failures:
    summary = "; ".join(
        f"{relpath!r}: {message}" for relpath, message in failures
    )
    raise ExtensionError(
        f"typst: {len(failures)} output path collision(s): {summary}"
    )
```

---

### `typsphinx/writer.py` — root-absolute import path (OUT-06)

**Analog:** `typsphinx/writer.py:69-106` (`compute_template_import_path_for_dir()`, itself, being
replaced)

```python
# CURRENT — depth-counted, replace this shape:
def compute_template_import_path_for_dir(wrapper_relative_dir: str) -> str:
    if not wrapper_relative_dir:
        depth = 0
    else:
        depth = len(PurePosixPath(wrapper_relative_dir).parts)
    return "".join(["../"] * depth) + "_template.typ"
```
Replace with (illustrative shape per RESEARCH.md, exact naming Claude's discretion):
```python
def compute_template_import_path(key: str, template_filename: str) -> str:
    return f"/_template/{key}/{template_filename}"
```
Note `typsphinx/writer.py:170-221`'s `_compute_template_import_path()` (static method) is
CONFIRMED dead code (zero non-docstring callers) — do not mistake it for the function needing
generalization; it is out of THIS phase's deletion responsibility (Deferred Ideas), but must not
be extended by mistake.

Call site to update is `render_wrapper()` (`typsphinx/writer.py:267-486`), around line 480, where
`template_file` is currently computed via the old depth-only helper — swap the call only; the rest
of `render_wrapper()`'s shape (already threading `template_entry: TemplateRegistryEntry | None`
from Phase 53) is unchanged.

---

### `typsphinx/template_engine.py` — `importlib.resources` for the bundled `"typst"` key (SC#2)

**Analog:** `typsphinx/template_engine.py:276-288` (`get_default_template_path()`, itself, being
replaced) — this is the ONLY site in the codebase resolving a package-bundled path today, and
`importlib.resources` has zero prior usage anywhere in `typsphinx/` (confirmed:
`grep -rn "importlib.resources" typsphinx/` → no hits).

```python
# CURRENT (276-288):
def get_default_template_path(self) -> str:
    package_dir = Path(__file__).parent
    template_dir = package_dir / "templates"
    default_template = template_dir / "base.typ"
    return str(default_template)
```
Replace per RESEARCH.md's Code Examples (directory support requires Python ≥3.12, this project's
own floor):
```python
import importlib.resources

def get_default_template_path(self) -> str:
    resource = importlib.resources.files("typsphinx") / "templates" / "base.typ"
    with importlib.resources.as_file(resource) as real_path:
        return str(real_path)
    # NOTE: as_file()'s context manager may clean up a temporary extraction
    # on exit for a non-filesystem loader; a caller needing the DIRECTORY to
    # persist for the bundle-copy driver's os.walk() must keep the `with`
    # block open around the ENTIRE copy operation, not just the path lookup.
```

---

### `typsphinx/__init__.py` — CONF-19 `config-inited` handler (this codebase's first)

**Analog:** No `app.connect(...)` precedent exists anywhere in this codebase (confirmed:
`grep -n "app.connect\|config-inited\|config_inited" typsphinx/*.py` → zero hits). The nearest
structural precedent is the existing `setup(app)` registration block itself — same function, same
"runs once, at extension setup" role, same file:

**Current `setup(app)` shape to extend** (`typsphinx/__init__.py:28-69`, full file read):
```python
def setup(app: Sphinx) -> Dict[str, Any]:
    app.add_builder(TypstBuilder)
    app.add_builder(TypstPDFBuilder)

    app.add_config_value("typst_documents", _default_typst_documents, "html", [list])
    app.add_config_value("typst_template", None, "html", [str, type(None)])
    ...
    app.add_config_value("typst_template_assets", None, "html", [list, type(None)])  # DELETE this line
    app.add_config_value("typst_document_templates", {}, "html", [dict])

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
```
New handler shape (RESEARCH.md's Code Examples, module-siting is Claude's discretion — either
alongside this block or a new module):
```python
_REMOVED_CONFIG_VALUES = {
    "typst_template_assets": "<D-09 bespoke message>",
    "typst_authors": "<D-09 bespoke message>",
    "typst_toctree_defaults": "<D-09 bespoke message, no replacement>",
}

def _warn_removed_config_values(app, config) -> None:
    raw = getattr(config, "_raw_config", {})   # D-06: defensive getattr
    for name, message in _REMOVED_CONFIG_VALUES.items():
        if name in raw:
            logger.warning(message)             # D-08: no type=/subtype=

def setup(app: Sphinx) -> Dict[str, Any]:
    ...
    app.connect("config-inited", _warn_removed_config_values)   # NEW, first ever
    ...
```
`logger` itself is not yet imported in `__init__.py` today (confirmed: `typsphinx/__init__.py`'s
full 70-line body has no `sphinx.util.logging` import) — the pattern to copy for THAT is
`typsphinx/builder.py:18,30`:
```python
from sphinx.util import logging
logger = logging.getLogger(__name__)
```

---

### `pyproject.toml` — package-data glob widening (D-12)

**Analog:** `pyproject.toml:72-73` (itself)
```toml
[tool.setuptools.package-data]
"typsphinx" = ["templates/*.typ"]
```
Widen to `"typsphinx" = ["templates/**/*"]` (D-12) — read the file directly before editing, as
line numbers may drift from an earlier phase's touch.

---

### `.github/workflows/ci.yml` — wheel-content assertion step (D-13)

**Analog:** `.github/workflows/ci.yml:127-151` (`build` job, already runs `uv build` → `dist/` →
`twine check dist/*`) — add a NEW step after the `uv build` step that opens the built `.whl`
(e.g. via `python -m zipfile -l dist/*.whl` or `unzip -l`) and asserts
`typsphinx/templates/README.md` is present in the listing. No existing step in this job opens a
wheel's contents today — this is a genuinely new step, not a modification of `twine check`.

---

## Shared Patterns

### Write-time accumulator → finish-time consumer

**Source:** `typsphinx/builder.py:231` (`self.images` init) + `:1296-1332`
(`copy_image_files()` consumer) + the (currently scattered) producer side that appends to
`self.images` during `write()`.
**Apply to:** `self._used_template_keys: set[str]` — init in `init()`, append in
`_write_typst_files()`'s existing wrapper loop, consume once in `finish()`. This is ROADMAP
constraint #4's explicitly named pattern.

### Accumulate-then-raise-once for a build-stopping error naming an offending docname/key

**Source:** `typsphinx/builder.py:517-628` (`_validate_output_path_collisions()`'s `_claim()` +
final `raise ExtensionError(...)`) and `typsphinx/template_registry.py:302-441` (CONF-16/CONF-17's
`failures: list[str]` accumulation, single `raise ExtensionError(f"typst_document_templates: {len(failures)} invalid definition(s): {summary}")` at the end).
**Apply to:** OUT-07's `_template/`-prefix reservation error, and D-05's fatal-template-copy
`ExtensionError`.

### Per-file copy with mixed fatal/non-fatal severity

**Source:** `typsphinx/builder.py:1408-1429` (`_copy_template_directory()`'s existing
`try/except Exception → logger.warning`-and-continue, per file).
**Apply to:** D-05's split — keep this shape verbatim for every bundle file EXCEPT the resolved
template file itself, which instead raises `ExtensionError` on failure.

### `_collision_key()` as the single normalization primitive

**Source:** `typsphinx/builder.py:437-515`.
**Apply to:** OUT-07's `_template/`-prefix check and any other new path-comparison logic this
phase adds — do not introduce a second normalization function (RESEARCH.md's Anti-Patterns
section explicitly warns against reusing `_escapes_outdir()`/`_is_drive_qualified()` for this, and
against a second casefold primitive).

### GATE-01 real-compile fixture + test scaffolding (the canonical instance)

**Source:** `tests/test_typst_lang_gate.py:90-231` (canonical/cleanest instance in this codebase —
918 lines, 8 fixtures, consistent shape throughout).

```python
# Module-level constants (lines 90-98)
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "typst_lang_gate"
JA_DEFAULT_FIXTURE_DIR = FIXTURES_DIR / "ja_default"
# ... one constant per fixture subdirectory

# subprocess-based sphinx-build runner (lines 101-126) -- run via
# `sys.executable -m sphinx`, NEVER `uv run sphinx-build` or a resolved
# `sphinx-build` binary, to sidestep the NixOS-sandbox PATH-shadowing hazard:
def _run_sphinx_build(source_dir: Path, build_dir: Path, builder: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", builder, str(source_dir), str(build_dir)],
        capture_output=True, text=True,
    )

# TYPST_AVAILABLE / PYPDF_AVAILABLE guards near top of file (lines ~79-84):
try:
    import typst  # noqa
    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

@pytest.mark.skipif(not TYPST_AVAILABLE, reason="typst-py is required for the GATE-01 ... gate")
class TestJapaneseSourceProof:
    @staticmethod
    @pytest.fixture(scope="class")
    def build(tmp_path_factory):
        build_dir = tmp_path_factory.mktemp("ja_default_build")
        result = _run_sphinx_build(JA_DEFAULT_FIXTURE_DIR, build_dir, "typstpdf")
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        typ_path = build_dir / "master.typ"
        assert typ_path.exists(), (
            f"master.typ (the wrapper) was not emitted:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        return {"result": result, "text": typ_path.read_text(encoding="utf-8"),
                 "pdf_path": build_dir / "master.pdf"}

    def test_lang_ja_emitted_in_show_rule_region(self, build):
        region = _show_rule_call_region(build["text"])
        assert 'lang: "ja",' in region
```
A second class in the same file (`TestGermanLinkageProof`, lines ~246-330) additionally opens the
compiled PDF with `pypdf.PdfReader(str(pdf_path))` and extracts text for a real-content proof —
that is the pattern to copy for OUT-05's user-template relative-asset fixture, which needs to
prove a `#image("logo.png")`-shaped relative reference actually resolved (i.e. the compile did not
merely succeed, but a specific asset reached the PDF).
**Apply to:** `tests/test_bundle_copy_layout_gate.py` (OUT-04) and
`tests/test_user_template_relative_asset_gate.py` (OUT-05) — both must be built as new fixture
directories under `tests/fixtures/`, one class per scenario, `build` fixture scoped to the class,
subprocess-based `sys.executable -m sphinx` invocation, `TYPST_AVAILABLE`/`PYPDF_AVAILABLE`
skipif guards.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `tests/test_bundle_copy_exclusion_manifest_gate.py` (BLD-06) | test | integration, manifest-diff | Searched `tests/test_collision_predicate_completeness_gate.py` and grepped broadly (`os.walk`, `listdir`, directory-manifest assertions) across `tests/` — no existing test asserts "the exact set of files present, no more no less" over a directory tree. Every existing filesystem-shaped test in this codebase asserts PRESENCE of specific expected files (e.g. `assert typ_path.exists()`), never a full manifest diff against an expected set. D-01's own text explicitly requires this fixture to build into a FRESH `tmp_path`-scoped directory (via `tmp_path_factory`, following the `test_typst_lang_gate.py` `build` fixture's own `tmp_path_factory.mktemp(...)` idiom) and then do something like `set(p.relative_to(bundle_root) for p in bundle_root.rglob("*") if p.is_file()) == EXPECTED_SET`. This is new test-authoring work, not a pattern-copy — say so explicitly per the agent's instructions rather than inventing a false precedent. |
| `typsphinx/__init__.py`'s `config-inited` handler registration | event handler | event-driven | No `app.connect(...)` call exists anywhere in this codebase today (confirmed via grep). Mapped above to the nearest structural precedent (the `setup(app)` function itself and its existing `app.add_config_value(...)` block), but this is a role-match only, not an exact analog. |

## Metadata

**Analog search scope:** `typsphinx/*.py` (all 6 production modules, full-file or targeted reads),
`typsphinx/templates/`, `pyproject.toml`, `.github/workflows/ci.yml`,
`tests/test_typst_lang_gate.py` (full targeted read of scaffolding), `tests/test_collision_predicate_completeness_gate.py` (grep pass), `tests/fixtures/typst_lang_gate/srcdir_shadow_lang/`
(listing).
**Files scanned:** 12 production files/sections read directly this session; 2 test files read or
grepped for scaffolding precedent; 1 fixture directory listed.
**Pattern extraction date:** 2026-08-15
