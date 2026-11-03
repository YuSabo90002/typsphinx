# Archive — 002-externalize-typst-deps

Milestone: externalize-typst-deps
Shipped: 2026-11-03
Final verdict: all criteria met; project verify passed
Waves: 2  Tasks: 5 done / 5 total  Review cycles used: 1/1
Carried forward: none

## Success criteria at ship

| Criterion | Verdict | Evidence |
|-----------|---------|----------|
| Single version source: under `typsphinx/` (all `.py` and `.typ` files, `templates/base.typ` included), `grep -rnE '@preview/(codly\|codly-languages\|mitex\|gentle-clues\|diagraph):' typsphinx/` matches only the one Python module that defines the default specs; `typsphinx/writer.py`, `typsphinx/template_engine.py`, and `typsphinx/templates/base.typ` contain no such literal and no `codly-init` / `codly(languages:` initialisation lines; a test asserts the generated `deps.typ` content equals the definitions in that module. | met | typsphinx/typst_deps.py:66-70; tests/test_preview_version_sync.py; .project/build/verify-ledger.jsonl (commit 92714623); .project/review/final-gap-1.md |
| Generated output tree, default (no `typst_dependencies`): a `typst` build writes `<outdir>/_typsphinx/deps.typ` that imports the five packages at the default versions and defines `typsphinx-init`; every content `.typ` and every wrapper `.typ` in the output imports `/_typsphinx/deps.typ`, applies `#show: typsphinx-init`, and contains no `#import "@preview/<five>:...` line (escaped body text that quotes such a spec, e.g. CHANGELOG history rendered into `changelog.typ`, is not an import) (C2); `examples/basic`, `examples/advanced`, and the project docs build with `typstpdf` to a PDF, and the existing render-gate tests (codly code blocks with highlights, admonitions, inline/block math, graphviz) pass unchanged in what they assert about rendered output. | met | .project/plan/PLAN.md Surface contract "generated Typst output tree"; tests/test_typst_dependencies_gate.py; tests/test_deps_output_gate.py; .project/review/wave-1.cycle1.md (T001/AC3); .project/build/verify-ledger.jsonl (92714623) |
| Generated output tree, override: with `typst_dependencies = "<srcdir-relative path>"`, the build copies that one file byte-identical to `<outdir>/_typsphinx/deps.typ` and generates no default file; a fixture whose own `deps.typ` uses a different, compiler-compatible version of one package (e.g. gentle-clues 1.3.0) builds with `typstpdf`, and its content files and wrappers import only `/_typsphinx/deps.typ`. A `typst_dependencies` path that does not exist stops the build with an error naming the configured value. | met | tests/fixtures/typst_dependencies_override/; tests/test_typst_dependencies_gate.py; .project/review/wave-1.cycle1.md (T002) |
| sphinx-build console output, drift warning: when any `.typ` file in a used template bundle contains `@preview/<one of the five>:<version>` with a version different from that package's version in the effective `deps.typ` (the user's file when `typst_dependencies` is set, else the defaults), the build prints one warning per (file, package) naming the file, the package, the template's version and the `deps.typ` version, and still exits 0; with matching versions, or no such import, no warning is printed. | met | typsphinx/builder.py `_warn_template_dependency_drift`; tests/test_template_dependency_drift_gate.py; .project/review/wave-2.cycle1.md (T003) |
| In-repo templates: `grep -rnE '@preview/(codly\|codly-languages\|mitex\|gentle-clues\|diagraph):' docs/source/_typst/ examples/ tests/fixtures/admonition_greyscale_probe/_templates/ tests/fixtures/typst_lang_gate/` prints nothing; those templates either import nothing from the five or import names from `/_typsphinx/deps.typ`; the docs `typstpdf` build and the examples still build. | met | tests/test_preview_version_sync.py; .project/review/wave-2.cycle1.md (T004) |
| Documentation surface: the configuration page documents `typst_dependencies` (path rule, single global file, verbatim copy, default when unset); a page lists the public `deps.typ` contract — the path `/_typsphinx/deps.typ`, every exported name (`codly`, `codly-init`, `codly-languages`, `mi`, `mitex`, `render`, the gentle-clues admonition functions the translator emits, `typsphinx-init`) — and states that output with a replaced `deps.typ` is not guaranteed because the translator targets the default versions' APIs; the templates page tells template authors to take package names from `/_typsphinx/deps.typ` rather than pinning versions; CHANGELOG `[Unreleased]` records the change; CLAUDE.md's `@preview` version-sync section describes the new single source. | met | docs/source/user_guide/configuration.rst; docs/source/user_guide/templates.rst; CHANGELOG.md; CLAUDE.md:64-66; .project/review/wave-2.cycle1.md (T005) |
| On the final HEAD, `LC_ALL=C uv run pytest tests/` reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean. | met | .project/build/verify-ledger.jsonl (last line, commit 92714623); .project/review/final-gap-1.md |

## Contents

- build/evidence.json
- build/verify-ledger.jsonl
- intent/INTENT.md
- plan/PLAN.md
- research/DOCS-AUDIT.md
- research/RESEARCH.md
- research/SYNTHESIS.md
- research/evidence-codebase.md
- review/FINAL.md
- review/final-gap-1.md
- review/wave-1.cycle1.md
- review/wave-2.cycle1.md
- tasks/T001-single-source-deps-typ.md
- tasks/T002-typst-dependencies-override.md
- tasks/T003-template-dependency-drift-warning.md
- tasks/T004-in-repo-templates-drop-pins.md
- tasks/T005-document-deps-contract.md

## Notes

- none
