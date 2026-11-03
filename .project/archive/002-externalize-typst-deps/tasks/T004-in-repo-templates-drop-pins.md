---
id: T004
title: Remove the five-package pins and top-level codly init from the repository's own templates and samples
wave: 2
deps: [T001]
status: done
agent: build_T004
base: 99b32c62d2369f3ced4ec6b270a4904502e51939
worktree: null
task_branch: null
files:
  - docs/source/_typst/custom_template.typ
  - examples/advanced/_typst/custom.typ
  - examples/advanced/conf.py
  - examples/advanced/README.md
  - tests/fixtures/admonition_greyscale_probe/_templates/minimal.typ
  - tests/fixtures/typst_lang_gate/custom_template_lang/_templates/custom.typ
  - tests/fixtures/typst_lang_gate/srcdir_shadow_lang/_typst/base.typ
  - tests/test_preview_version_sync.py
  - tests/test_typst_lang_gate.py
  - tests/test_admonition_greyscale_pipeline.py
---

# T004 — Remove the five-package pins and top-level codly init from the repository's own templates and samples

## Context

After T001, every content file and wrapper gets the five packages and codly init from `/_typsphinx/deps.typ`. The repository's own templates still carry their own `#import "@preview/<five>:<version>"` lines and a top-level `#show: codly-init.with()` / `#codly(languages: codly-languages)`. Those top-level show rules never reached included content anyway (measured in define: top-level show rules in a template file do not cross `#include`). Their template functions use none of the five packages' names. The pins sit in five templates: `docs/source/_typst/custom_template.typ:39-50`, `examples/advanced/_typst/custom.typ:12-19`, `tests/fixtures/admonition_greyscale_probe/_templates/minimal.typ:16-23`, `tests/fixtures/typst_lang_gate/custom_template_lang/_templates/custom.typ:13-20`, and `tests/fixtures/typst_lang_gate/srcdir_shadow_lang/_typst/base.typ:18-25`. The SC5 grep covers all of `examples/`, so the commented `typst_package_imports` sample at `examples/advanced/conf.py:93-97` and `examples/advanced/README.md:258-261`, which contains `@preview/codly:1.3.0` and `@preview/gentle-clues:1.3.1`, must change too. SYNTHESIS settled that `tests/test_preview_version_sync.py` hosts the SC5 no-pin check, replacing `test_example_templates_match_canonical_versions`, which T001 left comparing example pins against `DEFAULT_PACKAGES`.

## Approach

- Each template either imports nothing from the five or imports names from `/_typsphinx/deps.typ`. Remove the pinned imports and the top-level codly init lines, and update nearby comments that point at `tests/test_preview_version_sync.py`'s old lockstep rule so they stay true.
- `tests/fixtures/typst_lang_gate/srcdir_shadow_lang/_typst/base.typ` is a deliberate near-copy of the bundled `base.typ`, used by the PATH-shadowing test in `tests/test_typst_lang_gate.py` (around lines 590-650). Mirror the new bundled `base.typ` header (the deps import, no pins, no top-level init), and keep whatever `lang` behaviour and marker that test uses to tell the shadow from the bundled default (INTENT Risk 2).
- The `examples/advanced` `typst_package_imports` sample: `typst_package_imports` takes item names for the `typst_package` import (`typsphinx/template_engine.py:591-593`), not `#import` lines. Rewrite the commented sample in both `conf.py` and `README.md` to a correct, pin-free use, or remove it. Do not change `typst_package` / `typst_package_imports` behaviour or names (veto).
- In `tests/test_preview_version_sync.py`, replace `test_example_templates_match_canonical_versions` with an SC5 test. It walks `docs/source/_typst/`, `examples/`, `tests/fixtures/admonition_greyscale_probe/_templates/`, and `tests/fixtures/typst_lang_gate/` and fails on any `@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):` match. Keep T001's SC1 tests in that file unchanged.
- Rendered output must not change for these projects (N1/SC2): the docs PDF, the examples, the lang-gate PDFs, and the greyscale probe still build with the same assertions.

## Interface contract

- K3 — Every `typst`/`typstpdf` build's outdir contains `<outdir>/_typsphinx/deps.typ`, imported by the root-absolute path `/_typsphinx/deps.typ` (compile root = outdir). The default file exports `codly`, `codly-init`, `codly-languages`, `mi`, `mitex`, `render`, `abstract`, `danger`, `error`, `info`, `memo`, `notify`, `task`, `tip`, `warning`, and `typsphinx-init`. Every content `.typ` and wrapper `.typ` contains the lines `#import "/_typsphinx/deps.typ": *` and `#show: typsphinx-init`.

## Intent coverage

- SC5

## Acceptance criteria

1. SC5: `grep -rnE '@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):' docs/source/_typst/ examples/ tests/fixtures/admonition_greyscale_probe/_templates/ tests/fixtures/typst_lang_gate/` prints nothing.
2. SC5: each of the five templates either imports nothing from the five packages or imports names only from `/_typsphinx/deps.typ`, and none has a top-level `codly-init` or `codly(languages:` line. `tests/test_typst_lang_gate.py` (including the srcdir-shadow cases) and `tests/test_admonition_greyscale_pipeline.py` pass.
3. SC5: `tests/test_preview_version_sync.py` contains the no-pin test over the four directories. It fails if a pinned import is reintroduced in any of them, and `test_example_templates_match_canonical_versions` is gone.
4. SC5: `docs/source` builds with `-b typstpdf` to a PDF, and `examples/basic` and `examples/advanced` build with `-b typstpdf` to their PDFs, checked in Verify.

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && ! grep -rnE '@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):' docs/source/_typst/ examples/ tests/fixtures/admonition_greyscale_probe/_templates/ tests/fixtures/typst_lang_gate/ && ! grep -nE 'codly-init|codly\(languages' docs/source/_typst/custom_template.typ examples/advanced/_typst/custom.typ tests/fixtures/admonition_greyscale_probe/_templates/minimal.typ tests/fixtures/typst_lang_gate/custom_template_lang/_templates/custom.typ tests/fixtures/typst_lang_gate/srcdir_shadow_lang/_typst/base.typ && LC_ALL=C uv run pytest tests/test_preview_version_sync.py tests/test_typst_lang_gate.py tests/test_admonition_greyscale_pipeline.py -o addopts="" -q && d=$(mktemp -d) && LC_ALL=C uv run sphinx-build -q -E -b typstpdf examples/basic "$d/basic" && test -f "$d/basic/basic-example.pdf" && LC_ALL=C uv run sphinx-build -q -E -b typstpdf examples/advanced "$d/adv" && test -f "$d/adv/advanced-example.pdf" && LC_ALL=C uv run sphinx-build -q -E -b typstpdf docs/source "$d/docs" && ls "$d"/docs/*.pdf
```

Heavy: yes

## Log

- 2026-11-03 — created by planner
- 2026-11-03 — build_T004: removed the four `@preview/<five>` pins and the top-level `codly-init` / `codly(languages:` lines from the five templates, replacing them with `#import "/_typsphinx/deps.typ": *` (mirrors bundled base.typ; srcdir-shadow fixture keeps its CONF-12/D-I header and `lang` signature); rewrote the stale lockstep comment in examples/advanced/_typst/custom.typ; rewrote the commented `typst_package_imports` sample in examples/advanced/conf.py and README.md to a pin-free item-name use with `typst_package`; in tests/test_preview_version_sync.py replaced `test_example_templates_match_canonical_versions` (and its now-unused helper/regex) with `test_repo_templates_pin_none_of_the_five` over the four directories plus `test_no_pin_check_catches_a_reintroduced_pin`; SC1 tests unchanged. tests/test_typst_lang_gate.py and tests/test_admonition_greyscale_pipeline.py needed no change. Verify: pass (both greps empty; pytest 29 passed; examples/basic, examples/advanced, docs/source typstpdf PDFs produced). black/ruff clean on changed .py.
- 2026-11-03 — orchestrator Verify (sidecar gsd-path-verify/task-t004-verify): pass, exit 0; output tail:
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
   + typsphinx==0.9.8 (from file:///home/yuta/.gsd-path/projects/4018706f853274cd7713143cf7ba094e230867e5ad2bfc5891d0cd69027eb98b/4b529697c911aff5766d6b9c03f122ba2ed9565d87a00e2f51ea62f3fd0642ec/verify/task-t004-verify)
   + typst==0.15.0
   + urllib3==2.7.0
   + uv==0.13.6
   + virtualenv==21.5.1
  WARNING: html_static_path entry '_static' does not exist
  ```
- 2026-11-03 — orchestrator regression Verify of T001 (sidecar gsd-path-verify/task-t004-verify): pass, exit 0; output tail:
  ```
  ........................................................................ [ 25%]
  ........................................................................ [ 51%]
  ........................................................................ [ 77%]
  ..............................................................           [100%]
  278 passed in 18.86s
  /tmp/tmp.30VKJpBaZ6/docs/typsphinx.pdf
  Resolved 95 packages in 0.55ms
  Checked 94 packages in 0.48ms
  WARNING: html_static_path entry '_static' does not exist
  ```
