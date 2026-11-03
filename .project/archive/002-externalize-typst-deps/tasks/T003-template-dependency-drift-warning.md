---
id: T003
title: Warn once per (file, package) when a used template bundle pins one of the five packages at a version different from the effective deps.typ
wave: 2
deps: [T001, T002]
status: done
agent: build_T003
base: 9efd389a5e3aad555e0b86a1c1d18dfd84f9447b
worktree: null
task_branch: null
files:
  - typsphinx/typst_deps.py
  - typsphinx/builder.py
  - tests/test_template_dependency_drift_gate.py
  - tests/fixtures/template_dependency_drift
---

# T003 — Warn once per (file, package) when a used template bundle pins one of the five packages at a version different from the effective deps.typ

## Context

Typst has no version resolution, so a template that pins `@preview/gentle-clues:1.2.0` loads alongside the 1.3.1 that `deps.typ` imports, with no error. The owner ruled for a warning, not an error ("2.警告"; N2: never break a user's build over a template pin). SYNTHESIS settled the shape. After `_copy_used_template_bundles()` in `TypstBuilder.finish()`, call `_warn_template_dependency_drift()`. It scans every `.typ` file actually copied into `<outdir>/_template/<key>/` by `_copy_bundle_directory()` (`typsphinx/builder.py:2195-2270`); have that method return the copied relative paths, so the scan reads exactly the used-bundle set after `_is_excluded_bundle_entry` filtering. Package-alone keys have no bundle and are skipped. The effective versions are T001's `DEFAULT_PACKAGES` when `typst_dependencies` is `None`. When it is set, they come from `extract_preview_versions()` over the copied `<outdir>/_typsphinx/deps.typ`, decoded as UTF-8 with `errors="replace"`. Owner correction C1: comments are excluded from the scan ("E10はコメント除外").

## Approach

- Add to `typsphinx/typst_deps.py` (keep it a leaf module): `strip_typst_comments(text: str) -> str` and `extract_preview_versions(text: str) -> dict[str, set[str]]`. The second comment-strips its input, then matches only `@preview/(codly-languages|codly|mitex|gentle-clues|diagraph):(\d+\.\d+\.\d+)`. The `:` must follow the name immediately, so `codly` never matches `codly-languages:`, and `@local/...` or any other namespace is ignored.
- `strip_typst_comments` is a single left-to-right character scanner, not a regex. It does three things. (a) It copies double-quoted string literals through unchanged, honouring backslash escapes, and ends a string at an unescaped `"` or at end of line, so `"https://…"` is never read as a `//` comment. (b) It removes `/* … */` block comments with nesting-depth counting, as Typst nests them. (c) It removes `//` to end of line. Known limit, accepted under INTENT Risks bullet 4 as a best-effort aid: a `"` in markup-mode prose is treated as a string delimiter. Write that limit in the docstring.
- For each (file, package) where any version found differs from the effective version, emit exactly one `logger.warning` in the K5 format. Iterate sorted by (outdir-relative path, package). Use plain `logger.warning` with no `type`/`subtype`, matching every existing warning in `builder.py`. When the effective `deps.typ` has no version for a package (E9), that package is not compared. The build always continues and exits 0.
- Never modify any copied template file or the user's `deps.typ`: bundles stay byte-identical copies (INTENT Constraint, N3). Do not turn drift into an error and do not rewrite imports (vetoes).
- `tests/test_template_dependency_drift_gate.py` builds tmp projects with `sys.executable -m sphinx -b typst` under `LC_ALL=C` and asserts on stderr. It covers SC4 (mismatch → warning, exit 0; match or none → silent; override mode compares against the user's file), E7, E8, E9, and E10 (line, block, and nested block comments), plus the `"https://…"` URL line followed by a real pin. Add unit tests that call `strip_typst_comments` / `extract_preview_versions` directly, including the `codly` vs `codly-languages:` boundary. Fixture sources may live in `tests/fixtures/template_dependency_drift/`.

## Interface contract

- K1 — Module `typsphinx/typst_deps.py` (leaf; no typsphinx-internal imports) exports: `DEPS_OUTPUT_DIR = "_typsphinx"`, `DEPS_FILENAME = "deps.typ"`, `DEPS_IMPORT_PATH = "/_typsphinx/deps.typ"`, `INIT_FUNCTION_NAME = "typsphinx-init"`; `@dataclass(frozen=True) class PreviewPackage` with fields `spec: str` (e.g. `"@preview/codly:1.3.0"`) and `items: str` (e.g. `"*"`, `"mi, mitex"`, `"render"`) and read-only properties `name: str` (e.g. `"codly"`) and `version: str` (e.g. `"1.3.0"`); `DEFAULT_PACKAGES: tuple[PreviewPackage, ...]` ordered codly, codly-languages, mitex, gentle-clues, diagraph; `render_default_deps() -> str` (the full default `deps.typ` text); `deps_preamble_lines() -> list[str]` returning exactly `['#import "/_typsphinx/deps.typ": *', '#show: typsphinx-init']`.
- K2 — `TypstBuilder._write_dependencies_file(self) -> None` in `typsphinx/builder.py` is called as the first statement of `TypstBuilder.finish()`, before `copy_image_files()` and `_copy_used_template_bundles()`; it creates `<outdir>/_typsphinx/` and writes `<outdir>/_typsphinx/deps.typ` on every build; after it returns, that file holds the exact bytes of the effective dependencies file.
- K4 — Config value `typst_dependencies`, registered as `app.add_config_value("typst_dependencies", None, "html", [str, type(None)])`. `None` (default) means the generated default file. A `str` is resolved as `os.path.join(srcdir, value)` (an absolute value passes through), and that one file is copied byte-identical to `<outdir>/_typsphinx/deps.typ`. `""`, a non-`str` value, or a resolved path that is not an existing file raises `sphinx.errors.ExtensionError` from `TypstBuilder.write()` before any `.typ` file is written, with a message that starts with `typst_dependencies:` and contains the configured value rendered by `typsphinx.pathfmt.quote_path()`.
- K5 — Drift warning: one `logger.warning` per mismatched (file, package), with message text exactly `template dependency drift: {quote_path(relpath)} pins @preview/{package}:{template_versions}, but _typsphinx/deps.typ has @preview/{package}:{deps_version}`. `relpath` is the outdir-relative POSIX path of the copied file (`_template/<key>/<rel>.typ`). `template_versions` is every differing version found in that file, sorted by numeric (major, minor, patch) and joined by `, `. Warnings are emitted in ascending (relpath, package) order. The build exits 0.

## Intent coverage

- SC4

## Acceptance criteria

1. SC4: a used bundle `.typ` that imports `@preview/<one of the five>:<v>`, where `<v>` differs from that package's version in the effective `deps.typ`, produces exactly one K5 warning naming the file, the package, the template's version, and the `deps.typ` version, and the build exits 0. With matching versions, or no such import, no drift warning is printed. In override mode the comparison uses the user's file: a template pinning gentle-clues 1.3.1 against a user `deps.typ` with 1.3.0 warns.
2. E7 (held-out, ruling "an `@preview/` import of a package outside the five is ignored; a `@local/` or other-namespace import of one of the five is ignored"): `tests/test_template_dependency_drift_gate.py` asserts that `@preview/charged-ieee:0.1.0` and `@local/codly:9.9.9` produce no warning.
3. E8 (held-out, ruling "the same mismatch in two bundle files gives two warnings, one per file; two mismatched packages in one file give two warnings; warnings are emitted in sorted (file, package) order"): `tests/test_template_dependency_drift_gate.py` asserts exactly those counts and the sorted order of the warning lines on stderr.
4. E9 (held-out, ruling "when the user's `deps.typ` has no version for a package, that package is not compared and no warning is printed for it"): `tests/test_template_dependency_drift_gate.py` uses a user `deps.typ` that omits diagraph, and asserts that a template pinning `@preview/diagraph:0.1.0` produces no warning while another mismatched package in the same file still warns.
5. E10 (held-out, ruling "comments are excluded from the scan: a pin that appears only inside a `//` line comment or a `/* */` block comment does not warn"): `tests/test_template_dependency_drift_gate.py` asserts no warning for pins inside a `//` comment, a `/* */` comment, and a nested `/* /* */ */` comment. It also asserts that a real pin after a `"https://example.com"` string on the same line still warns.
6. Only `.typ` files copied into `<outdir>/_template/<key>/` for used keys are scanned. A `typst_package`-only key is skipped. Every copied template file stays byte-identical to its source after the scan.
7. SC4 surface: the PLAN.md "sphinx-build console output" walkthrough passes with a real `sphinx-build` run in Verify.

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev && LC_ALL=C uv run pytest tests/test_template_dependency_drift_gate.py -o addopts="" -q && d=$(mktemp -d) && cp -r examples/basic "$d/p" && mkdir -p "$d/p/_tpl" && cp typsphinx/templates/base.typ "$d/p/_tpl/base.typ" && printf '\n#import "@preview/gentle-clues:1.2.0": *\n// #import "@preview/codly:1.0.0": *\n' >> "$d/p/_tpl/base.typ" && printf 'typst_template = "%s/%s"\n' _tpl base.typ >> "$d/p/conf.py" && LC_ALL=C uv run sphinx-build -E -b typst "$d/p" "$d/out" 2> "$d/err.txt" && cat "$d/err.txt" && test "$(grep -c 'template dependency drift' "$d/err.txt")" -eq 1 && grep 'template dependency drift' "$d/err.txt" | grep -F "'_template/typst/base" | grep -F 'gentle-clues:1.2.0' | grep -F 'gentle-clues:1.3.1' && cmp "$d/p/_tpl/base.typ" "$d/out/_template/typst/base.typ" && sed -i 's/gentle-clues:1.2.0/gentle-clues:1.3.1/' "$d/p/_tpl/base.typ" && LC_ALL=C uv run sphinx-build -E -b typst "$d/p" "$d/out2" 2> "$d/err2.txt" && test "$(grep -c 'template dependency drift' "$d/err2.txt")" -eq 0
```

Heavy: no

## Log

- 2026-11-03 — created by planner
- 2026-11-03 — build_T003 (coder): implemented. `typsphinx/typst_deps.py` (still a leaf) gains `strip_typst_comments()` (single left-to-right scanner: strings copied through with backslash escapes, ending at unescaped `"` or end of line; nested `/* */` removed and replaced by one space, unterminated runs to EOF; `//` removed up to the newline; markup-mode `"` limit documented in the docstring), `extract_preview_versions()` (comment-strips, then matches `@preview/(codly-languages|codly|mitex|gentle-clues|diagraph):(\d+\.\d+\.\d+)`), and helper `version_sort_key()`. `typsphinx/builder.py`: `_copy_bundle_directory()` now returns the dest-relative POSIX paths it copied; `_copy_used_template_bundles()` returns `_template/<key>/<rel>` paths (`[]` when nothing used); `finish()` calls new `_warn_template_dependency_drift()` after the bundle copy. Effective versions: `DEFAULT_PACKAGES` when `typst_dependencies is None`, else `extract_preview_versions()` over the copied `<outdir>/_typsphinx/deps.typ` (UTF-8, `errors="replace"`). Implementation decision: when the user's `deps.typ` pins one package at several versions, a template version differs only if it is in none of them, and `{deps_version}` lists them numerically sorted joined by `, `. Plain `logger.warning`, no type/subtype; read-only scan. Tests: `tests/test_template_dependency_drift_gate.py` (28 tests: SC4 default/override, E7, E8, E9, E10, URL-string line, numeric sort of several versions, unused key / `.git` / backup exclusion, package-only skip, byte-identical copies, scanner/extractor units incl. `codly` vs `codly-languages:`); fixtures in `tests/fixtures/template_dependency_drift/` (`index.rst`, `template_body.typ`, `user_deps.typ`).
- For T005 (docs catalogue, if the error/warning catalogue gate covers warnings): message fragment `template dependency drift: {quote_path(relpath)} pins @preview/{package}:{template_versions}, but _typsphinx/deps.typ has @preview/{package}:{deps_version}`.
- Verify (task command, run in primary checkout): pass — pytest 28 passed; sphinx-build mismatch run printed exactly 1 drift warning naming `'_template/typst/base.typ'`, `gentle-clues:1.2.0`, `gentle-clues:1.3.1`; `cmp` byte-identical; matching rerun 0 drift warnings; exit 0. Note: the Verify's exact `uv sync --extra dev` removes the docs extra from the main `.venv`; restored afterwards with `uv sync --extra dev --extra docs`. black/ruff/mypy clean.
- 2026-11-03 — build_T003 (coder): full-suite check `LC_ALL=C uv run pytest tests/` surfaced `tests/test_preview_version_sync.py::test_five_specs_appear_only_in_typst_deps_module` failing on a docstring example spec in `builder.py`; reworded (no five-package spec literal outside `typst_deps.py`). Re-ran: that file + drift gate 33 passed; task Verify re-run exit 0. Full suite otherwise 1801 passed / 1 skipped, only remaining failure is the known T005-owned `test_registry_documentation_gate.py::TestErrorCatalogueAgreesWithCode::test_code_to_docs_every_non_excluded_shape_is_published`.
- 2026-11-03 — orchestrator Verify (sidecar gsd-path-verify/task-t003-verify): pass, exit 0; output tail:
  ```
   + sphinx==9.1.1
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
   + typsphinx==0.9.8 (from file:///home/yuta/.gsd-path/projects/4018706f853274cd7713143cf7ba094e230867e5ad2bfc5891d0cd69027eb98b/4b529697c911aff5766d6b9c03f122ba2ed9565d87a00e2f51ea62f3fd0642ec/verify/task-t003-verify)
   + typst==0.15.0
   + urllib3==2.7.0
   + uv==0.13.6
   + virtualenv==21.5.1
  ```
- 2026-11-03 — orchestrator regression Verify of T001 (sidecar gsd-path-verify/task-t003-verify): pass, exit 0; output tail:
  ```
  ........................................................................ [ 25%]
  ........................................................................ [ 51%]
  ........................................................................ [ 77%]
  .............................................................            [100%]
  277 passed in 18.67s
  /tmp/tmp.V0Lp05rMII/docs/typsphinx.pdf
  Resolved 95 packages in 0.53ms
  Installed 9 packages in 4ms
   + accessible-pygments==0.0.5
   + beautifulsoup4==4.15.0
   + furo==2025.12.19
   + mdit-py-plugins==0.6.1
   + myst-parser==5.1.0
   + soupsieve==2.8.4
   + sphinx-autodoc-typehints==3.17.4
   + sphinx-basic-ng==1.0.0b2
   + sphinx-intl==2.4.0
  WARNING: html_static_path entry '_static' does not exist
  ```
- 2026-11-03 — orchestrator regression Verify of T002 (sidecar gsd-path-verify/task-t003-verify): pass, exit 0; output tail:
  ```
  .........................                                                [100%]
  25 passed in 5.95s
  /tmp/tmp.RHXh6BF9ij/out/depsoverride.pdf
      sphinx.errors.ExtensionError: typst_dependencies: file not found: 'missing/deps.typ' (resolved to '/tmp/tmp.RHXh6BF9ij/p/missing/deps.typ')
      sphinx.errors.ExtensionError: typst_dependencies: file not found: 'missing/deps.typ' (resolved to '/tmp/tmp.RHXh6BF9ij/p/missing/deps.typ')
  Resolved 95 packages in 0.55ms
  Uninstalled 9 packages in 7ms
   - accessible-pygments==0.0.5
   - beautifulsoup4==4.15.0
   - furo==2025.12.19
   - mdit-py-plugins==0.6.1
   - myst-parser==5.1.0
   - soupsieve==2.8.4
   - sphinx-autodoc-typehints==3.17.4
   - sphinx-basic-ng==1.0.0b2
   - sphinx-intl==2.4.0
  WARNING: html_static_path entry '_static' does not exist
  ```
