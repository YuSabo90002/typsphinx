<!-- refreshed: 2026-07-04 -->
# Architecture

**Analysis Date:** 2026-07-04

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                    Sphinx Entry Point                        │
│  typsphinx.__init__.setup() registers builders              │
└─────────────────────────────────────────────────────────────┘
         │
         ├─────────────────────┬─────────────────────┐
         ▼                     ▼                     ▼
┌──────────────────────┐ ┌──────────────────────┐ ┌─────────────┐
│   TypstBuilder       │ │ TypstPDFBuilder      │ │   Config    │
│  `builder.py`        │ │  (extends TypstB.)   │ │ `__init__.py`│
│  Orchestrator        │ │ PDF compilation      │ └─────────────┘
└─────────┬────────────┘ └──────────┬───────────┘
          │                         │
          └──────────┬──────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   TypstWriter        │
          │   `writer.py`        │
          │ Translation & Templ. │
          └──────┬───────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │  TypstTranslator       │
        │  `translator.py`       │
        │  Visitor pattern for   │
        │  docutils node->Typst  │
        └────────┬───────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │  TemplateEngine        │
        │  `template_engine.py`  │
        │  Template loading &    │
        │  parameter mapping     │
        └────────┬───────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │  PDF Compilation       │
        │  `pdf.py`              │
        │  typst-py wrapper      │
        └────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| TypstBuilder | Orchestrate document translation; manage build lifecycle; coordinate writer and asset copying | `typsphinx/builder.py` |
| TypstPDFBuilder | Extend TypstBuilder to compile .typ files to PDF using typst-py | `typsphinx/builder.py` |
| TypstWriter | Create translator instances; coordinate template application; output Typst markup | `typsphinx/writer.py` |
| TypstTranslator | Visit docutils nodes and generate Typst markup code; manage translation state | `typsphinx/translator.py` |
| TemplateEngine | Load default/custom templates; map Sphinx metadata to template parameters; render final output | `typsphinx/template_engine.py` |
| PDF Utilities | Compile Typst markup to PDF using typst-py package; error handling | `typsphinx/pdf.py` |

## Pattern Overview

**Overall:** Sphinx Builder Extension with Visitor Pattern Translation

**Key Characteristics:**
- Implements Sphinx Builder interface (`sphinx.builders.Builder`)
- Uses visitor pattern (docutils) to traverse and translate document trees
- Separates concerns: building, writing, translating, templating, compilation
- Supports two output formats: Typst markup (.typ) and PDF (.pdf)
- Handles both master documents (with template) and included documents (#include())

## Layers

**Sphinx Integration Layer:**
- Purpose: Register with Sphinx and hook into build process
- Location: `typsphinx/__init__.py`
- Contains: Extension setup, builder registration, config value registration
- Depends on: sphinx.application, sphinx.builders
- Used by: Sphinx application loader

**Build Orchestration Layer:**
- Purpose: Manage build lifecycle and coordinate document processing
- Location: `typsphinx/builder.py` (TypstBuilder, TypstPDFBuilder classes)
- Contains: Document discovery, writer setup, output directory management, asset copying (images, templates), PDF compilation orchestration
- Depends on: sphinx.builders.Builder, docutils.nodes
- Used by: Sphinx build system

**Document Translation Layer:**
- Purpose: Convert Sphinx docutils document trees to Typst markup
- Location: `typsphinx/writer.py`, `typsphinx/translator.py`
- Contains: 
  - Writer: orchestrates translation, applies templates, manages document/master distinction
  - Translator: stateful visitor that walks doctree and generates Typst code
- Depends on: docutils.nodes, sphinx.util.docutils.SphinxTranslator
- Used by: TypstBuilder during write phase

**Template & Configuration Layer:**
- Purpose: Handle template loading, parameter mapping, and document rendering
- Location: `typsphinx/template_engine.py`
- Contains: Template resolution (custom → search paths → default), Sphinx metadata mapping, Typst Universe package support, template rendering with parameters
- Depends on: pathlib, typing
- Used by: TypstWriter for document rendering

**PDF Compilation Layer:**
- Purpose: Compile generated Typst markup to PDF
- Location: `typsphinx/pdf.py`
- Contains: Typst availability checking, PDF compilation via typst-py, error handling and parsing
- Depends on: typst package, logging, tempfile
- Used by: TypstPDFBuilder.finish()

## Data Flow

### Primary Request Path: Document Translation

1. **Build Initiation** (`typsphinx/__init__.py:setup()`)
   - Sphinx loads extension via entry point
   - Registers TypstBuilder and TypstPDFBuilder
   - Registers configuration values (typst_documents, typst_template, typst_use_mitex, etc.)

2. **Build Phase: Preparation** (`typsphinx/builder.py:TypstBuilder.prepare_writing()`)
   - Creates TypstWriter instance
   - Writes template file (_template.typ) to output directory for master documents to import
   - Template file uses TemplateEngine to load and render template with metadata

3. **Build Phase: Document Writing** (`typsphinx/builder.py:TypstBuilder.write()`)
   - Iterates over all documents to build
   - For each document: calls `env.get_doctree()` to get document tree (preserving toctree nodes)
   - Applies post-transforms to doctree
   - Calls `write_doc()` for each document

4. **Single Document Translation** (`typsphinx/builder.py:TypstBuilder.write_doc()`)
   - Gets doctree for document
   - Calls `self.writer.translate()` to translate to Typst
   - Saves output to .typ file in output directory (preserving source directory structure)
   - Collects images via `post_process_images()`

5. **Translation to Typst Markup** (`typsphinx/writer.py:TypstWriter.translate()`)
   - Creates TypstTranslator with document and builder context
   - Calls `document.walkabout(visitor)` to visit all nodes
   - Translator generates body content as Typst markup
   - For included documents (not in typst_documents): wraps body in essential imports, returns
   - For master documents (in typst_documents):
     - Creates TemplateEngine with configuration
     - Gathers Sphinx metadata (project, author, release, copyright, custom elements)
     - Maps parameters using TemplateEngine.map_parameters()
     - Extracts toctree options
     - Renders with template: `template_engine.render(params, body, template_file="_template.typ")`

6. **Node Translation** (`typsphinx/translator.py:TypstTranslator` - visitor methods)
   - Maintains state: section_level, in_figure, in_table, in_paragraph, list_stack, etc.
   - Visits each docutils node type (title, paragraph, emphasis, code, table, etc.)
   - Generates Typst function calls and markup
   - All content wrapped in code mode block `#{...}` for unified syntax
   - Uses Typst functions: heading(), par(), text(), emph(), etc.

7. **Finish Phase: Asset Copying** (`typsphinx/builder.py:TypstBuilder.finish()`)
   - Copies image files from source to output (preserving paths)
   - Copies template assets (fonts, logos, etc.) if custom template used
   - Logs completion

### Secondary Path: PDF Generation (TypstPDFBuilder only)

1. **Override write_doc()** (`typsphinx/builder.py:TypstPDFBuilder.write_doc()`)
   - Generates .typ file (same as parent TypstBuilder)
   - Does not generate .pdf yet (deferred to finish())

2. **PDF Compilation** (`typsphinx/builder.py:TypstPDFBuilder.finish()`)
   - Calls parent `super().finish()` to copy assets
   - For each master document (typst_documents):
     - Reads .typ file from output directory
     - Calls `compile_typst_to_pdf()` with content and root_dir
     - Writes PDF to output directory with same docname
     - Logs success or error

3. **Typst Compilation** (`typsphinx/pdf.py:compile_typst_to_pdf()`)
   - Validates typst package is available
   - Writes Typst content to temporary file (in root_dir if provided)
   - Calls `typst.compile(temp_file, root=root_dir)` → returns PDF bytes
   - Cleans up temporary file
   - Handles and parses errors via `_parse_typst_error()`

**State Management:**
- Builder maintains current docname, outdir, srcdir
- Writer maintains builder reference and document state
- Translator maintains extensive state: section level, context flags (in_table, in_figure, in_paragraph, etc.), list nesting stack, buffered content
- TemplateEngine is stateless (holds config, loads templates on demand)

## Key Abstractions

**Visitor Pattern (Translator):**
- Purpose: Stateful traversal of docutils document trees
- Examples: `visit_paragraph()`, `visit_title()`, `visit_emphasis()`, etc.
- Pattern: Each node type has visit_* and depart_* methods managing state and output
- Located in: `typsphinx/translator.py` (extends `sphinx.util.docutils.SphinxTranslator`)

**Master vs. Included Documents:**
- Purpose: Different output for different document roles in typst_documents config
- Master documents: full template wrapping (headers, imports, layout)
- Included documents: minimal imports only (included via #include() in master)
- Implementation: `typsphinx/writer.py:TypstWriter._is_master_document()`
- Decision point: `typsphinx/writer.py:TypstWriter.translate()` branches based on master status

**Template Resolution Chain:**
- Purpose: Flexible template discovery with fallback to default
- Priority: explicit template_path → search_paths → default bundled template
- Implementation: `typsphinx/template_engine.py:TemplateEngine.load_template()`
- Supports: custom paths, directory search, Typst Universe packages (@preview/*)

**Typst Universe Package Support:**
- Purpose: Use external Typst templates from @preview namespace
- Config options: typst_package (package spec), typst_template_function (template function name), typst_package_imports (specific imports)
- When active: skips custom template file writing, relies on Typst package instead
- Location: checked throughout builder and writer

## Entry Points

**Sphinx Extension Entry Point:**
- Location: `typsphinx/__init__.py:setup(app: Sphinx) -> Dict[str, Any]`
- Triggers: When Sphinx loads extension (via entry point in pyproject.toml)
- Responsibilities: Register builders, register config values
- Returns: Metadata dict with version, parallel_read_safe, parallel_write_safe

**Build Entry Points:**
- TypstBuilder.init(): Initial builder setup
- TypstBuilder.get_outdated_docs(): Rebuild all documents (simple strategy)
- TypstBuilder.prepare_writing(): Setup before build
- TypstBuilder.write(): Main build loop
- TypstBuilder.finish(): Post-build asset copying

**Build Format Registration:**
- `sphinx.builders:typst` → TypstBuilder
- `sphinx.builders:typstpdf` → TypstPDFBuilder
- Invoked via `sphinx-build -b typst` or `sphinx-build -b typstpdf`

## Architectural Constraints

- **Sphinx Compatibility:** Must inherit from `sphinx.builders.Builder` and follow Sphinx build lifecycle
- **Threading:** `allow_parallel = True` on builders; stateless design where possible (state in builder/writer/translator instances)
- **Global State:** Minimal; each document gets new TypstTranslator instance with fresh state
- **Circular Imports:** Avoided via careful layering (builder imports writer, writer imports translator and template_engine, translator doesn't import builder)
- **Python Version:** Must support Python 3.9+ (declared in pyproject.toml)
- **Dependencies:** Core requires sphinx ≥5.0, docutils ≥0.18, typst ≥0.14.1; PDF requires typst-py
- **Template File Format:** Typst markup with parameter injection (not Jinja2 or Python templating)
- **Code Mode Design:** All translation output uses Typst code mode `#{...}` (no hybrid markup/code)

## Anti-Patterns

### State Mutation in Visitor During Traversal

**What happens:** Translator state (section_level, in_table, etc.) is modified during node visitation without proper cleanup

**Why it's wrong:** If visitor pattern traversal is interrupted or reordered, state can become inconsistent, leading to malformed output

**Do this instead:** Always pair visit_* and depart_* methods. Increment in visit_*, decrement in depart_. Use try-finally or context managers if cleanup is critical. `typsphinx/translator.py` implements this correctly (e.g., `visit_section` increments, `depart_section` decrements).

### Mixing Translation Logic with Template Rendering

**What happens:** Earlier code versions tried to apply templates during translation

**Why it's wrong:** Couples node translation to document role (master/included), makes testing harder, reduces reusability

**Do this instead:** Translate to plain Typst markup first, then apply template in Writer layer. `typsphinx/writer.py:TypstWriter.translate()` does this correctly—generates body content first, then wraps in template only for master documents.

### Hardcoded File Paths Without Preservation

**What happens:** Builder outputs flat directory structure, losing source directory nesting

**Why it's wrong:** Multi-level documentation (chapters/sections as subdirectories) produces confusing flat output

**Do this instead:** Preserve source directory structure in output. `typsphinx/builder.py:TypstBuilder.write_doc()` uses `path.join(self.outdir, docname + self.out_suffix)` where docname includes path (e.g., "chapter1/section1"), and calls `ensuredir()` to create nested directories.

## Error Handling

**Strategy:** Graceful degradation with logging; critical errors raise exceptions

**Patterns:**
- File not found (images, templates): Log warning, continue (don't break build)
- Template loading: Fallback to default template if custom not found
- Typst compilation: Catch exception, parse error details, raise TypstCompilationError with context
- Invalid nodes: Log debug message, skip or output placeholder

**Error Types:**
- `TypstCompilationError` (from pdf.py): Wraps typst-py exceptions with context
- Standard exceptions: TypeError, ValueError for config validation
- Sphinx warnings: Logged via sphinx.util.logging

## Cross-Cutting Concerns

**Logging:** Via `sphinx.util.logging.getLogger(__name__)` in each module; uses Sphinx's logger for consistency and control

**Validation:** Config values validated in setup() and builder init(); docutils nodes assumed valid (Sphinx guarantees)

**Image/Asset Handling:** Tracked during translation, copied in finish() phase; preserves relative paths

**Configuration:** Registered in setup(), accessed via builder.config; supports custom values (typst_documents, typst_template, typst_use_mitex, typst_elements, etc.)

---

*Architecture analysis: 2026-07-04*
