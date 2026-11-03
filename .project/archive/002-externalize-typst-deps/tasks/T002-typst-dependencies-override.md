---
id: T002
title: Add the typst_dependencies config value that replaces the generated _typsphinx/deps.typ with a verbatim copy of the user's file
wave: 1
deps: [T001]
status: done
agent: build_T002
base: 10ec848c0f42cec98d0a40a6ad8bd18057567900
worktree: null
task_branch: null
files:
  - typsphinx/__init__.py
  - typsphinx/builder.py
  - tests/test_typst_dependencies_gate.py
  - tests/fixtures/typst_dependencies_override
---

# T002 — Add the typst_dependencies config value that replaces the generated _typsphinx/deps.typ with a verbatim copy of the user's file

## Context

T001 makes every build write the generated default `<outdir>/_typsphinx/deps.typ` from `TypstBuilder._write_dependencies_file()`, called first in `finish()`. This task adds the owner-chosen override: `typst_dependencies`, a path to one file (relative to srcdir, or absolute) that is copied byte-identical to the same output path in place of the generated default. It is global, never per template, and is a single file, never a directory. SYNTHESIS settled several rules. Registration mirrors `typst_template` (`typsphinx/__init__.py:46`). Resolution is `os.path.join(srcdir, value)`, as `typst_template` is resolved (`typsphinx/writer.py:366-371`). `None` generates the default and `""` stops the build. Validation raises `sphinx.errors.ExtensionError` from a `TypstBuilder` method called at the top of `write()`, next to `_validate_output_path_collisions()`, `_validate_registry_key_references()`, and `_validate_used_template_paths()` (`typsphinx/builder.py:1683-1718`), so a bad value leaves zero `.typ` files. The user's file is never parsed, validated, or modified (N3).

## Approach

- Register `app.add_config_value("typst_dependencies", None, "html", [str, type(None)])` in `typsphinx/__init__.py`. Do not use the `config-inited` hook; that hook is reserved for removed names (`typsphinx/__init__.py:62-73`).
- Add `TypstBuilder._validate_typst_dependencies()`, called from `write()` before any file is written. `None` passes. Any other non-`str` (Sphinx only warns on type mismatches) or `""` is an `ExtensionError`. A `str` whose resolved path is not an existing regular file (missing, or a directory) is also an `ExtensionError`. Messages begin `typst_dependencies:` and name the configured value and the resolved path through `typsphinx.pathfmt.quote_path()`, for example `typst_dependencies: file not found: 'deps/my-deps.typ' (resolved to '/abs/src/deps/my-deps.typ')`.
- Extend `_write_dependencies_file()` (T001's seam). When the value is set, copy the bytes with `shutil.copyfile(resolved, dest)`: no re-encoding, no newline change, no metadata promise. When it is unset, keep T001's default write. Both modes write the one fixed path on every build, so switching modes between builds always leaves the newly effective file (E2). Nothing else under `_typsphinx/` is created or deleted. The method re-checks the resolved path itself, because tests drive `finish()` directly (the CONF-17 hoist-plus-finish-guard precedent).
- Burn down the gentle-clues unknown. The fixture `tests/fixtures/typst_dependencies_override/` has a `conf.py` setting `typst_dependencies = "deps/my-deps.typ"`. Its `<fixture>/deps/my-deps.typ` is the default file's content with gentle-clues pinned to `1.3.0` (the other four at defaults), defining the same `typsphinx-init`. Its document carries `note`/`warning`/`tip` admonitions, a code block, and math, compiled with `-b typstpdf`. A planning probe compiled all nine gentle-clues functions the translator emits from 1.3.0 under typst-py 0.15.0, but from the local package cache. Re-prove it in your sidecar, where the package is fetched. If 1.3.0 fails, choose another compiler-compatible release, record the measurement in the Log, and keep the fixture's admonitions to `info`/`warning`/`tip`.
- `tests/test_typst_dependencies_gate.py` builds in tmp dirs with `sys.executable -m sphinx` under `LC_ALL=C` and pins E2, E4, and E6 exactly as their rulings state (see Acceptance criteria). Make the E6 byte-copy test use `-b typst`, with a source file containing CRLF line endings, non-ASCII UTF-8 bytes, and no trailing newline, so any re-encoding or newline translation shows.
- Do not add a per-template key to `typst_document_templates`, a directory copy, a conf.py dict of versions, or a preamble string (vetoes). Do not rewrite user templates. Do not rename `typst_package` / `typst_package_imports`.

## Interface contract

- K1 — Module `typsphinx/typst_deps.py` (leaf; no typsphinx-internal imports) exports: `DEPS_OUTPUT_DIR = "_typsphinx"`, `DEPS_FILENAME = "deps.typ"`, `DEPS_IMPORT_PATH = "/_typsphinx/deps.typ"`, `INIT_FUNCTION_NAME = "typsphinx-init"`; `@dataclass(frozen=True) class PreviewPackage` with fields `spec: str` (e.g. `"@preview/codly:1.3.0"`) and `items: str` (e.g. `"*"`, `"mi, mitex"`, `"render"`) and read-only properties `name: str` (e.g. `"codly"`) and `version: str` (e.g. `"1.3.0"`); `DEFAULT_PACKAGES: tuple[PreviewPackage, ...]` ordered codly, codly-languages, mitex, gentle-clues, diagraph; `render_default_deps() -> str` (the full default `deps.typ` text); `deps_preamble_lines() -> list[str]` returning exactly `['#import "/_typsphinx/deps.typ": *', '#show: typsphinx-init']`.
- K2 — `TypstBuilder._write_dependencies_file(self) -> None` in `typsphinx/builder.py` is called as the first statement of `TypstBuilder.finish()`, before `copy_image_files()` and `_copy_used_template_bundles()`; it creates `<outdir>/_typsphinx/` and writes `<outdir>/_typsphinx/deps.typ` on every build; after it returns, that file holds the exact bytes of the effective dependencies file.
- K4 — Config value `typst_dependencies`, registered as `app.add_config_value("typst_dependencies", None, "html", [str, type(None)])`. `None` (default) means the generated default file. A `str` is resolved as `os.path.join(srcdir, value)` (an absolute value passes through), and that one file is copied byte-identical to `<outdir>/_typsphinx/deps.typ`. `""`, a non-`str` value, or a resolved path that is not an existing file raises `sphinx.errors.ExtensionError` from `TypstBuilder.write()` before any `.typ` file is written, with a message that starts with `typst_dependencies:` and contains the configured value rendered by `typsphinx.pathfmt.quote_path()`.

## Intent coverage

- SC2
- SC3

## Acceptance criteria

1. SC3: `typst_dependencies` is registered with default `None`. With `typst_dependencies = "deps/my-deps.typ"`, `<outdir>/_typsphinx/deps.typ` is byte-identical to the user's file and differs from `render_default_deps()`, and no other file is written under `<outdir>/_typsphinx/`.
2. SC3: the `tests/fixtures/typst_dependencies_override/` fixture, whose `deps.typ` pins gentle-clues 1.3.0 (or the measured compatible release recorded in the Log), builds with `-b typstpdf` to a PDF. Its content files and wrappers import only `/_typsphinx/deps.typ`: no `@preview/` literal of the five appears in any `.typ` outside `_typsphinx/` and `_template/`.
3. SC3: a `typst_dependencies` path that does not exist stops the build with a non-zero exit and an error starting `typst_dependencies:` that names the configured value, and zero `.typ` files are written.
4. E4 (held-out, ruling "`typst_dependencies = None` (the default) means generate the default file; an empty string `""` stops the build with an error"): `tests/test_typst_dependencies_gate.py` asserts that an explicit `None` yields bytes equal to `render_default_deps().encode("utf-8")`, and that `""` stops the build with a `typst_dependencies:` error and no `.typ` files.
5. E6 (held-out, ruling "an absolute path is accepted, as for `typst_template`; the file is copied as bytes (no re-encoding, no newline changes)"): `tests/test_typst_dependencies_gate.py` asserts that an absolute path builds. It also asserts that a source file with CRLF line endings, non-ASCII UTF-8, and no trailing newline arrives byte-identical.
6. E2 (held-out, ruling "rebuilding (incremental or `-E`) rewrites `<outdir>/_typsphinx/deps.typ` with identical bytes; switching from `typst_dependencies` set to unset (or back) between builds leaves the newly effective file, never the stale one"): `tests/test_typst_dependencies_gate.py` asserts identical bytes across an incremental rebuild and a `-E` rebuild in both modes. It also asserts that set→unset leaves the default bytes and unset→set leaves the user's bytes, in the same outdir.
7. SC2/SC3 surface: the PLAN.md "generated Typst output tree" walkthrough passes, covering both the default `examples/basic` build and the override fixture build, and is run in Verify.

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev && LC_ALL=C uv run pytest tests/test_typst_dependencies_gate.py tests/test_deps_output_gate.py -o addopts="" -q && d=$(mktemp -d) && LC_ALL=C uv run sphinx-build -q -E -b typstpdf examples/basic "$d/basic" && test -f "$d/basic/basic-example.pdf" && grep -qxF '#import "/_typsphinx/deps.typ": *' "$d/basic/index.typ" && grep -qxF '#show: typsphinx-init' "$d/basic/basic-example.typ" && cp -r tests/fixtures/typst_dependencies_override "$d/p" && LC_ALL=C uv run sphinx-build -q -E -b typstpdf "$d/p" "$d/out" && cmp "$d/p/deps/my-deps.typ" "$d/out/_typsphinx/deps.typ" && ls "$d"/out/*.pdf && test "$(ls -A "$d/out/_typsphinx")" = "deps.typ" && ! grep -rlE '@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):' --include='*.typ' --exclude-dir=_typsphinx --exclude-dir=_template "$d/out" && printf 'typst_dependencies = "%s/%s"\n' missing deps.typ >> "$d/p/conf.py" && ! LC_ALL=C uv run sphinx-build -q -E -b typst "$d/p" "$d/out2" 2> "$d/err.txt" && grep -F 'typst_dependencies:' "$d/err.txt" && grep -F 'missing/deps' "$d/err.txt" && test -z "$(find "$d/out2" -name '*.typ' 2>/dev/null)"
```

Heavy: yes

## Log

- 2026-11-03 — created by planner
- 2026-11-03 — build_T002: registered `typst_dependencies` (default `None`, `[str, type(None)]`) in `typsphinx/__init__.py`; added `TypstBuilder._resolve_typst_dependencies()` (raises `ExtensionError` `typst_dependencies: ...` for non-`str`, `""`, missing path, non-regular file; value and resolved path via `quote_path()`) and `_validate_typst_dependencies()` called in `write()` right after `_validate_used_template_paths()`; `_write_dependencies_file()` now re-resolves and `shutil.copyfile`s the user file, else writes the default bytes. Added `tests/test_typst_dependencies_gate.py` (registration, SC3 byte copy + only `deps.typ` under `_typsphinx/`, typstpdf PDF + no five-spec literals, missing/dir/non-str refusals with zero `.typ`, E4, E6 absolute + CRLF/non-ASCII/no-trailing-newline byte identity, E2 incremental/-E both modes and set→unset→set) and fixture `tests/fixtures/typst_dependencies_override/` (`deps/my-deps.typ` = default with gentle-clues 1.3.0; note/warning/tip, code block, inline+block math).
- 2026-11-03 — build_T002: gentle-clues 1.3.0 measurement: built the fixture with `-b typstpdf` under an empty `XDG_CACHE_HOME` (typst-py 0.15.0); the cache then held freshly fetched `preview/gentle-clues/1.3.0` (plus codly 1.3.0, codly-languages 0.1.10, mitex 0.2.7, diagraph 0.3.7, linguify 0.5.0); rc=0 and PDF written. 1.3.0 kept. (`TYPST_PACKAGE_CACHE_PATH` is not honoured by typst-py.)
- 2026-11-03 — build_T002: Verify (task command, verbatim) — pass (VERIFY_RC=0; pytest 25 passed). black/ruff repo-wide clean, mypy typsphinx/ clean. Full `LC_ALL=C uv run pytest tests/`: 1774 passed, 1 skipped, 1 failed — `tests/test_registry_documentation_gate.py::TestErrorCatalogueAgreesWithCode::test_code_to_docs_every_non_excluded_shape_is_published` flags the four new `typst_dependencies:` raise sites as unpublished in configuration.rst's "When the Build Stops" catalogue. That path is outside T002 `files`; T005 (wave 2) owns adding the stop case there. Fragments to publish (each one literal chunk): `typst_dependencies: expected a file path (str) or None, got `, `typst_dependencies: empty path `, `typst_dependencies: file not found: `, `typst_dependencies: not a regular file: `. Red until T005 lands.
- 2026-11-03 — orchestrator Verify (sidecar gsd-path-verify/task-t002-verify): pass, exit 0; output tail:
  ```
   + sphinxcontrib-applehelp==2.0.0
   + sphinxcontrib-bibtex==2.7.0
   + sphinxcontrib-devhelp==2.0.0
   + sphinxcontrib-htmlhelp==2.1.0
   + sphinxcontrib-jsmath==1.0.1
   + sphinxcontrib-qthelp==2.0.0
   + sphinxcontrib-serializinghtml==2.0.0
   + tomli-w==1.2.0
   + tox==4.64.10
   + tox-uv==1.37.2
   + tox-uv-bare==1.37.2
   + twine==7.0.0
   + types-docutils==0.23.0.20260923
   + typing-extensions==4.16.0
   + typsphinx==0.9.8 (from file:///home/yuta/.gsd-path/projects/4018706f853274cd7713143cf7ba094e230867e5ad2bfc5891d0cd69027eb98b/4b529697c911aff5766d6b9c03f122ba2ed9565d87a00e2f51ea62f3fd0642ec/verify/task-t002-verify)
   + typst==0.15.0
   + urllib3==2.7.0
   + uv==0.13.6
   + virtualenv==21.5.1
  WARNING: html_static_path entry '_static' does not exist
  ```
