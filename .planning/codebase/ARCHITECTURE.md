<!-- refreshed: 2026-07-22 -->
# Architecture

**Analysis Date:** 2026-07-22

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│           Sphinx Application & Documentation                │
│    (reStructuredText files, Sphinx environment)              │
├──────────────────────────────────────────────────────────────┤
│  `docs/source/`, `examples/`, `tests/roots/`                │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│         Sphinx Builder / Writer Layer                        │
│  TypstBuilder (read-phase) / prepare_writing()              │
│  `typsphinx/builder.py` ← init, get_outdated_docs, write()  │
└────────────────┬───────────────────────────────────────────┬─┘
                 │                                           │
                 ▼                                           ▼
        ┌──────────────────┐                    ┌────────────────────┐
        │ TypstWriter      │                    │ TemplateEngine     │
        │ translate()      │                    │ (load template +   │
        │ ─────────────    │                    │  render)           │
        │ Master: apply    │                    └────────────────────┘
        │ template         │
        │ Included: add    │
        │ imports only     │
        └────────┬─────────┘
                 │
                 ▼
        ┌──────────────────────────┐
        │   TypstTranslator        │
        │   translate() method     │
        │   ─────────────────────  │
        │   visit_*/depart_*       │
        │   methods (~140 methods) │
        │   `typsphinx/translator  │
        │   .py`                   │
        └────────┬─────────────────┘
                 │
                 ▼
        ┌──────────────────────────┐
        │   Body Typst Markup      │
        │   (code-mode wrapped)    │
        └────────┬─────────────────┘
                 │
                 ▼
        ┌──────────────────────────┐
        │   Output Rendering       │
        │   (_template.typ +       │
        │    body content)         │
        └────────┬─────────────────┘
                 │
                 ▼
        ┌──────────────────────────┐
        │   .typ files written     │
        │   to outdir/             │
        │   `typsphinx/builder.py` │
        │   write_doc()            │
        └────────┬─────────────────┘
                 │
                 ▼
   ┌─────────────────────────────────┐
   │  PDF Compilation (TypstPDFBuilder)
   │  typst.compile() → PDF bytes    │
   │  `typsphinx/pdf.py`             │
   └─────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| TypstBuilder | Orchestrates write loop, image copying, template file prep, doc tracking | `typsphinx/builder.py` |
| TypstPDFBuilder | Extends TypstBuilder; adds PDF compilation in finish() | `typsphinx/builder.py` |
| TypstWriter | Controls translation flow; routes master vs included documents; applies template | `typsphinx/writer.py` |
| TypstTranslator | Core node-to-Typst conversion (~140 visitor methods); state management | `typsphinx/translator.py` |
| TemplateEngine | Template loading, parameter mapping, Sphinx metadata injection, final rendering | `typsphinx/template_engine.py` |
| PDF Compiler | Wrapper over typst-py; file-based compilation with error handling | `typsphinx/pdf.py` |

## Pattern Overview

**Overall:** Sphinx builder → writer → translator layering with single-pass visitor traversal. The pipeline is **document-centric**: each document flows independently through writer → translator → output, with shared template and configuration applied per-document-type (master vs. included).

**Key Characteristics:**
- **Visitor pattern** on docutils/Sphinx AST nodes (docutils standard SphinxTranslator base)
- **Code-mode block wrapping** for continuous Typst code generation (all body output wrapped in `#{...}`)
- **Master vs. included document routing** (defined by `typst_documents` config):
  - Master documents: receive full template via TemplateEngine, produce complete `.typ`
  - Included documents: receive minimal imports only (no template), meant for `#include()` in master
- **Toctree preservation** (builder overrides default Sphinx expansion): raw toctree nodes converted to Typst `#include()` calls
- **Label namespacing by docname** (not output filename): enables cross-document references to work across renamed masters
- **Single shared template file** (`_template.typ`) written at outdir root, imported by all master documents with depth-relative paths

## Layers

**Registration & Setup Layer:**
- Purpose: Register builders and config values with Sphinx
- Location: `typsphinx/__init__.py`
- Contains: Entry point, `setup()` function, builder registration, config value declarations
- Depends on: Sphinx API
- Used by: Sphinx framework (automatic on extension load)

**Builder & Coordination Layer:**
- Purpose: Orchestrate the write loop, manage document lifecycle, handle images and template prep
- Location: `typsphinx/builder.py`
- Contains: `TypstBuilder.write()`, `prepare_writing()`, `write_doc()`, `_write_template_file()`, `_compute_master_included_docnames()`, image post-processing
- Depends on: TypstWriter, Sphinx Builder base, toctree graph
- Used by: Sphinx write phase

**Translation Routing Layer:**
- Purpose: Route documents through translation pipeline; decide template application; manage imports
- Location: `typsphinx/writer.py`
- Contains: `TypstWriter.translate()`, `_is_master_document()`, `_compute_template_import_path()`, master vs. included branching
- Depends on: TypstTranslator, TemplateEngine
- Used by: TypstBuilder.write_doc()

**Core Translation Layer:**
- Purpose: Convert docutils nodes to Typst markup line-by-line
- Location: `typsphinx/translator.py`
- Contains: `TypstTranslator` with ~140 `visit_*`/`depart_*` methods, string building, state tracking
- Depends on: docutils/Sphinx node classes, escape utilities
- Used by: TypstWriter.translate()

**Template & Rendering Layer:**
- Purpose: Load templates, map Sphinx metadata to Typst parameters, render final output
- Location: `typsphinx/template_engine.py`
- Contains: `TemplateEngine.render()`, `map_parameters()`, `extract_toctree_options()`, template file search
- Depends on: Template files (default at `typsphinx/templates/base.typ`)
- Used by: TypstWriter for master documents

**PDF Compilation Layer:**
- Purpose: Wrap typst-py compiler; handle errors and version checking
- Location: `typsphinx/pdf.py`
- Contains: `compile_typst_file_to_pdf()`, `TypstCompilationError`, `check_typst_available()`, error parsing
- Depends on: typst Python package
- Used by: TypstPDFBuilder.finish()

## Data Flow

### Primary Request Path (Master Document)

1. **Read phase** — Sphinx parses `.rst` files into doctree, builds toctree graph (`env.toctree_includes`)
2. **Write phase preparation** (`builder.py:write()`, line ~358–372):
   - `prepare_writing()` creates TypstWriter instance
   - `_write_template_file()` writes shared `_template.typ` to outdir root (once per build)
   - `_compute_master_included_docnames()` walks toctree graph, populates `master_included_docnames` set for cross-ref degradation
3. **Per-document write** (`builder.py:write_doc()`, called for each docname):
   - `env.get_doctree(docname)` retrieves document AST (preserves toctree nodes, not expanded)
   - Passed to `writer.write(doctree)` (docutils Writer API)
4. **Translation routing** (`writer.py:translate()`):
   - Creates `TypstTranslator` instance, walks doctree node-by-node
   - Translator accumulates body content in `self.body` list
   - Returns `body = visitor.astext()` (joined Typst markup)
   - **Master document branch**: passes body + config to `TemplateEngine.render()` with `template_file` reference
   - Receives rendered output: template imports + parameters + body, output to `.typ` file
5. **PDF compilation** (TypstPDFBuilder only, `builder.py:finish()`):
   - For each master in `typst_documents`, calls `compile_typst_file_to_pdf(outdir/stem.typ)`
   - Writes PDF bytes to `outdir/stem.pdf`

### Included Document Request Path

1. **Same read phase and write setup as master**
2. **Per-document write** (identical to master through step 3)
3. **Translation routing** (`writer.py:translate()`):
   - **Included document branch**: adds minimal `@preview` imports (codly, codly-languages, mitex, gentle-clues)
   - No template application; output is body content only + imports
   - Output written to `.typ` file (meant to be `#include()`d by master)
4. **No direct PDF compilation** (included documents are inlined via `#include()` into master's compiled PDF)

### Secondary Flow: Toctree Conversion to #include()

- **Entry point**: `translator.py:visit_toctree()` (line ~3345)
- **Decision**: check document type via `builder.master_included_docnames` set
  - If docname not in set (orphan or excluded): skip (no `#include()` emitted)
  - Else: iterate child docnames, emit `#include("relpath/to/child.typ")` calls
- **Path computation**: uses `_resolve_xref_docname()` (translator method) to compute relative path from current master to child doc's output file
- **Deduplication**: builder's `_included_docnames` set tracks which docs have been included; a doc is `#include()`d at most once even if reachable via multiple toctree paths (diamond problem)

### Tertiary Flow: Cross-Document Reference Degradation

- **Entry point**: `translator.py:visit_pending_xref()` (line ~2885)
- **Decision**: if target docname not in `builder.master_included_docnames`, degrade to plain text (not a Typst link) to avoid "label does not exist" compile error
- **Reason**: Typst's `link(<label>, ...)` fails if label is not emitted anywhere in the compiled document; orphan/excluded docs are never `#include()`d, so their labels never appear

## Key Abstractions

**Document Tree Visitor (TypstTranslator):**
- Purpose: Encapsulates node-type-specific conversion logic
- Examples: `visit_section()`, `visit_paragraph()`, `visit_table()`, `visit_reference()`
- Pattern: Docutils visitor pattern; each node type gets `visit_*` (enter) and `depart_*` (exit) methods; state tracked in instance variables

**Code-Mode Block (Typst `#{...}`):**
- Purpose: Typst's only way to emit multiple statements/expressions in a sequence (adjacent juxtaposition in markup mode is not valid outside `code()` blocks)
- Example: body output starts with `#{` and ends with `}`, with all statements inside (paragraphs, lists, headings, etc. as Typst calls)
- Implementation: `writer.py:translate()` wraps body in `#{...}` if not already wrapped; translator emits bare function calls inside

**State Management (Translator Instance Variables):**
- Purpose: Track context when walking deep/nested document structures (lists, tables, figures, etc.)
- Examples:
  - `section_level`: heading depth
  - `in_list_item`, `_list_item_stack`: track nesting for proper para separation
  - `in_table`, `in_thead`: table context
  - `figure_content`, `figure_caption`: buffer content during figure traversal
- Pattern: Push/pop on visit/depart; initialized in `__init__`, reset/modified per-context

**Label Namespace (Docname Prefix):**
- Purpose: Ensure `<label>` identifiers are unique across the whole compiled document (Typst requires each label to be unique)
- Implementation: `translator.py:_namespace_label(label)` prepends docname to any generated anchor/label
- Example: anchor `"sec-intro"` in doc `"chapter1"` becomes label `"chapter1:sec-intro"`

**Template Parameter Mapping:**
- Purpose: Allow users to customize which Sphinx config values map to which template function parameters
- Example: Sphinx's `project` → template's `title`, `author` → `authors`, `release` → `date` (default mapping)
- Implementation: `template_engine.py:DEFAULT_PARAMETER_MAPPING`, user override via `typst_template_mapping` config

## Entry Points

**Sphinx Extension Entry:**
- Location: `typsphinx/__init__.py:setup(app)`
- Triggers: Sphinx calls on extension load (when `typsphinx` listed in `conf.py:extensions`)
- Responsibilities: Register builders, config values, set metadata

**Builder Entry:**
- Location: `typsphinx/builder.py:TypstBuilder.write()`
- Triggers: Sphinx calls during write phase (`sphinx-build -b typst`)
- Responsibilities: Coordinate all document writing

**Writer Entry:**
- Location: `typsphinx/writer.py:TypstWriter.translate()`
- Triggers: Builder calls for each document
- Responsibilities: Route translation and template application

**Translator Entry:**
- Location: `typsphinx/translator.py:TypstTranslator.__init__()` and `visit_*()` methods
- Triggers: Writer instantiates and calls `document.walkabout(translator)`
- Responsibilities: Convert nodes to Typst markup

## Architectural Constraints

- **Threading:** Sphinx allows parallel writes (`allow_parallel = True`), but each document is translated independently in its own process; no shared state between workers
- **Global state:** Module-level config values stored in Sphinx app; no module-level singletons in translator or writer (state is instance-based)
- **Circular imports:** None detected; builder imports writer, writer imports translator, clear dependency graph
- **Toctree expansion:** Builder uses `env.get_doctree()` (preserves toctree nodes), NOT `env.get_and_resolve_doctree()` (expands toctree to paragraphs) — a deliberate override to capture raw toctree structure for `#include()` emission
- **Template import path computation:** Uses depth-based relative path (`../` × depth + `_template.typ`) to avoid directory-name collisions with synthetic sentinel (`_template`); see `writer.py:_compute_template_import_path()` for rationale
- **Label namespace**: All cross-document labels are prefixed with source docname; Typst compile fails if a label is referenced but not defined — degradation of cross-refs to orphan docs prevents this failure

## Anti-Patterns

### Expanding Toctree in Builder

**What happens:** Early implementation used `env.get_and_resolve_doctree()`, which expands toctree nodes into compact paragraph with link lists.

**Why it's wrong:** Typst needs raw toctree structure to emit `#include()` calls for document assembly; expanded form loses that information, making multi-document builds impossible.

**Do this instead:** Use `env.get_doctree()` to preserve toctree nodes (`builder.py:write()`, line ~379).

### Unconditional Shared Template Import in Package-Only Route

**What happens:** Previous implementation always wrote and imported `_template.typ`, even when no custom template was configured (package-only route).

**Why it's wrong:** When only `typst_package` is set (no custom `typst_template`), the builder must NOT create `_template.typ` (the package itself IS the template); unconditional import tried to load a file that was never written, causing "file not found" compile error.

**Do this instead:** Use single routing decision `resolve_package_for_engine()` in exactly one place; builder and writer must agree (`template_engine.py`, `writer.py:translate()`, `builder.py:_write_template_file()`).

### Relativizing Master Import Path Against Sentinel Docname

**What happens:** Earlier implementation computed template import path by using translator's "relativize docname against docname" helper, passing synthetic sentinel `"_template"`.

**Why it's wrong:** When the master's own directory is literally named `_template` (e.g., master docname is `"_template/index"`), string equality collides and the helper returns a malformed path.

**Do this instead:** Compute depth-based relative path directly from nesting depth of master's docname (`writer.py:_compute_template_import_path()`, line ~106).

### Unconditional Cross-Reference Link Emission

**What happens:** Early implementation emitted Typst `link(<label>, ...)` for every cross-reference, including to orphan/excluded documents.

**Why it's wrong:** Typst's `link()` function requires the label to exist in the compiled document; orphan documents are never `#include()`d, so their labels never appear, causing "label does not exist" compile fatal.

**Do this instead:** Degrade cross-ref to plain text if target docname is not in `builder.master_included_docnames` (`translator.py:visit_pending_xref()`, line ~2885).

## Error Handling

**Strategy:** Catch exceptions at three layers:
1. **Builder level** (`builder.py`): Image processing, file I/O errors logged; build continues
2. **Translator level** (`translator.py`): Unsupported node types logged as warnings; emit placeholder text instead of crashing
3. **PDF compiler level** (`pdf.py`): Typst compilation errors caught, wrapped in `TypstCompilationError` with source location and original error attached

**Patterns:**
- Unsupported nodes: log warning, emit `[unsupported node type]` or skip silently (depends on node criticality)
- Missing config values: graceful defaults (empty string, empty dict, etc.)
- Template/image file not found: log warning, fall back to default or skip

## Cross-Cutting Concerns

**Logging:** Sphinx logger (`sphinx.util.logging.getLogger(__name__)`) used throughout; enables integration with Sphinx's logging UI and file output.

**Validation:** Config values validated in `__init__.py:setup()` (type hints via `add_config_value()` second-to-last parameter); builder validates `typst_documents` format (must be tuple with at least 2 elements).

**Authentication:** None (no external API auth needed; Typst Universe packages are public).

---

*Architecture analysis: 2026-07-22*
