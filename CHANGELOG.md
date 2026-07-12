# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.0] - 2026-07-13

Real-world robustness: compile a large real-world documentation set (Sphinx's
own `doc/` tree) through the `typstpdf` builder with no fatal Typst errors, and
render the most-frequent previously-dropped docutils/Sphinx nodes correctly.
Driven by Issue #114. Zero new runtime dependencies — all work is in
`typsphinx/translator.py`; the bundled `@preview` version-sync surface is
untouched.

### Fixed

- **Issue #114 — fatal figure/image bugs**
  - `.. figure::`/image `:width:`/`:height:` in `px` (or other CSS length units)
    now converts to valid Typst — `px`→`pt` numeric conversion (1px = 0.75pt),
    `%`/`em`/`pt`/`cm`/`mm`/`in` pass through, unrecognized units are
    warned-and-dropped instead of emitted verbatim (FIG-01)
  - `.. figure::`/standalone image with a `:target:` link now emits valid
    `#figure(link(...)[#image(...)], caption: [...])` — the caption reaches the
    `caption:` argument via a buffer-swap and no longer leaks as a stray
    juxtaposed `text(...)` call (FIG-02)
  - Fixed additional latent fatals surfaced by the real-compile gate: labels
    attached to code-mode statements, a dangling `:term:` glossary anchor, and a
    footnote-buffer-swap paragraph-state clobber

### Added

- **High-frequency previously-dropped node handlers** (all with real-compile
  acceptance fixtures)
  - `refid` same-document cross-references (`:ref:` section anchors, `:term:`
    glossary links) render as working links instead of degrading to plain text
    (XREF-01)
  - `versionadded`/`versionchanged`/`deprecated`/`versionremoved` render as an
    unboxed italic Sphinx-worded label, not a callout box (VER-01)
  - Autodoc signature sub-parts: `desc_returns`, `desc_signature_line`,
    `desc_optional`, `desc_inline` (DESC-01…04)
  - `footnote`/`footnote_reference` via Typst-native `footnote[...]` using a
    document-order doctree pre-pass — first cite defines, repeat cites reuse by
    label (FN-01)
  - `transition` → horizontal rule, `.. topic::` → titled aside, `line`/
    `line_block` → verbatim `linebreak()`, `.. glossary::` → definition list,
    `.. tabularcolumns::` safely skipped, `:abbr:` → "term (expansion)"
    (BLK-01…06)
- **Graceful degradation** — `graphviz` and `inheritance_diagram` render a
  visible placeholder block + exactly one warning, with no raw source leaking
  (DEG-01/DEG-02)
- **Validation gates**
  - Standing real-compile acceptance-fixture pattern
    (`sphinx-build → typst.compile() → pypdf`) extended by every node-handler
    group (GATE-01)
  - Full-corpus gate: Sphinx's own `doc/` tree compiles end-to-end through
    `-b typstpdf` with no fatal `TypstCompilationError` (~14.4 MiB PDF,
    0 errors); residual `unknown_visit` warnings catalogued and the empty-URL
    reduction measured before/after (GATE-02)

## [0.5.0] - 2026-07-11

### Changed

- **Forward-Ecosystem Port**
  - Sphinx re-pinned to the `>=9.1,<10` line, `docutils` to `>=0.21,<0.23`, and `typst` to
    the `>=0.15.0,<0.16` line
  - Python floor raised to 3.12-3.13 (3.10 and 3.11 dropped from the support matrix)
  - Bundled `@preview` packages bumped in lockstep: `mitex` (`0.2.4`→`0.2.7`, the fix for
    `unknown variable: kai` under typst 0.15), `gentle-clues` (`1.2.0`→`1.3.1`), and
    `codly-languages` (`0.1.1`→`0.1.10`); `codly` confirmed to already compile cleanly at `1.3.0`

### Fixed

- **Admonition Rendering** (Phase 8.1)
  - Fixed a translator markup/code-mode mismatch that caused `.. note::`-style admonitions
    to render literal, unevaluated Typst source instead of typeset prose
  - Added coverage for previously-missing admonition types (`hint`, `error`, `danger`,
    `attention`, generic `.. admonition::`)

### Added

- **CI Durability Guardrails**
  - Added a `typst compile` smoke test that exercises all bundled `@preview` packages via
    real function calls, catching `kai`-class breaks before release
  - Updated `drift.yml` and the Dependabot dependency group to the new major-version ceilings

## [0.4.3] - 2025-11-01

### Changed

- **Project Status & Authorship**
  - Updated development status to "Production/Stable" in PyPI classifiers
  - Updated author information across all project files
  - Removed "Beta Release" designation from PyPI installation instructions

### Added

- **Template Asset Support** ([#75](https://github.com/YuSabo90002/typsphinx/issues/75))
  - Automatic copying of template assets (fonts, images, logos) to output directory
  - Three operation modes:
    - Default: Automatically copy entire template directory
    - Explicit: Specify assets with `typst_template_assets` list (supports glob patterns)
    - Disabled: Empty list `[]` prevents automatic copying
  - New configuration value: `typst_template_assets`
  - Only applies to local templates (`typst_template`), not Typst Universe packages
  - Added 8 comprehensive test cases for all scenarios
  - Updated documentation with usage examples

### Fixed

- **Empty URL Link Handling for Typst 0.14.1+ Compatibility** ([#77](https://github.com/YuSabo90002/typsphinx/issues/77))
  - Fixed empty URL references causing Typst 0.14.1 compilation errors
  - References with empty `refuri` attributes now rendered as plain text instead of invalid `link("", ...)`
  - Added warning messages for broken references to aid debugging
  - Updated Typst dependency to `>=0.14.1` for stricter URL validation support
  - Added comprehensive test coverage for empty URL handling scenarios
  - Prevents "URL must not be empty" errors in CI/CD pipelines

## [0.4.2] - 2025-10-29

### Fixed

- **Empty Table Cells Rendering** ([#68](https://github.com/YuSabo90002/typsphinx/issues/68), [#70](https://github.com/YuSabo90002/typsphinx/pull/70))
  - Fixed empty table cells causing Typst compilation errors
  - All table cells (normal and spanning) now wrapped in content blocks `{}`
  - Empty cells output as `{}` instead of bare commas
  - Prevents "unexpected comma" syntax errors in Typst
  - Added 5 comprehensive test cases for empty cell scenarios

- **Image Relative Paths in Nested Documents** ([#69](https://github.com/YuSabo90002/typsphinx/issues/69), [#72](https://github.com/YuSabo90002/typsphinx/pull/72))
  - Fixed image paths in nested documents failing to resolve during Typst compilation
  - Implemented `_compute_relative_image_path()` method (mirrors Issue #5 toctree fix)
  - Image URIs now adjusted based on output file location
  - Supports all path patterns: root, nested, deep nested, same directory, subdirectory, cross-directory
  - Added 6 comprehensive test cases for image path adjustment
  - Backward compatible: root document images unchanged

## [0.4.1] - 2025-10-26

### Fixed

- **Table Cell Unified Code Mode Compliance** ([#65](https://github.com/YuSabo90002/typsphinx/pull/65))
  - Fixed `table.cell()` argument order to match Typst signature (content as first positional argument)
  - Removed unnecessary markup mode `[...]` wrapping from table cells
  - Table cells now pass content type directly: `table.cell(content, colspan: 2)`
  - Improved consistency with Unified Code Mode guideline across all table elements

## [0.4.0] - 2025-10-26

### Fixed

- **Document Wrapper Preservation** ([#61](https://github.com/YuSabo90002/typsphinx/issues/61))
  - Fixed `#{...}` wrapper being lost in nested toctree structures
  - Implemented stream-based rendering to replace body swapping anti-pattern
  - Document wrapper now preserved throughout nested structures

- **Nested Lists Syntax** ([#62](https://github.com/YuSabo90002/typsphinx/issues/62))
  - Fixed nested lists generating invalid Typst syntax (`strong(...)list(...)`)
  - List items now use content blocks with newline separators
  - Proper separation between elements in list items

### Changed

- **Stream-Based Rendering Architecture**
  - Replaced body swapping with direct appending to `self.body`
  - State management using flags instead of buffer manipulation
  - Improved maintainability and predictability

- **Content Block Architecture**
  - Changed `strong()` and `emph()` to use content blocks: `strong({...})`, `emph({...})`
  - List items wrapped in `{...}` blocks with newline separators
  - Enables proper nesting: `strong({text("bold")})\nlist({...})`

- **Unified Code Mode Compliance**
  - Updated `link()` format from `link(url)[content]` to `link(url, content)`
  - Removed `#` prefixes from functions in code mode (table, admonitions)
  - Added `#` prefixes inside markup mode blocks `[...]` for label attachment
  - API signatures properly formatted: `text("(") + text("param") + text(")")`

### Changed (from v0.3.0)

- **BREAKING: Unified Code Mode Architecture** ([#4](https://github.com/YuSabo90002/typsphinx/issues/4))
  - Entire document now wrapped in `#{...}` code block for consistent function syntax
  - All Typst elements use bare function names without `#` prefix inside code block
  - All text wrapped in `text()` function with proper string escaping
  - All paragraphs wrapped in `par()` function to mark boundaries
  - Lists use function calls: `list(...)`, `enum(...)`, `terms(...)`
  - Inline code uses `raw()` with string escaping for `+` operator compatibility
  - Math functions use backtick raw strings: `mi(\`...\`)`, `mitex(\`...\`)`
  - Toctree uses `{...}` scope block for `set` rule isolation
  - Fixes underscores in text being interpreted as subscript markup
  - Fixes special characters requiring escaping in content mode
  - Generated `.typ` files compile cleanly without syntax errors
  - PDF output remains identical to previous versions
  - **Migration**: Existing projects will need to regenerate `.typ` files

- **Migrate CI to Tox**
  - GitHub Actions workflows now use tox commands for consistency
  - Added `docs-html`, `docs-pdf`, and `docs` tox environments
  - Simplified CI configuration with single source of truth in `tox.ini`
  - Improved local/CI consistency - same commands work in both environments
  - Updated test, lint, type-check, and coverage jobs to use tox
  - Documentation builds now reproducible locally with `tox -e docs-html` or `tox -e docs-pdf`
  - Fixed paths in existing tox environments (sphinxcontrib/ → typsphinx/)

### Added

- **Documentation Site with GitHub Pages** ([#36](https://github.com/YuSabo90002/typsphinx/issues/36))
  - Comprehensive documentation site hosted on GitHub Pages at https://yusabo90002.github.io/typsphinx/
  - Complete user guide covering installation, quickstart, configuration, builders, and templates
  - Extensive examples section with basic and advanced use cases
  - API reference with autodoc integration
  - Contributing guide with development workflow
  - Automated documentation deployment via GitHub Actions
  - HTML documentation built with Sphinx and Furo theme
  - PDF documentation generated using typsphinx itself (dogfooding)
  - PDF artifacts uploaded to GitHub Releases for tagged versions
  - Documentation badge added to README
  - 13 comprehensive documentation pages created

- **Typst Universe Template Support** ([#13](https://github.com/YuSabo90002/typsphinx/issues/13))
  - Full support for Typst Universe templates (charged-ieee, modern-cv, etc.)
  - `typst_template_function` now accepts dictionary format: `{"name": "ieee", "params": {...}}`
  - New `typst_authors` configuration for detailed author information (department, organization, email)
  - Template-specific parameters can be configured directly in `conf.py`
  - Python variable references work naturally in configuration (no special syntax needed)
  - Backward compatibility maintained for all existing configurations
  - Added comprehensive charged-ieee examples demonstrating two approaches:
    - Approach 1: Configuration-based (recommended, simple)
    - Approach 2: Custom template with Typst code (flexible)
  - Added 8 new test cases (4 for dict format, 4 for author details)
  - All 365 tests passing with full backward compatibility

- **Image File Copying Support** ([#38](https://github.com/YuSabo90002/typsphinx/issues/38))
  - Image files referenced in documents are now automatically copied to the output directory
  - Preserves directory structure when copying images
  - Enables successful PDF builds for documents containing images
  - Implemented `post_process_images()` and `copy_image_files()` methods in TypstBuilder
  - Images are copied before PDF compilation in TypstPDFBuilder
  - Added 9 comprehensive test cases covering various scenarios
  - No configuration required - images are copied automatically

- **Table Header Wrapping Support** ([#40](https://github.com/YuSabo90002/typsphinx/issues/40))
  - Table headers now wrapped in `table.header()` for proper Typst rendering
  - Enables automatic header repetition on multi-page tables
  - Provides accessibility metadata for screen readers and assistive technologies
  - Supports multi-row headers (`:header-rows: N` with N > 1)
  - Maintains backward compatibility for tables without headers
  - Added `in_thead` state flag to track header section in translator
  - Modified cell storage to include `is_header` flag
  - Updated `depart_table()` to generate `table.header()` wrapper for header cells
  - Complies with Typst documentation recommendations for table accessibility
  - Added 4 comprehensive test cases covering various header scenarios

- **Table Cell Spanning Support** ([#39](https://github.com/YuSabo90002/typsphinx/issues/39))
  - Added support for horizontal cell spanning (colspan) via `morecols` attribute
  - Added support for vertical cell spanning (rowspan) via `morerows` attribute
  - Cells with spanning now generate `table.cell(colspan: N, rowspan: M)` syntax
  - Supports combined horizontal and vertical spanning in same cell
  - Works correctly with header cells inside `table.header()`
  - Maintains backward compatibility for tables without cell spanning
  - Created `_format_table_cell()` helper method for consistent cell formatting
  - Reads `morecols`/`morerows` attributes in `visit_entry()`
  - Extended cell storage to include `colspan` and `rowspan` fields
  - Added 5 comprehensive test cases covering various spanning scenarios

## [0.3.0] - 2025-10-23

### Changed (Breaking)
- **Package Rename**: `sphinxcontrib-typst` → `typsphinx`
  - Changed to a simpler and more unique name
  - Reflects the nature of this package as a builder
  - PyPI package name: `typsphinx`
  - Python import: `import typsphinx`
  - Sphinx extension name: `extensions = ['typsphinx']`
  - Package structure: `sphinxcontrib/typst/` → `typsphinx/`
  - **Migration steps**:
    1. `pip uninstall sphinxcontrib-typst`
    2. `pip install typsphinx`
    3. Update `conf.py`: `extensions = ['sphinxcontrib.typst']` → `extensions = ['typsphinx']`

### Rationale
- `sphinxcontrib-*` namespace is traditionally for extensions that add directives or roles
- This package is primarily a builder (Sphinx→Typst conversion) and needs a more appropriate name
- Current low user base makes this the optimal timing for the change
- Unique and memorable name that represents the integration of Typst and Sphinx

## [0.2.2] - 2025-10-23

### Added
- **Additional Code Block Options Support** ([#31](https://github.com/YuSabo90002/typsphinx/issues/31))
  - Added support for `:lineno-start:` option to specify starting line number for code blocks
  - Added support for `:dedent:` option (handled automatically by Sphinx during parsing)
  - `:lineno-start:` works with codly's `start` parameter to display custom line numbers
  - Both options work correctly in combination with existing options (`:linenos:`, `:emphasize-lines:`, etc.)
  - Sphinx now supports 6 out of 8 standard code-block directive options (75%)
  - Added 7 comprehensive test cases covering various scenarios

- **Raw Directive Support** ([#25](https://github.com/YuSabo90002/typsphinx/issues/25))
  - Added support for docutils `raw` directive (`.. raw:: typst`)
  - Typst-specific content (`format='typst'`) is passed through to output
  - Other formats (html, latex, etc.) are skipped and logged
  - Format name matching is case-insensitive
  - Implemented `visit_raw()` and `depart_raw()` methods in TypstTranslator
  - Added 6 comprehensive test cases covering various scenarios

### Fixed
- **Code Block Directive Options Support** ([#20](https://github.com/YuSabo90002/typsphinx/issues/20))
  - Fixed `:linenos:` option being ignored - now properly controls line number display in code blocks
  - Fixed `:caption:` and `:name:` options causing "unknown node type: container" warnings
  - Code blocks with `:caption:` now wrapped in `#figure()` with proper caption
  - Code blocks with `:name:` now generate Typst labels for cross-referencing
  - Added `visit_container()` and `depart_container()` methods to handle Sphinx literal-block-wrapper containers
  - Extended `visit_literal_block()` and `depart_literal_block()` to support caption and label generation
  - Modified `visit_caption()` to skip caption text output for captioned code blocks (prevents duplication)
  - Line numbers now disabled by default when `:linenos:` is not specified (via `#codly(number-format: none)`)
  - All four options (`:linenos:`, `:caption:`, `:name:`, `:emphasize-lines:`) now work correctly together
  - Added comprehensive test coverage for all code block option combinations

- **PDF Builder codly Import Missing** ([#28](https://github.com/YuSabo90002/typsphinx/issues/28))
  - Fixed `typstpdf` builder failing with "unknown variable: codly" error
  - Added codly package imports to document-level essential imports in `template_engine.py`
  - Document files now include `#import "@preview/codly:1.3.0": *` and `#import "@preview/codly-languages:0.1.1": *`
  - Enables PDF generation for documents with code blocks (prerequisite for Issue #20)
  - No breaking changes - only adds imports alongside existing mitex/gentle-clues imports

### Documentation
- **README Math Example Fix** ([#33](https://github.com/YuSabo90002/typsphinx/pull/33))
  - Fixed incorrect double-escaped backslashes in math directive example
  - Changed `\\int` to `\int` for correct reStructuredText syntax
  - Helps users write proper reStructuredText files

## [0.2.1] - 2025-10-18

### Fixed
- **Table Content Duplication** ([#19](https://github.com/YuSabo90002/typsphinx/issues/19))
  - Fixed duplicate table content in Typst output where cell content appeared both as plain text and inside `#table()` structure
  - Affects all reStructuredText table formats: list-table, grid table, simple table, csv-table
  - Modified `add_text()` method to route text to `table_cell_content` when inside table cells
  - Modified `depart_table()` to use `self.body.append()` directly for table structure output
  - Added comprehensive test coverage for all table formats

- **RST Comments Rendered as Plain Text** ([#21](https://github.com/YuSabo90002/typsphinx/issues/21))
  - Fixed reStructuredText comments appearing as plain text in Typst output
  - Comments (lines starting with `..`) are now properly skipped during conversion
  - Resolved "unknown node type: comment" warning messages
  - Added `visit_comment()` and `depart_comment()` methods to TypstTranslator
  - Comments are completely omitted from output as intended for source-level documentation

## [0.1.0b1] - 2025-10-13

### Added

#### Core Features
- **Sphinx Builder Integration** (Requirement 1)
  - TypstBuilder registered as standard Sphinx builder
  - Entry point automatic discovery: `sphinx.builders` → `typst = "sphinxcontrib.typst"`
  - Command: `sphinx-build -b typst` and `sphinx-build -b typstpdf`

- **Doctree to Typst Conversion** (Requirement 2)
  - TypstWriter and TypstTranslator for node conversion
  - Support for 70+ standard docutils nodes + 14+ Sphinx addnodes
  - Document structure: sections, paragraphs, lists, tables
  - Inline elements: emphasis, strong, literal, subscript, superscript
  - Admonitions via gentle-clues (`@preview/gentle-clues:1.2.0`):
    - `note` → `#info[]`
    - `warning`/`caution` → `#warning[]`
    - `tip` → `#tip[]`
    - `important` → `#warning(title: "Important")[]`
    - `seealso` → `#info(title: "See Also")[]`

- **Cross-References and Links** (Requirement 3)
  - `nodes.reference` → `#link(url)[text]`
  - `nodes.target` → `<label>`
  - `addnodes.pending_xref` → `#link(<label>)[text]` or `#ref(<label>)`
  - Document and figure cross-references with `numref`
  - Inline references (`nodes.inline` with `xref` class)

- **Mathematical Expressions** (Requirements 4 & 5)
  - **LaTeX math via mitex** (`@preview/mitex:0.2.4`):
    - Block math: `#mitex(\`...\`)`
    - Inline math: `#mi(\`...\`)`
    - Supports LaTeX commands, environments, user-defined macros
  - **Native Typst math**:
    - Block: `$ ... $` with labeled equations
    - Inline: `$...$`
    - Typst-specific functions: `cal()`, `bb()`, `subset.eq`, etc.
  - **Fallback mode**: Basic LaTeX→Typst conversion when `typst_use_mitex = False`

- **Images and Figures** (Requirement 6)
  - `nodes.image` → `#image("path")`
  - `nodes.figure` → `#figure()` with captions
  - `nodes.table` → `#table()` with headers and rows
  - Figure/table labels and cross-references

- **Code Highlighting** (Requirement 7)
  - **Codly integration** (`@preview/codly:1.3.0` + `@preview/codly-languages:0.1.1`):
    - Automatic line numbering for all code blocks
    - Syntax highlighting for 50+ languages
    - Highlight specific lines via `#codly-range(highlight: (...))`
    - Language-specific icons and colors

- **Template System** (Requirement 8)
  - TemplateEngine for Typst template management
  - Default template with project metadata integration
  - Custom template support via `typst_template` config
  - Template parameter mapping: `typst_template_mapping`
  - Sphinx metadata → template parameters (title, authors, date, etc.)
  - Support for Typst Universe packages

- **Self-Contained PDF Generation** (Requirement 9)
  - TypstPDFBuilder using typst-py (PyPI: `typst>=0.11.1`)
  - No external Typst CLI required
  - Command: `sphinx-build -b typstpdf`
  - Automatic .typ → .pdf conversion
  - Platform support: Linux, macOS, Windows

- **Error Handling and Logging** (Requirement 10)
  - Sphinx logger integration with warning/error levels
  - Unknown node fallback with warnings
  - Template/resource error handling
  - PDF compilation error reporting (`TypstCompilationError`)

- **Multi-Document Integration** (Requirement 13)
  - Each .rst → independent .typ file
  - `toctree` → `#include()` directives
  - Heading level adjustment: `#set heading(offset: 1)`
  - `#outline()` managed in templates (not in document body)
  - Toctree options → template parameters:
    - `:maxdepth:` → `toctree_maxdepth`
    - `:numbered:` → `toctree_numbered`
    - `:caption:` → `toctree_caption`

#### Configuration Options
- `typst_use_mitex`: Enable/disable mitex for LaTeX math (default: `True`)
- `typst_template`: Custom template path
- `typst_elements`: Template parameters (paper size, fonts, etc.)
- `typst_template_mapping`: Sphinx metadata to template parameter mapping
- `typst_toctree_defaults`: Default toctree options
- `typst_package`: External Typst Universe package
- `typst_package_imports`: Package imports
- `typst_template_function`: Template function name
- `typst_output_dir`: Output directory structure
- `typst_debug`: Debug mode

#### Documentation and Examples
- Installation guide: `docs/installation.rst`
- Usage guide: `docs/usage.rst` (600+ lines)
- Configuration reference: `docs/configuration.rst` (400+ lines, 11 config values)
- Basic example: `examples/basic/`
- Advanced example: `examples/advanced/` (toctree, LaTeX math, code, tables)

#### Testing and Quality Assurance
- **286 tests** with **93% code coverage**:
  - Unit tests: builder, translator, template engine, PDF generation
  - Integration tests: basic, multi-document, advanced features
  - Documentation tests: installation, configuration, usage
  - Example tests: basic and advanced examples
- **Multi-version testing** via tox:
  - Python 3.9, 3.10, 3.11, 3.12
  - tox environments: py39, py310, py311, py312, lint, type, cov
- **CI/CD pipeline** (GitHub Actions):
  - Test matrix: 3 OSes × 4 Python versions
  - Lint (black, ruff), type check (mypy)
  - Code coverage reporting (Codecov)
  - Package build validation (twine check)
- **Code quality tools**:
  - black (code formatting)
  - ruff (linting)
  - mypy (type checking)

### Known Limitations

- **Requirement 11** (Extensibility and Plugin Support): Custom node handler registry not yet implemented
  - Planned for v0.2.0
  - Workaround: Extend TypstTranslator directly
- **Bibliography**: BibTeX integration not yet supported
- **Glossary**: Glossary generation not yet supported
- **Index**: Index generation not yet supported

### Technical Details

#### Requirements Fulfilled
- ✅ Requirement 1: Sphinx Builder Integration (100%)
- ✅ Requirement 2: Doctree to Typst Conversion (100%)
- ✅ Requirement 3: Cross-References and Links (100%)
- ✅ Requirement 4: Math Support (mitex) (100%)
- ✅ Requirement 5: Typst Native Math (100%)
- ✅ Requirement 6: Figures and Tables (100%)
- ✅ Requirement 7: Code Highlighting (100%)
- ✅ Requirement 8: Templates and Customization (100%)
- ✅ Requirement 9: Self-Contained PDF Generation (100%)
- ✅ Requirement 10: Error Handling and Logging (100%)
- ⏳ Requirement 11: Extensibility (Planned for v0.2.0)
- ✅ Requirement 12: Testing and Documentation (100%)
- ✅ Requirement 13: Multi-Document Integration (100%)

**Total: 12 out of 13 requirements fully implemented**

#### Dependencies
- Python: ≥3.9
- Sphinx: ≥5.0
- docutils: ≥0.18
- typst (typst-py): ≥0.11.1

#### Typst Packages Used
- `@preview/mitex:0.2.4`: LaTeX math rendering
- `@preview/codly:1.3.0`: Code syntax highlighting
- `@preview/codly-languages:0.1.1`: Language definitions
- `@preview/gentle-clues:1.2.0`: Admonition styling

### Development Tools
- **uv**: Fast package management and dependency resolution
- **pytest**: Testing framework (286 tests)
- **tox**: Multi-version testing automation
- **black**: Code formatting
- **ruff**: Linting
- **mypy**: Type checking
- **sphinx-testing**: Sphinx extension testing helpers

---

## [0.2.0] - 2025-10-16

### Fixed

- **Issue #5**: Fixed nested toctree relative path issues in `#include()` directives (PR #14)
  - Corrected relative path calculation for nested toctree structures
  - Added comprehensive debug logging for path resolution
  - Added E2E Typst compilation tests and integration tests
  - Improved code coverage to 94%

- **Issue #10**: Fixed typstpdf builder auto-discovery (PR #12)
  - Registered `typstpdf` builder in `entry_points` for automatic Sphinx discovery
  - Updated documentation to reflect optional extension registration
  - Added test coverage for typstpdf entry point

### Improved

- **Issue #7**: Simplified toctree output format (PR #15)
  - Changed from multiple `#block(breakable: true)[]` to single content block
  - Improved readability and maintainability of generated Typst code
  - Resolved lint and format errors in test files

### Documentation

- **Issue #6**: Documented custom node support using Sphinx standard API (PR #16)
  - Added "Working with Third-Party Extensions" section to README.md
  - Documented usage of Sphinx's standard `app.add_node()` API
  - Provided practical example with sphinxcontrib-mermaid integration
  - Clarified that NodeHandlerRegistry is unnecessary - Sphinx already provides this functionality
  - **Requirement 11 is now complete**: Custom node support via Sphinx's standard extension mechanism

- **Issue #8**: Added acknowledgment for AI-assisted development (PR #9)
  - Added Claude Code and Kiro-style Spec-Driven Development to acknowledgments

- **PR #11**: Improved CLAUDE.md with repository information and guidelines
  - Added repository owner and URL information
  - Added language guidelines for GitHub interactions
  - Added issue template references

### Dependencies

- **Dependabot updates**:
  - Bump astral-sh/setup-uv from 4 to 7 (PR #1)
  - Bump actions/checkout from 4 to 5 (PR #2)
  - Bump codecov/codecov-action from 4 to 5 (PR #3)

### Requirements Status

**All 13 requirements now fully implemented**:
- ✅ Requirement 1: Sphinx Builder Integration (100%)
- ✅ Requirement 2: Doctree to Typst Conversion (100%)
- ✅ Requirement 3: Cross-References and Links (100%)
- ✅ Requirement 4: Math Support (mitex) (100%)
- ✅ Requirement 5: Typst Native Math (100%)
- ✅ Requirement 6: Figures and Tables (100%)
- ✅ Requirement 7: Code Highlighting (100%)
- ✅ Requirement 8: Templates and Customization (100%)
- ✅ Requirement 9: Self-Contained PDF Generation (100%)
- ✅ Requirement 10: Error Handling and Logging (100%)
- ✅ Requirement 11: Extensibility and Plugin Support (100%) - **Now complete**
- ✅ Requirement 12: Testing and Documentation (100%)
- ✅ Requirement 13: Multi-Document Integration (100%)

### Testing

- **317 tests** with **94% code coverage**
- All tests passing across Python 3.9, 3.10, 3.11, 3.12
- CI/CD pipeline validated on Linux, macOS, Windows

---

## [Unreleased]

### Planned for Future Releases
- BibTeX/bibliography support
- Glossary generation
- Index generation
- Pre-commit hooks
- Additional Typst Universe template integration

---

[0.5.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.5.0
[0.4.3]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.4.3
[0.4.2]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.4.2
[0.4.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.4.1
[0.4.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.4.0
[0.3.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.3.0
[0.2.2]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.2.2
[0.2.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.2.1
[0.2.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.2.0
[0.1.0b1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.1.0b1
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.5.0...HEAD
