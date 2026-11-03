# Intent — typsphinx

Lane: standard   <!-- several independent deliverables (single version source + deps.typ emission, typst_dependencies override, drift warning, in-repo template cleanup, docs) exceed the two-task quick bound -->

Review panel: off

Finding skeptics: off

Surfaces: sphinx-build console output, generated Typst output tree, typsphinx documentation (configuration and templates pages)

## Summary

typsphinx hard-codes the five Typst Universe `@preview` dependencies (codly, codly-languages, mitex, gentle-clues, diagraph) — their imports and the codly initialisation — in three places (`writer.py`, `template_engine.py`, `templates/base.typ`), and custom templates repeat their own copies, so versions can silently diverge inside one document and a user cannot swap package versions to test them. This milestone, a refactoring at heart, moves the version definitions to one Python location and has every build emit one shared `<outdir>/_typsphinx/deps.typ` holding the imports plus a `typsphinx-init` show function, which every content file, wrapper, and the bundled default template import instead of hard-coding versions. A new `typst_dependencies` config value (a srcdir-relative file path, mirroring `typst_template`) replaces the generated file with the user's own, copied verbatim. A build warning names any template bundle file that hard-codes one of the five packages at a version different from the effective `deps.typ`, and the repository's own templates drop their now-ineffective package imports.

## Problem

- The version-sync hazard: the same five package specs and the codly init lines live in `typsphinx/writer.py:266-274`, `typsphinx/template_engine.py:705-712`, and `typsphinx/templates/base.typ:8-29`; only `tests/test_preview_version_sync.py` keeps them in lockstep.
- Typst has no version resolution: different versions of one package load side by side. Measured on typst-py 0.15: a parent importing gentle-clues 1.2.0 that `#include`s a child importing 1.3.1 compiles with no error or warning; an old version that is incompatible with the compiler (codly 1.2.0, mitex 0.2.5) fails with an opaque `unknown variable: pattern` / `unknown variable: kai`.
- Custom templates hard-code their own pins (repo: `docs/source/_typst/custom_template.typ`, `examples/advanced/_typst/custom.typ`, test fixtures; external user gdsfactory/quantum-rf-pdk `docs/typst/qpdk.typ` pins codly 1.3.0 and caps `typsphinx<0.10`). Nothing checks user templates against typsphinx's versions.
- A maintainer or user cannot run a build against a different package version without patching typsphinx.

## Users

- typsphinx users with custom templates (e.g. quantum-rf-pdk), who need their template's package names without duplicating version pins.
- The maintainer, who wants to test typsphinx output against other package versions and bump versions in one place.
- Users who never configure anything: their output must keep rendering the same.

## Success criteria

1. Single version source: under `typsphinx/` (all `.py` and `.typ` files, `templates/base.typ` included), `grep -rnE '@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):' typsphinx/` matches only the one Python module that defines the default specs; `typsphinx/writer.py`, `typsphinx/template_engine.py`, and `typsphinx/templates/base.typ` contain no such literal and no `codly-init` / `codly(languages:` initialisation lines; a test asserts the generated `deps.typ` content equals the definitions in that module.
2. Generated output tree, default (no `typst_dependencies`): a `typst` build writes `<outdir>/_typsphinx/deps.typ` that imports the five packages at the default versions and defines `typsphinx-init`; every content `.typ` and every wrapper `.typ` in the output imports `/_typsphinx/deps.typ`, applies `#show: typsphinx-init`, and contains no `#import "@preview/<five>:...` line (escaped body text that quotes such a spec, e.g. CHANGELOG history rendered into `changelog.typ`, is not an import) (C2); `examples/basic`, `examples/advanced`, and the project docs build with `typstpdf` to a PDF, and the existing render-gate tests (codly code blocks with highlights, admonitions, inline/block math, graphviz) pass unchanged in what they assert about rendered output.
3. Generated output tree, override: with `typst_dependencies = "<srcdir-relative path>"`, the build copies that one file byte-identical to `<outdir>/_typsphinx/deps.typ` and generates no default file; a fixture whose own `deps.typ` uses a different, compiler-compatible version of one package (e.g. gentle-clues 1.3.0) builds with `typstpdf`, and its content files and wrappers import only `/_typsphinx/deps.typ`. A `typst_dependencies` path that does not exist stops the build with an error naming the configured value.
4. sphinx-build console output, drift warning: when any `.typ` file in a used template bundle contains `@preview/<one of the five>:<version>` with a version different from that package's version in the effective `deps.typ` (the user's file when `typst_dependencies` is set, else the defaults), the build prints one warning per (file, package) naming the file, the package, the template's version and the `deps.typ` version, and still exits 0; with matching versions, or no such import, no warning is printed.
5. In-repo templates: `grep -rnE '@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):' docs/source/_typst/ examples/ tests/fixtures/admonition_greyscale_probe/_templates/ tests/fixtures/typst_lang_gate/` prints nothing; those templates either import nothing from the five or import names from `/_typsphinx/deps.typ`; the docs `typstpdf` build and the examples still build.
6. Documentation surface: the configuration page documents `typst_dependencies` (path rule, single global file, verbatim copy, default when unset); a page lists the public `deps.typ` contract — the path `/_typsphinx/deps.typ`, every exported name (`codly`, `codly-init`, `codly-languages`, `mi`, `mitex`, `render`, the gentle-clues admonition functions the translator emits, `typsphinx-init`) — and states that output with a replaced `deps.typ` is not guaranteed because the translator targets the default versions' APIs; the templates page tells template authors to take package names from `/_typsphinx/deps.typ` rather than pinning versions; CHANGELOG `[Unreleased]` records the change; CLAUDE.md's `@preview` version-sync section describes the new single source.
7. On the final HEAD, `LC_ALL=C uv run pytest tests/` reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean.

## Edge coverage

| Edge | Criterion | Category | Disposition | Detail |
|------|-----------|----------|-------------|--------|
| E1 | SC1 | none | dismissed | static source check on one tree; no data shape |
| E2 | SC2 | idempotency | held-out | rebuilding (incremental or `-E`) rewrites `_typsphinx/deps.typ` with identical bytes; switching from `typst_dependencies` set to unset (or back) between builds leaves the newly effective file, never the stale one |
| E3 | SC2 | empty | held-out | a document with no code block, math, admonition, or graphviz still imports `/_typsphinx/deps.typ` and applies `typsphinx-init` (imports stay unconditional) |
| E4 | SC3 | empty | held-out | `typst_dependencies = None` (the default) means generate the default file; an empty string `""` stops the build with an error |
| E5 | SC3 | boundary | criterion SC3 | |
| E6 | SC3 | encoding | held-out | an absolute path is accepted, as for `typst_template`; the file is copied as bytes (no re-encoding, no newline changes) |
| E7 | SC4 | adjacency | held-out | an `@preview/` import of a package outside the five is ignored; a `@local/` or other-namespace import of one of the five is ignored |
| E8 | SC4 | ordering | held-out | the same mismatch in two bundle files gives two warnings, one per file; two mismatched packages in one file give two warnings; warnings are emitted in sorted (file, package) order |
| E9 | SC4 | empty | held-out | when the user's `deps.typ` has no version for a package, that package is not compared and no warning is printed for it |
| E10 | SC4 | encoding | held-out | comments are excluded from the scan: a pin that appears only inside a `//` line comment or a `/* */` block comment does not warn |
| E11 | SC5 | none | dismissed | static path check over named directories |
| E12 | SC6 | none | dismissed | documentation text; no data shape |
| E13 | SC7 | none | dismissed | read-only checks on one HEAD |

## Prohibitions

| Prohibition | Criterion | Must not | Disposition | Detail |
|-------------|-----------|----------|-------------|--------|
| N1 | SC2 | silently change the rendered output of a project that configures nothing | criterion SC2 | |
| N2 | SC4 | break an existing user's build because their template pins a different version | criterion SC4 | |
| N3 | SC3 | modify the user's `deps.typ` or template files on copy | criterion SC3 | |
| N4 | SC6 | promise that a replaced `deps.typ` with other versions produces correct output | judgment | the docs state plainly that only the default versions are supported and a replaced file is at the user's risk |
| N5 | SC1 | none | dismissed | internal source layout; affects no user's output |
| N6 | SC5 | none | dismissed | repository-owned templates only; their rendered output is covered by N1/SC2 |
| N7 | SC7 | none | dismissed | read-only quality checks |

## Scope: in

- One Python module holding the five default package specs; `writer.py`, `template_engine.py`, `templates/base.typ` stop hard-coding imports and codly init (SC1).
- Emit `<outdir>/_typsphinx/deps.typ` (imports + `typsphinx-init`); content files, wrappers, and the default template import it and apply `#show: typsphinx-init` (SC2).
- `typst_dependencies` config value: srcdir-relative (or absolute) path to one file, copied verbatim; global, not per template (SC3).
- Build-time drift warning over used template bundle `.typ` files against the effective `deps.typ` (SC4).
- Remove the five-package imports from the repository's own templates (docs, examples, test fixtures) (SC5).
- Documentation, CHANGELOG, CLAUDE.md updates (SC6).
- Update the tests that pin the old shape (version-sync gate, goldens that contain the old import block) (SC7).

## Scope: out (vetoes)

- Renaming `typst_package` / `typst_package_imports` — "改名問題は一旦新規に追加するパッケージ搦みの設定が消失したので、放置すべきだと思った" (the motivating name collision disappeared with the file-path design).
- A conf.py dict of versions or a conf.py preamble string — owner chose the file-path form ("B方式: ファイルパス指定").
- Per-template `deps.typ` (a `typst_document_templates` entry key) — content files are shared across wrappers, so one global file only.
- Copying a `deps.typ` bundle directory — "コピー範囲: ファイル1つ".
- Rewriting import lines inside user templates on copy — templates stay copied verbatim.
- Making the drift check an error — owner ruling "2.警告".
- Version-dependent branches in the translator, a public Python API for package versions, registration of extra packages through config, and importing only the packages a file uses.

## Constraints

- Python 3.12+; black/ruff/mypy clean as CI runs them; CI matrix py312/py313.
- `/_typsphinx/deps.typ`, its exported names, and `typsphinx-init` become a public contract (owner ruling "1.公開の約束にする"); external users exist (gdsfactory/quantum-rf-pdk).
- Template bundles keep being copied wholesale and unmodified to `<outdir>/_template/<key>/`.
- Test commands that assert warning text run under `LC_ALL=C`.
- Integration mode is `pull-request`: Path opens the PR, the owner merges; PR checks and merge are observed at integration, not judged as criteria.
- LESSONS: check `git check-ignore` against `.project/` paths at planning time; criteria must be observable at the final-review HEAD before integration.

## Current state (brownfield only)

- **What exists**: typsphinx 0.9.8, Sphinx extension with `typst`/`typstpdf` builders (Sphinx ≥9.1, docutils, typst-py 0.15). Builder → writer → translator layering; content `.typ` per docname with unconditional imports, wrapper per `typst_documents` entry applying the template and `#include`-ing content. Baseline at 79ed090e: 1731 passed / 18 skipped / 0 failed (CPython 3.14 sidecar), black/ruff/mypy clean.
- **Measured Typst facts**: imported names do not cross `#include` (`unknown variable: codly|info|mi|render` when a content file lacks its own import); show rules applied inside a template function do reach included content, top-level show rules in a template file do not; re-exporting through a shared `deps.typ` works; a `typsphinx-init` show function exported from `deps.typ` applies codly in both wrapper and included content.
- **Must not break**: rendered output of unconfigured projects; verbatim template bundle copy; `typst_package` / `typst_template` / `typst_document_templates` routes; the translator's emitted API calls.
- **Doc-vs-code rulings**: DOCS-AUDIT queue #1 (`docs/S04-PUBLISHED-SITE-EVIDENCE.md`, live readthedocs.org claim, unverifiable) → accept-drift — "S04はaccept-drift".
- **Ground truth**: `.project/research/evidence-codebase.md`, `.project/research/DOCS-AUDIT.md`

## Risks

- Goldens and gate tests under `tests/fixtures/` assert the old per-file import block; many will change, and a careless regeneration could hide a real rendering change (N1).
- `tests/fixtures/typst_lang_gate/srcdir_shadow_lang/_typst/base.typ` is a deliberate copy of `base.typ`; changing it must keep that test's meaning.
- Root-absolute `/_typsphinx/deps.typ` assumes the Typst compile root is the outdir, as the existing `/_template/...` import already does.
- The regex drift scan cannot see dynamically built import strings or imports reached through other files (accepted: warning is a best-effort aid).

## Open questions

- none

## Corrections

- C1 2026-11-03: "E10はコメント除外"
- C2 2026-11-03: "1. SC2 の文言を「#import \"@preview/<five>:... 行がない」に修正する（推奨）。"

