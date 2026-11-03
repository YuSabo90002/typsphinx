# Plan — typsphinx

<!-- Written by the planner role. Executed wave-by-wave by /gsd-path-build. -->

Project verify: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev && LC_ALL=C uv run pytest tests/ && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/`

## Config

- max_review_cycles: 3
- wave_budget: none
- review_panel: off
- finding_skeptics: off

## Wave 1 — risk burn-down and single-source skeleton

Goal: Land the single version source (`typsphinx/typst_deps.py`) and the generated `<outdir>/_typsphinx/deps.typ` with the two-line preamble in every content file, wrapper, and the bundled `base.typ` (T001). Then layer the `typst_dependencies` override on top (T002). This wave settles both SYNTHESIS "Still unknown" items. First, T001 compiles the legacy inline-default-template route, which repeats `#import "/_typsphinx/deps.typ": *`. A planning-time probe on typst-py 0.15.0 compiled cleanly; T001 re-proves it in its sidecar. If it fails, T001 falls back to the SYNTHESIS runner-up: no preamble on the inline route. Second, T002 compiles the SC3 override fixture with gentle-clues 1.3.0. A planning-time probe compiled all nine translator-emitted functions under typst-py 0.15.0 from the local package cache; T002 re-proves this where packages are fetched. If 1.3.0 fails, T002 picks another compiler-compatible gentle-clues release and records the measurement; the plan does not change. If `#show: typsphinx-init` does not reproduce today's codly rendering in `#include`d content, the render gates in T001's Verify fail, and the init mechanism must be re-decided before wave 2.
Review depth: full

## Wave 2 — drift warning, in-repo template cleanup, documentation

Goal: Add the build-time drift warning over the `.typ` files of used template bundles, checked against the effective `deps.typ` (T003). Remove the five-package pins from the repository's own templates and samples (T004). In parallel, T003 and T004 have disjoint files. Then document the new public contract and prove the final-HEAD quality bar (T005, after T003 and T004 land).
Review depth: full

## Surface contract

### generated Typst output tree — T002

Criteria: SC2, SC3
Entry: `LC_ALL=C uv run sphinx-build -E -b typst <srcdir> <outdir>` (or `-b typstpdf`), then list `<outdir>` and open `<outdir>/_typsphinx/deps.typ`, a content `.typ`, and a wrapper `.typ`
States: empty — a project whose only document has no code block, math, admonition, or graphviz still gets `<outdir>/_typsphinx/deps.typ`, and its content file and wrapper still carry `#import "/_typsphinx/deps.typ": *` and `#show: typsphinx-init` (E3); loading — normal Sphinx progress lines, then `typst: wrote N wrapper file(s)`; error — when `typst_dependencies` names a missing file or is `""`, the build exits non-zero with an error starting `typst_dependencies:` that names the configured value, and no `.typ` file is written; success — `_typsphinx/deps.typ` holds the generated default (five `#import` lines plus `#let typsphinx-init`) or, with `typst_dependencies` set, a byte-identical copy of the user's file; every content and wrapper `.typ` imports `/_typsphinx/deps.typ`, applies `#show: typsphinx-init`, and carries no `@preview/<five>:` literal; `-b typstpdf` writes the PDF.
Walkthrough:
1. In a fresh worktree run `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`.
2. Run `d=$(mktemp -d); LC_ALL=C uv run sphinx-build -E -b typstpdf examples/basic "$d/basic"`, then confirm `"$d/basic/basic-example.pdf"` exists and `cat "$d/basic/_typsphinx/deps.typ"` shows `@preview/codly:1.3.0`, `@preview/codly-languages:0.1.10`, `@preview/mitex:0.2.7`, `@preview/gentle-clues:1.3.1`, `@preview/diagraph:0.3.7` and `#let typsphinx-init`.
3. Run `head -3 "$d/basic/index.typ" "$d/basic/basic-example.typ"` and see `#import "/_typsphinx/deps.typ": *` and `#show: typsphinx-init` in both. Then confirm `grep -rlE '@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):' --include='*.typ' --exclude-dir=_typsphinx --exclude-dir=_template "$d/basic"` prints nothing.
4. Copy `tests/fixtures/typst_dependencies_override` to `"$d/p"` and build it with `-b typstpdf` into `"$d/out"`. Confirm that `cmp "$d/p/deps/my-deps.typ" "$d/out/_typsphinx/deps.typ"` is silent, that the PDF exists, and that `grep gentle-clues "$d/out/_typsphinx/deps.typ"` shows `1.3.0`.
5. Append `typst_dependencies = "missing/deps.typ"` to `"$d/p/conf.py"` and build again into a new outdir. Confirm a non-zero exit, a stderr line starting `typst_dependencies:` that names `missing/deps.typ`, and no `.typ` file in the new outdir.

### sphinx-build console output — T003

Criteria: SC4
Entry: `LC_ALL=C uv run sphinx-build -b typst <srcdir> <outdir>` on a project whose template bundle pins one of the five packages
States: empty — a project whose bundle `.typ` files import none of the five (or pin them only inside `//` or `/* */` comments) prints no drift warning; loading — normal Sphinx progress lines; error — none: drift never fails the build (exit 0 without `-W`); success — one `WARNING: template dependency drift: '<_template/KEY/REL.typ>' pins @preview/<package>:<template versions>, but _typsphinx/deps.typ has @preview/<package>:<deps version>` line per mismatched (file, package), in sorted (file, package) order, and the build still reports `build succeeded`
Walkthrough:
1. In a fresh worktree run `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`.
2. Copy `examples/basic` to `"$d/p"`. Copy `typsphinx/templates/base.typ` to `"$d/p/_tpl/base.typ"`, then append to that copy the lines `#import "@preview/gentle-clues:1.2.0": *` and `// #import "@preview/codly:1.0.0": *`. Append `typst_template = "_tpl/base.typ"` to `"$d/p/conf.py"`.
3. Run `LC_ALL=C uv run sphinx-build -E -b typst "$d/p" "$d/out" 2> "$d/err.txt"; echo "rc=$?"`. Confirm `rc=0`, and confirm `grep 'template dependency drift' "$d/err.txt"` prints exactly one line naming `'_template/typst/base.typ'`, `gentle-clues`, `1.2.0`, and `1.3.1`, with no line for codly.
4. Change the appended pin to `1.3.1`, rebuild into a new outdir, and confirm `grep -c 'template dependency drift'` prints 0.

### typsphinx documentation (configuration and templates pages) — T005

Criteria: SC6
Entry: `uv run sphinx-build -b html docs/source <out>`, then open `<out>/user_guide/configuration.html` and `<out>/user_guide/templates.html`; also CHANGELOG.md and CLAUDE.md at the repository root
States: empty — before this milestone, neither page mentions `typst_dependencies` or `/_typsphinx/deps.typ`; loading — n/a (static pages); error — a broken cross-reference or a malformed rST section shows as a Sphinx warning in the docs build output; success — the configuration page has a `typst_dependencies` entry (path rule, one global file, verbatim copy, default when unset, build stops on a missing or empty value); the templates page has the `deps.typ` contract section (path, all sixteen exported names, plain statement that only the default versions are supported and a replaced file is at the user's risk) and tells template authors to import names from `/_typsphinx/deps.typ` instead of pinning versions; CHANGELOG `[Unreleased]` and CLAUDE.md describe the change
Walkthrough:
1. In a fresh worktree run `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs`.
2. Run `d=$(mktemp -d); uv run sphinx-build -b html docs/source "$d/html"`, then open `"$d/html/user_guide/configuration.html"` and read the `typst_dependencies` entry against SC6.
3. Open `"$d/html/user_guide/templates.html"` and find the `/_typsphinx/deps.typ` section. Check that it lists `codly`, `codly-init`, `codly-languages`, `mi`, `mitex`, `render`, `abstract`, `danger`, `error`, `info`, `memo`, `notify`, `task`, `tip`, `warning`, and `typsphinx-init`, and that it states a replaced `deps.typ` is unsupported and at the user's risk (N4).
4. Open CHANGELOG.md: `## [Unreleased]` records the single-source change, `typst_dependencies`, and the drift warning. Open CLAUDE.md: the `@preview` section names `typsphinx/typst_deps.py` as the one source.

## Intent coverage

| Criterion | Task | Acceptance |
|-----------|------|------------|
| SC1 | T001 | AC1 |
| SC2 | T001 | AC2 |
| SC2 | T001 | AC3 |
| SC2 | T001 | AC4 |
| SC2 | T002 | AC6 |
| SC2 | T002 | AC7 |
| SC3 | T002 | AC1 |
| SC3 | T002 | AC2 |
| SC3 | T002 | AC3 |
| SC3 | T002 | AC4 |
| SC3 | T002 | AC5 |
| SC4 | T003 | AC1 |
| SC4 | T003 | AC2 |
| SC4 | T003 | AC3 |
| SC4 | T003 | AC4 |
| SC4 | T003 | AC5 |
| SC4 | T003 | AC7 |
| SC5 | T004 | AC1 |
| SC5 | T004 | AC2 |
| SC5 | T004 | AC3 |
| SC5 | T004 | AC4 |
| SC6 | T005 | AC1 |
| SC6 | T005 | AC2 |
| SC6 | T005 | AC3 |
| SC6 | T005 | AC4 |
| SC6 | T005 | AC5 |
| SC6 | T005 | AC6 |
| SC7 | T005 | AC7 |

## Held-out checks

| Edge | Task | Test |
|------|------|------|
| E2 | T002 | tests/test_typst_dependencies_gate.py |
| E3 | T001 | tests/test_deps_output_gate.py |
| E4 | T002 | tests/test_typst_dependencies_gate.py |
| E6 | T002 | tests/test_typst_dependencies_gate.py |
| E7 | T003 | tests/test_template_dependency_drift_gate.py |
| E8 | T003 | tests/test_template_dependency_drift_gate.py |
| E9 | T003 | tests/test_template_dependency_drift_gate.py |
| E10 | T003 | tests/test_template_dependency_drift_gate.py |

## Dependency notes

- T002 depends on T001 (data plus shared files). T002 consumes `typsphinx/typst_deps.py`'s `DEPS_OUTPUT_DIR`, `DEPS_FILENAME`, and `render_default_deps()`, and extends `TypstBuilder._write_dependencies_file()`, which T001 defines (Interface contract K1, K2). Both tasks edit `typsphinx/builder.py`, so they run as two layers of wave 1. A reviewer sees `_write_dependencies_file` called first in `TypstBuilder.finish()` at T002's base.
- T003 depends on T001 and T002 (data plus shared files). T003 adds `strip_typst_comments()` and `extract_preview_versions()` to `typsphinx/typst_deps.py` and reads `DEFAULT_PACKAGES` from it (K1). It reads the effective `<outdir>/_typsphinx/deps.typ` that `_write_dependencies_file()` leaves (K2), and it branches on `config.typst_dependencies` (K4) to choose between default versions and the user's file. T003 edits `typsphinx/builder.py` after T001 and T002.
- T004 depends on T001 (data plus a shared file). T004's templates may import names from `/_typsphinx/deps.typ`, which exists only once T001 writes it (K3). T004 replaces the example-pin test that T001 rewrote in `tests/test_preview_version_sync.py` to compare against `DEFAULT_PACKAGES`.
- T005 depends on T001, T002, T003, and T004. Three parts are data. First, its docs gate checks the documented `deps.typ` exports against the default file T001 generates (K3). Second, it documents the `typst_dependencies` rules T002 implements (K4). Third, it quotes the drift-warning format T003 emits (K5). Its CLAUDE.md text also names the SC5 no-pin test that T004 adds to `tests/test_preview_version_sync.py`. The fourth part is a landed effect. T005 owns SC7, whose evidence is the full suite plus black/ruff/mypy on a HEAD that contains every other task. A reviewer sees the T003 and T004 landing commits in T005's base.
- T003 and T004 are independent: they share no file and exchange nothing. T004's pins match the default versions, so they produce no drift warning before or after T003.
- `.project/` paths are not matched by any product ignore rule (`git check-ignore -v .project/plan/PLAN.md .project/tasks/T001-x.md .project/build/x` printed nothing at planning time, per LESSONS 001), so no task owns `.gitignore`.
- SC2 reading for the project docs: a planning-time `-b typst` build of `docs/source` put the literal `@preview/codly:1.3.0` into `changelog.typ`. That text is CHANGELOG.md history prose rendered as escaped text, not an import. T001's Verify therefore checks the docs output for no `#import "@preview/<five>:` line, and checks examples and fixtures with the plain literal grep. INTENT correction C2 (owner ruling, 2026-11-03) now states SC2 in exactly this form, so the final reviewer judges SC2 as written.
- Planning-time measurements (scratch copy of HEAD 79ed090e, not evidence for any task): a minimal prototype of the T001 preamble change failed 33 tests in 15 files, all of them in T001's `files`, and the render gates for codly, admonitions, math, and graphviz passed. A duplicate `#import "/_typsphinx/deps.typ": *` compiled. gentle-clues 1.3.0 compiled `abstract`, `danger`, `error`, `info`, `memo`, `notify`, `task`, `tip`, and `warning` under typst-py 0.15.0.
