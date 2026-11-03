---
id: T002
title: Add the typst_dependencies config value that replaces the generated _typsphinx/deps.typ with a verbatim copy of the user's file
wave: 1
deps: [T001]
status: pending
agent: null
base: null
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
