---
id: T001
title: Move deps.typ to codly 2.0.0, emit every code block as code-mode codly.new(raw(...)), rewrite the 1.3-era tests and document the contract change
wave: 1
deps: []
status: pending
agent: null
base: null
worktree: null
task_branch: null
files:
  - typsphinx/typst_deps.py
  - typsphinx/translator.py
  - typsphinx/templates/base.typ
  - docs/source/user_guide/templates.rst
  - docs/source/_typst/custom_template.typ
  - CHANGELOG.md
  - README.md
  - tests/test_preview_version_sync.py
  - tests/test_deps_contract_docs_gate.py
  - tests/test_deps_output_gate.py
  - tests/test_integration_basic.py
  - tests/test_translator.py
  - tests/test_pdf_render_gate.py
  - tests/test_template_codly.py
  - tests/test_codly_caption_listitem_leak_render_gate.py
  - tests/test_deflist_definition_multiblock_render_gate.py
  - tests/test_doctest_block_render_gate.py
  - tests/test_preview_smoke_gate.py
  - tests/test_template_engine.py
  - tests/test_admonitions.py
  - tests/test_typst_dependencies_gate.py
  - tests/test_template_mitex.py
  - tests/test_package_only_config_gate.py
  - tests/test_integration_advanced.py
  - tests/test_citation_caption_dangling_label_gate.py
  - tests/test_rubric_propagated_target_render_gate.py
  - tests/fixtures/codly_caption_listitem_leak_render_gate
  - tests/fixtures/codly_config_leak_render_gate
  - tests/fixtures/codly_offset_render_gate
  - tests/fixtures/deflist_definition_multiblock_render_gate
  - tests/fixtures/doctest_block_render_gate
  - tests/fixtures/preview_smoke
  - tests/fixtures/typst_dependencies_override
  - tests/fixtures/template_dependency_drift
---

# T001 — Move deps.typ to codly 2.0.0, emit every code block as code-mode codly.new(raw(...)), rewrite the 1.3-era tests and document the contract change

## Context

typsphinx pins `@preview/codly:1.3.0` in `typsphinx/typst_deps.py` (`DEFAULT_PACKAGES`, the single source) and `typsphinx-init` calls `codly-init` + `codly(languages: ...)`; `TypstTranslator.visit_literal_block` (translator.py:2433-2628, shared by `visit_doctest_block`) emits per-block `codly(number-format: none)` / `codly(offset: N)` / `codly(highlights: ...)` calls, a ``` fence, a mode-dependent `codly_prefix` `#` and list-item `{`/`#{` wrappers, and a captioned block as markup `figure(caption: [CAPTION])[...] <label>`. codly 2.0.0 (needs Typst 0.15, matching typst-py 0.15) replaces that with `codly.new(body, ..fields)` plus scoped `codly.set_` / `codly.lang-set_` show rules. SYNTHESIS settles: import codly as a module (`as codly`; `*` re-exports codly's top-level `line`, `highlight`, `info`, ... and shadows Typst builtins the translator emits), keep codly-languages 0.1.10 and the other three packages unchanged, no 1.3 shim, no global `show raw` rule (E9), codly 2.0 default look and highlight palette (C1, Q2). Once deps.typ exports a module named `codly`, every 1.3-style `codly(...)` in output fails to compile, so the deps change, the emission rewrite and the rewrite of every test asserting 1.3 strings must land together (SYNTHESIS wave-1 blocker 1). The contract docs (templates.rst export table and `typsphinx-init` paragraph, CHANGELOG breaking-change entry) are derived from `render_default_deps()` by `tests/test_deps_contract_docs_gate.py`, so they move in this task too.

## Approach

- `typst_deps.py`: codly spec `@preview/codly:2.0.0`; extend frozen `PreviewPackage` with `alias: str | None = None` (and `items` defaulting to `""`), validate in `__post_init__` that exactly one of `items` / `alias` is set (ValueError otherwise); `import_line()` returns `#import "SPEC" as ALIAS` when aliased, the existing `#import "SPEC": ITEMS` otherwise. Codly entry: `PreviewPackage(spec="@preview/codly:2.0.0", alias="codly")`. `_INIT_FUNCTION` body becomes the single rule `show: codly.lang-set_(languages: codly-languages)` then `body`, multi-line as today. No `codly-init`, no `codly.set_` defaults, no `codly.highlight-set_`, no `show raw` rule. The spec literal stays only in this module; `_PREVIEW_PIN_RE` needs no change. Update the module docstring.
- Translator: rewrite `visit_literal_block` to emit exactly the Interface-contract expression once from `node.astext()` through the existing `escape_typst_string` (translator.py:158; not the inline-literal zero-width-space variants), then perform the `depart_literal_block` bookkeeping inline (list-item `list_item_needs_separator`, captioned-state cleanup as today) and `raise nodes.SkipNode`, so parsed-literal children are never visited (their inline markup is flattened to text) and `visit_Text`'s `in_literal_block` passthrough is no longer reached for code blocks. Delete the fence, `codly_prefix` / `in_markup_context`, and the list-item `{` / `#{` wrapper; keep `_emit_id_anchors(node)` and the list-item leading separator. Keep the `linenos` / `linenostart != 1` guard (literalinclude always sets `linenostart`); `0` → `offset: -1`, `1000` → `offset: 999`. `highlighted` = `sorted(set(hl_lines))`, each plus `linenostart - 1` only when an offset is emitted (codly 2.0 keys `highlighted` by DISPLAYED numbers; current 1.3 output highlights nothing for `:lineno-start: 10` + `:emphasize-lines: 2`); a single entry keeps its trailing comma. Language: `""`, `"none"`, `"default"` → `lang` omitted; doctest_block with no language → `"python"` (D-02/D-03 node-class fallback, `highlight_language` not followed); anything else passed through. `skip-last-empty: false` only when `node.astext().strip() == ""`.
- Captioned path (`visit_container` sets `code_block_caption` from `caption.astext()`): emit `figure(<codly.new expr>, caption: text("<escape_typst_string(caption)>"), kind: raw)` in code mode. Do not attach a `<label>` to the figure (codly 2.0 then emits one hidden `codly-line` figure per line) and do not set `block-label`; the `:name:` stays anchored by the `[#metadata(none) <label>]` that `visit_container` already emits through `_emit_id_anchors`. A caption containing `]`, `#` or `$` must render verbatim (today `]` aborts the compile).
- Docstrings/comments: replace the 1.3 rationale comments with the 2.0 mapping. `typsphinx.translator` (and builder/writer/pdf/template_engine) are rendered by `docs/source/api/index.rst` automodule, so no docstring in those modules may contain a ``` run or a bare `codly(` (SC2's absence grep runs over docs/source output in T002). Code comments (`#`) are not rendered, but this task's Verify greps `typsphinx/translator.py` for any ``` run and for `codly_prefix`, so write neither anywhere in that file (say "markup fence" instead).
- Tests: rewrite every assertion of 1.3 output (grep `codly(`, `number-format`, `codly-init`, ```` ``` ````, `codly_prefix`, `codly:1.3.0`, `#{` around code blocks) to the new shape; keep the leak/nesting gates (`test_codly_caption_listitem_leak_render_gate.py`, the `codly_config_leak_render_gate` and `codly_offset_render_gate` tests in `test_pdf_render_gate.py`, `test_deflist_definition_multiblock_render_gate.py`, `test_doctest_block_render_gate.py`) and re-point them at the new invariant (no ```, no bare `codly(`, PDF compiles, no leaked config text in PDF text) — do not delete them. `test_preview_version_sync.py` compares import lines against `package.import_line()` and a literal list showing `#import "@preview/codly:2.0.0" as codly`. `test_deps_contract_docs_gate.py`'s export derivation must understand the `as` form (export `codly`, no `codly-init`). Migrate `tests/fixtures/typst_dependencies_override/deps/my-deps.typ` to the 2.0 shape (`as codly`, `codly.lang-set_`) because emitted `codly.new` needs `codly` to be a module; `tests/fixtures/template_dependency_drift/user_deps.typ` may keep its deliberate 1.3.0 pin only if no test compiles it. Fixture prose/comments describing 1.3 behaviour are updated where they would now mislead. The full list in `files` is the measured candidate set; any other test the full-suite run shows asserting 1.3 emission is a plan gap — report it as `NEEDS-ORCHESTRATOR` rather than editing an unlisted file.
- Docs: `templates.rst` export table codly row → version 2.0.0 (the row format `   * - codly\n     - 2.0.0\n` is gated) and exported name ``codly`` (a module: `codly.new`, `codly.set_`, `codly.lang-set_`, ...); `typsphinx-init` paragraph → registers `codly-languages` through `codly.lang-set_`, installs no raw→codly rule; add a migration note for templates that imported `codly` / `codly-init` from deps.typ (use `codly.new(...)` / `show: codly.set_(...)`; user `typst_dependencies` files must import codly ` as codly`); check the `#import "/_typsphinx/deps.typ": info, codly` example (templates.rst:186) still holds. `CHANGELOG.md` `## [Unreleased]` gets a breaking-change entry (no version or release section — release is vetoed) with: codly 2.0.0 upgrade; `codly-init` and the state-style codly calls are gone, templates use `codly.new(...)` / `codly.set_`; `typst_dependencies` files must import codly ` as codly`; raw blocks written by users (custom templates, `.. raw:: typst`) are no longer rendered through codly by `typsphinx-init` (E9); code blocks are now emitted as code-mode `codly.new(raw(...))` expressions; known limitation: form feed / vertical tab / NEL / U+2028 in code split raw lines (no transformation, E2/C4). Prefer wording that avoids the literal `codly(` (e.g. "state-style `codly` configuration calls") so T002's changelog exemption does not grow. `README.md:25` names `@preview/codly:1.3.0` — update to 2.0.0. `templates/base.typ` and `docs/source/_typst/custom_template.typ` only need comment wording if it now misleads (they import deps.typ `*` and carry no codly code).
- Vetoes: no 1.3-compatibility shim or `codly-init` alias, no recreation of 1.3 styling (`fill: yellow` dropped), no global raw→codly rule, no version bump/release section, no bump of mitex, gentle-clues, diagraph or codly-languages.
- Tests stay OS-neutral (CI ubuntu/windows/macos): compare text and structure, never native paths or ANSI/colour codes; run warning-text tests under `LC_ALL=C`.

## Interface contract

- deps.typ (generated by `render_default_deps()`), import and init lines, exactly:
  - `#import "@preview/codly:2.0.0" as codly`
  - `#import "@preview/codly-languages:0.1.10": *` (other three import lines unchanged)
  - `#let typsphinx-init(body) = {` / `  show: codly.lang-set_(languages: codly-languages)` / `  body` / `}`
- One code block (literal_block or doctest_block), one code-mode expression, no leading `#`, no ``` fence, no `{`/`#{` wrapper, followed by a newline:
  `codly.new(raw("ESC", block: true[, lang: "LANG"])[, number-enabled: false][, offset: OFF][, highlighted: (H1, H2, ...)][, skip-last-empty: false])`
  - `ESC` = `escape_typst_string(node.astext())`
  - `, lang: "LANG"` omitted when the language is `""`, `"none"` or `"default"`; doctest_block without a language → `lang: "python"`
  - `number-enabled: false` iff `node["linenos"]` is false
  - `offset: OFF` with `OFF = linenostart - 1` iff linenos is true and `highlight_args["linenostart"]` is set and `!= 1`
  - `highlighted:` iff `hl_lines` is non-empty: `sorted(set(hl_lines))`, each plus `OFF` when an offset is emitted, separated by `, `; a single entry is `(K,)`
  - `skip-last-empty: false` iff `node.astext().strip() == ""`
  - named arguments appear in the order above
- Captioned code block (literal-block-wrapper container): `figure(<the codly.new expression>, caption: text("ESC_CAPTION"), kind: raw)` with `ESC_CAPTION = escape_typst_string(caption.astext())`; the figure carries no `<label>`; a `:name:` is anchored only by the `[#metadata(none) <LABEL>]` that `visit_container` emits before it.

## Intent coverage

- SC1
- SC6

## Acceptance criteria

1. SC1: `DEFAULT_PACKAGES` names `@preview/codly:2.0.0`; a `typst` build of `tests/roots/test-basic` writes `_typsphinx/deps.typ` whose codly import line is `#import "@preview/codly:2.0.0" as codly` and whose `typsphinx-init` contains no `codly-init`, no state-setting `codly(` call and no `show raw` rule (E9); `tests/test_preview_version_sync.py` passes, with the five specs appearing only in `typsphinx/typst_deps.py`.
2. Every literal_block and doctest_block the translator emits matches the Interface-contract grammar; the translator source no longer emits ``` or a bare `codly(` for code blocks, and `codly_prefix` and the list-item `{`/`#{` code-block wrapper are gone.
3. A captioned code block emits `figure(codly.new(...), caption: text("..."), kind: raw)` with the caption string-escaped and no label on the figure; a caption containing `]`, `#` and `$` compiles.
4. Every rewritten leak/nesting gate (captioned list item, config leak, offset, deflist multi-block, doctest) still builds its fixture to PDF and asserts no ``` and no bare `codly(` in its `.typ` and no leaked configuration text in its PDF text; none of those gates was deleted.
5. `tests/fixtures/typst_dependencies_override/deps/my-deps.typ` imports codly ` as codly` and its build compiles; no test compiles a file that imports codly 1.3.0.
6. SC6: `docs/source/user_guide/templates.rst` lists codly 2.0.0 exporting the module ``codly`` (no ``codly-init`` export), describes `typsphinx-init` as registering `codly-languages` through `codly.lang-set_` with no raw→codly rule, and carries a migration note for templates that imported `codly`/`codly-init`; `CHANGELOG.md` `## [Unreleased]` records the codly 2.0.0 upgrade as a breaking change with that migration note and states that user-written raw blocks (custom templates, `.. raw:: typst`) are no longer rendered through codly by `typsphinx-init`; the built HTML Templates page shows the 2.0.0 row and `codly.lang-set_`; `tests/test_deps_contract_docs_gate.py` passes against the new export list.
7. `README.md` no longer names `@preview/codly:1.3.0`.
8. On this task's tree `LC_ALL=C uv run pytest tests/` (dev + docs extras installed) reports 0 failed, and `black --check`, `ruff check` and `mypy typsphinx/` are clean.

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && LC_ALL=C uv run pytest tests/test_preview_version_sync.py tests/test_deps_contract_docs_gate.py tests/test_translator.py tests/test_pdf_render_gate.py tests/test_template_codly.py tests/test_codly_caption_listitem_leak_render_gate.py tests/test_deflist_definition_multiblock_render_gate.py tests/test_doctest_block_render_gate.py tests/test_preview_smoke_gate.py tests/test_typst_dependencies_gate.py -o addopts="" -q && grep -q '"@preview/codly:2.0.0"' typsphinx/typst_deps.py && ! grep -nE '`{3}|codly_prefix' typsphinx/translator.py && ! grep -q 'codly:1.3.0' README.md && T=$(mktemp -d) && LC_ALL=C uv run sphinx-build -q -E -b html docs/source "$T/html" && grep -q '2.0.0' "$T/html/user_guide/templates.html" && grep -q 'lang-set_' "$T/html/user_guide/templates.html" && LC_ALL=C uv run pytest tests/ && uv run black --check typsphinx tests && uv run ruff check typsphinx tests && uv run mypy typsphinx/
```

Heavy: yes

## Log

- 2026-11-03 — created by planner
- 2026-11-03 — build_T001: NEEDS-ORCHESTRATOR: may T001 edit `tests/test_deps_output_gate.py` and `tests/test_integration_basic.py` (both absent from `files`), which the full-suite run shows asserting 1.3-era output? — readings: (a) add both to T001 `files` and redispatch; the fixes are mechanical: `test_deps_output_gate.py:102` `_assert_default_deps` builds `f'#import "{package.spec}": {package.items}'`, which must become `package.import_line()` (6 failures), and `test_integration_basic.py:185` asserts unescaped fence text `'print("Hello, World!")'` while the code is now a string literal (`print(\"Hello, World!\")`) (1 failure); (b) leave them to another task, so T001's AC8 and Verify `pytest tests/` cannot pass on this tree.
  - Implemented (all within `files`): `typst_deps.py` codly `@preview/codly:2.0.0` `alias="codly"` (`PreviewPackage.alias` + `__post_init__` exactly-one validation, `import_line()` `as` form); `typsphinx-init` = `show: codly.lang-set_(languages: codly-languages)` + `body`. `translator.visit_literal_block` emits the Interface-contract `codly.new(raw("ESC", block: true[, lang]), [number-enabled: false][, offset][, highlighted][, skip-last-empty: false])` + newline, then raises SkipNode; captioned → `figure(<expr>, caption: text("ESC"), kind: raw)`, no label on the figure; fence, `codly_prefix`, list-item `{`/`#{` wrapper, `in_literal_block` passthrough and dead `code_block_label` removed; `depart_literal_block` is now a no-op. templates.rst row/`typsphinx-init` paragraph/migration note; CHANGELOG Unreleased breaking entry (no literal `codly(`); README pin → 2.0.0; base.typ/custom_template.typ comment wording. Tests rewritten for the new shape (translator, pdf_render_gate offset/config-leak gates, caption-listitem, deflist, doctest, preview_smoke, template_codly, preview_version_sync, deps_contract_docs_gate, admonitions, integration_advanced, typst_dependencies_gate); none of the leak gates was deleted; fixture prose updated; `typst_dependencies_override/deps/my-deps.typ` migrated to `as codly` + `codly.lang-set_`; `template_dependency_drift/user_deps.typ` keeps its 1.3.0 pin (only built with `-b typst`, never compiled).
  - Verify (run in primary checkout, LC_ALL=C): uv sync dev+docs OK; listed pytest subset 230 passed; codly 2.0.0 grep OK; no ``` / `codly_prefix` in translator.py; README has no `codly:1.3.0`; HTML templates page has `2.0.0` and `lang-set_`; `pytest tests/` → 7 failed, 1838 passed, 1 skipped (all 7 in the two unlisted files above) → Verify exit 1. Run separately after: `black --check typsphinx tests` clean, `ruff check typsphinx tests` clean, `mypy typsphinx/` clean.
- 2026-11-03 — Orchestrator answer: (a) — both files are added to T001 `files` as a documented plan defect repair; T001 AC8 and INTENT SC9 require `pytest tests/` to pass on this landing, SYNTHESIS decision "Existing tests and fixtures that encode 1.3 output" assigns 1.3-era test rewrites to the emission task, and neither file is declared by T002/T003. Edit them as described and rerun Verify.
- 2026-11-03 — build_T001 (redispatch after Orchestrator answer (a)): `tests/test_deps_output_gate.py` `_assert_default_deps` now compares against `package.import_line()`; `tests/test_integration_basic.py::test_generated_typ_has_code_block` asserts the escaped `print(\"Hello, World!\")` plus `codly.new(raw(`. Nothing else changed. Full task Verify rerun exactly as written (primary checkout): exit 0 — listed subset 230 passed; greps OK; HTML templates page has `2.0.0` and `lang-set_`; `LC_ALL=C uv run pytest tests/` 1845 passed, 1 skipped, 0 failed; `black --check typsphinx tests` 387 unchanged; `ruff check typsphinx tests` clean; `mypy typsphinx/` clean.
- 2026-11-03 — orchestrator Verify (sidecar gsd-path-verify/task-t001-verify): fail, exit 2; output tail:
  ```
  bash: -c: line 1: unexpected EOF while looking for matching `''
  ```
- 2026-11-03 — orchestrator plan defect repair: the Verify's literal triple-backtick grep pattern closed the Verify code fence early, so the isolate ran a truncated command (bash EOF while looking for matching quote, exit 2); the pattern is rewritten to the equivalent ERE '`{3}|codly_prefix' with no other change. No product change.
- 2026-11-03 — orchestrator Verify (sidecar gsd-path-verify/task-t001-verify): pass, exit 0; output tail:
  ```
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
  All done! ✨ 🍰 ✨
  387 files would be left unchanged.
  ```
- 2026-11-03 — orchestrator: `finish` refused landing ("landing allow-list differs from the base task: extra tests/test_deps_output_gate.py, tests/test_integration_basic.py") because the `files` and Verify repairs must be part of the dispatch base. Returned to pending for a fresh serial dispatch at a new base that carries both repairs. The coder's complete ready diff (30 modified paths, all declared, no untracked files) is preserved outside the repo as a patch (sha256 e8ae8cfa6fbeb9923011d072a8bef27286c14b37f3b2b3437a39e43f72c4d43c) and the primary product paths are restored to the base so the base is clean; the redispatch re-applies that diff and reruns Verify.
