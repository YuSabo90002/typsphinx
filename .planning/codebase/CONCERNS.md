# Codebase Concerns

**Analysis Date:** 2026-07-04

## Tech Debt

**Hardcoded Typst Package Versions:**
- Issue: Critical external dependency versions are hardcoded in two locations with no configuration option to customize them
- Files: `typsphinx/writer.py` (lines 94-97), `typsphinx/template_engine.py` (lines 313-316)
- Versions hardcoded:
  - `@preview/codly:1.3.0`
  - `@preview/codly-languages:0.1.1`
  - `@preview/mitex:0.2.4`
  - `@preview/gentle-clues:1.2.0`
- Impact: When Typst Universe updates these packages with breaking changes, builds fail with no way to override versions without modifying source code. Users cannot use newer package versions even if compatible.
- Fix approach: Extract hardcoded versions to configuration values in `typsphinx/__init__.py` under `app.add_config_value()` for `typst_package_versions` dict. Modify `writer.py` and `template_engine.py` to reference these configurable values.

**Inefficient Document Rebuild Strategy:**
- Issue: `TypstBuilder.get_outdated_docs()` (line 57 in `builder.py`) always returns all documents for rebuilding instead of tracking actual changes
- Files: `typsphinx/builder.py:48-58`
- Impact: Every build processes all documents regardless of changes, wasting CPU/IO time. Scales poorly with large documentation sets (hundreds of documents). Makes incremental builds impossible.
- Fix approach: Implement proper rebuild tracking by storing document timestamps or hashes. Compare source modification times against output file timestamps using `os.path.getmtime()`.

**Broad Exception Handling:**
- Issue: Multiple locations catch generic `Exception` instead of specific exception types
- Files:
  - `typsphinx/builder.py:280` (image copying), `typsphinx/builder.py:377` (asset copying), `typsphinx/builder.py:453` (single asset copying), `typsphinx/builder.py:566` (PDF compilation)
  - `typsphinx/pdf.py:102` (version detection), `typsphinx/pdf.py:152` (compilation), `typsphinx/pdf.py:168` (cleanup)
- Impact: Masks underlying errors and makes debugging difficult. Silent failures could cause incorrect behavior (e.g., cleanup errors silently ignored).
- Fix approach: Catch specific exceptions: `OSError` for file operations, `ImportError` for module imports, `ChildProcessError` for compilation.

## Known Issues

**Fragile Document Wrapper Detection:**
- Issue: `writer.py:75-80` includes WORKAROUND comment noting that `visit_document()` may not be called, requiring manual `#{...}` wrapping detection
- Files: `typsphinx/writer.py:60-105`
- Symptoms: Document body may be missing code mode wrapper in certain Sphinx configurations
- Trigger: Non-standard document tree structures where root `document` node doesn't invoke visitor method
- Workaround: Code checks `body.startswith("#{")` and `body.endswith("}")`; adds wrappers if missing
- Risk: This fragile workaround could fail silently for edge cases, producing invalid Typst syntax

**Nested Image Path Calculation:**
- Issue: Complex relative path computation for nested documents (changelog #69, commit 9bb0045)
- Files: `typsphinx/translator.py` (contains `_compute_relative_image_path()` and related logic)
- Trigger: Documents in subdirectories referencing images at different levels
- Risk: Path calculation could fail for unusual nested structures or symlinks. Manual path computation is error-prone compared to using `pathlib.Path.relative_to()`.

**Template File Write-Once Pattern:**
- Issue: `_write_template_file()` only writes template once during `prepare_writing()`, not refreshed if config changes
- Files: `typsphinx/builder.py:201-245`
- Impact: If Sphinx config changes mid-build or between incremental builds, cached template file could be stale
- Risk: Produces inconsistent output across multiple builds with different configurations

## Performance Bottlenecks

**Full Document Tree Traversal on Every Build:**
- Problem: `get_outdated_docs()` always yields all documents in `self.env.found_docs` without any change tracking
- Files: `typsphinx/builder.py:48-58`
- Cause: No comparison between source and output modification times
- Improvement path: Implement change detection using `os.path.getmtime()` comparison or store modification checksums in `self.env.temp_data`

**Template Compilation Without Caching:**
- Problem: Template content re-loaded and re-processed on every document write
- Files: `typsphinx/template_engine.py:107-154` (load_template called each time from writer)
- Cause: No memoization of template content
- Improvement path: Cache template content in `TemplateEngine.__init__()` or `self.template_cache` dict

## Fragile Areas

**TypstTranslator State Management:**
- Files: `typsphinx/translator.py:19-92`
- Why fragile: 
  - 2679-line file with 20+ state variables tracking nested contexts
  - State variables include: `in_figure`, `in_table`, `in_thead`, `list_stack`, `figure_content`, `code_block_caption`, `in_paragraph`, `in_list_item`, `in_literal_block`, `is_first_list_item`, `_in_reference_with_target`, `_in_markup_mode`, `in_desc_parameter`, etc.
  - Each state variable adds complexity to visitor methods
  - Nested list/table structures require careful state management
- Safe modification: 
  - Add state assertions at entry/exit of complex visitor methods: `assert not self.in_figure, "Already in figure"`
  - Create context managers for state: `with self._table_context(): self.in_table = True; try: ... finally: self.in_table = False`
  - Add logging for state transitions: `logger.debug(f"State: in_table={self.in_table}, in_thead={self.in_thead}")`
- Test coverage: Existing 29 test files cover happy paths, but edge cases with deeply nested mixed content (tables in figures with lists) lack coverage

**Image Path Resolution for Nested Documents:**
- Files: `typsphinx/translator.py` (image handling logic), `typsphinx/builder.py:139-161`
- Why fragile: 
  - Manual path computation for relative/nested paths is error-prone
  - Doesn't use Python's `pathlib.Path.relative_to()` for robustness
  - Handles nested paths like `../images/diagram.png` which could break with symlinks
- Safe modification: 
  - Use `pathlib.Path` API instead of manual string manipulation
  - Add unit tests for various path patterns: `./image.png`, `../image.png`, `../../image.png`, etc.
  - Test with symlinked directories

## Scaling Limits

**Memory Usage with Large Documents:**
- Current capacity: Tested with 37 test files covering basic to advanced scenarios
- Limit: As document tree accumulates in `self.body[]` (translator.py line 37), memory usage grows linearly with content size
- Scaling path: For massive documents (10k+ pages), consider streaming output to file instead of accumulating in memory

**Build Time with Large Documentation Sets:**
- Current capacity: Per-file processing appears linear, but with always-rebuild strategy, builds O(n) where n = all documents
- Limit: Large projects with 500+ source files will rebuild everything even if 1 file changes
- Scaling path: Implement change tracking in `get_outdated_docs()` to enable true incremental builds

## Dependencies at Risk

**Typst Version Coupling:**
- Risk: Project requires `typst>=0.14.1` (pyproject.toml line 32), but hardcoded package versions may not be compatible with future Typst releases
- Impact: When Typst 0.15 or later introduces breaking changes to package ecosystem, builds silently fail or produce incorrect output
- Example: Issue #77 (empty URL links) required `typst>=0.14.1` update
- Migration plan: 
  - Make package versions configurable (see Tech Debt section)
  - Add compatibility matrix testing for Typst versions 0.14.1, 0.15.x, 0.16.x
  - Test against latest Typst Universe packages quarterly

**External typst-py Package Availability:**
- Risk: `typst` Python package (dependency from PyPI) might be abandoned, renamed, or moved to different maintainer
- Impact: If typst-py becomes unavailable, `TypstPDFBuilder` cannot function
- Current mitigation: Package is `>=0.14.1` (reasonable version constraint)
- Recommendations: 
  - Monitor typst-py repository for maintenance status
  - Consider vendoring compilation logic if external package becomes unavailable
  - Implement graceful fallback to suggest manual compilation if package missing

**Sphinx Version Compatibility:**
- Risk: Requires `sphinx>=5.0` (loose constraint allows 5.x, 6.x, 7.x)
- Impact: Future Sphinx versions (8.x) may change builder APIs, breaking this extension
- Current protection: Relies on SphinxTranslator base class which is relatively stable
- Recommendations: Pin to tested ranges like `sphinx>=5.0,<8.0` and test against Sphinx 8 beta

## Test Coverage Gaps

**Hardcoded Package Version Resilience:**
- What's not tested: Behavior when Typst packages update to new versions that introduce breaking changes
- Files: `typsphinx/writer.py` (line 94-97), `typsphinx/template_engine.py` (lines 313-316)
- Risk: Package updates silently break builds without clear error messages
- Priority: **High** - impacts production builds

**Incremental Build Correctness:**
- What's not tested: Only rebuilding modified documents (not implemented yet)
- Files: `typsphinx/builder.py:48-58`
- Risk: Implementing change detection requires comprehensive testing to ensure no stale files are served
- Priority: **High** - affects developer experience

**Large Document Sets (500+ files):**
- What's not tested: Build performance and memory usage with large projects
- Files: `typsphinx/builder.py` (entire write pipeline)
- Risk: Unknown performance characteristics could cause CI timeout failures
- Priority: **Medium**

**Edge Case State Management in Translator:**
- What's not tested: Deeply nested combinations (e.g., table with figures inside list items inside another table)
- Files: `typsphinx/translator.py` (lines 19-92)
- Risk: State variables not initialized or cleared for unusual nesting patterns could produce invalid Typst
- Priority: **Medium**

**Path Resolution for Symlinked Directories:**
- What's not tested: Image/template resolution when source directory contains symlinks
- Files: `typsphinx/builder.py` (image copying), `typsphinx/template_engine.py` (template loading)
- Risk: `os.path.join()` may not resolve correctly with symlinks; should use `os.path.realpath()`
- Priority: **Low**

---

*Concerns audit: 2026-07-04*
