---
phase: 45-documentation-currency-carried-hygiene
plan: 03
subsystem: docs
tags: [sphinx, typst-documents, quickstart, readme, docs-gate]

# Dependency graph
requires:
  - phase: 44-typst-documents-default-derivation-builder-input-hardening
    provides: "CONF-08's _default_typst_documents() derivation (root_doc/project/author -> make_filename_from_project stem)"
  - phase: 44.2-typst-documents-title-and-author-consumption
    provides: "configuration.rst's title/author element-list prose (items 3 and 4), left untouched by this plan"
provides:
  - "README.md Quick Start section names typst_documents, states it need not be set, states the derived <project>.typ stem shape, states explicit-wins precedence, states which documents become PDFs"
  - "README.md Configuration Options bullet no longer claims typst_documents is mandatory for PDF output"
  - "docs/source/quickstart.rst names build/pdf/myproject.pdf as the real output of its own steps, replacing the stale build/pdf/index.pdf"
  - "docs/source/user_guide/configuration.rst documents the derived default ahead of the typst_documents code block"
  - "tests/test_quickstart_docs_gate.py -- real-sphinx-build gate binding all of the above to a measured build"
affects: [46-v0.7.1-release-prep]

# Actuals (#2632)
actuals:
  tokens: 4120
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Real-sphinx-build docs gate (TestQuickstartFirstPdfGate/TestPublishedQuickstartTextMatchesBuild) mirroring tests/test_default_typst_documents_gate.py's must-SUCCEED pattern, plus a no-skip prose-binding class"

key-files:
  created:
    - tests/test_quickstart_docs_gate.py
    - tests/fixtures/quickstart_docs_gate/conf.py
    - tests/fixtures/quickstart_docs_gate/index.rst
  modified:
    - README.md
    - docs/source/quickstart.rst
    - docs/source/user_guide/configuration.rst

key-decisions:
  - "Task 1's work (real-build gate) was adopted via git cherry-pick from an abandoned worktree branch rather than redone, since it was byte-identical and additive-only against this worktree's own base"
  - "quickstart.rst's 'Your First PDF' flow gained an explicit conf.py project-setting step (previously absent) so the reader can see where the derived myproject.pdf filename comes from, per the plan's instruction not to present the stem as a constant"
  - "ruff's venv binary (installed by uv sync) fails to execute under this NixOS sandbox (dynamically-linked ELF, no interpreter); worked around by running nixpkgs' own ruff build via `nix-shell -p ruff --run \"ruff check .\"`, which passed clean -- a pre-existing environment gap, not a plan defect"

requirements-completed: [DOC-11]

coverage:
  - id: D1
    description: "README.md Quick Start states all five ROADMAP SC#1 facts about typst_documents (what it does, that it's optional, the derived <project>.typ stem shape, explicit-wins precedence, which documents become PDFs) and no longer claims it is mandatory"
    requirement: "DOC-11"
    verification:
      - kind: integration
        ref: "tests/test_quickstart_docs_gate.py::TestPublishedQuickstartTextMatchesBuild::test_readme_quickstart_explains_typst_documents"
        status: pass
      - kind: integration
        ref: "tests/test_quickstart_docs_gate.py::TestPublishedQuickstartTextMatchesBuild::test_readme_no_longer_calls_typst_documents_mandatory"
        status: pass
    human_judgment: false
  - id: D2
    description: "docs/source/quickstart.rst's 'Your First PDF' step names the output path a real -b typstpdf build of its own steps actually produces (build/pdf/myproject.pdf), not the stale build/pdf/index.pdf"
    requirement: "DOC-11"
    verification:
      - kind: integration
        ref: "tests/test_quickstart_docs_gate.py::TestPublishedQuickstartTextMatchesBuild::test_quickstart_names_the_measured_output_path"
        status: pass
      - kind: integration
        ref: "tests/test_quickstart_docs_gate.py::TestQuickstartFirstPdfGate (both tests)"
        status: pass
    human_judgment: false
  - id: D3
    description: "docs/source/user_guide/configuration.rst's Typst Documents section states the setting is optional, describes the derived entry, and states an explicit value (including an empty list) wins -- without altering Phase 44.2's title/author element-list text"
    requirement: "DOC-11"
    verification:
      - kind: other
        ref: "git diff 8c74b85 -- docs/source/user_guide/configuration.rst (pure insertion ahead of the code block; items 3/4 untouched)"
        status: pass
      - kind: e2e
        ref: "uv run python -m sphinx -b html docs/source <tmp> (exit 0, no WARNING mentioning quickstart or configuration)"
        status: pass
    human_judgment: false

duration: ~20min (this session; Task 1's original authoring time is not tracked -- it was produced by a prior interrupted session and adopted via cherry-pick)
completed: 2026-08-10
status: complete
---

# Phase 45 Plan 03: Documentation Currency for typst_documents Summary

**README, quickstart.rst, and configuration.rst now describe CONF-08's actual derived-default behaviour, bound to a real `-b typstpdf` build of the Quick Start's own steps via a standing no-skip gate.**

## Performance

- **Duration:** ~20 min (this session, Tasks 2-3; Task 1 adopted via cherry-pick from a prior interrupted session)
- **Tasks:** 3 (Task 1 adopted, not redone; Tasks 2-3 executed fresh)
- **Files modified:** 6 (3 created by Task 1, 3 modified by Tasks 2-3)

## Accomplishments
- Real-`sphinx-build` gate (`tests/test_quickstart_docs_gate.py`) mirrors the published Quick Start's own project/author values and asserts the emitted filename is `myproject.pdf`/`myproject.typ`, never `index.pdf`/`index.typ` (Task 1, adopted)
- README.md's Quick Start section now states all five ROADMAP SC#1 facts about `typst_documents`, and its Configuration Options bullet no longer claims the setting is mandatory for PDF output (Task 2)
- `docs/source/quickstart.rst`'s "Your First PDF" flow now names the real output path (`build/pdf/myproject.pdf`) its own steps produce, with a `project`-setting step added so the reader sees where the derived name comes from (Task 3)
- `docs/source/user_guide/configuration.rst`'s Typst Documents section now documents the derived default ahead of the code block, without touching Phase 44.2's title/author element-list prose (Task 3)
- All 5 gate assertions green; the two build tests were green from Task 1, the three prose-binding tests turned green as Tasks 2-3 landed the corrections they check

## Task Commits

Task 1 was completed by a prior interrupted executor session and adopted here via `git cherry-pick`, not redone:

1. **Task 1: Real-build gate for the published Quick Start's own steps** - `687fc7d` (test) -- adopted via cherry-pick of the original `ed30d93`
2. **Task 2: Correct the README's Quick Start and Configuration Options** - `7ed6457` (docs)
3. **Task 3: Correct quickstart.rst's output path and add the derived default to configuration.rst** - `d6fe2d9` (docs)

## Files Created/Modified
- `tests/test_quickstart_docs_gate.py` - `TestQuickstartFirstPdfGate` (real build, must succeed) + `TestPublishedQuickstartTextMatchesBuild` (no-skip prose-binding assertions)
- `tests/fixtures/quickstart_docs_gate/conf.py` - mirrors the published Quick Start's `project`/`author`/`release` values, deliberately no `typst_documents` line
- `tests/fixtures/quickstart_docs_gate/index.rst` - reproduces the Quick Start's sample document
- `README.md` - new `#### typst_documents` subsection under Quick Start's Basic Configuration (all five SC#1 facts); Configuration Options bullet rewritten to state the setting is optional
- `docs/source/quickstart.rst` - "Your First PDF" step 3 corrected to `build/pdf/myproject.pdf` with a new `project`-setting step and explanatory note; "Configuration Options" gained an optional/derived-default sentence cross-linking to `user_guide/configuration`
- `docs/source/user_guide/configuration.rst` - new paragraph ahead of the `typst_documents` code block describing the derived default and explicit-wins precedence

## Decisions Made
- Adopted Task 1's commit via `git cherry-pick` rather than re-authoring the fixture/test module, since it applied cleanly (same base, additive-only, 262 insertions / 0 deletions)
- Added a `project = "My Project"` conf.py step to quickstart.rst's "Your First PDF" flow (it previously set no project name before naming an output path), per the plan's instruction that the derived filename must not be presented as a constant
- Ran `ruff check .` via `nix-shell -p ruff` rather than the `uv`-installed venv binary, which fails to execute under this NixOS sandbox (`Could not start dynamically linked executable`) -- a pre-existing environment gap unrelated to this plan's changes; nixpkgs' own ruff build reported "All checks passed!" against the same tree

## Deviations from Plan

None - plan executed exactly as written. The one environment workaround (ruff invocation via `nix-shell`) did not change any code or documentation content; it only substituted the tool binary used to run an unmodified lint command that the venv-installed binary could not execute in this sandbox.

## Issues Encountered
- The worktree's `uv sync --extra dev` alone does not install `sphinx-autodoc-typehints`/`furo`/`sphinx-intl` (the `docs` extras group); the `-b html`/`-b typstpdf` verification builds needed `uv sync --extra dev --extra docs` first. Resolved by installing the additional extra; no code change required.
- The venv's `ruff` binary is a dynamically-linked ELF that this NixOS sandbox refuses to exec directly (`Could not start dynamically linked executable`). Resolved by running `nix-shell -p ruff --run "ruff check ."` instead, which uses nixpkgs' own properly-linked build against the identical unmodified source tree; result was clean.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- DOC-11 is complete: README, quickstart.rst, and configuration.rst all describe CONF-08's actual behaviour, bound to a real build via a standing no-skip gate that will fail loudly if the docs and the measured build ever diverge again.
- `docs/source/user_guide/templates.rst` was left untouched (verified via `git diff` against the plan's base commit) -- its DOC-13 custom-template contract correction remains scoped to Phase 45.1.
- No blockers for Phase 45.1 or Phase 46.

## Self-Check: PASSED

All 7 claimed files exist on disk (`tests/test_quickstart_docs_gate.py`,
`tests/fixtures/quickstart_docs_gate/conf.py`,
`tests/fixtures/quickstart_docs_gate/index.rst`, `README.md`,
`docs/source/quickstart.rst`, `docs/source/user_guide/configuration.rst`,
this SUMMARY). All 3 claimed commit hashes (`687fc7d`, `7ed6457`, `d6fe2d9`)
are present in `git log --oneline --all`.

---
*Phase: 45-documentation-currency-carried-hygiene*
*Completed: 2026-08-10*
