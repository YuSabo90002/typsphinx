---
id: T001
title: Move the five @preview specs to typsphinx/typst_deps.py and emit a shared _typsphinx/deps.typ imported by every content file, wrapper, and base.typ
wave: 1
deps: []
status: done
agent: build_T001
base: 1b901dfa8cb9dccc641315a0a90f74818fafe928
worktree: null
task_branch: null
files:
  - typsphinx/typst_deps.py
  - typsphinx/writer.py
  - typsphinx/template_engine.py
  - typsphinx/templates/base.typ
  - typsphinx/builder.py
  - tests/test_deps_output_gate.py
  - tests/fixtures/deps_output_gate
  - tests/test_preview_version_sync.py
  - tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
  - tests/fixtures/inline_image_separator_render_gate/goldens
  - tests/test_desc_rubric_decoupling_render_gate.py
  - tests/test_inline_image_separator_render_gate.py
  - tests/test_diagraph_escaping_render_gate.py
  - tests/test_empty_typst_documents_optout_gate.py
  - tests/test_hand_compile_root_gate.py
  - tests/test_integration_nested_toctree.py
  - tests/test_package_only_config_gate.py
  - tests/test_preview_smoke_gate.py
  - tests/test_registry_prewrite_validation_gate.py
  - tests/test_template_codly.py
  - tests/test_template_engine.py
  - tests/test_template_mitex.py
  - tests/test_templates_path_collision_gate.py
  - tests/test_two_layer_output_gate.py
  - tests/test_config_other_options.py
  - tests/test_graphviz_render_gate.py
  - tests/test_signature_page_boundary_render_gate.py
  - tests/test_output_layout_docs_gate.py
---

# T001 — Move the five @preview specs to typsphinx/typst_deps.py and emit a shared _typsphinx/deps.typ imported by every content file, wrapper, and base.typ

## Context

Today the five Typst Universe imports (codly 1.3.0, codly-languages 0.1.10, mitex 0.2.7, gentle-clues 1.3.1, diagraph 0.3.7) and the codly init lines are hard-coded three times: `typsphinx/writer.py:263-277` (the content-file preamble in `TypstWriter.translate()`), `typsphinx/template_engine.py:690-712` (the wrapper preamble in `TemplateEngine.render()`, with the CR-01 `will_inline_default_template` skip), and `typsphinx/templates/base.typ:6-29`. SYNTHESIS settled the replacement. A new leaf module `typsphinx/typst_deps.py` holds the specs as literal strings and is the only file under `typsphinx/` that matches the SC1 grep. Every build writes `<outdir>/_typsphinx/deps.typ`: the five `#import` lines in today's order with today's items (`codly: *`, `codly-languages: *`, `mitex: mi, mitex`, `gentle-clues: *`, `diagraph: render`), plus `#let typsphinx-init(body) = { show: codly-init.with(); codly(languages: codly-languages); body }`. Every content file and every wrapper starts with the two-line preamble `#import "/_typsphinx/deps.typ": *` + `#show: typsphinx-init`. In wrappers the preamble goes after the optional `generate_package_import()` line and before the template import or inline template, on every route, including the legacy inline-default route. `base.typ` drops its pins and its top-level codly init and imports `/_typsphinx/deps.typ` instead. In define the owner measured that imported names do not cross `#include`, and that a `typsphinx-init` show function exported from `deps.typ` applies codly in both the wrapper and the included content.

## Approach

- `typsphinx/typst_deps.py` imports nothing from `writer`, `template_engine`, `builder`, or `translator`. It holds the specs as full literal strings such as `"@preview/codly:1.3.0"`, never as a name and version joined at runtime, so the SC1 grep still finds them. The `codly-init` and `codly(languages:` text lives only here. Shapes are fixed by the Interface contract.
- `TypstBuilder._write_dependencies_file()` runs as the first statement of `TypstBuilder.finish()` (`typsphinx/builder.py:2462-2479`), so `TypstPDFBuilder.finish()` (which calls `super().finish()` first) always compiles against it. It runs on every build regardless of the write set. It writes with `Path.write_bytes(render_default_deps().encode("utf-8"))`, which avoids newline translation and gives identical bytes on every rebuild. Tests drive `finish()` directly, so the method must tolerate a builder whose `outdir` exists but whose `write()` never ran. T002 later adds the override branch to this same method; leave a single clear seam for it, but do not implement it here.
- Extend OUT-07 (`_reserves_template_prefix()` at `typsphinx/builder.py:1017-1066`, used in `_validate_output_path_collisions()` at `:1068-1235`). A content file or wrapper whose first output-path segment folds, through `_collision_key()`, to `_typsphinx` must be a build-stopping failure in the same aggregated `ExtensionError` as `_template`, and the message must name the matching directory. Without this, docname `_typsphinx/deps` would be overwritten by `finish()`.
- Burn down the inline-route unknown. Compile the `TemplateEngine.render()` output of the inline-default route (no `template_file`, no `typst_package`) with `typst-py`, with `deps.typ` written at the compile root. A planning probe compiled a duplicate `#import "/_typsphinx/deps.typ": *` cleanly. If your compile fails, fall back to the SYNTHESIS runner-up (skip the preamble on that route, emit `#show: typsphinx-init` after the inlined template) and record the measurement in the Log. Restate the old CR-01 tests in `tests/test_template_engine.py` as: `#show: typsphinx-init` appears exactly once in every route's output.
- Goldens (`tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` and all ten files in `tests/fixtures/inline_image_separator_render_gate/goldens/`, including `pass_c_image_first_in_paragraph.pre_fix.typ`) are edited by exact replacement. Replace the old eleven-line block, from `// Essential imports for included document` through `#codly(languages: codly-languages)` and its trailing blank line, with the new preamble plus one blank line. Never regenerate goldens from a build: that is how a rendering change hides (INTENT Risk 1, N1). Give `pass_c` and its `.pre_fix` twin the identical transform so their one-blank-line delta test keeps its meaning.
- Gate tests that assert the old literals or the old file set change only their import/init-shape or file-count assertions. Render and PDF assertions stay byte-for-byte. The planning prototype failed exactly these 15 files: the two golden gates, diagraph_escaping, empty_typst_documents_optout (file set now includes `<outdir>/_typsphinx/deps.typ`), hand_compile_root, integration_nested_toctree, package_only_config, preview_smoke, preview_version_sync, registry_prewrite_validation, template_codly, template_engine, template_mitex, templates_path_collision, and two_layer_output. `test_config_other_options.py`, `test_graphviz_render_gate.py`, `test_signature_page_boundary_render_gate.py`, and `test_output_layout_docs_gate.py` passed but reference the old shape in comments or counts. Fix them only if they are wrong.
- Content files now need the compile root to be the outdir, as `/_template/...` imports already do: `typst: file not found (searched at …/<subdir>/_typsphinx/deps.typ)` in the prototype. `tests/test_integration_nested_toctree.py::TestE2ETypstCompilation::test_compilation_uses_correct_root_directory` and `tests/test_hand_compile_root_gate.py` must keep their meaning: the hand-compile gate still proves that a non-outdir root fails, naming a missing root-absolute file. Any test that compiles writer or engine output outside a builder outdir must write `deps.typ` at its compile root, using `render_default_deps()`.
- Rewrite `tests/test_preview_version_sync.py` in place as the single-source gate. Add a grep-equivalent of SC1 over `typsphinx/**/*.py` and `typsphinx/**/*.typ`, plus the no-`codly-init`/`codly(languages:` check on `writer.py`, `template_engine.py`, and `typsphinx/templates/base.typ`. Add a test that builds a project and asserts the built `<outdir>/_typsphinx/deps.typ` equals `render_default_deps()` and contains exactly one `#import "<spec>": <items>` line per `DEFAULT_PACKAGES` entry, in order. Keep `test_example_templates_match_canonical_versions` alive, but compare example pins against `DEFAULT_PACKAGES`; T004 replaces it.
- New `tests/test_deps_output_gate.py` (fixtures under `tests/fixtures/deps_output_gate/`, built in tmp dirs with `sys.executable -m sphinx`) covers four things. (a) The SC2 default output tree over the content-file route, an explicit-template wrapper route, and a `typst_package`-only wrapper route. (b) E3. (c) The `_typsphinx` reservation. (d) The inline-route compile.
- Do not change `typst_package` / `typst_package_imports` (veto), the translator, `pdf.py`, the template bundle copy, or any default version. Do not add the `typst_dependencies` config value (that is T002).

## Interface contract

- K1 — Module `typsphinx/typst_deps.py` (leaf; no typsphinx-internal imports) exports: `DEPS_OUTPUT_DIR = "_typsphinx"`, `DEPS_FILENAME = "deps.typ"`, `DEPS_IMPORT_PATH = "/_typsphinx/deps.typ"`, `INIT_FUNCTION_NAME = "typsphinx-init"`; `@dataclass(frozen=True) class PreviewPackage` with fields `spec: str` (e.g. `"@preview/codly:1.3.0"`) and `items: str` (e.g. `"*"`, `"mi, mitex"`, `"render"`) and read-only properties `name: str` (e.g. `"codly"`) and `version: str` (e.g. `"1.3.0"`); `DEFAULT_PACKAGES: tuple[PreviewPackage, ...]` ordered codly, codly-languages, mitex, gentle-clues, diagraph; `render_default_deps() -> str` (the full default `deps.typ` text); `deps_preamble_lines() -> list[str]` returning exactly `['#import "/_typsphinx/deps.typ": *', '#show: typsphinx-init']`.
- K2 — `TypstBuilder._write_dependencies_file(self) -> None` in `typsphinx/builder.py` is called as the first statement of `TypstBuilder.finish()`, before `copy_image_files()` and `_copy_used_template_bundles()`; it creates `<outdir>/_typsphinx/` and writes `<outdir>/_typsphinx/deps.typ` on every build; after it returns, that file holds the exact bytes of the effective dependencies file.
- K3 — Every `typst`/`typstpdf` build's outdir contains `<outdir>/_typsphinx/deps.typ`, imported by the root-absolute path `/_typsphinx/deps.typ` (compile root = outdir). The default file exports `codly`, `codly-init`, `codly-languages`, `mi`, `mitex`, `render`, `abstract`, `danger`, `error`, `info`, `memo`, `notify`, `task`, `tip`, `warning`, and `typsphinx-init`. Every content `.typ` and wrapper `.typ` contains the lines `#import "/_typsphinx/deps.typ": *` and `#show: typsphinx-init`.

## Intent coverage

- SC1
- SC2

## Acceptance criteria

1. SC1: `grep -rlE --include='*.py' --include='*.typ' '@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):' typsphinx/` prints exactly `typsphinx/typst_deps.py`. `typsphinx/writer.py`, `typsphinx/template_engine.py`, and `typsphinx/templates/base.typ` contain no such literal and no `codly-init` or `codly(languages:` line. `tests/test_preview_version_sync.py` asserts both, and asserts that a built `<outdir>/_typsphinx/deps.typ` equals `render_default_deps()` and holds one `#import "<spec>": <items>` line per `DEFAULT_PACKAGES` entry (codly 1.3.0, codly-languages 0.1.10, mitex 0.2.7, gentle-clues 1.3.1, diagraph 0.3.7), in order.
2. SC2: a default `typst` build writes `<outdir>/_typsphinx/deps.typ` that imports the five packages at the default versions and defines `typsphinx-init`. Every content `.typ` and wrapper `.typ` in the output carries both preamble lines (K3) and contains no `@preview/<five>:` literal. This holds on the content-file, explicit-template, `typst_package`-only, and default-template routes, proven in `tests/test_deps_output_gate.py`.
3. SC2: `examples/basic`, `examples/advanced`, and `docs/source` each build with `-b typstpdf` to a PDF, checked in Verify. The render gates for codly code blocks with highlights, admonitions, inline/block math, and graphviz (`tests/test_template_codly.py`, `tests/test_template_mitex.py`, `tests/test_graphviz_render_gate.py`, `tests/test_diagraph_escaping_render_gate.py`, `tests/test_preview_smoke_gate.py`, and the golden gates) pass with only import/init-shape assertions changed. Each golden's diff removes exactly the old eleven-line block and inserts exactly the new preamble; no other line changes.
4. E3 (held-out, ruling "a document with no code block, math, admonition, or graphviz still imports `/_typsphinx/deps.typ` and applies `typsphinx-init` (imports stay unconditional)"): `tests/test_deps_output_gate.py` builds a fixture whose only document is plain paragraphs, and asserts that both its content file and its wrapper contain both preamble lines.
5. A docname whose output path's first segment folds to `_typsphinx` (for example `_typsphinx/deps`, `_Typsphinx/x`) stops the build with an `ExtensionError` naming the reserved directory, and no `.typ` file is written. `_typsphinxes/x` is not refused.
6. The inline-default-template route's `TemplateEngine.render()` output compiles under `typst-py` with `deps.typ` at the compile root, and `#show: typsphinx-init` appears exactly once in every route's output, per `tests/test_template_engine.py`. If the duplicate import did not compile, the Log records the measurement and the runner-up fallback.
7. Every test file in `files` passes under `LC_ALL=C`.

Note on the docs build: the project docs' `changelog.typ` renders CHANGELOG.md history prose, which quotes old pins such as `@preview/codly:1.3.0` as escaped text. That text is not an import. For `docs/source` output the SC2 "no `@preview/<five>:` literal" check is therefore applied as "no `#import "@preview/<five>:` line". For `examples/basic`, `examples/advanced`, and the test fixtures it is applied as the plain literal grep.

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && test "$(grep -rlE --include='*.py' --include='*.typ' '@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):' typsphinx/)" = "typsphinx/typst_deps.py" && ! grep -nE 'codly-init|codly\(languages' typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ && LC_ALL=C uv run pytest tests/test_deps_output_gate.py tests/test_preview_version_sync.py tests/test_desc_rubric_decoupling_render_gate.py tests/test_inline_image_separator_render_gate.py tests/test_diagraph_escaping_render_gate.py tests/test_empty_typst_documents_optout_gate.py tests/test_hand_compile_root_gate.py tests/test_integration_nested_toctree.py tests/test_package_only_config_gate.py tests/test_preview_smoke_gate.py tests/test_registry_prewrite_validation_gate.py tests/test_template_codly.py tests/test_template_engine.py tests/test_template_mitex.py tests/test_templates_path_collision_gate.py tests/test_two_layer_output_gate.py tests/test_config_other_options.py tests/test_graphviz_render_gate.py tests/test_signature_page_boundary_render_gate.py tests/test_output_layout_docs_gate.py -o addopts="" -q && d=$(mktemp -d) && LC_ALL=C uv run sphinx-build -q -E -b typstpdf examples/basic "$d/basic" && test -f "$d/basic/basic-example.pdf" && LC_ALL=C uv run sphinx-build -q -E -b typstpdf examples/advanced "$d/adv" && test -f "$d/adv/advanced-example.pdf" && LC_ALL=C uv run sphinx-build -q -E -b typstpdf docs/source "$d/docs" && ls "$d"/docs/*.pdf && for o in basic adv docs; do test -f "$d/$o/_typsphinx/deps.typ" || exit 1; for f in $(find "$d/$o" -name '*.typ' -not -path '*/_template/*' -not -path '*/_typsphinx/*'); do grep -qxF '#import "/_typsphinx/deps.typ": *' "$f" && grep -qxF '#show: typsphinx-init' "$f" || { echo "missing preamble: $f"; exit 1; }; done; done && ! grep -rlE '@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):' --include='*.typ' --exclude-dir=_template --exclude-dir=_typsphinx "$d/basic" "$d/adv" && ! grep -rlE '#import "@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):' --include='*.typ' --exclude-dir=_template --exclude-dir=_typsphinx "$d/docs"
```

Heavy: yes

## Log

- 2026-11-03 — created by planner
- 2026-11-03 — build_T001 (coder): implemented. New leaf `typsphinx/typst_deps.py` (K1: constants, frozen `PreviewPackage` with `name`/`version` properties plus an `import_line()` helper, `DEFAULT_PACKAGES`, `render_default_deps()`, `deps_preamble_lines()`); it is the only `.py`/`.typ` under `typsphinx/` naming a five-package spec and the only home of `codly-init`/`codly(languages:`. `writer.py` content preamble = `deps_preamble_lines()` + blank line. `template_engine.render()` emits the preamble on every route (after the optional package import, before the template import or inlined template); the CR-01 skip is gone. `base.typ` drops pins and top-level codly init, imports `/_typsphinx/deps.typ`, and never applies `typsphinx-init`. `builder.py`: `_write_dependencies_file()` is the first statement of `finish()` (`Path.write_bytes(render_default_deps().encode("utf-8"))`, single commented seam for T002's override); OUT-07 extended through new `_reserved_output_dir()` (folds via `_collision_key()`), so content/wrapper paths under `_typsphinx` fail in the same aggregated `ExtensionError` naming `'_typsphinx'` (`_template` message unchanged). Inline-route measurement: `TemplateEngine().render()` with no template_file/no package compiled under typst-py 0.15 with `deps.typ` at root (duplicate `#import "/_typsphinx/deps.typ": *` accepted; `#show: typsphinx-init` count 1); no runner-up fallback needed; pinned in `tests/test_deps_output_gate.py::TestInlineDefaultTemplateRouteCompiles`. Goldens (desc_rubric + all ten inline_image incl. `.pre_fix`) edited by exact replacement of the 11-line block + blank with the 2-line preamble + blank. Tests updated only in import/init-shape or file-count assertions; `test_integration_nested_toctree` compile root is now the outdir; hand-compile gate now expects the error to name `_typsphinx/deps.typ` (the first unresolvable root-absolute import). Side constraint found: `tests/test_repr_census_guard.py` (not in `files`) pins line numbers in `test_registry_prewrite_validation_gate.py` and `test_template_engine.py`, so edits there keep line counts unchanged before those sites. Verify (task command, verbatim): pass — uv sync ok, SC1 grep = `typsphinx/typst_deps.py`, no codly init in the three sites, 277 passed, examples/basic, examples/advanced, docs/source built typstpdf PDFs, preamble present in every emitted `.typ`, no forbidden `@preview` literal/import. Extra: `LC_ALL=C uv run pytest tests/` 1762 passed / 1 skipped / 0 failed; black --check, ruff, mypy clean.
- 2026-11-03 — orchestrator Verify (sidecar gsd-path-verify/task-t001-verify): pass, exit 0; output tail:
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
   + typsphinx==0.9.8 (from file:///home/yuta/.gsd-path/projects/4018706f853274cd7713143cf7ba094e230867e5ad2bfc5891d0cd69027eb98b/4b529697c911aff5766d6b9c03f122ba2ed9565d87a00e2f51ea62f3fd0642ec/verify/task-t001-verify)
   + typst==0.15.0
   + urllib3==2.7.0
   + uv==0.13.6
   + virtualenv==21.5.1
  WARNING: html_static_path entry '_static' does not exist
  ```
